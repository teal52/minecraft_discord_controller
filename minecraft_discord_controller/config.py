import os
from dataclasses import dataclass

def _req(name: str) -> str:
  v = os.environ.get(name)
  if v is None or v== "":
    raise RuntimeError(f"Enviroment variable '{name}' is requred but not set" )  # 必須環境変数が未設定の場合はエラー
  return v

def _req_int(name: str) -> int:
  try:
    return int(_req(name))  # 環境変数を整数に変換
  except ValueError as exc:
    raise RuntimeError(f"Enviroment variable '{name}' must be an integer") from exc  # 整数として解釈できない場合はエラー

def _opt(name: str, default: str | None = None) -> str | None:
  v = os.environ.get(name)
  return v if (v is not None and v != "") else default  # 環境変数が空の場合はデフォルト値を返す

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