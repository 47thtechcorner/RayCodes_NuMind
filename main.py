"""
Vision to Insight - 100% Local Image-to-JSON QnA Pipeline
NuExtract3 (VLM) extracts structured JSON from an image.
Gemma4 / fast-qna answers natural-language questions about that JSON.
"""

import os
import json
import requests
import ollama

# ── Config ────────────────────────────────────────────────
IMAGE_URL  = "https://upload.wikimedia.org/wikipedia/commons/0/0b/ReceiptSwiss.jpg"
IMAGE_PATH = "receipt.jpg"

EXTRACT_MODEL = "nuextract"
QNA_MODEL     = "fast-qna"

SCHEMA_PROMPT = (
    "Extract data from this receipt into this exact JSON schema: "
    "{'vendor': 'string', 'items': [{'name': 'string', 'price': 'float'}], "
    "'total': 'float', 'tax': 'float'}. Output ONLY valid JSON."
)

QNA_PROMPT = (
    "Here is parsed JSON data from a receipt: {extracted_json}. "
    "What is the name of the vendor, and if I bought two of every item on this list, "
    "what would my new total be before tax? Give a concise answer."
)


# ── Step 1: Download receipt image ────────────────────────
def download_image():
    if os.path.exists(IMAGE_PATH):
        print(f"[✓] Receipt image already exists: {IMAGE_PATH}")
        return
    print("[→] Downloading sample receipt image...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(IMAGE_URL, headers=headers, stream=True, timeout=30)
    resp.raise_for_status()
    with open(IMAGE_PATH, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"[✓] Saved: {IMAGE_PATH}")


# ── Step 2: Extract JSON from image via NuExtract ─────────
def extract_json(image_path: str) -> str:
    print(f"\n[→] Extracting JSON with NuExtract ({EXTRACT_MODEL})...")
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = ollama.chat(
        model=EXTRACT_MODEL,
        messages=[{"role": "user", "content": SCHEMA_PROMPT, "images": [image_bytes]}],
        options={"temperature": 0.1}
    )

    raw = response["message"]["content"].strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = "\n".join(
            line for line in raw.splitlines()
            if not line.strip().startswith("```")
        ).strip()

    print(f"[✓] Extracted JSON:\n{raw}\n")
    return raw


# ── Step 3: QnA over extracted JSON via fast-qna ──────────
def run_qna(extracted_json: str) -> str:
    print(f"[→] Running QnA with fast-qna ({QNA_MODEL})...")
    response = ollama.chat(
        model=QNA_MODEL,
        messages=[{"role": "user", "content": QNA_PROMPT.format(extracted_json=extracted_json)}],
        options={"temperature": 0.1}
    )
    return response["message"]["content"].strip()


# ── Main ──────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  Vision to Insight - Image-to-JSON QnA Pipeline")
    print("=" * 50)

    download_image()

    extracted_json = extract_json(IMAGE_PATH)

    try:
        json.loads(extracted_json)
    except json.JSONDecodeError as e:
        print(f"[!] Warning: output may not be valid JSON: {e}")

    answer = run_qna(extracted_json)

    print("=" * 50)
    print("  FINAL QnA ANSWER")
    print("=" * 50)
    print(answer)
    print("=" * 50)

    open("receipt_extracted.json", "w").write(extracted_json)
    open("qna_answer.txt", "w").write(answer)
    print("[✓] Outputs saved: receipt_extracted.json  |  qna_answer.txt")


if __name__ == "__main__":
    main()
