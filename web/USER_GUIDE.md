# LoRA Lab — User Guide

LoRA Lab is an app that runs on top of your own **ComfyUI**. You write one prompt, pick some LoRAs, and LoRA Lab makes
one image per LoRA with the same seed, so you can compare them side by side. It also helps you write prompts, keep
characters consistent, start from photos, and clean up images afterwards.

Everything runs on your own computer. Nothing is uploaded anywhere.

---

## 1. Before you start

**You need:**

- **ComfyUI** (recent version), with LoRA Lab installed in its `custom_nodes` folder. See the README for install steps.
- **At least one model** for the kind of image you want (see [Model types](#4-model-types)).
- **LoRAs** (optional) in ComfyUI's `models/loras` folder.

**Open LoRA Lab:**

- In any browser: `http://127.0.0.1:8188/lora-lab` (use your ComfyUI port if it isn't 8188 — Comfy Desktop often uses 8000).
- On Windows you can also run `launcher/LoRALab.exe`, which opens LoRA Lab in its own window and starts ComfyUI for
  you if needed.

The dot at the top left turns **green** when LoRA Lab is connected to ComfyUI.

---

## 2. The screen at a glance

**Left sidebar — your setup, in the order you'll use it:**

| Section | What it's for |
|---|---|
| **General / Adult 18+** switch | Two separate workspaces (see [Workspaces](#11-workspaces-general-and-adult-18)). |
| **1 · Model** | Choose the model type and the model file. |
| **2 · LoRAs to compare** | Tick the LoRAs you want; each one becomes a column. |
| **3 · Character** *(optional)* | Use a saved character's look, outfit and LoRAs. |
| **4 · Reference images** *(optional)* | Start from a photo, or combine two or three images. |
| **5 · Size & seed** | Image size, how many images, the seed, and advanced settings. |

Click a section's title to fold it away. LoRA Lab remembers which sections you folded.

**Right side — two tabs:**

- **Create** — the prompt box, the **Generate** button, the **Tag library**, and your results.
- **Characters** — create and edit characters.

---

## 3. Your first image (2 minutes)

1. In **1 · Model**, click a model type (for example **Illustrious / Pony**) and choose a model file.
2. In **2 · LoRAs to compare**, leave everything unticked for now. "Include a No LoRA image" makes one plain image.
3. In the **Prompt** box, type what you want. For Illustrious/Pony use comma-separated tags:
   `1girl, solo, long silver hair, golden eyes, black kimono, wooden bridge, cherry blossoms, night`
4. Press **Generate** (or **Ctrl+Enter**).
5. Watch the progress bar and live preview. Click the finished image to see it full size.

Now tick two or three LoRAs and press Generate again — you'll get one column per LoRA, all with the same seed.

---

## 4. Model types

Pick the model type first; LoRA Lab sets good defaults for each.

| Model type | Best for | How to write prompts | Typical speed on a 6 GB GPU |
|---|---|---|---|
| **Illustrious / Pony** (any SDXL checkpoint) | Anime and illustration; realistic photos with checkpoints like RealVisXL | Tags: `1girl, long hair, red dress` | ~20–60 s |
| **Anima** | Anime | Tags | ~40–60 s |
| **Klein** (FLUX.2 Klein 4B / 9B) | Photoreal images, editing photos, combining 2–3 reference images | Sentences: "A woman in a red dress on a balcony at night…" | ~60–120 s |
| **Z-Image** (Z-Image Turbo) | Photoreal ads and posters, readable text in images | Sentences; put text to render in "quotes" | ~60–90 s |

- **Pony** checkpoints are detected automatically and get Pony's quality tags (`score_9, score_8_up, …`).
- Each model type has its own LoRAs. LoRA Lab reads each LoRA's built-in info and only lists the ones that fit.
- If a model type says *"No … model found"*, its files aren't in ComfyUI's model folders yet.

---

## 5. Comparing LoRAs

Each ticked LoRA becomes a **column**. Every column uses the **same seed**, so the only difference is the LoRA.

On each LoRA card:

- **Tick box** — include it in the next run.
- **Strength** (number box) — how strongly the LoRA applies. 0.6–1.0 is usual; lower is subtler.
- **Badges** — the model type it's for (SDXL, Anima, Klein, Z-Image) and **Pony** if it was trained on Pony.
- **18+** — moves the LoRA to the other workspace (see [Workspaces](#11-workspaces-general-and-adult-18)).
- Tick a LoRA to open its details:
  - **Trigger words** — words this LoRA needs. They're added to the start of your prompt for that column only.
  - **Trained tags** — the tags it was trained on. Click one to add it to the trigger words.

Other LoRA options:

- **All / None** — tick or untick every LoRA shown.
- **↻** — rescan the LoRA folder after you add new files.
- **Include a "No LoRA" image** — adds a plain column to compare against.
- **Images per LoRA** (in **5 · Size & seed**) — more images per column; each extra image uses the next seed.
- **Show LoRAs made for other model types** (advanced settings) — shows them greyed out.

LoRAs trained on child-related content are **blocked** and never load. The LoRA section says which ones.

---

## 6. Writing prompts

### The prompt box

- **Tags or sentences?** Illustrious, Pony and Anima understand **tags**. Klein and Z-Image understand **sentences**.
- **Quality tags & negative prompt** (fold-out under the prompt) — filled in automatically for each model type. Press
  **↺** to reset them. You rarely need to change these.
- 🔒 Safety terms are always added to the negative prompt; you can't remove them.

### The AI prompt writer (optional)

Type an idea in the line under the prompt ("a knight resting by a campfire at night") and press **✨ Write**
(or Enter). The AI writes a full prompt in the right style for your model type — tags or sentences. **Undo** brings
your old prompt back.

This needs [Ollama](https://ollama.com) running with a chat model (for example `ollama pull mistral`). On slower PCs
it can take a minute or two. If a character is active, the writer also reads that character's **Memory**.

### The Tag library

Below the prompt box. Click a tag to add it to the prompt; click it again to remove it. Tags already in your prompt are
highlighted.

- **Categories** — Subject, Hair, Face, Body, Clothing, Pose, Setting, Camera & light, Style… Click **All** to see every tag.
- **Search** — type to filter.
- **✎ Edit** —
  - Add your own tags (comma-separated) to the selected category, or to **My tags** if "All" is selected.
  - **+ From current prompt** saves every tag in your prompt into the category.
  - Click a tag to delete it; **Delete category** removes the whole category.
  - **New category** creates one. Categories you create in the Adult workspace stay in the Adult workspace.

The tag library is saved on the computer running ComfyUI, so every device that opens LoRA Lab shares it.

---

## 7. Reference images

Open **4 · Reference images** and drop a picture on **Image 1** (or paste with Ctrl+V, or click to choose).

### Get prompts from an image

As soon as you add Image 1, LoRA Lab reads it and writes ready-made prompts for each model type:

- **Copy** copies one; **Use** switches to that model type and puts it in your prompt.
- **Tag threshold** — lower gives more tags, higher gives fewer.
- **Klein / Z-Image** — press **✨ Describe** to have the AI prompt writer turn the tags into sentences.

The first time, the image tagger downloads (about 1.3 GB, once).

### Start from the image

Tick **Use the reference images when generating**.

- **How much to change** — 0.3–0.5 stays close to the photo (same pose, colours, layout); 0.6 is balanced;
  0.8–1.0 only follows it loosely.
- **Match the image's shape** — sets the output size to the photo's proportions.
- **Klein mode:**
  - **Reference edit** (default) keeps the person and scene and changes what your prompt says
    ("make her dress blue"). Great for consistent faces.
  - **Image-to-image** works like the other model types.

### Two or three images (Klein)

Under Image 1 you'll find **Image 2** (and **Image 3** with Klein). Only **Klein** can combine several images:

- Adding Image 2 while on Klein switches the references on automatically.
- On another model type you'll see a yellow note and a **Switch to Klein** button.
- The summary under Generate shows "· 2 reference images" when both will be used.

---

## 8. Recipes

### Virtual try-off (garment on white, "invisible mannequin")

1. Download the fal **virtual try-off** LoRA for Klein 9B into `models/loras`.
2. Model type **Klein**, model **Klein 9B**. Tick the try-off LoRA — its "TRYOFF…" text is filled in for you.
3. Drop a photo of someone wearing the outfit on **Image 1**, tick **Use the reference images**, Klein mode **Reference edit**.
4. Prompt: name the garment, e.g. `the red satin evening dress`. Generate.
5. In the viewer, press **✂ Remove background** for a transparent PNG.

### Virtual try-on (person + top + bottom)

1. Download the fal **virtual try-on** LoRA for Klein 9B. Model type **Klein**, model **Klein 9B**, tick the LoRA.
2. **Image 1** = the person, **Image 2** = the top, **Image 3** = the bottom.
3. Prompt: describe the person and the clothes, e.g. `young woman with long dark hair, black oversized t-shirt and blue jeans`.

### An ad with headline text

1. Model type **Z-Image**.
2. Prompt in sentences, with the text in quotes:
   `Studio product shot of a white sneaker on a pastel podium, soft shadows, bold headline text "RUN LIGHTER"`.
3. Upscale the result with **⤢ Upscale 4×** for print sizes.

### Find the best style LoRA

Tick 4–6 style LoRAs, tick **Include a No LoRA image**, set **Images per LoRA** to 2, and Generate. You get a grid with
two seeds per LoRA plus a plain baseline.

### Keep a character consistent

Create a character with a reference image and appearance tags (see the next section), then use **Klein → Reference edit**
with the character's reference image, or Illustrious/Pony with the character's LoRA.

> Licenses: Klein 9B is **non-commercial**. For paid work use Klein 4B, Z-Image or another model whose license allows it.

---

## 9. Characters

Characters save everything that makes a person look the same in every image.

### Create one

Go to the **Characters** tab → **+ New character**. Everything saves automatically.

| Field | What it does |
|---|---|
| **Reference image** | Drop or paste a picture. The first one also fills in Appearance and Outfit automatically. |
| **Name** and **Made for** | Name, and which model type the character is meant for. |
| **Name tag / trigger words** | A LoRA trigger word or a known character tag. |
| **Appearance** | Hair, eyes, body — things that don't change. |
| **Outfit** | Clothes — change this to change their outfit. |
| **Character LoRAs** | LoRAs added to every image of this character (each with its own strength). |
| **Extra negative tags** | Things to avoid for this character. |
| **Memory** | Personality, backstory, rules about how they look. The AI prompt writer reads this. |
| **Notes** | Your own notes. |

- **✨ Tags from image** reads the reference image again and adds appearance and outfit tags.
- Tip: click into **Appearance** or **Outfit**, then click tags in the **Tag library** — they go into that field.

### Use one

In the sidebar under **3 · Character**, pick the character (or press **Use this character** in the editor). Then tick
what to use:

- **Appearance / Outfit** — added before your prompt, so your prompt only needs the scene ("sitting on a bridge, night").
- **Their LoRAs** — stacked under every column's LoRA, so you can still compare style LoRAs on top.
- **Reference image** — the character's image is used as the reference.

### Memory

LoRA Lab remembers, for each character and each workspace:

- **↺ Use last settings** — the model, size, LoRAs and strengths you last used with them.
- **Recent prompts** — your last 20 prompts with them; pick one to reuse it.
- **Gallery** — every image made with them. **★** marks a favourite (favourites come first);
  **⤴** makes that image their reference image.

Characters belong to the workspace you create them in.

---

## 10. Results and the image viewer

Each Generate run adds a block to **Create** with one column per LoRA. The block's header shows the model, size,
steps, seed and character.

- **Reuse settings** — load that run's settings back into the sidebar.
- **Remove** — delete the block from the list (the image files stay on disk).
- Toolbar: **Thumb size**, **Cancel queued**, **Free VRAM** (unloads models from the GPU), **Clear results**,
  **▶ Generate**.

**Click any image** to open the viewer:

- **← / →** keys move between images; **Esc** closes.
- **Open full size** and **Download**.
- **⤢ Upscale 4×** — needs an upscale model in `models/upscale_models`.
- **✂ Remove background** — transparent PNG; needs a model in `models/background_removal`.

Upscaled and cut-out images appear right after the original in the viewer and are saved in
`output/LoRA-Lab/upscaled` and `output/LoRA-Lab/cutouts`. All other images are saved in `output/LoRA-Lab/<date>/`
(in a subfolder per character when one is active).

---

## 11. Workspaces: General and Adult 18+

The switch at the top of the sidebar flips between two completely separate workspaces. Each keeps its **own** prompt,
model choice, LoRA selection, reference images, characters and results.

**General:**

- Adult LoRAs are not listed and can't run.
- Adult tag categories are hidden.
- The AI prompt writer is told to keep things safe for work, and tags read from reference images skip explicit tags.

**Adult 18+** (for adults only; switching in asks you to confirm):

- Shows adult LoRAs; tick **Also show General LoRAs** to use General ones too.
- The app turns rose-coloured so you always know where you are.

A LoRA is sorted into Adult automatically when its training tags or name are explicit. If the guess is wrong, press
its **18+** button to move it. Your choice is saved for every device.

---

## 12. Settings

Under **5 · Size & seed**:

- **Size** — presets, or Custom. 832 × 1216 (portrait) is a good default; larger sizes need more memory.
- **Images per LoRA** — how many images each column gets.
- **Seed** — the same seed with the same settings gives the same image. **🎲** picks a new one;
  **New random seed every time** does that automatically.
- **Show advanced settings** — reveals:
  - **Model files** — VAE, text encoder, clip skip (SDXL).
  - **Steps** — more steps can add detail but take longer. Defaults: SDXL 28, Anima 30, Klein 4, Z-Image 10.
  - **CFG** — how strictly the prompt is followed. Defaults: SDXL 6, Anima 4, Klein 1.5, Z-Image 1.5.
  - **Sampler / Scheduler**.

---

## 13. Using LoRA Lab from your phone or another PC

LoRA Lab is a web page served by ComfyUI. If ComfyUI is started with `--listen` (or `"listen_on_network": true` in
`LoRALab.json` when you use the launcher), another device on the **same network** can open
`http://<your PC's address>:8188/lora-lab`.

- On a phone, use **Add to Home Screen** for an app-like icon.
- **ComfyUI has no password.** Only do this on a network you trust, and never open ComfyUI to the internet.
  To use it away from home, use a private network tool such as Tailscale.
- Each browser keeps its own layout and workspace; the tag library, characters and images are shared.

---

## 14. Speed and memory tips

- First runs are slower while models load; later runs reuse them.
- Out of memory? Use a smaller size, fewer images per LoRA, GGUF or fp8 model files, or start ComfyUI with `--lowvram`.
- **Free VRAM** before switching to a very different model type, or before using the AI prompt writer.
- Close other GPU-heavy programs (games, video editors) while generating.

---

## 15. Troubleshooting

| Problem | Fix |
|---|---|
| The dot stays red / "Disconnected" | ComfyUI isn't running, or you opened the wrong port. |
| "… isn't loaded — restart ComfyUI once" | You updated LoRA Lab; restart ComfyUI so the new version loads. |
| "No … model found" | Put the model files in the right `models/` folder (see the README) and press **↻**. |
| A LoRA is missing | It may be for another model type, sorted into the other workspace, or blocked. Press **↻** after adding files. |
| Tagging says it's downloading | The image tagger downloads once (about 1.3 GB). Try again in a few minutes. |
| Prompt writer errors | Install Ollama, pull a chat model, and keep Ollama running. |
| Black or broken images | Try another seed or model file. For SDXL, try a different VAE under advanced settings (for example `sdxl_vae`). |
| Errors in red on an image | Hover to read the full message; the ComfyUI console has details. |

---

## 16. Good to know

- **Who owns the images?** Check each model's license — some forbid commercial use (for example Klein 9B and Anima).
  In many countries, images made entirely by AI may not be protected by copyright.
- **Your data** stays on your computer: tag library, characters and LoRA settings in `ComfyUI/user/default/`, images in
  `ComfyUI/output/LoRA-Lab/`.
- **Safety rules** (always on): child-related terms are always in the negative prompt and are removed from tags,
  characters and prompts; LoRAs trained on child-related content are blocked; adult content stays in the Adult workspace.

### Keyboard shortcuts

| Keys | Action |
|---|---|
| Ctrl+Enter | Generate |
| Ctrl+V | Paste an image as Image 1 (or as the character image on the Characters tab) |
| Enter (in the idea box) | Run the AI prompt writer |
| ← / → / Esc | Previous / next / close in the image viewer |
