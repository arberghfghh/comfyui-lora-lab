# Manual Adult/General overrides for LoRAs, shared by every LoRA Lab window and device.
import json
import os
import threading

import folder_paths

PATH = os.path.join(folder_paths.get_user_directory(), "default", "lora-lab-lora-flags.json")
FLAGS = {"adult", "general"}
_lock = threading.Lock()


def _read():
    if os.path.exists(PATH):
        try:
            with open(PATH, encoding="utf-8") as f:
                data = json.load(f).get("flags", {})
            return {str(k)[:260]: v for k, v in data.items() if v in FLAGS}
        except (OSError, ValueError, AttributeError):
            pass
    return {}


def load():
    with _lock:
        return {"flags": _read()}


def set_flag(name, flag):
    name = str(name or "")[:260]
    if not name:
        raise ValueError("Missing LoRA name")
    with _lock:
        flags = _read()
        if flag in FLAGS:
            flags[name] = flag
        else:
            flags.pop(name, None)   # back to automatic
        os.makedirs(os.path.dirname(PATH), exist_ok=True)
        tmp = PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"flags": flags}, f, ensure_ascii=False, indent=1)
        os.replace(tmp, PATH)
        return {"flags": flags}
