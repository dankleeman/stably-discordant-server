from dataclasses import dataclass
from typing import Any, Coroutine
import discord


@dataclass
class WorkUnit:
    discord_message: discord.Message
    args: Coroutine[Any, Any, dict[str, Any]]
