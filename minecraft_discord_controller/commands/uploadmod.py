import os
import tempfile
import discord
from discord import app_commands

from minecraft_discord_controller.config import settings
from minecraft_discord_controller.utils.permissions import ensure_allowed
from minecraft_discord_controller.service.minecraft import local_copy_to_mods
from minecraft_discord_controller.service.mods import extract_mod_metadata

_last_uploaded_jar: dict[int, str] = {}  # ギルドごとの最後にアップロードしたJARファイル名を記録

# @fn get_last_uploaded
# @brief ギルドごとの最後にアップロードした jar 名を取得する
# @details ギルドIDをキーに保持しているメモリ上の辞書から、最新に記録されたファイル名を返します
# @param guild_id ギルドID
# @return 最後に記録された jar 名。存在しない場合は None
def get_last_uploaded(guild_id: int) -> str | None:
    return _last_uploaded_jar.get(guild_id)

# @fn set_last_uploaded
# @brief 最後にアップロードした jar 名を記録する
# @details ギルドIDをキーとした辞書に jar 名を上書き保存し、後続の参照に備えます
# @param guild_id ギルドID
# @param name 記録する jar ファイル名
# @return なし
def set_last_uploaded(guild_id: int, name: str):
    _last_uploaded_jar[guild_id] = name

# @fn register
# @brief /uploadmod コマンドをツリーへ登録する
# @details CommandTree に uploadmod コマンドを追加し、添付ファイル処理を行うハンドラーをセットします
# @param tree コマンド登録先の CommandTree
# @return なし
def register(tree: app_commands.CommandTree):
    # @fn uploadmod
    # @brief モッド jar をアップロードして配置する
    # @details ensure_allowed で権限を確認し、添付 jar を一時ディレクトリへ保存してメタデータ抽出後、local_copy_to_mods で mods へコピーします
    # @param inter コマンドを実行した Interaction
    # @param jar 添付された mod jar ファイル
    # @return なし
    @tree.command(name="uploadmod", description="modのjarをアップロードしてサーバーに配置します")
    @app_commands.describe(jar="Forge/Fabric の .jar ファイルを添付してください")
    async def uploadmod(inter: discord.Interaction, jar: discord.Attachment):
        if not await ensure_allowed(inter):
            return
        if not jar.filename.lower().endswith(".jar"):  # JARファイルかどうかをチェック
            await inter.response.send_message("`.jar` 以外は受け付けません。", ephemeral=True)
            return

        await inter.response.defer(thinking=True, ephemeral=True)  # 処理に時間がかかることを通知

        with tempfile.TemporaryDirectory() as td:  # 一時ディレクトリを作成
            local_path = os.path.join(td, jar.filename)
            data = await jar.read()  # Discordから添付ファイルをダウンロード
            with open(local_path, "wb") as f:
                f.write(data)  # 一時ディレクトリにファイルを保存

            mod_name, mod_ver = extract_mod_metadata(local_path)  # JARファイルからメタデータを抽出

            try:
                local_copy_to_mods(local_path, settings.MC_MODS_DIR, jar.filename)  # modsディレクトリにコピー
            except Exception as e:
                await inter.followup.send(f"アップロード失敗: {e}", ephemeral=True)
                return

        set_last_uploaded(inter.guild_id, jar.filename)  # 最後にアップロードしたファイル名を記録
        pretty = f"**{mod_name}** v{mod_ver}" if mod_name else f"`{jar.filename}`"  # メタデータがある場合は整形
        await inter.followup.send(f"{pretty} を `mods/` に配置しました。再起動で反映されます。", ephemeral=True)
