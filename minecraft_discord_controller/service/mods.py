import json
import zipfile
import tomli
from typing import Optional, Tuple

# @fn extract_mod_metadata
# @brief モッドの表示名とバージョンを抽出する
# @details zipfile で jar を開き、Forge は mods.toml、Fabric は fabric.mod.json をパースして先頭エントリの name/id と version を拾います
# @param local_jar 解析するローカルの jar ファイルパス
# @return (表示名, バージョン) のタプル。取得できない場合は (None, None)
def extract_mod_metadata(local_jar: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        with zipfile.ZipFile(local_jar, "r") as z:
            for name in z.namelist():
                if name.endswith("META-INF/mods.toml"):  # Forgeモッドのメタデータファイルを探す
                    with z.open(name) as f:
                        data = tomli.loads(f.read().decode("utf-8", errors="ignore"))  # TOML形式をパース
                    mods = data.get("mods") or []
                    if mods:
                        disp = mods[0].get("displayName") or mods[0].get("modId")  # 表示名またはmodIdを取得
                        ver = mods[0].get("version")
                        return disp, ver
            if "fabric.mod.json" in z.namelist():  # Fabricモッドのメタデータファイルを探す
                with z.open("fabric.mod.json") as f:
                    data = json.loads(f.read().decode("utf-8", errors="ignore"))  # JSON形式をパース
                disp = data.get("name") or data.get("id")  # 名前またはIDを取得
                ver = data.get("version")
                return disp, ver
    except Exception:
        pass
    return None, None  # メタデータの抽出に失敗した場合はNoneを返す
