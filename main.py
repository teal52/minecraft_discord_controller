import logging
import discord

from minecraft_discord_controller.config import settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("minecraft_discord_controller")

intents = discord.Intents.default()

