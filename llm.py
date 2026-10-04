# Prompt writer: turns a short idea into a model-specific prompt using a local Ollama model.
# Optional: needs Ollama (https://ollama.com) with at least one chat model pulled.
import asyncio
import os
import re

import aiohttp

_host = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434").replace("0.0.0.0", "127.0.0.1")
OLLAMA_URL = (_host if _host.startswith("http") else "http://" + _host).rstrip("/")
# Set LORA_LAB_LLM_MODEL to pick a model; otherwise the first of PREFERRED that is installed, else any chat model.
DEFAULT_MODEL = os.environ.get("LORA_LAB_LLM_MODEL", "")
PREFERRED = ("dolphin-venice", "dolphin", "mistral", "llama", "qwen", "gemma")

_ADULTS = "Every person in the image is an adult (18 or older); never describe minors, children or childlike features."
_TAGS = ("Output ONLY lowercase Danbooru tags separated by commas: start with the subject count (e.g. 1girl, 1boy, 2girls, solo), "
         "then character appearance, clothing, pose, expression, setting, lighting and composition. 20-40 tags. "
         "Do NOT include quality or score tags, do not write sentences, do not explain anything.")
SYSTEM = {
    "illustrious": f"You write prompts for Illustrious-XL, an anime image model trained on Danbooru tags. {_TAGS} {_ADULTS}",
    "pony": f"You write prompts for Pony Diffusion V6 XL, an anime image model trained on Danbooru tags. {_TAGS} {_ADULTS}",
    "anima": f"You write prompts for Anima, an anime image model trained on Danbooru tags. {_TAGS} {_ADULTS}",
    "klein": ("You write prompts for FLUX.2 Klein, a photorealistic image model that understands natural language. "
              "Output ONLY the prompt: 2-4 vivid sentences describing the subject, their appearance, clothing, pose and expression, "
              f"the setting, lighting, and camera or art style. No lists, no headings, no explanations. {_ADULTS}"),
    "zimage": ("You write prompts for Z-Image Turbo, a photorealistic image model that understands natural language and can render text. "
               "Output ONLY the prompt: 2-4 vivid sentences describing the subject, setting, lighting, camera and style; if the idea "
               "includes words that should appear in the image (a slogan, brand name or sign), put them in double quotes. "
               f"No lists, no headings, no explanations. {_ADULTS}"),
}
TAG_TARGETS = {"illustrious", "pony", "anima"}

# Same list the page uses for reference-image tags.
BLOCKED_TAGS = {"loli", "shota", "child", "female child", "male child", "kid", "toddler", "baby", "aged down", "underage",
                "young child", "kindergartener", "elementary school student", "middle school student", "childlike body", "randoseru"}


def _clean(text, target):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    text = re.sub(r"^\s*(prompt|tags)\s*:\s*", "", text, flags=re.I).strip().strip('"').strip()
    if target in TAG_TARGETS:
        tags = []
        for t in re.split(r"[,\n]+", text):
            # Strip list markers ("- ", "* ", "3. ") but keep tags like "1girl".
            t = re.sub(r"^(?:[-*•]\s*|\d+[.)]\s+)", "", t.strip().lower()).replace("_", " ").strip(" .")
            if t and t not in BLOCKED_TAGS and t not in tags:
                tags.append(t)
        return ", ".join(tags)
    return " ".join(text.split())


async def _chat(session, model, messages, options):
    payload = {"model": model, "messages": messages, "stream": False, "keep_alive": "2m", "options": options}
    async with session.post(OLLAMA_URL + "/api/chat", json=payload) as r:
        body = await r.json(content_type=None)
        if r.status != 200:
            raise RuntimeError((body or {}).get("error") or f"Ollama returned HTTP {r.status}")
        return body["message"]["content"]


SFW = ("This is the General (safe-for-work) workspace: no nudity, no sexual content and no suggestive poses, "
       "even if the idea asks for it.")


def _character_context(ch):
    """Tell the writer who the image is of, so the scene stays true to the character's memory."""
    if not isinstance(ch, dict) or not ch.get("name"):
        return ""
    parts = [f'The image shows the character "{str(ch["name"])[:60]}".']
    if ch.get("memory"):
        parts.append("Keep these facts about them in mind: " + str(ch["memory"])[:2000])
    parts.append("Their appearance and outfit tags are added automatically, so do not repeat them; "
                 "describe the pose, expression, action, setting and lighting in a way that fits who they are.")
    return " ".join(parts)


async def _pick_model(session, requested):
    async with session.get(OLLAMA_URL + "/api/tags") as r:
        names = [m["name"] for m in (await r.json(content_type=None)).get("models", [])]
    chat = [n for n in names if "embed" not in n.lower()]
    if requested:
        match = next((n for n in chat if n == requested or n.split(":")[0] == requested), None)
        if match:
            return match
    for pref in PREFERRED:
        match = next((n for n in chat if n.lower().startswith(pref)), None)
        if match:
            return match
    if chat:
        return chat[0]
    raise RuntimeError("Ollama has no models yet. Install one, e.g. `ollama pull mistral`, then try again.")


async def write_prompt(idea, target, model=DEFAULT_MODEL, free_vram=None, sfw=False, character=None):
    if target not in SYSTEM:
        raise ValueError(f"Unknown target {target!r}")
    if free_vram:
        free_vram()
        await asyncio.sleep(3)  # let ComfyUI's worker release VRAM before Ollama sizes its GPU layers
    system = " ".join(x for x in (SYSTEM[target], SFW if sfw else "", _character_context(character)) if x)
    messages = [{"role": "system", "content": system}, {"role": "user", "content": idea}]
    options = {"temperature": 0.4, "num_predict": 300}
    timeout = aiohttp.ClientTimeout(total=900)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            model = await _pick_model(session, model)
            try:
                text = await _chat(session, model, messages, options)
            except RuntimeError as e:
                if "memory" not in str(e).lower():
                    raise
                # Not enough VRAM next to ComfyUI: run on CPU only.
                text = await _chat(session, model, messages, dict(options, num_gpu=0))
    except aiohttp.ClientConnectorError:
        raise RuntimeError("Can't reach Ollama. The prompt writer is optional: install Ollama from ollama.com, "
                           "pull a chat model (e.g. `ollama pull mistral`) and keep it running.")
    return _clean(text, target)
