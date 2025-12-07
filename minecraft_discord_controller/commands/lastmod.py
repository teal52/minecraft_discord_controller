import discord
from discord import app_commands
from minecraft_discord_controller.commands.uploadmod import get_last_uploaded
from minecraft_discord_controller.utils.permissions import ensure_allowed

# @brief 最後のモッド表示コマンドをDiscordコマンドツリーに登録する
# @param tree Discordアプリケーションコマンドツリー
# @details 最後にアップロードしたモッドファイル名を表示するスラッシュコマンドを登録します
def register(tree: app_commands.CommandTree):
    @tree.command(name="lastmod", description="最後にアップロードしたmodファイル名を表示します")
    async def lastmod(inter: discord.Interaction):
        if not await ensure_allowed(inter):
            return
        name = get_last_uploaded(inter.guild_id)  # 最後にアップロードしたJARファイル名を取得
        await inter.response.send_message(name or "（記録なし）", ephemeral=True)  # 記録がない場合は「記録なし」を表示
