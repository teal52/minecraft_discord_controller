import asyncio
import discord
from discord import app_commands

from minecraft_discord_controller.config import settings
from minecraft_discord_controller.utils.permissions import ensure_allowed
from minecraft_discord_controller.service.minecraft import (
    restart_via_rcon, restart_via_local_systemd, tail_log_until
)
from minecraft_discord_controller.commands.uploadmod import get_last_uploaded

def register(tree: app_commands.CommandTree):
    @tree.command(name="restart", description="サーバーを再起動し、mod読み込みを監視します")
    @app_commands.describe(watch="直近のアップロードjarを監視ヒントに使う(推奨)(default: True)")
    async def restart(inter: discord.Interaction, watch: bool = True):
        if not await ensure_allowed(inter):
            return
        await inter.response.defer(thinking=True)

        filename_hint = get_last_uploaded(inter.guild_id) if watch else None

        try:
            if settings.RESTART_METHOD == "LOCAL_SYSTEMD":
                restart_via_local_systemd()
            else:
                await inter.followup.send(
                    f"再起動を開始します（{settings.RESTART_COUNTDOWN_SECONDS}s後にstop）。",
                    ephemeral=True
                )
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, lambda: restart_via_rcon(settings.RESTART_COUNTDOWN_SECONDS))
        except Exception as e:
            await inter.followup.send(f"再起動に失敗: {e}", ephemeral=True)
            return

        await inter.followup.send(
            f"起動を監視中…（タイムアウト {settings.STARTUP_TIMEOUT_SECONDS}s）",
            ephemeral=True
        )

        hint = filename_hint or "Done"
        loaded = await tail_log_until(hint, settings.STARTUP_TIMEOUT_SECONDS)

        ch: discord.abc.MessageableChannel = inter.channel
        if loaded:
            await ch.send("✅ サーバー起動＆モッド読み込みを検知しました。")
        else:
            await ch.send("⚠️ 起動/読み込みの検知に失敗しました（タイムアウト）。ログを確認してください。")
