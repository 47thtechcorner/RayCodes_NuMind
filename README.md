<!-- YOUTUBE SEO BLOCK — helps Google index this repo alongside the video -->
<!-- Video: NuExtract3 + Gemma 4: 100% Local Image-to-JSON Pipeline -->
<!-- Watch: [https://youtu.be/a_vPhVIPTmU](https://youtu.be/L66rOi7xjuc) -->

# Vision to Insight - 100% Local Image-to-JSON QnA Pipeline

> **As featured in the YouTube video:** 🎬 [NuExtract3 + Gemma 4: 100% Local Image-to-JSON Pipeline](https://youtu.be/L66rOi7xjuc) - A fully offline, two-stage AI pipeline that turns any image into structured JSON using a local Vision-Language Model (NuExtract3), then answers natural-language questions about that data using Gemma4 - no cloud APIs, no subscriptions, no data leaving your machine.

[![YouTube Video](https://img.shields.io/badge/YouTube-Watch%20the%20Video-red?logo=youtube&style=for-the-badge)](https://youtu.be/L66rOi7xjuc)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&style=for-the-badge)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-black?logo=ollama&style=for-the-badge)](https://ollama.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## 🧠 How It Works

```
Receipt Image (JPG)
       │
       ▼
 ┌─────────────────────────────────┐
 │  Stage 1: NuExtract3 (VLM)      │  ← Vision model reads the image
 │  Ollama model: nuextract         │     and outputs structured JSON
 └─────────────┬───────────────────┘
               │  { "vendor": ..., "items": [...], "total": ..., "tax": ... }
               ▼
 ┌─────────────────────────────────┐
 │  Stage 2: Gemma4 (LLM)          │  ← Language model receives the JSON
 │  Ollama model: fast-qna          │     and answers your question
 └─────────────┬───────────────────┘
               │
               ▼
       Terminal Answer ✅
```

**Stage 1 - NuExtract3 (`nuextract`):** A quantized VLM (Q2_K GGUF) specialized for structured data extraction. It receives the raw image and a target JSON schema, and returns only valid JSON - no prose, no padding.

**Stage 2 - Gemma4 (`fast-qna`):** A fast, instruction-tuned LLM that receives the extracted JSON as context and answers a natural-language question with calculations. Configured to skip `<think>` reasoning tokens and return only the direct answer.

---

## 🛠️ Tech Stack

| Component | Model | Purpose |
|---|---|---|
| Inference runtime | [Ollama](https://ollama.com) | Local model serving |
| Vision extraction | [NuExtract3](https://huggingface.co/numind/NuExtract3-GGUF) (Q2_K) | Image → JSON |
| QnA + reasoning | [Gemma4](https://ollama.com/library/gemma4) (e2b) | JSON → Answer |
| Python client | `ollama` Python library | API calls to Ollama |

---

## ✅ Prerequisites

1. **Ollama installed globally** - Download from [https://ollama.com](https://ollama.com) and ensure `ollama` is on your `PATH`.

2. **Gemma4 e2b pulled** - The `fast-qna` model is built on top of this base. Pull it once:
   ```powershell
   ollama pull gemma4:e2b
   ```

3. **Python 3.9+** with pip available.

4. **~500 MB free disk space** - for the NuExtract3 GGUF file.

---

## 📦 Install Dependencies

```powershell
pip install ollama requests
```

---

## ⚙️ One-Time Setup

### 1. Download the NuExtract3 GGUF model
Download `NuExtract3-Q2_K.gguf` and place it in the project root:
```
https://huggingface.co/numind/NuExtract3-GGUF/resolve/main/NuExtract3-Q2_K.gguf
```

### 2. Register both models with Ollama
Run these two commands once from the project directory:
```powershell
ollama create nuextract -f Modelfile.nuextract
ollama create fast-qna  -f Modelfile.gemma
```
Verify they appear:
```powershell
ollama list
```

---

## 🚀 Run & Test

```powershell
# Navigate to the project directory
cd "d:\Ray Codes\AG Projects\NuMind"

# Run the pipeline
python main.py
```

**What happens:**
1. Downloads `receipt.jpg` (sample Swiss receipt from Wikipedia) if not present
2. Sends image to `nuextract` → prints extracted JSON
3. Sends JSON to `fast-qna` → prints the final answer

**To use your own image:**
```powershell
copy "C:\path\to\your\receipt.jpg" ".\receipt.jpg"
python main.py
```

---

## 📁 Project Structure

```
Vision-to-Insight/
├── main.py                   # Full pipeline script
├── Modelfile.nuextract       # Ollama config for NuExtract3 VLM
├── Modelfile.gemma           # Ollama config for Gemma4 LLM
├── README.md                 # This file
├── receipt.jpg               # Auto-downloaded on first run
├── receipt_extracted.json    # Ideal Stage 1 output (reference)
├── qna_answer.txt            # Ideal Stage 2 output (reference)
└── NuExtract3-Q2_K.gguf     # Auto-downloaded on first run (~500 MB)
```

---

## 🔧 Modelfile Details

### `Modelfile.nuextract`
```
FROM ./NuExtract3-Q2_K.gguf   ← Loads the local GGUF file
PARAMETER temperature 0.1      ← Near-deterministic for reliable JSON
PARAMETER num_ctx 4096         ← Context window for image + schema
SYSTEM "..."                   ← Instructs model to output only JSON
```

### `Modelfile.gemma`
```
FROM gemma4:e2b                ← Builds on top of locally pulled Gemma4
PARAMETER temperature 0.1      ← Keeps answers concise and factual
SYSTEM "..."                   ← Blocks <think> tokens, directs to JSON context
```

Both models are registered in Ollama's local registry under custom names (`nuextract`, `fast-qna`), keeping them isolated from your other Ollama models.

---

## 💡 Practical Use Cases

- **Expense Automation** - Snap receipts and auto-populate expense reports with structured data
- **Retail Analytics** - Digitize paper receipts from stores into queryable JSON databases
- **Medical Records** - Extract structured fields from scanned lab reports or prescription slips
- **Legal Document Processing** - Pull key clauses or figures from contract images locally (privacy-safe)
- **Inventory Management** - Parse delivery invoices or purchase orders into item-level records

---

## 🔮 Future Feature Ideas

- **Batch Processing** - Accept a folder of images and process all receipts in a loop
- **Streamlit UI** - Add a drag-and-drop web interface to upload images and display results
- **Schema Configurator** - Let users define custom JSON schemas via a YAML config file
- **SQLite Export** - Auto-insert extracted JSON rows into a local SQLite database
- **Multi-language Support** - Extend prompts to handle receipts in French, German, or Japanese

---

## 🔒 Privacy

100% of inference runs locally. No images, JSON, or answers are ever sent to an external server. Ideal for sensitive financial, medical, or legal documents.

---

---

## 📺 Watch the Full Video

**[Can Tiny AI Beast HRM Text 1B Do Math Reasoning? Tested Against Local LLMs](https://youtu.be/a_vPhVIPTmU)** — Ray Codes on YouTube

This project was built live as part of the video above. Subscribe to [Ray Codes](https://youtube.com/@RayCodes) for more local AI experiments, Python projects, and LLM deep-dives.

> **Keywords:** local LLM, NuExtract3, Gemma4, Ollama, image to JSON, VLM, vision language model, receipt extraction, offline AI, Python AI pipeline, HRM Text 1B, math reasoning LLM, local AI benchmark

---

*Vision to Insight — Built with [Ollama](https://ollama.com) · [NuExtract3](https://huggingface.co/numind/NuExtract3-GGUF) · [Gemma4](https://ollama.com/library/gemma4) | Featured on [Ray Codes YouTube](https://youtube.com/@RayCodes)*
