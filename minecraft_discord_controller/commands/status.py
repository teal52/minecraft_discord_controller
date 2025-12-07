import discord
from discord import app_commands
from minecraft_discord_controller.service.minecraft import query_status
from minecraft_discord_controller.utils.permissions import ensure_allowed

# @brief ステータスコマンドをDiscordコマンドツリーに登録する
# @param tree Discordアプリケーションコマンドツリー
# @details サーバーの状態を表示するスラッシュコマンドを登録します
def register(tree: app_commands.CommandTree):
    @tree.command(name="status", description="サーバーの状態を表示します")
    async def status(inter: discord.Interaction):
        if not await ensure_allowed(inter):
            return
        await inter.response.defer(thinking=True, ephemeral=True)  # 処理中であることを通知（他人には見えない）
        msg = query_status()  # サーバーのステータス情報を取得
        await inter.followup.send(msg, ephemeral=True)  # ステータス情報を送信（他人には見えない）
