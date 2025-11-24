import asyncio
import contextlib
import os
import re
import shutil
import subprocess
from typing import Optional

from mcrcon import MCRcon
from mcstatus import JavaServer
from minecraft_discord_controller.config import settings

# ---- ファイル配置（ローカル） ----
def local_copy_to_mods(local_path: str, remote_dir: str, remote_filename: str) -> str:
    os.makedirs(remote_dir, exist_ok=True)
    dst = os.path.join(remote_dir, remote_filename)
    shutil.copy2(local_path, dst)
    return dst

# ---- ログ追尾（ローカル） ----
async def tail_log_until(filename_hint: str, timeout: int) -> bool:
    """
    ローカルの latest.log を tail -F して、filename_hint(jarファイル名 or "Done")を検知。
    見つかれば True、タイムアウトで False。
    """
    proc = await asyncio.create_subprocess_exec(
        "tail", "-n", "0", "-F", settings.MC_LOG_PATH,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    loop = asyncio.get_event_loop()
    start = loop.time()
    pattern = re.compile(re.escape(os.path.basename(filename_hint)))
    done_pattern = re.compile(r'Done \([0-9\.]+s\)!', re.IGNORECASE)
    want_done = filename_hint.lower() == "done"

    try:
        while True:
            if loop.time() - start > timeout:
                with contextlib.suppress(ProcessLookupError):
                    proc.terminate(); proc.kill()
                return False

            line = await asyncio.wait_for(proc.stdout.readline(), timeout=0.5)
            if not line:
                await asyncio.sleep(0.1)
                continue

            s = line.decode(errors="ignore")
            if want_done and done_pattern.search(s):
                with contextlib.suppress(ProcessLookupError):
                    proc.terminate(); proc.kill()
                return True
            if not want_done and pattern.search(s):
                with contextlib.suppress(ProcessLookupError):
                    proc.terminate(); proc.kill()
                return True
    except asyncio.TimeoutError:
        with contextlib.suppress(ProcessLookupError):
            proc.terminate(); proc.kill()
        return False
    finally:
        with contextlib.suppress(Exception):
            if proc.returncode is None:
                proc.terminate()

# ---- RCON ----
def rcon_command(cmd: str) -> str:
    with MCRcon(settings.RCON_HOST, settings.RCON_PASSWORD, port=settings.RCON_PORT) as mcr:
        return mcr.command(cmd) or ""

def restart_via_rcon(countdown: int):
    try:
        rcon_command(f"say Server restarting in {countdown} seconds...")
    except Exception:
        pass
    for i in range(countdown, 0, -1):
        try:
            if i in (countdown, 10, 5, 4, 3, 2, 1):
                rcon_command(f"say Restarting in {i}...")
        except Exception:
            pass
        asyncio.run(asyncio.sleep(1))
    rcon_command("say Stopping now...")
    rcon_command("stop")

# ---- （任意）ローカルsystemd再起動フック：Macでは通常使わない ----
def restart_via_local_systemd():
    rc = subprocess.run(
        ["systemctl", "restart", settings.SYSTEMD_UNIT],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if rc.returncode != 0:
        raise RuntimeError(rc.stderr.strip())

# ---- ステータス ----
def query_status(host_for_query: Optional[str] = None, port: int = 25565) -> str:
    host = host_for_query or settings.RCON_HOST
    try:
        server = JavaServer.lookup(f"{host}:{port}")
        stat = server.status()
        return f"**Online**: {stat.players.online}/{stat.players.max} | Version: {stat.version.name}"
    except Exception:
        return "**Offline** or unreachable."