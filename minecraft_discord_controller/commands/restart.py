import asyncio
import discord
from discord import app_commands

from minecraft_discord_controller.config import settings
from minecraft_discord_controller.utils.permissions import ensure_allowed
from minecraft_discord_controller.service.minecraft import (
    restart_via_rcon, restart_via_local_systemd, tail_log_until
)
from minecraft_discord_controller.commands.uploadmod import get_last_uploaded

# @fn register
# @brief /restart コマンドをツリーへ登録する
# @details CommandTree に restart スラッシュコマンドを追加し、watch オプション付きのハンドラーをセットアップします
# @param tree コマンド登録先の CommandTree
# @return なし
def register(tree: app_commands.CommandTree):
    # @fn restart
    # @brief サーバーを再起動し、起動を監視する
    # @details 権限チェック後に RESTART_METHOD に応じて RCON か systemd を実行し、tail_log_until でヒントに基づいてログを監視します
    # @param inter コマンドを実行した Interaction
    # @param watch 直近のアップロード jar を監視ヒントに使うかどうか
    # @return なし
    @tree.command(name="restart", description="サーバーを再起動し、mod読み込みを監視します")
    @app_commands.describe(watch="直近のアップロードjarを監視ヒントに使う(推奨)(default: True)")
    async def restart(inter: discord.Interaction, watch: bool = True):
        if not await ensure_allowed(inter):
            return
        await inter.response.defer(thinking=True)  # 処理に時間がかかることを通知

        filename_hint = get_last_uploaded(inter.guild_id) if watch else None  # 監視対象のJARファイル名を取得

        try:
            if settings.RESTART_METHOD == "LOCAL_SYSTEMD":
                restart_via_local_systemd()  # systemd経由で再起動
            else:
                await inter.followup.send(
                    f"再起動を開始します（{settings.RESTART_COUNTDOWN_SECONDS}s後にstop）。",
                    ephemeral=True
                )
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, lambda: restart_via_rcon(settings.RESTART_COUNTDOWN_SECONDS))  # RCON経由で再起動（別スレッドで実行）
        except Exception as e:
            await inter.followup.send(f"再起動に失敗: {e}", ephemeral=True)
            return

        await inter.followup.send(
            f"起動を監視中…（タイムアウト {settings.STARTUP_TIMEOUT_SECONDS}s）",
            ephemeral=True
        )

        hint = filename_hint or "Done"  # ヒントがない場合は"Done"を監視
        loaded = await tail_log_until(hint, settings.STARTUP_TIMEOUT_SECONDS)  # ログを監視して起動・モッド読み込みを検知

        ch: discord.abc.MessageableChannel = inter.channel
        if loaded:
            await ch.send("✅ サーバー起動＆モッド読み込みを検知しました。")
        else:
            await ch.send("⚠️ 起動/読み込みの検知に失敗しました（タイムアウト）。ログを確認してください。")
