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

def local_copy_to_mods(local_path: str, remote_dir: str, remote_filename: str) -> str:
    os.makedirs(remote_dir, exist_ok=True)  # ディレクトリが存在しない場合は作成
    dst = os.path.join(remote_dir, remote_filename)
    shutil.copy2(local_path, dst)  # ファイルをコピー（メタデータも保持）
    return dst

async def tail_log_until(filename_hint: str, timeout: int) -> bool:
    proc = await asyncio.create_subprocess_exec(
        "tail", "-n", "0", "-F", settings.MC_LOG_PATH,  # ログファイルをリアルタイムで監視
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    loop = asyncio.get_event_loop()
    start = loop.time()
    pattern = re.compile(re.escape(os.path.basename(filename_hint)))  # JARファイル名のパターンをコンパイル
    done_pattern = re.compile(r'Done \([0-9\.]+s\)!', re.IGNORECASE)  # サーバー起動完了のパターン
    want_done = filename_hint.lower() == "done"  # "Done"を検索するかどうか

    try:
        while True:
            if loop.time() - start > timeout:  # タイムアウトチェック
                with contextlib.suppress(ProcessLookupError):
                    proc.terminate(); proc.kill()
                return False

            line = await asyncio.wait_for(proc.stdout.readline(), timeout=0.5)  # ログの1行を読み込み
            if not line:
                await asyncio.sleep(0.1)
                continue

            s = line.decode(errors="ignore")
            if want_done and done_pattern.search(s):  # サーバー起動完了を検知
                with contextlib.suppress(ProcessLookupError):
                    proc.terminate(); proc.kill()
                return True
            if not want_done and pattern.search(s):  # JARファイル名を検知
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
                proc.terminate()  # プロセスを確実に終了させる

def rcon_command(cmd: str) -> str:
    with MCRcon(settings.RCON_HOST, settings.RCON_PASSWORD, port=settings.RCON_PORT) as mcr:  # RCON接続を確立
        return mcr.command(cmd) or ""  # コマンドを実行してレスポンスを取得

def restart_via_rcon(countdown: int):
    try:
        rcon_command(f"say Server restarting in {countdown} seconds...")  # 再起動開始のメッセージ
    except Exception:
        pass
    for i in range(countdown, 0, -1):
        try:
            if i in (countdown, 10, 5, 4, 3, 2, 1):  # 特定の秒数でのみカウントダウンメッセージを表示
                rcon_command(f"say Restarting in {i}...")
        except Exception:
            pass
        asyncio.run(asyncio.sleep(1))  # 1秒待機
    rcon_command("say Stopping now...")
    rcon_command("stop")  # サーバーを停止

def restart_via_local_systemd():
    rc = subprocess.run(
        ["systemctl", "restart", settings.SYSTEMD_UNIT],  # systemd経由でサーバーを再起動
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if rc.returncode != 0:
        raise RuntimeError(rc.stderr.strip())  # コマンド失敗時はエラーを投げる

def query_status(host_for_query: Optional[str] = None, port: int = 25565) -> str:
    host = host_for_query or settings.RCON_HOST
    try:
        server = JavaServer.lookup(f"{host}:{port}")  # サーバーに接続
        stat = server.status()  # ステータス情報を取得
        return f"**Online**: {stat.players.online}/{stat.players.max} | Version: {stat.version.name}"
    except Exception:
        return "**Offline** or unreachable."  # 接続失敗時はオフラインと表示