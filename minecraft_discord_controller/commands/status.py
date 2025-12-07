import discord
from discord import app_commands
from minecraft_discord_controller.service.minecraft import query_status
from minecraft_discord_controller.utils.permissions import ensure_allowed

# @fn register
# @brief /status コマンドをツリーへ登録する
# @details CommandTree に status スラッシュコマンドをデコレーターで追加し、ハンドラーを束ねます
# @param tree コマンド登録先の CommandTree
# @return なし
def register(tree: app_commands.CommandTree):
    # @fn status
    # @brief サーバーの状態を応答する
    # @details ensure_allowed で権限を確認し、query_status を呼び出して取得した文字列を followup 経由でエフェメラル返信します
    # @param inter コマンドを実行した Interaction
    # @return なし
    @tree.command(name="status", description="サーバーの状態を表示します")
    async def status(inter: discord.Interaction):
        if not await ensure_allowed(inter):
            return
        await inter.response.defer(thinking=True, ephemeral=True)  # 処理中であることを通知（他人には見えない）
        msg = query_status()  # サーバーのステータス情報を取得
        await inter.followup.send(msg, ephemeral=True)  # ステータス情報を送信（他人には見えない）
