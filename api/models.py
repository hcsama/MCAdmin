from pydantic import BaseModel
from typing import List, Optional, Dict, Union

class ModInfo(BaseModel):
    id: str
    version: str
    file: Optional[str] = None

class ServerStatus(BaseModel):
    online: bool
    version: str
    forge_version: Optional[str] = None
    mods: List[ModInfo] = []
    motd: str
    uptime: Optional[str] = None
    error: Optional[str] = None

class WorldState(BaseModel):
    time: int
    time_formatted: str
    phase: str
    days: int
    daylight_cycle: bool = True
    weather: str = "clear"
    weather_cycle: bool = True

class PlayerInfo(BaseModel):
    name: str
    uuid: Optional[str] = None
    avatar_url: Optional[str] = None
    whitelisted: bool = False

class PlayerState(BaseModel):
    online: int
    max: int
    list: List[PlayerInfo] = []

class WhitelistState(BaseModel):
    enabled: bool
    members: List[PlayerInfo]

class GamerulesState(BaseModel):
    rules: Dict[str, Union[bool, int]]
    statuses: Dict[str, str] = {} # pending, active, unsupported

class BroadcastRequest(BaseModel):
    message: str
