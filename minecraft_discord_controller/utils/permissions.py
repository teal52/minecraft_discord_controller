import discord
from minecraft_discord_controller.config import settings

def has_allowed_role(user: discord.abc.User | discord.Member) -> bool:
  if settings.ALLOWED_ROLE_ID is None:
    return True  # ロールIDが設定されていない場合は全員許可
  role_ids = [str(r.id) for r in getattr(user, "roles", [])]  # ユーザーが持つロールIDのリストを取得
  return settings.ALLOWED_ROLE_ID in role_ids  # 許可されたロールIDが含まれているかチェック

async def ensure_allowed(inter: discord.Interaction) -> bool:
  if has_allowed_role(inter.user):
    return True
  await inter.response.send_message("You are not allowed to use this command.", ephemeral=True)  # 権限がない場合はエラーメッセージを送信
  return False