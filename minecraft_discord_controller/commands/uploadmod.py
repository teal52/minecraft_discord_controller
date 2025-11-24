import os
import tempfile
import discord
from discord import app_commands

from minecraft_discord_controller.config import settings
from minecraft_discord_controller.utils.permissions import ensure_allowed
from minecraft_discord_controller.service.minecraft import local_copy_to_mods
from minecraft_discord_controller.service.mods import extract_mod_metadata

_last_uploaded_jar: dict[int, str] = {}

def get_last_uploaded(guild_id: int) -> str | None:
    return _last_uploaded_jar.get(guild_id)

def set_last_uploaded(guild_id: int, name: str):
    _last_uploaded_jar[guild_id] = name

def register(tree: app_commands.CommandTree):
    @tree.command(name="uploadmod", description="modのjarをアップロードしてサーバーに配置します")
    @app_commands.describe(jar="Forge/Fabric の .jar ファイルを添付してください")
    async def uploadmod(inter: discord.Interaction, jar: discord.Attachment):
        if not await ensure_allowed(inter):
            return
        if not jar.filename.lower().endswith(".jar"):
            await inter.response.send_message("`.jar` 以外は受け付けません。", ephemeral=True)
            return

        await inter.response.defer(thinking=True, ephemeral=True)

        with tempfile.TemporaryDirectory() as td:
            local_path = os.path.join(td, jar.filename)
            data = await jar.read()
            with open(local_path, "wb") as f:
                f.write(data)

            mod_name, mod_ver = extract_mod_metadata(local_path)

            try:
                local_copy_to_mods(local_path, settings.MC_MODS_DIR, jar.filename)
            except Exception as e:
                await inter.followup.send(f"アップロード失敗: {e}", ephemeral=True)
                return

        set_last_uploaded(inter.guild_id, jar.filename)
        pretty = f"**{mod_name}** v{mod_ver}" if mod_name else f"`{jar.filename}`"
        await inter.followup.send(f"{pretty} を `mods/` に配置しました。再起動で反映されます。", ephemeral=True)
