
# Connecting the Dots – Round 1A  
PDF Outline Extraction Solution
================================

## 1 · Overview  
This repository contains a **Docker-ready, offline** solution for **Round 1A** of Adobe’s *Connecting the Dots* challenge.  
The container receives PDF files (≤ 50 pages) inside **`/app/input`**, extracts the document **title** plus **H1/H2/H3 headings** (with page numbers) and writes a matching JSON file to **`/app/output`** — all in **< 10 s** on CPU, with **≤ 200 MB** of total model/code size and **zero network access**.

---

## 2 · Approach  

| Stage | Description |
|-------|-------------|
| **1. Text extraction** | Uses **PyMuPDF (`fitz`)** for fast parsing of text, font sizes, positions, and page layout. |
| **2. Noise cleanup** | Removes repetitive headers/footers using Y-position clustering. |
| **3. Heading candidates** | Extracts short, large-font lines and filters out long paragraphs or noise. |
| **4. Level inference** | Maps top font sizes to heading levels (H1/H2/H3) using frequency buckets. |
| **5. Title detection** | Picks the largest, top-of-page text block on page 1 as title. |
| **6. Multilingual bonus** | Works language-independently using only layout — supports Latin, RTL, CJK out of the box. |
| **7. JSON output** | Outputs a clean JSON tree with deduplication, artifact fixing, and proper hierarchy. |

> 🎯 This implementation does **not use ML models**, keeping size small and startup instant.

---

## 3 · Dependencies  

| Package | Purpose | Size |
|---------|---------|------|
| `PyMuPDF` | Fast PDF parsing | ~45 MB |
| `regex` / `re` | Text and numeric matching | negligible |
| ❌ No ML, Pandas, or Numpy | Keeps image ≤ 200 MB | ✅ |

All dependencies are listed in `requirements.txt` and are installed inside the Docker image.

---

## 4 · Build the Docker Image  

Open a terminal in the repo root and run:

```bash
docker build --platform linux/amd64 -t outline-extractor:latest .
```

> 🐳 This builds a self-contained container from `python:3.11-slim` with all scripts and dependencies installed.

---

## 5 · Prepare Input and Output Folders  

In your project folder:

```bash
mkdir input output
```

Place your test PDFs in the `input/` folder.  
Each file should be ≤ 50 pages, per the challenge requirement.

---

## 6 · Run the Extractor  

### ✅ For **Linux/macOS/WSL**:

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  --network none \
  outline-extractor:latest
```

### ✅ For **Windows PowerShell**:

```powershell
docker run --rm `
  -v "${PWD}\input:/app/input" `
  -v "${PWD}\output:/app/output" `
  --network none `
  outline-extractor:latest
```

### ✅ For **Windows CMD**:

```cmd
docker run --rm ^
  -v "%cd%\input:/app/input" ^
  -v "%cd%\output:/app/output" ^
  --network none ^
  outline-extractor:latest
```

You should see:
```
✓ processed 5 PDF(s)
```

---

## 7 · View Output  

Each `file.pdf` in `input/` produces a `file.json` in `output/`.

Use any viewer or formatter to read the result:

```bash
cat output/yourfile.json | jq .
```

Or simply open in VS Code / browser.

---

## 8 · Project Structure  

```
pdf-outline-extractor/
├── Dockerfile
├── extractor.py        ← heading-extraction logic
├── run.sh              ← entry point
├── requirements.txt
├── README.md           ← this file
├── input/              ← place PDFs here
└── output/             ← extracted JSONs here
```

---

## 9 · Limitations & Future Work  
- Tables/figures with bold captions may be misclassified as headings.  
- PDF files with too many font-size variations might need adaptive thresholds.  
- A small optional on-device ML model (<200 MB) could enhance precision further.

---

## 10 · Credits  
Created by **Beyond Code** for Adobe *Connecting the Dots Hackathon 2025*.  
Happy Hacking! 🎉

---

✅ **Works Offline** · 🐳 Dockerized · ⚡ Fast · 📑 Accurate · 🌍 Multilingual · 📁 Outputs JSON
