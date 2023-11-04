from dataclasses import dataclass
from typing import Any
import discord

import secrets


@dataclass
class WorkUnit:
    discord_message: discord.Message
    args: dict[str, Any]
    id_num = secrets.token_hex(16)

