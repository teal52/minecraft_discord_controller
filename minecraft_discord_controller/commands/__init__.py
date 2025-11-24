import logging
import discord
from discord import app_commands
from discord.ext import commands

from minecraft_discord_controller.config import Settings
from .status import register as register_status
from .uploadmod import register as register_uploadmod
from .restart import register as register_restart
from .lastmod import register as register_lastmod


log = logging.getLogger(__name__)

async def register_all_commands(bot: commands.Bot, settings: Settings):
    tree: app_commands.CommandTree = bot.tree
    register_status(tree)
    register_uploadmod(tree)
    register_restart(tree)
    register_lastmod(tree)
    try:
        if settings.GUILD_ID:
            guild = discord.Object(id=int(settings.GUILD_ID))
            await tree.sync(guild=guild)
            log.info("Slash commands synced (guild).")
        else:
            await tree.sync()
            log.info("Slash commands synced (global).")
    except Exception as e:
        log.error(f"Slash command sync failed: {e}")