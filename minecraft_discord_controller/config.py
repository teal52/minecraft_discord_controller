import os
from dataclasses import dataclass

def _req(name: str) -> str:
  v = os.environ.get(name)
  if v is None or v== "":
    raise RuntimeError(f"Enviroment variable '{name}' is requred but not set" )
  return v

def _req_int(name: str) -> int:
  try:
    return int(_req(name))
  except ValueError as exc:
    raise RuntimeError(f"Enviroment variable '{name}' must be an integer") from exc

def _opt(name: str, default: str | None = None) -> str | None:
  v = os.environ.get(name)
  return v if (v is not None and v != "") else default

def _opt_int(name: str, default: int) -> int:
  v = os.environ.get(name)
  return int(v) if (v is not None and v != "") else default

@dataclass(frozen=True)
class Settings:
  DISCORD_TOKEN: str = _req("DISCORD_TOKEN")
  GUILD_ID: str | None = _opt("GUILD_ID")
  ALLOWED_ROLE_ID: str | None = _opt("ALLOWED_ROLE_ID")

  # RCON接続情報
  RCON_HOST: str = _req("RCON_HOST")
  RCON_PORT: int = _req_int("RCON_PORT")
  RCON_PASSWORD: str = _req("RCON_PASSWORD")

  # ローカルのMinecraft関連パス
  MC_DIR: str = _req("MC_DIR")
  MC_LOG_PATH: str = _req("MC_LOG_PATH")
  MC_MODS_DIR: str = _req("MC_MODS_DIR")

  # 再起動情報
  RESTART_METHOD: str = _req("RESTART_METHOD")
  SYSTEMD_UNIT: str = _req("SYSTEMD_UNIT")

  # パラメータ
  RESTART_COUNTDOWN_SECONDS: int = _opt_int("RESTART_COUNTDOWN_SECONDS", 10)
  STARTUP_TIMEOUT_SECONDS: int = _opt_int("STARTUP_TIMEOUT_SECONDS", 240)


settings = Settings()