import logging
import discord

import minecraft_discord_controller import settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("minecraft_discord_controller")

intents = discord.Intents.default()

