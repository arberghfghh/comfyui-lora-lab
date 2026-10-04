# Character library: one JSON file in ComfyUI's user folder, shared by every LoRA Lab window and device.
# Characters are saved one at a time (upsert), so two devices editing different characters don't clash.
import json
import os
import re
import threading
import time
import uuid

import folder_paths

from .llm import BLOCKED_TAGS

PATH = os.path.join(folder_paths.get_user_directory(), "default", "lora-lab-characters.json")
ENGINES = {"any", "sdxl", "anima", "klein", "zimage"}
MAX_CHARACTERS, MAX_IMAGES, MAX_LORAS, MAX_PROMPTS = 200, 300, 10, 20
MODES = ("general", "adult")

_lock = threading.Lock()


def _tags(value, limit):
    out, seen = [], set()
    for tag in str(value or "").split(","):
        tag = " ".join(tag.split())
        key = tag.lower().replace("_", " ")
        if tag and key not in BLOCKED_TAGS and key not in seen:
            seen.add(key)
            out.append(tag)
    return ", ".join(out)[:limit]


def _text(value, limit):
    return str(value or "").strip()[:limit]


def _file_ref(value, name_key):
    if not isinstance(value, dict) or not value.get(name_key):
        return None
    ref = {name_key: _text(value[name_key], 200), "subfolder": _text(value.get("subfolder"), 200)}
    if "type" in value:
        ref["type"] = "input" if value["type"] == "input" else "output"
    return ref


def _clean(c, stored=None):
    stored = stored or {}
    cid = re.sub(r"[^a-z0-9]", "", str(c.get("id") or "").lower())[:16] or uuid.uuid4().hex[:12]
    loras = []
    for l in (c.get("loras") or [])[:MAX_LORAS]:
        if isinstance(l, dict) and l.get("name"):
            try:
                strength = max(-2.0, min(3.0, float(l.get("strength", 1.0))))
            except (TypeError, ValueError):
                strength = 1.0
            loras.append({"name": _text(l["name"], 260), "strength": round(strength, 2)})
    size = c.get("refSize")
    size = {"w": int(size["w"]), "h": int(size["h"])} if isinstance(size, dict) and size.get("w") and size.get("h") else None
    now = int(time.time() * 1000)
    return {
        "id": cid,
        "name": _text(c.get("name"), 60) or "Unnamed",
        "engine": c.get("engine") if c.get("engine") in ENGINES else "any",
        # Which workspace the character lives in; characters made before workspaces existed are Adult.
        "workspace": c.get("workspace") if c.get("workspace") in MODES else stored.get("workspace", "adult"),
        "appearance": _tags(c.get("appearance"), 2000),
        "outfit": _tags(c.get("outfit"), 2000),
        "triggers": _tags(c.get("triggers"), 300),
        "negative": _tags(c.get("negative"), 1000),
        "notes": _text(c.get("notes"), 2000),
        # Memory: notes and favourites come from the editor; last settings and recent prompts are
        # server-owned (see remember()), kept per workspace so General and Adult never mix.
        "memory": _text(c.get("memory"), 4000),
        "favorites": [_text(f, 300) for f in (c.get("favorites") or []) if f][:MAX_IMAGES],
        "last": stored.get("last", {}),
        "prompts": stored.get("prompts", {}),
        "loras": loras,
        "ref": _file_ref(c.get("ref"), "name"),
        "refSize": size,
        "images": stored.get("images", []),     # only add_image() changes the gallery
        "created": stored.get("created", now),
        "updated": now,
    }


def _read():
    if os.path.exists(PATH):
        try:
            with open(PATH, encoding="utf-8") as f:
                data = json.load(f)
            chars = [c for c in data.get("characters", []) if isinstance(c, dict) and c.get("id")]
            for c in chars:
                c.setdefault("workspace", "adult")
            return chars
        except (OSError, ValueError):
            pass
    return []


def _write(chars):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    tmp = PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"characters": chars}, f, ensure_ascii=False, indent=1)
    os.replace(tmp, PATH)


def load():
    with _lock:
        return {"characters": _read()}


def upsert(c):
    with _lock:
        chars = _read()
        stored = next((x for x in chars if x["id"] == str(c.get("id") or "")), None)
        clean = _clean(c, stored)
        if stored:
            chars[chars.index(stored)] = clean
        elif len(chars) < MAX_CHARACTERS:
            chars.append(clean)
        else:
            raise ValueError(f"Character limit reached ({MAX_CHARACTERS})")
        _write(chars)
        return clean


def delete(cid):
    with _lock:
        chars = _read()
        kept = [x for x in chars if x["id"] != cid]
        _write(kept)
        return len(kept) != len(chars)


def add_image(cid, item):
    with _lock:
        chars = _read()
        c = next((x for x in chars if x["id"] == cid), None)
        image = _file_ref(item.get("image"), "filename")
        if not c or not image:
            return None
        entry = {"image": image, "seed": item.get("seed"), "lora": _text(item.get("lora"), 260) or None,
                 "model": _text(item.get("model"), 260), "engine": _text(item.get("engine"), 10),
                 "mode": item.get("mode") if item.get("mode") in MODES else "adult", "time": int(time.time() * 1000)}
        c["images"] = (c.get("images", []) + [entry])[-MAX_IMAGES:]
        _write(chars)
        return entry


def remember(cid, mode, settings, prompt):
    """Store the settings and prompt last used with a character, per workspace."""
    if mode not in MODES:
        raise ValueError("Unknown workspace")
    settings = settings if isinstance(settings, dict) and len(json.dumps(settings)) < 8000 else None
    prompt = _text(prompt, 2000)
    with _lock:
        chars = _read()
        c = next((x for x in chars if x["id"] == cid), None)
        if not c:
            return None
        if settings:
            c.setdefault("last", {})[mode] = settings
        if prompt:
            recent = [p for p in c.setdefault("prompts", {}).get(mode, []) if p != prompt]
            c["prompts"][mode] = ([prompt] + recent)[:MAX_PROMPTS]
        _write(chars)
        return {"last": c.get("last", {}), "prompts": c.get("prompts", {})}
