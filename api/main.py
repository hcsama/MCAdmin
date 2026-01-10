from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from minecraft import MinecraftService
from models import ServerStatus, WorldState, PlayerState, WhitelistState, PlayerInfo, GamerulesState, BroadcastRequest
from pydantic_settings import BaseSettings
import asyncio
import logging
import json
from typing import List, Any, Optional, Union
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:     %(message)s')
logger = logging.getLogger("minecraft-admin")

class Settings(BaseSettings):
    mc_host: str = "localhost"
    mc_port: int = 25575
    mc_game_port: int = 25565
    mc_rcon_password: str = "minecraft"
    
    # Independent Polling Intervals
    mc_poll_interval_server: int = 10
    mc_poll_interval_world: int = 5
    mc_poll_interval_players: int = 5
    mc_poll_interval_whitelist: int = 10
    mc_poll_interval_gamerules: int = 60

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()
mc_service = MinecraftService(
    settings.mc_host, 
    settings.mc_game_port, 
    settings.mc_port, 
    settings.mc_rcon_password
)

# Domain-specific states
states = {
    "server": ServerStatus(online=False, version="Unknown", motd="Initial loading..."),
    "world": WorldState(time=0, time_formatted="06:00", phase="Day", days=0),
    "players": PlayerState(online=0, max=0, list=[]),
    "whitelist": WhitelistState(enabled=True, members=[]),
    "gamerules": GamerulesState(
        rules={},
        statuses={rule: "pending" for rule in [
            "disableRaids", "announceAdvancements", "doFireTick", "doImmediateRespawn",
            "doLimitedCrafting", "drowningDamage", "enderPearlsVanishOnDeath",
            "fallDamage", "fireDamage", "forgiveDeadPlayers", "freezeDamage",
            "globalSoundEvents", "keepInventory", "lavaSourceConversion",
            "naturalRegeneration", "projectilesCanBreakBlocks", "showDeathMessages",
            "snowAccumulationHeight", "universalAnger", "waterSourceConversion"
        ]}
    )
}

GAMERULES = [
    "disableRaids", "announceAdvancements", "doFireTick", "doImmediateRespawn",
    "doLimitedCrafting", "drowningDamage", "enderPearlsVanishOnDeath",
    "fallDamage", "fireDamage", "forgiveDeadPlayers", "freezeDamage",
    "globalSoundEvents", "keepInventory", "lavaSourceConversion",
    "naturalRegeneration", "projectilesCanBreakBlocks", "showDeathMessages",
    "snowAccumulationHeight", "universalAnger", "waterSourceConversion"
]

# List of active SSE client queues
clients: List[asyncio.Queue] = []

async def broadcast_update(domain: str, data: Any):
    """Broadcast domain-tagged updates to all connected SSE clients."""
    if not clients:
        return
    # Use model_dump for Pydantic models
    payload = data.model_dump() if hasattr(data, "model_dump") else data
    message = f"data: {json.dumps({'domain': domain, 'data': payload})}\n\n"
    for queue in clients:
        await queue.put(message)

async def update_server_loop():
    global states
    while True:
        try:
            new_status = await mc_service.get_server_status()
            if new_status != states["server"]:
                states["server"] = new_status
                await broadcast_update("server", new_status)
        except Exception as e:
            logger.error(f"Error in server update loop: {e}")
        await asyncio.sleep(settings.mc_poll_interval_server)

async def update_world_loop():
    global states
    while True:
        if states["server"].online:
            try:
                new_world = await mc_service.get_world_state()
                if new_world and new_world != states["world"]:
                    states["world"] = new_world
                    await broadcast_update("world", new_world)
            except Exception as e:
                logger.error(f"Error in world update loop: {e}")
        await asyncio.sleep(settings.mc_poll_interval_world)

async def update_player_loop():
    global states
    while True:
        if states["server"].online:
            try:
                new_players = await mc_service.get_player_state()
                if new_players and new_players != states["players"]:
                    states["players"] = new_players
                    await broadcast_update("players", new_players)
            except Exception as e:
                logger.error(f"Error in player update loop: {e}")
        await asyncio.sleep(settings.mc_poll_interval_players)

async def update_whitelist_loop():
    global states
    while True:
        if states["server"].online:
            try:
                new_whitelist = await mc_service.get_whitelist_state()
                if new_whitelist and new_whitelist != states["whitelist"]:
                    states["whitelist"] = new_whitelist
                    await broadcast_update("whitelist", new_whitelist)
            except Exception as e:
                logger.error(f"Error in whitelist update loop: {e}")
        await asyncio.sleep(settings.mc_poll_interval_whitelist)

