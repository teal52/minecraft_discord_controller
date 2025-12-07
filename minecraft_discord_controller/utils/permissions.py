import discord
from minecraft_discord_controller.config import settings

# @fn has_allowed_role
# @brief ユーザーが許可されたロールを持つか判定する
# @details 設定のロールIDが未指定なら早期 True を返し、指定があれば保持ロールID一覧と突き合わせて一致をチェックします
# @param user 判定対象のユーザーまたはメンバー
# @return 許可されている場合は True、そうでなければ False
def has_allowed_role(user: discord.abc.User | discord.Member) -> bool:
  if settings.ALLOWED_ROLE_ID is None:
    return True  # ロールIDが設定されていない場合は全員許可
  role_ids = [str(r.id) for r in getattr(user, "roles", [])]  # ユーザーが持つロールIDのリストを取得
  return settings.ALLOWED_ROLE_ID in role_ids  # 許可されたロールIDが含まれているかチェック

# @fn ensure_allowed
# @brief コマンド利用者の権限を検証する
# @details has_allowed_role で検証し、拒否時は Interaction にエフェメラルでメッセージを返して以降の処理を停止します
# @param inter Discord の Interaction オブジェクト
# @return 許可されている場合は True、そうでなければ False
async def ensure_allowed(inter: discord.Interaction) -> bool:
  if has_allowed_role(inter.user):
    return True
  await inter.response.send_message("You are not allowed to use this command.", ephemeral=True)  # 権限がない場合はエラーメッセージを送信
  return False
