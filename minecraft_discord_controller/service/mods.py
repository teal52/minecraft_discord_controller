import json
import zipfile
import tomli
from typing import Optional, Tuple

def extract_mod_metadata(local_jar: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Forge: META-INF/mods.toml → mods[0].displayName/version
    Fabric: fabric.mod.json → name/version
    """
    try:
        with zipfile.ZipFile(local_jar, "r") as z:
            for name in z.namelist():
                if name.endswith("META-INF/mods.toml"):
                    with z.open(name) as f:
                        data = tomli.loads(f.read().decode("utf-8", errors="ignore"))
                    mods = data.get("mods") or []
                    if mods:
                        disp = mods[0].get("displayName") or mods[0].get("modId")
                        ver = mods[0].get("version")
                        return disp, ver
            if "fabric.mod.json" in z.namelist():
                with z.open("fabric.mod.json") as f:
                    data = json.loads(f.read().decode("utf-8", errors="ignore"))
                disp = data.get("name") or data.get("id")
                ver = data.get("version")
                return disp, ver
    except Exception:
        pass
    return None, None