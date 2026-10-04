# LoRA Lab

A friendly app on top of **your own ComfyUI**: write one prompt, tick several LoRAs, and get them side by side with the
same seed. No models are included — you use whatever checkpoints and LoRAs you already have, and how fast it runs
depends only on your own computer.

![LoRA Lab icon](web/icon-192.png)

## What it does

- **Compare LoRAs** — one column per LoRA (plus an optional "No LoRA" column), same seed, one click.
- **Four model types** — Illustrious / Pony / any SDXL checkpoint, Anima, FLUX.2 Klein, and Z-Image Turbo.
- **Reference images** — start from a photo (image-to-image), or with Klein combine two or three images
  (for example a person plus a top and a bottom garment for virtual try-on).
- **Image → prompt** — drop an image and get ready-made prompts for each model type (WD EVA02 tagger).
- **Tag library** — click tags to add them; add your own categories.
- **Characters** — save a character's look, outfit, LoRAs, reference image and memory (personality, last settings,
  recent prompts, favourite images) and reuse them.
- **Prompt writer (optional)** — describe an idea and a local LLM (via Ollama) writes the prompt.
- **Upscale 4×** and **remove background** from the image viewer.
- **Two separate workspaces** — *General* and *Adult 18+* each keep their own prompt, LoRAs, characters and
  results, so they never mix.

## Requirements

| | |
|---|---|
| **ComfyUI** | A recent version (built and tested on ComfyUI 0.38). [Comfy Desktop](https://www.comfy.org/download), the portable build or a manual install all work. |
| **GPU** | NVIDIA with 6 GB+ VRAM works (slowly) — 8–12 GB is comfortable. Apple Silicon and AMD work wherever ComfyUI runs, at their own speed. |
| **Models** | At least one model for the model type you want (see below). |
| **Optional** | [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF) for `.gguf` models · [Ollama](https://ollama.com) for the prompt writer |

## Install

**With ComfyUI-Manager:** *Manager → Install via Git URL →* paste this repository's URL, then restart ComfyUI.

**By hand:**

```bash
cd ComfyUI/custom_nodes
git clone <this repository's URL> comfyui-lora-lab
# then install the one dependency into ComfyUI's Python:
<ComfyUI's python> -m pip install -r comfyui-lora-lab/requirements.txt
```

(or download the ZIP and extract it into `ComfyUI/custom_nodes/comfyui-lora-lab`.)

Restart ComfyUI and open **`http://127.0.0.1:8188/lora-lab`**
(use your ComfyUI port if it isn't 8188 — Comfy Desktop often uses 8000).

**Windows app window (optional):** run `launcher/LoRALab.exe`. It opens LoRA Lab in its own window and starts ComfyUI
in the background if it isn't running (it finds Comfy Desktop automatically; for other installs copy
`LoRALab.example.json` to `LoRALab.json` and set `comfyui_folder`). Make a shortcut to it on your desktop or Start menu.

## Models — download only what you want

Put files in the matching ComfyUI `models/` folder, then press **↻** in LoRA Lab's LoRA list (or restart ComfyUI).

| Model type | Main model (`models/…`) | Also needs | Good for |
|---|---|---|---|
| **Illustrious / Pony** | any SDXL checkpoint → `checkpoints/` (e.g. [Illustrious XL](https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0), [NoobAI XL](https://huggingface.co/Laxhar/noobai-XL-1.1), Pony V6, [RealVisXL](https://huggingface.co/SG161222/RealVisXL_V5.0)) | — | anime & illustration (tags); RealVisXL for realistic photos |
| **Anima** | `anima-base-v1.0.safetensors` → `diffusion_models/` ([circlestone-labs/Anima](https://huggingface.co/circlestone-labs/Anima)) | `qwen_3_06b_base` → `text_encoders/`, `qwen_image_vae` → `vae/` (same repo) | anime (tags) |
| **Klein** | FLUX.2 Klein 4B or 9B → `diffusion_models/` ([4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B), [9B](https://huggingface.co/black-forest-labs/FLUX.2-klein-9B); GGUF versions need ComfyUI-GGUF) | text encoder + VAE from [Comfy-Org (4B)](https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-4b) / [(9B)](https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-9b) | photoreal, photo editing, 2–3 reference images |
| **Z-Image** | `z_image_turbo_bf16` → `diffusion_models/` ([Comfy-Org/z_image_turbo](https://huggingface.co/Comfy-Org/z_image_turbo)) | `qwen_3_4b` → `text_encoders/`, `ae.safetensors` → `vae/` | photoreal ads & posters with readable text |

LoRAs go in `models/loras/`. LoRA Lab reads each LoRA's built-in info to show which model type it belongs to.

**Extras (optional):** background removal — `birefnet.safetensors` from
[Comfy-Org/BiRefNet](https://huggingface.co/Comfy-Org/BiRefNet) → `models/background_removal/` ·
4× upscale — e.g. [RealESRGAN_x4plus.pth](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth)
→ `models/upscale_models/` · the image tagger (~1.3 GB) downloads itself the first time you use it.

**Licenses:** each model has its own license — check it before commercial use. Apache-2.0 (commercial OK): FLUX.2 Klein
**4B**, Z-Image Turbo. **Non-commercial:** FLUX.2 Klein **9B**, Anima. The full list is in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Where your data lives

Everything stays on your computer:

- Tag library, characters and LoRA settings: `ComfyUI/user/default/lora-lab-*.json`
- Generated images: ComfyUI's `output/LoRA-Lab/` folder
- Per-browser settings (workspace, layout): the browser's local storage

## Using it from another device

LoRA Lab is a web page served by ComfyUI, so a phone or another PC on your network can use it if ComfyUI is started
with `--listen` (or `"listen_on_network": true` in `LoRALab.json`). **ComfyUI has no password** — only do this on a
network you trust, and never expose it to the internet.

## Content rules

LoRA Lab is a tool; you are responsible for what you make with it and for following the law and each model's license.
The *Adult 18+* workspace is for adults only. These safeguards are built in and can't be switched off:

- Child-related terms are always added to the negative prompt, and stripped from tag lists, characters and prompts.
- LoRAs trained on child-related content (detected from their training tags) are blocked.
- The General workspace never runs adult LoRAs, hides adult tag categories and asks the prompt writer for safe content.

## Troubleshooting

- **"The tagger isn't loaded" / buttons do nothing** — restart ComfyUI after installing; check its console for
  `[LoRA Lab]` errors (usually a missing `onnxruntime`: install `requirements.txt` into ComfyUI's Python).
- **A model type says "No … model found"** — the files aren't in the folders above, or ComfyUI hasn't rescanned yet.
- **Out of memory** — use smaller sizes, fewer images per LoRA, a GGUF/fp8 model, or start ComfyUI with `--lowvram`.
- **Prompt writer errors** — it's optional; install Ollama and run e.g. `ollama pull mistral`.
  Set `LORA_LAB_LLM_MODEL` to choose a specific model.

## User guide

The full guide is in [web/USER_GUIDE.md](web/USER_GUIDE.md), and inside the app under **? Guide** (top left).

## License

MIT — see [LICENSE](LICENSE). Models and LoRAs you download are covered by their own licenses; see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for credits and licenses of everything LoRA Lab works with.

LoRA Lab is an independent project, not affiliated with Comfy Org or any model maker named here.
