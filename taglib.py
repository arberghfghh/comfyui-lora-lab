# Shared tag library: one JSON file in ComfyUI's user folder, used by every LoRA Lab window and device.
import json
import os
import re
import threading

import folder_paths

from .llm import BLOCKED_TAGS

PATH = os.path.join(folder_paths.get_user_directory(), "default", "lora-lab-tags.json")
MAX_CATEGORIES, MAX_TAGS, MAX_TAG_LEN, MAX_NAME_LEN = 50, 500, 80, 40

DEFAULT = {"categories": [
    {"name": "Subject", "tags": ["1girl", "1boy", "2girls", "solo", "couple", "mature female", "mature male", "adult"]},
    {"name": "Hair", "tags": ["long hair", "short hair", "ponytail", "twintails", "braid", "bob cut", "messy hair",
                              "blonde hair", "black hair", "brown hair", "red hair", "silver hair", "pink hair", "blue hair"]},
    {"name": "Face", "tags": ["blue eyes", "green eyes", "red eyes", "golden eyes", "smile", "blush", "open mouth",
                              "closed eyes", "looking at viewer", "looking away", "serious", "smirk"]},
    {"name": "Clothing", "tags": ["dress", "evening gown", "kimono", "hoodie", "leather jacket", "business suit", "armor",
                                  "swimsuit", "thighhighs", "gloves", "hat", "glasses", "jewelry"]},
    {"name": "Pose", "tags": ["standing", "sitting", "lying", "kneeling", "walking", "from behind", "arms up",
                              "hand on hip", "leaning forward", "crossed arms"]},
    {"name": "Setting", "tags": ["outdoors", "indoors", "city", "night", "beach", "forest", "bedroom", "cafe", "rooftop",
                                 "rain", "snow", "cherry blossoms"]},
    {"name": "Camera & light", "tags": ["close-up", "upper body", "cowboy shot", "full body", "from above", "from below",
                                        "wide shot", "depth of field", "cinematic lighting", "soft lighting", "backlighting",
                                        "rim light", "sunset", "neon lights"]},
    {"name": "Style", "tags": ["anime coloring", "cel shading", "watercolor", "oil painting", "sketch", "realistic",
                               "photorealistic", "3d", "pixel art", "monochrome"]},
]}

_lock = threading.Lock()
ADULT_NAME = re.compile(r"nsfw|rule34|18\+", re.I)


def _clean(data):
    categories, seen_names = [], set()
    for cat in ((data or {}).get("categories") or [])[:MAX_CATEGORIES]:
        name = " ".join(str(cat.get("name", "")).split())[:MAX_NAME_LEN]
        if not name or name.lower() in seen_names:
            continue
        seen_names.add(name.lower())
        tags, seen_tags = [], set()
        for tag in cat.get("tags") or []:
            tag = " ".join(str(tag).split())[:MAX_TAG_LEN]
            key = tag.lower().replace("_", " ")
            if tag and key not in seen_tags and key not in BLOCKED_TAGS:
                seen_tags.add(key)
                tags.append(tag)
            if len(tags) >= MAX_TAGS:
                break
        # Adult categories only show in the Adult 18+ workspace; older files are flagged by name.
        adult = bool(cat["adult"]) if "adult" in cat else bool(ADULT_NAME.search(name))
        categories.append({"name": name, "tags": tags, "adult": adult})
    return {"categories": categories}


def load():
    with _lock:
        if os.path.exists(PATH):
            try:
                with open(PATH, encoding="utf-8") as f:
                    return _clean(json.load(f))
            except (OSError, ValueError):
                pass
        return _clean(DEFAULT)


def save(data):
    data = _clean(data)
    with _lock:
        os.makedirs(os.path.dirname(PATH), exist_ok=True)
        tmp = PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, PATH)
    return data
