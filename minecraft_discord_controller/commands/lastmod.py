import discord
from discord import app_commands
from minecraft_discord_controller.commands.uploadmod import get_last_uploaded
from minecraft_discord_controller.utils.permissions import ensure_allowed

# @fn register
# @brief /lastmod コマンドをツリーへ登録する
# @details CommandTree に lastmod スラッシュコマンドを追加し、応答ハンドラーを束ねます
# @param tree コマンド登録先の CommandTree
# @return なし
def register(tree: app_commands.CommandTree):
    # @fn lastmod
    # @brief 直近のアップロードファイル名を返す
    # @details ensure_allowed で権限を確認し、get_last_uploaded で取得した名前を Interaction.response でエフェメラル送信します
    # @param inter コマンドを実行した Interaction
    # @return なし
    @tree.command(name="lastmod", description="最後にアップロードしたmodファイル名を表示します")
    async def lastmod(inter: discord.Interaction):
        if not await ensure_allowed(inter):
            return
        name = get_last_uploaded(inter.guild_id)  # 最後にアップロードしたJARファイル名を取得
        await inter.response.send_message(name or "（記録なし）", ephemeral=True)  # 記録がない場合は「記録なし」を表示
