import discord
from discord import app_commands
from minecraft_discord_controller.service.minecraft import query_status
from minecraft_discord_controller.utils.permissions import ensure_allowed

def register(tree: app_commands.CommandTree):
    @tree.command(name="status", description="サーバーの状態を表示します")
    async def status(inter: discord.Interaction):
        if not await ensure_allowed(inter):
            return
        await inter.response.defer(thinking=True, ephemeral=True)
        msg = query_status()
        await inter.followup.send(msg, ephemeral=True)
