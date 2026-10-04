# LoRA Lab: a standalone page for generating the same prompt across several LoRAs.
# It adds no nodes; ComfyUI just serves ./web at /extensions/lora-lab/
# Open: http://127.0.0.1:8188/lora-lab
import asyncio
import logging
import os

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

try:
    from aiohttp import web
    from server import PromptServer

    from . import tagger

    # Stable address: /lora-lab works whatever folder name the node was installed under.
    _page = "/extensions/" + os.path.basename(os.path.dirname(os.path.abspath(__file__))) + "/index.html"

    @PromptServer.instance.routes.get("/lora-lab")
    async def lora_lab_page(request):
        raise web.HTTPFound(_page)

    @PromptServer.instance.routes.post("/lora-lab/tag")
    async def lora_lab_tag(request):
        form = await request.post()
        upload = form.get("image")
        if upload is None or not hasattr(upload, "file"):
            return web.json_response({"error": "No image uploaded"}, status=400)
        data = upload.file.read()
        pending = tagger.ensure_model()
        if pending:
            return web.json_response({"error": pending}, status=503)
        try:
            result = await asyncio.get_running_loop().run_in_executor(None, tagger.tag_image, data)
        except FileNotFoundError as e:
            return web.json_response({"error": str(e)}, status=503)
        except Exception as e:
            logging.exception("[LoRA Lab] tagging failed")
            return web.json_response({"error": f"{type(e).__name__}: {e}"}, status=500)
        return web.json_response(result)

    from . import llm

    def _free_comfy_vram():
        queue = PromptServer.instance.prompt_queue
        if queue.get_tasks_remaining() == 0:
            queue.set_flag("unload_models", True)
            queue.set_flag("free_memory", True)

    @PromptServer.instance.routes.post("/lora-lab/llm")
    async def lora_lab_llm(request):
        body = await request.json()
        idea = (body.get("idea") or "").strip()
        if not idea:
            return web.json_response({"error": "Type an idea first"}, status=400)
        try:
            text = await llm.write_prompt(idea, body.get("target", ""), body.get("model") or llm.DEFAULT_MODEL, _free_comfy_vram,
                                          sfw=bool(body.get("sfw")), character=body.get("character"))
        except Exception as e:
            logging.exception("[LoRA Lab] prompt writer failed")
            return web.json_response({"error": str(e)}, status=500)
        return web.json_response({"text": text})

    from . import taglib

    @PromptServer.instance.routes.get("/lora-lab/tags")
    async def lora_lab_tags_get(request):
        return web.json_response(taglib.load())

    @PromptServer.instance.routes.post("/lora-lab/tags")
    async def lora_lab_tags_save(request):
        try:
            data = await request.json()
            return web.json_response(taglib.save(data))
        except Exception as e:
            logging.exception("[LoRA Lab] saving tag library failed")
            return web.json_response({"error": str(e)}, status=500)

    from . import charlib

    @PromptServer.instance.routes.get("/lora-lab/characters")
    async def lora_lab_chars_get(request):
        return web.json_response(charlib.load())

    @PromptServer.instance.routes.post("/lora-lab/characters")
    async def lora_lab_chars_save(request):
        try:
            return web.json_response(charlib.upsert(await request.json()))
        except Exception as e:
            logging.exception("[LoRA Lab] saving character failed")
            return web.json_response({"error": str(e)}, status=500)

    @PromptServer.instance.routes.post("/lora-lab/characters/delete")
    async def lora_lab_chars_delete(request):
        body = await request.json()
        return web.json_response({"deleted": charlib.delete(str(body.get("id", "")))})

    @PromptServer.instance.routes.post("/lora-lab/characters/image")
    async def lora_lab_chars_image(request):
        body = await request.json()
        entry = charlib.add_image(str(body.get("id", "")), body)
        if entry is None:
            return web.json_response({"error": "Unknown character or image"}, status=404)
        return web.json_response(entry)

    @PromptServer.instance.routes.post("/lora-lab/characters/remember")
    async def lora_lab_chars_remember(request):
        try:
            body = await request.json()
            out = charlib.remember(str(body.get("id", "")), body.get("mode"), body.get("settings"), body.get("prompt"))
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
        if out is None:
            return web.json_response({"error": "Unknown character"}, status=404)
        return web.json_response(out)

    from . import loraflags

    @PromptServer.instance.routes.get("/lora-lab/lora-flags")
    async def lora_lab_flags_get(request):
        return web.json_response(loraflags.load())

    @PromptServer.instance.routes.post("/lora-lab/lora-flags")
    async def lora_lab_flags_set(request):
        try:
            body = await request.json()
            return web.json_response(loraflags.set_flag(body.get("name"), body.get("flag")))
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
except Exception:
    logging.exception("[LoRA Lab] image tagger unavailable")
