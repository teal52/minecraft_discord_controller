#!/usr/bin/env python3
import logging
import discord
from discord.ext import commands

from minecraft_discord_controller.config import settings
from minecraft_discord_controller.commands import register_all_commands

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("minecraft_discord_controller")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await register_all_commands(bot, settings)  # Bot起動時にすべてのスラッシュコマンドを登録
    log.info(f"Logged in as {bot.user}")

if __name__ == "__main__":
    bot.run(settings.DISCORD_TOKEN)