async def update_gamerules_loop():
    global states
    while True:
        if states["server"].online:
            # We want to poll ALL rules within mc_poll_interval_gamerules
            delay = settings.mc_poll_interval_gamerules / len(GAMERULES) if GAMERULES else 60
            
            logger.debug(f"Starting gamerules polling pass (interval: {settings.mc_poll_interval_gamerules}s)")
            for rule_id in GAMERULES:
                try:
                    if not states["server"].online:
                        break
                    
                    # Skip rules already determined to be unsupported
                    if states["gamerules"].statuses.get(rule_id) == "unsupported":
                        continue

                    val = await mc_service.get_gamerule(rule_id)
                    
                    if val == "unsupported":
                        # Explicitly unsupported by the server
                        logger.info(f"Marking gamerule {rule_id} as unsupported (explicit rejection)")
                        states["gamerules"].statuses[rule_id] = "unsupported"
                        await broadcast_update("gamerules", states["gamerules"])
                    elif val is not None:
                        # Rule is active (True, False, or Number)
                        states["gamerules"].statuses[rule_id] = "active"
                        if states["gamerules"].rules.get(rule_id) != val:
                            states["gamerules"].rules[rule_id] = val
                            await broadcast_update("gamerules", states["gamerules"])
                    # If val is None (timeout/error), we keep current status (pending/active)

                except Exception as e:
                    logger.error(f"Error polling gamerule {rule_id}: {e}")
                
                await asyncio.sleep(delay)
        else:
            await asyncio.sleep(settings.mc_poll_interval_server)

async def detect_forge_task():
    """Performs a one-time detection of Forge and Mods when the server is online."""
    while not mc_service._forge_detected:
        if states["server"].online:
            success = await mc_service.detect_forge_and_mods()
            if success:
                # Update server state to include the new data
                states["server"] = await mc_service.get_server_status()
                await broadcast_update("server", states["server"])
            break
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start separate background tasks
    tasks = [
        asyncio.create_task(update_server_loop()),
        asyncio.create_task(update_world_loop()),
        asyncio.create_task(update_player_loop()),
        asyncio.create_task(update_whitelist_loop()),
        asyncio.create_task(update_gamerules_loop()),
        asyncio.create_task(detect_forge_task())
    ]
    yield
    # Cleanup
    await mc_service.close()
    for task in tasks:
        task.cancel()

app = FastAPI(title="Minecraft Admin API", lifespan=lifespan)

class CommandRequest(BaseModel):
    command: str

@app.get("/status")
async def get_status():
    return states

@app.get("/status-stream")
async def status_stream(request: Request):
    """SSE endpoint to stream domain-tagged updates to clients."""
    queue = asyncio.Queue()
    clients.append(queue)
    
    async def event_generator():
        # Send initial full state
        initial_payload = {k: v.model_dump() for k, v in states.items()}
        yield f"data: {json.dumps({'domain': 'all', 'data': initial_payload})}\n\n"
        
        try:
            while True:
                if await request.is_disconnected():
                    break
                message = await queue.get()
                yield message
        finally:
            if queue in clients:
                clients.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/command")
async def run_command(request: CommandRequest):
    try:
        response = await mc_service.run_command(request.command)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ToggleRequest(BaseModel):
    enabled: bool

class MemberRequest(BaseModel):
    name: str

@app.post("/whitelist/toggle")
async def toggle_whitelist(request: ToggleRequest):
    try:
        success, message = await mc_service.toggle_whitelist(request.enabled)
        # Immediate local update for instant UI response
        states["whitelist"].enabled = request.enabled
        await broadcast_update("whitelist", states["whitelist"])
        return {"success": success, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/whitelist/members")
async def add_whitelist_member(request: MemberRequest):
    try:
        success, message = await mc_service.add_whitelist(request.name)
        # Immediate local update only if successful
        if success and not any(p.name == request.name for p in states["whitelist"].members):
            states["whitelist"].members.append(PlayerInfo(name=request.name, whitelisted=True))
            # Sort for consistency
            states["whitelist"].members.sort(key=lambda x: x.name)
            await broadcast_update("whitelist", states["whitelist"])
        return {"success": success, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class WeatherRequest(BaseModel):
    type: str # clear, rain, thunder
    duration: Optional[int] = None

@app.post("/world/weather")
async def set_weather(request: WeatherRequest):
    try:
        success = await mc_service.set_weather(request.type, request.duration)
        # Immediate world state update
        states["world"].weather = request.type
        await broadcast_update("world", states["world"])
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/world/weather-cycle")
async def toggle_weather_cycle(request: ToggleRequest):
    try:
        success = await mc_service.toggle_weather_cycle(request.enabled)
        # Immediate update
        states["world"].weather_cycle = request.enabled
        await broadcast_update("world", states["world"])
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/world/daylight-cycle")
async def toggle_daylight_cycle(request: ToggleRequest):
    try:
        success = await mc_service.toggle_daylight_cycle(request.enabled)
        # Immediate update
        states["world"].daylight_cycle = request.enabled
        await broadcast_update("world", states["world"])
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/whitelist/members/{name}")
async def remove_whitelist_member(name: str):
    try:
        success, message = await mc_service.remove_whitelist(name)
        # Immediate update
        states["whitelist"].members = [p for p in states["whitelist"].members if p.name != name]
        await broadcast_update("whitelist", states["whitelist"])
        return {"success": success, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GameruleToggleRequest(BaseModel):
    value: Union[bool, int]

@app.post("/world/gamerules/{rule_id}")
async def set_gamerule(rule_id: str, request: GameruleToggleRequest):
    try:
        success = await mc_service.set_gamerule(rule_id, request.value)
        # Immediate local update
        states["gamerules"].rules[rule_id] = request.value
        states["gamerules"].statuses[rule_id] = "active"
        await broadcast_update("gamerules", states["gamerules"])
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/server/broadcast")
async def broadcast_message(request: BroadcastRequest):
    try:
        success = await mc_service.broadcast_message(request.message)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
