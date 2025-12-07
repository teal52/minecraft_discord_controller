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

# @fn local_copy_to_mods
# @brief ローカルファイルを mods ディレクトリにコピーする
# @details os.makedirs で設置先を作成し、shutil.copy2 でメタデータごと複製して配置パスを返します
# @param local_path コピー元のローカルファイルパス
# @param remote_dir コピー先ディレクトリパス
# @param remote_filename コピー先のファイル名
# @return コピー先のファイルパス
def local_copy_to_mods(local_path: str, remote_dir: str, remote_filename: str) -> str:
    os.makedirs(remote_dir, exist_ok=True)  # ディレクトリが存在しない場合は作成
    dst = os.path.join(remote_dir, remote_filename)
    shutil.copy2(local_path, dst)  # ファイルをコピー（メタデータも保持）
    return dst

# @fn tail_log_until
# @brief ログファイルを監視して特定のパターンが出現するまで待機する
# @details subprocess で tail -F を起動し、正規表現で JAR 名または Done パターンをチェックしつつタイムアウトまで非同期で読み続けます
# @param filename_hint 検索するファイル名のヒント、または"Done"（サーバー起動完了を検知）
# @param timeout タイムアウト時間（秒）
# @return パターンが見つかった場合はTrue、タイムアウトした場合はFalse
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

# @fn rcon_command
# @brief RCON でコマンドを実行する
# @details MCRcon コンテキストを開き、指定コマンドを送信して得たレスポンス文字列を返します
# @param cmd 実行する RCON コマンド
# @return コマンド実行結果のレスポンス文字列（空の場合は空文字）
def rcon_command(cmd: str) -> str:
    with MCRcon(settings.RCON_HOST, settings.RCON_PASSWORD, port=settings.RCON_PORT) as mcr:  # RCON接続を確立
        return mcr.command(cmd) or ""  # コマンドを実行してレスポンスを取得

# @fn restart_via_rcon
# @brief RCON 経由でサーバーを再起動する
# @details カウントダウン中に say を逐次送信し、最後に stop を発行するシーケンスを同期実行します
# @param countdown 再起動までの秒数
# @return なし
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

# @fn restart_via_local_systemd
# @brief systemd を通じてサーバーを再起動する
# @details subprocess.run で systemctl restart を呼び出し、非ゼロ終了時は stderr を含む RuntimeError を投げます
# @return なし
def restart_via_local_systemd():
    rc = subprocess.run(
        ["systemctl", "restart", settings.SYSTEMD_UNIT],  # systemd経由でサーバーを再起動
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if rc.returncode != 0:
        raise RuntimeError(rc.stderr.strip())  # コマンド失敗時はエラーを投げる

# @fn query_status
# @brief サーバーのステータスを問い合わせる
# @details JavaServer.lookup で対象に接続し status() のレスポンスから人数とバージョンを組み立て、例外時はオフライン表記を返します
# @param host_for_query 接続先ホスト（未指定時は設定値を使用）
# @param port 接続ポート
# @return ステータス文字列（オンライン情報、またはオフラインメッセージ）
def query_status(host_for_query: Optional[str] = None, port: int = 25565) -> str:
    host = host_for_query or settings.RCON_HOST
    try:
        server = JavaServer.lookup(f"{host}:{port}")  # サーバーに接続
        stat = server.status()  # ステータス情報を取得
        return f"**Online**: {stat.players.online}/{stat.players.max} | Version: {stat.version.name}"
    except Exception:
        return "**Offline** or unreachable."  # 接続失敗時はオフラインと表示
