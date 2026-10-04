# Third-party notices

LoRA Lab's own code (the Python files, `web/`, and `launcher/`) is original work released under the MIT License
(see `LICENSE`). It does **not** include any model weights, LoRAs, images or fonts. The page uses no third-party
JavaScript or CSS libraries.

LoRA Lab is an independent project. It is **not affiliated with or endorsed by** Comfy Org, Black Forest Labs,
Alibaba/Tongyi, CircleStone Labs, OnomaAI, Laxhar, Pony Diffusion's authors, fal.ai, SmilingWolf, Danbooru, Ollama or
any other project named below. Their names are used only to say what LoRA Lab works with.

## Software LoRA Lab runs with (not included)

| Project | License | How LoRA Lab uses it |
|---|---|---|
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | GPL-3.0 | LoRA Lab is a ComfyUI custom node and runs inside ComfyUI. See the note below. |
| [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF) | Apache-2.0 | Optional, loads `.gguf` models. |
| [Ollama](https://github.com/ollama/ollama) | MIT | Optional, runs the AI prompt writer. |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime) | MIT | Runs the image tagger (installed from `requirements.txt`). |
| [huggingface_hub](https://github.com/huggingface/huggingface_hub) | Apache-2.0 | Downloads the image tagger model (comes with ComfyUI). |

**About ComfyUI's GPL-3.0 license:** custom nodes run inside ComfyUI's process. MIT is compatible with the GPL, so
LoRA Lab can be published under MIT, and many ComfyUI custom nodes are. When LoRA Lab is distributed *together with*
ComfyUI as one bundle, the bundle as a whole falls under GPL-3.0. If you prefer to match ComfyUI exactly, you can
release LoRA Lab under GPL-3.0 instead.

## Material derived from other projects

| What | Source | License |
|---|---|---|
| Kaomoji list and image preprocessing for the tagger (`tagger.py`) | [SmilingWolf's WD tagger reference code](https://huggingface.co/spaces/SmilingWolf/wd-tagger) | Apache-2.0 |
| Default "TRYON" / "TRYOFF" prompts for the virtual try-on LoRAs (`web/index.html`) | [fal/flux-klein-9b-virtual-tryon-lora](https://huggingface.co/fal/flux-klein-9b-virtual-tryon-lora), [fal/virtual-tryoff-lora](https://huggingface.co/fal/virtual-tryoff-lora) model cards | Apache-2.0 |
| Starter tag names in the tag library (`taglib.py`) | Common [Danbooru](https://danbooru.donmai.us) tag conventions (single words and short phrases) | Not copyrightable facts; credited for the naming convention |

## Models users can download (not included)

Each model has its own license. Users download and accept these themselves.

| Model | License | Commercial use of the model |
|---|---|---|
| [WD EVA02 Large Tagger v3](https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3) (downloaded on first use) | Apache-2.0 | Yes |
| [Illustrious XL v2.0](https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0) | CreativeML OpenRAIL-M | Yes, with the license's use restrictions |
| [NoobAI XL](https://huggingface.co/Laxhar/noobai-XL-1.1) | Fair AI Public License 1.0-SD | Read the license (it has conditions on sharing derivatives) |
| [RealVisXL V5.0](https://huggingface.co/SG161222/RealVisXL_V5.0) | CreativeML OpenRAIL++-M | Yes, with use restrictions |
| Pony Diffusion V6 XL | See its Civitai page | Read its license |
| [Anima](https://huggingface.co/circlestone-labs/Anima) | CircleStone Labs Non-Commercial License | **No** |
| [FLUX.2 Klein 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) | Apache-2.0 | Yes |
| [FLUX.2 Klein 9B](https://huggingface.co/black-forest-labs/FLUX.2-klein-9B) (and its text encoder) | FLUX Non-Commercial License | **No** (needs a license from Black Forest Labs) |
| [Z-Image Turbo](https://huggingface.co/Comfy-Org/z_image_turbo) | Apache-2.0 | Yes |
| [BiRefNet](https://huggingface.co/Comfy-Org/BiRefNet) (background removal) | MIT | Yes |
| [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) (upscaling) | BSD-3-Clause | Yes |
| fal virtual try-on / try-off LoRAs | Apache-2.0 | The LoRAs yes, but they need Klein 9B (non-commercial) |
