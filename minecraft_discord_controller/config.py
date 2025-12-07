import os
from dataclasses import dataclass

# @fn _req
# @brief 必須の環境変数を取得する
# @details os.environ から値を読み出し、None もしくは空文字の場合は RuntimeError を投げるガードとして働きます
# @param name 環境変数名
# @return 取得した環境変数の文字列値
def _req(name: str) -> str:
  v = os.environ.get(name)
  if v is None or v== "":
    raise RuntimeError(f"Enviroment variable '{name}' is requred but not set" )  # 必須環境変数が未設定の場合はエラー
  return v

# @fn _req_int
# @brief 必須の環境変数を整数として取得する
# @details _req で文字列を取得後に int 変換を行い、ValueError 発生時は RuntimeError にラップして入力を検証します
# @param name 環境変数名
# @return 取得した整数値
def _req_int(name: str) -> int:
  try:
    return int(_req(name))  # 環境変数を整数に変換
  except ValueError as exc:
    raise RuntimeError(f"Enviroment variable '{name}' must be an integer") from exc  # 整数として解釈できない場合はエラー

# @fn _opt
# @brief 任意の環境変数を取得する
# @details 環境変数を読み出し、None/空文字の場合は default を返すフォールバックロジックを持ちます
# @param name 環境変数名
# @param default デフォルト値（未設定時に返す値）
# @return 取得した文字列値、またはデフォルト値
def _opt(name: str, default: str | None = None) -> str | None:
  v = os.environ.get(name)
  return v if (v is not None and v != "") else default  # 環境変数が空の場合はデフォルト値を返す

# @fn _opt_int
# @brief 任意の環境変数を整数として取得する
# @details 環境変数の存在を確認し、設定されていれば int 変換し、未設定や空文字なら default を返す単純なパーサとして機能します
# @param name 環境変数名
# @param default デフォルトの整数値
# @return 取得した整数値、またはデフォルト値
def _opt_int(name: str, default: int) -> int:
  v = os.environ.get(name)
  return int(v) if (v is not None and v != "") else default  # 環境変数が空の場合はデフォルト値を返す

@dataclass(frozen=True)
class Settings:
  DISCORD_TOKEN: str = _req("DISCORD_TOKEN")
  GUILD_ID: str | None = _opt("GUILD_ID")
  ALLOWED_ROLE_ID: str | None = _opt("ALLOWED_ROLE_ID")

  RCON_HOST: str = _req("RCON_HOST")
  RCON_PORT: int = _req_int("RCON_PORT")
  RCON_PASSWORD: str = _req("RCON_PASSWORD")

  MC_DIR: str = _req("MC_DIR")
  MC_LOG_PATH: str = _req("MC_LOG_PATH")
  MC_MODS_DIR: str = _req("MC_MODS_DIR")

  RESTART_METHOD: str = _req("RESTART_METHOD")
  SYSTEMD_UNIT: str = _req("SYSTEMD_UNIT")

  RESTART_COUNTDOWN_SECONDS: int = _opt_int("RESTART_COUNTDOWN_SECONDS", 10)
  STARTUP_TIMEOUT_SECONDS: int = _opt_int("STARTUP_TIMEOUT_SECONDS", 240)

settings = Settings()
