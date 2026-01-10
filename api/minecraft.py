import re
import asyncio
import aiomcrcon
import httpx
from mcstatus import JavaServer
from typing import Optional, List, Union
from models import ServerStatus, WorldState, PlayerState, PlayerInfo, WhitelistState, ModInfo
import logging

logger = logging.getLogger("minecraft-admin")

class MinecraftService:
    def __init__(self, host: str, game_port: int, rcon_port: int, rcon_password: str):
        self.host = host
        self.game_port = game_port
        self.rcon_port = rcon_port
        self.rcon_password = rcon_password
        self._ping_successful = False
        self._rcon_successful = False
        self._whitelist_enabled = False
        self._whitelist_status_detected = False
        self._rcon_lock = asyncio.Lock()
        self._forge_version: Optional[str] = None
        self._mods: List[ModInfo] = []
        self._forge_detected = False
        self._avatar_cache: Dict[str, str] = {} # player_name -> avatar_url
        self._http_client = httpx.AsyncClient(timeout=5.0)

    async def close(self):
        """Closes the persistent HTTP client."""
        await self._http_client.aclose()

    async def _get_world_uptime(self) -> Optional[str]:
        """Calculates 'Real Uptime' based on Minecraft gametime ticks."""
        try:
            resp = await self._send_rcon("time query gametime")
            match = re.search(r"The time is (\d+)", resp)
            if not match:
                return None
            
            ticks = int(match.group(1))
            # 20 ticks = 1 second
            total_seconds = ticks // 20
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            
            parts = []
            if days > 0:
                parts.append(f"{days} day{'s' if days != 1 else ''}")
            if hours > 0 or not parts:
                parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            
            return ", ".join(parts)
        except Exception:
            return None

    async def _send_rcon(self, command: str) -> str:
        async with self._rcon_lock:
            client = aiomcrcon.Client(self.host, self.rcon_port, self.rcon_password)
            try:
                await asyncio.wait_for(client.connect(), timeout=5.0)
                if not self._rcon_successful:
                    logger.info(f"Successfully established RCON connection to {self.host}:{self.rcon_port}")
                    self._rcon_successful = True
                response, _ = await client.send_cmd(command)
                return response
            except Exception as e:
                self._rcon_successful = False
                raise e
            finally:
                await client.close()

    async def get_server_status(self) -> ServerStatus:
        uptime = await self._get_world_uptime()
        try:
            server = await JavaServer.async_lookup(f"{self.host}:{self.game_port}")
            status = await server.async_status()
            if not self._ping_successful:
                logger.info(f"Successfully Pinged Minecraft server at {self.host}:{self.game_port}")
                self._ping_successful = True
            return ServerStatus(
                online=True,
                version=status.version.name,
                forge_version=self._forge_version,
                mods=self._mods,
                motd=status.motd.to_plain(),
                uptime=uptime
            )
        except Exception as e:
            self._ping_successful = False
            # Fallback to RCON if Ping fails
            try:
                # We use 'list' as a basic health check
                await self._send_rcon("list")
                return ServerStatus(
                    online=True,
                    version="Unknown (RCON Only)",
                    forge_version=self._forge_version,
                    mods=self._mods,
                    motd="Minecraft Server",
                    uptime=uptime
                )
            except Exception as rcon_error:
                return ServerStatus(
                    online=False,
                    version="Unknown",
                    motd="Offline",
                    uptime=uptime,
                    error=str(e)
                )

    async def get_world_state(self) -> Optional[WorldState]:
        try:
            time_resp = await self._send_rcon("time query daytime")
            # "The time is 6000"
            time_match = re.search(r"The time is (\d+)", time_resp)
            if not time_match:
                return None
            
            ticks = int(time_match.group(1))
            
            # Days
            day_resp = await self._send_rcon("time query day")
            day_match = re.search(r"The time is (\d+)", day_resp)
            days = int(day_match.group(1)) if day_match else 0

            # Formatting
            hours = (ticks // 1000 + 6) % 24
            minutes = int((ticks % 1000) * 60 / 1000)
            time_formatted = f"{hours:02d}:{minutes:02d}"

            # Phase (Based on official Minecraft Wiki: 0:00=06:00, 6000=12:00, etc.)
            if 23000 <= ticks:
                phase = "Dawn"
            elif 0 <= ticks < 12000:
                phase = "Day"
            elif 12000 <= ticks < 13000:
                phase = "Dusk"
            else:
                phase = "Night"

            # Daylight Cycle
            cycle_resp = await self._send_rcon("gamerule doDaylightCycle")
            daylight_cycle = "true" in cycle_resp.lower()

            # Weather Cycle
            weather_cycle_resp = await self._send_rcon("gamerule doWeatherCycle")
            weather_cycle = "true" in weather_cycle_resp.lower()

            return WorldState(
                time=ticks,
                time_formatted=time_formatted,
                phase=phase,
                days=days,
                daylight_cycle=daylight_cycle,
                weather_cycle=weather_cycle
            )
        except Exception:
            return None

    async def _get_whitelisted_names(self) -> set:
        try:
            # "There are 2 whitelisted players: player1, player2"
            response = await self._send_rcon("whitelist list")
            if ":" not in response:
                return set()
            
            names_part = response.split(":", 1)[1].strip()
            if not names_part:
                return set()
            
            return {n.strip() for n in names_part.split(",")}
        except Exception:
            return set()

    async def get_player_state(self) -> Optional[PlayerState]:
        try:
            # Fetch whitelist first
            whitelisted_names = await self._get_whitelisted_names()

            # Use 'list' command
            response = await self._send_rcon("list")
            # "There are 0 of a max of 20 players online: "
            match = re.search(r"There are (\d+) of a max of (\d+) players online", response)
            if not match:
                return None
            
            online = int(match.group(1))
            max_players = int(match.group(2))
            
            # Extract player list if available after the colon
            player_list = []
            if ":" in response:
                names_part = response.split(":", 1)[1].strip()
                if names_part:
                    names = [n.strip() for n in names_part.split(",")]
                    player_list = []
                    for name in names:
                        avatar_url = await self.fetch_player_avatar(name)
                        player_list.append(PlayerInfo(
                            name=name,
                            whitelisted=(name in whitelisted_names),
                            avatar_url=avatar_url
                        ))
            
            return PlayerState(
                online=online,
                max=max_players,
                list=player_list
            )
        except Exception:
            return None

    async def get_whitelist_state(self) -> Optional[WhitelistState]:
        try:
            # "There are 2 whitelisted players: player1, player2"
            # OR "Whitelist is currently enabled: ..." (Paper/Spigot)
            response = await self._send_rcon("whitelist list")
            
            # 1. Attempt detection from 'whitelist list' response
            lowered = response.lower()
            if "whitelist is currently enabled" in lowered or "whitelist is enabled" in lowered:
                self._whitelist_enabled = True
                self._whitelist_status_detected = True
            elif "whitelist is currently disabled" in lowered or "whitelist is disabled" in lowered:
                self._whitelist_enabled = False
                self._whitelist_status_detected = True
            
            # 2. If detection failed (likely Vanilla), perform a one-time probe
            if not self._whitelist_status_detected and self._rcon_successful:
                # We probe by attempting to turn it ON.
                # If it says 'already', it was ON. If it says 'turned on', it was OFF (so we turn it back off).
                probe_resp = await self._send_rcon("whitelist on")
                if "already" in probe_resp.lower():
                    self._whitelist_enabled = True
                else:
                    # It was off, we switched it on, now switch it back off
                    await self._send_rcon("whitelist off")
                    self._whitelist_enabled = False
                
                self._whitelist_status_detected = True

            # 3. Parse members
            player_members = []
            if ":" in response:
                names_part = response.split(":", 1)[1].strip()
                if names_part:
                    names = sorted([n.strip() for n in names_part.split(",")])
                    for name in names:
                        avatar_url = await self.fetch_player_avatar(name)
                        player_members.append(PlayerInfo(
                            name=name, 
                            whitelisted=True,
                            avatar_url=avatar_url
                        ))
            
            return WhitelistState(
                enabled=self._whitelist_enabled,
                members=player_members
            )
        except Exception:
            return None

    async def add_whitelist(self, name: str) -> tuple[bool, str]:
        response = await self._send_rcon(f"whitelist add {name}")
        success = "Added" in response or "already" in response
        return success, response

    async def remove_whitelist(self, name: str) -> tuple[bool, str]:
        response = await self._send_rcon(f"whitelist remove {name}")
        success = "Removed" in response
        return success, response

    async def toggle_whitelist(self, enabled: bool) -> tuple[bool, str]:
        command = "whitelist on" if enabled else "whitelist off"
        response = await self._send_rcon(command)
        # "Whitelist is now turned on" or "Whitelist is already on"
        # "Whitelist is now turned off" or "Whitelist is already off"
        success = "on" in response.lower() or "off" in response.lower()
        if success:
            self._whitelist_enabled = enabled
        return success, response

    async def toggle_daylight_cycle(self, enabled: bool) -> bool:
        command = f"gamerule doDaylightCycle {str(enabled).lower()}"
        response = await self._send_rcon(command)
        return "true" in response.lower() or "false" in response.lower() or "changed" in response.lower()

    async def toggle_weather_cycle(self, enabled: bool) -> bool:
        command = f"gamerule doWeatherCycle {str(enabled).lower()}"
        response = await self._send_rcon(command)
        return "true" in response.lower() or "false" in response.lower() or "changed" in response.lower()

    async def set_weather(self, weather_type: str, duration: Optional[int] = None) -> bool:
        """Sets the weather. Duration is in ticks by default in modern MC (1.19.4+).
        If no unit is specified, Java Edition defaults to ticks.
        """
        command = f"weather {weather_type}"
        if duration is not None:
            command += f" {duration}"
        
        response = await self._send_rcon(command)
        return "set" in response.lower() or "changing" in response.lower() or "clear" in response.lower() or "rain" in response.lower() or "thunder" in response.lower()

    async def run_command(self, command: str) -> str:
        return await self._send_rcon(command)

    async def get_gamerule(self, rule_id: str) -> Union[bool, int, str, None]:
        """Fetches the value of a specific gamerule via RCON."""
        try:
            response = await self._send_rcon(f"gamerule {rule_id}")
            logger.debug(f"Gamerule {rule_id} RCON response: {response}")

            # Check for explicit rejections
            if "incorrect argument" in response.lower() or "unknown or incomplete" in response.lower():
                return "unsupported"

            # Responses: "Gamerule doFireTick is currently: true" or "... is currently: 1"
            if "true" in response.lower():
                return True
            if "false" in response.lower():
                return False
            
            # Handle numbers
            match = re.search(r"currently (?:set to: )?(\d+)", response)
            if match:
                return int(match.group(1))
            
            logger.warning(f"Unexpected response for gamerule {rule_id}: {response}")
            return None
        except Exception as e:
            logger.error(f"Error fetching gamerule {rule_id}: {e}")
            return None

    async def set_gamerule(self, rule_id: str, value: Union[bool, int]) -> bool:
        """Sets the value of a specific gamerule via RCON."""
        val_str = str(value).lower() if isinstance(value, bool) else str(value)
        command = f"gamerule {rule_id} {val_str}"
        response = await self._send_rcon(command)
        return "true" in response.lower() or "false" in response.lower() or "changed" in response.lower() or str(value) in response

    async def broadcast_message(self, message: str) -> bool:
        """Sends a message to all players via RCON 'say'."""
        response = await self._send_rcon(f"say {message}")
        # 'say' command usually doesn't return a specific success confirmation pattern like 'changed'
        # but if we get a response and no exception, it's generally successful.
        return True

    async def detect_forge_and_mods(self) -> bool:
        """Detects if the server is a Forge server and fetches the mods list."""
        if self._forge_detected:
            return True
            
        try:
            # Use 'forge mods' which is a Forge-only command
            response = await self._send_rcon("forge mods")
            if "unknown or incomplete" in response.lower() or "incorrect argument" in response.lower():
                self._forge_detected = True # We detected it's NOT forge (by rejection)
                return False
                
            self._forge_detected = True
            logger.info("Detected Forge server. Parsing mods list...")
            
            # Example: 
            # Mod List: 
            # • mods_folder grappling_hook_mod-1.20.1-1.20.1-v13.jar : grapplemod (1.20.1-v13) - 1
            # • minecraft forge-1.20.1-47.4.10-universal.jar : forge (47.4.10) - 1
            
            lines = response.splitlines()
            mods = []
            
            for line in lines:
                # Basic cleanup
                clean_line = line.strip()
                if not clean_line or ":" not in clean_line:
                    continue
                
                # Split into source/jar part and mod-info part
                parts = clean_line.split(":", 1)
                source_part = parts[0].strip()
                info_part = parts[1].strip()
                
                # Clean up source_part (remove bullet point etc)
                source_part = re.sub(r"^[^\w]+", "", source_part).lower()
                
                # Match info_part (ModID (Version))
                info_match = re.search(r"([\w\d_\-]+)\s+\(([^)]+)\)", info_part)
                if not info_match:
                    continue
                    
                mod_id = info_match.group(1)
                version = info_match.group(2)
                
                # Extract filename if possible
                filename = None
                if source_part.startswith("mods_folder"):
                    # source_part looks like "mods_folder grappling_hook_mod-1.20.1-1.20.1-v13.jar"
                    filename = source_part.replace("mods_folder", "").strip()
                
                if source_part.startswith("minecraft forge"):
                    self._forge_version = version
                    logger.info(f"Detected Forge version: {version}")
                elif source_part.startswith("mods_folder"):
                    mods.append(ModInfo(id=mod_id, version=version, file=filename))
            
            self._mods = mods
            if not mods and not self._forge_version:
                logger.debug("Forge command 'forge mods' was accepted but no mods or version identified.")
            else:
                logger.info(f"Identified {len(mods)} server-side mods.")
            return True
        except Exception as e:
            logger.debug(f"Forge detection attempt failed (likely non-forge or offline): {e}")
            return False

    async def fetch_player_avatar(self, player_name: str) -> Optional[str]:
        """Fetches player UUID from Mojang and returns an mc-heads.net avatar URL."""
        if player_name in self._avatar_cache:
            return self._avatar_cache[player_name]
            
        try:
            url = f"https://api.mojang.com/users/profiles/minecraft/{player_name}"
            response = await self._http_client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                uuid = data.get("id")
                if uuid:
                    # Constructing the body avatar URL as requested
                    avatar_url = f"https://mc-heads.net/body/{uuid}/10"
                    self._avatar_cache[player_name] = avatar_url
                    return avatar_url
            elif response.status_code == 204: # No Content - Player not found
                logger.debug(f"Player {player_name} not found in Mojang API.")
            else:
                logger.warning(f"Mojang API returned status {response.status_code} for {player_name}")
                    
        except Exception as e:
            logger.error(f"Error fetching avatar for {player_name}: {e}")
            
        return None
