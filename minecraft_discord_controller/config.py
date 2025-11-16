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
  except ValueError:
    return RuntimeError(f"Enviroment variable '{name}' musr be an interger" )

def _opt(name: str, default: str | None = None) -> str | None:
  v = os.environ.get(name)
  return v if (v is not None and v != "") else default

def _opt_int(name: str, default: int) -> int:
  v = os.environ.get(name)
  return int(v) if (v is not None and v != "") else default

@dataclass(frozen=True)
class Settings:
  DISCORD_TOKEN: str = os.environ.get("IDSCORDTOKEN", "")
  GUILD_ID: str | None = _opt("GUILD_ID")
  ALLOWED_ROLE_ID: str | None = _opt("ALLOWED_ROLE_ID")

  #RCON
  RCON_HOST: str = _req("RCON_HOST")
  RCON_PORT: int = _req_int("RCON_PORT")
  RCON_PASSWORD: str = _req("RCON_PASSWORD")

  #Local pass
  MC_DIR: str = _req("RCON_DIR")
  MC_LOG_PATH: str = _req("MC_LOG_PATH")
  MC_MODS_DIR: str = _req("MC_MODS_DIR")

  #再起動形式
  RESTART_METHOD: str = _req("RESTART_METHOD")
  SYSTEND_UNIT: str = _req("SYSTEMD_UNIT")

  #params
  RESTART_COUTDOWN_SECONDS: int = _opt_int("RESTART_COUNTDOWN_SECONS", 10)
  STARTUP_TIMEOUT_SECONDS: int = _opt_int("START_TIMEOUT_SECONDS", 240)

  settings = Settings()