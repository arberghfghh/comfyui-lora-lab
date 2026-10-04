# WD EVA02 v3 tagger: image -> Danbooru tags with confidences (CPU, onnxruntime).
import csv
import io
import os
import threading

import numpy as np
from PIL import Image, ImageOps

import folder_paths

MODEL_NAME = "wd-eva02-large-tagger-v3"
MODEL_DIR = os.path.join(folder_paths.models_dir, "wd_tagger", MODEL_NAME)

# Tags that keep their underscores (from SmilingWolf's reference implementation).
KAOMOJIS = {
    "0_0", "(o)_(o)", "+_+", "+_-", "._.", "<o>_<o>", "<|>_<|>", "=_=", ">_<", "3_3", "6_9", ">_o",
    "@_@", "^_^", "o_o", "u_u", "x_x", "|_|", "||_||",
}

_lock = threading.Lock()
_session = None
_tags = None

# The model (~1.3 GB) is downloaded from Hugging Face the first time someone tags an image.
REPO = "SmilingWolf/" + MODEL_NAME
_dl_lock = threading.Lock()
_dl_thread = None
_dl_error = None


def _model_ready():
    return all(os.path.exists(os.path.join(MODEL_DIR, f)) for f in ("model.onnx", "selected_tags.csv"))


def _download():
    global _dl_error
    try:
        from huggingface_hub import hf_hub_download
        os.makedirs(MODEL_DIR, exist_ok=True)
        for f in ("selected_tags.csv", "model.onnx"):
            hf_hub_download(REPO, f, local_dir=MODEL_DIR)
    except Exception as e:
        _dl_error = f"{type(e).__name__}: {e}"


def ensure_model():
    """None when the tagger is ready; otherwise starts the one-time download and returns a message."""
    global _dl_thread, _dl_error
    if _model_ready():
        return None
    with _dl_lock:
        if _dl_error:
            err, _dl_error, _dl_thread = _dl_error, None, None
            return f"Downloading the image tagger failed ({err}). Try again, or download {REPO} into {MODEL_DIR}."
        if _dl_thread is None or not _dl_thread.is_alive():
            _dl_thread = threading.Thread(target=_download, daemon=True)
            _dl_thread.start()
    return "Downloading the image tagger (about 1.3 GB, one time only). Try again in a few minutes."


def _load():
    global _session, _tags
    with _lock:
        if _session is None:
            import onnxruntime as ort

            model_path = os.path.join(MODEL_DIR, "model.onnx")
            csv_path = os.path.join(MODEL_DIR, "selected_tags.csv")
            if not (os.path.exists(model_path) and os.path.exists(csv_path)):
                raise FileNotFoundError(f"Tagger model not found in {MODEL_DIR}")
            with open(csv_path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            _tags = [(r["name"] if r["name"] in KAOMOJIS else r["name"].replace("_", " "), int(r["category"])) for r in rows]
            _session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    return _session, _tags


def _prepare(data, size):
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGBA")
    flat = Image.new("RGBA", img.size, (255, 255, 255, 255))
    flat.alpha_composite(img)
    img = flat.convert("RGB")
    w, h = img.size
    side = max(w, h)
    square = Image.new("RGB", (side, side), (255, 255, 255))
    square.paste(img, ((side - w) // 2, (side - h) // 2))
    square = square.resize((size, size), Image.BICUBIC)
    arr = np.asarray(square, dtype=np.float32)[:, :, ::-1]  # RGB -> BGR, 0-255, NHWC
    return np.ascontiguousarray(arr)[None]


def tag_image(data):
    session, tags = _load()
    inp = session.get_inputs()[0]
    probs = session.run([session.get_outputs()[0].name], {inp.name: _prepare(data, int(inp.shape[1]))})[0][0]
    ratings, general, character = {}, [], []
    for (name, category), p in zip(tags, probs):
        p = float(p)
        if category == 9:
            ratings[name] = p
        elif category == 4 and p >= 0.5:
            character.append([name, p])
        elif category == 0 and p >= 0.2:
            general.append([name, p])
    general.sort(key=lambda t: -t[1])
    character.sort(key=lambda t: -t[1])
    return {"ratings": ratings, "general": general, "character": character}
