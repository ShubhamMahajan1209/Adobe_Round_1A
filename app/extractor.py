#!/usr/bin/env python3
"""
Round‑1A  •  Connecting‑the‑Dots challenge
=========================================
Input : single PDF path            (argv[1])
Output: JSON written to argv[2]    (Title + H1/H2/H3 outline)

Pure PyMuPDF – fast, deterministic, ≤ 30 MB image.  Works fully offline and
handles mixed scripts because it relies on geometric / typographic cues only.
"""
from __future__ import annotations
import fitz, json, re, sys
from collections import Counter, defaultdict

# ─── heuristics ────────────────────────────────────────────────────────────────
MIN_SIZE          = 8              # ignore microscopic footer text
MAX_HEADING_WORDS = 14
TITLE_BAND        = 0.35           # top‑of‑page fraction used for title lines
IGNORE_TOKENS = {
    "copyright", "page", "signature", "telephone",
    "email", "fax", "version", "remarks"
}

def normalise(txt: str) -> str:
    return re.sub(r"\s+", " ", txt.strip(" .:\u2022\t\r\n"))

def is_noise(txt: str) -> bool:
    lo = txt.lower()
    if len(txt.split()) > MAX_HEADING_WORDS:
        return True
    if any(tok in lo for tok in IGNORE_TOKENS):
        return True
    # all‑caps line containing digits → probably address / footer
    return txt.isupper() and any(ch.isdigit() for ch in txt)

def font_buckets(doc):
    sizes = [
        round(sp["size"])
        for pg in doc
        for bl in pg.get_text("dict")["blocks"]
        for ln in bl.get("lines", [])
        for sp in ln["spans"]
    ]
    # four most frequent sizes, descending
    return sorted({s for s, _ in Counter(sizes).most_common(4)}, reverse=True)

def lvl(sz, buckets):
    for i, b in enumerate(buckets):
        if sz >= b:               # bucket 0 → H1, bucket 1 → H2, …
            return f"H{i+1}"
    return None

def glue_single_letters(items):
    """Join the ‘T  o  P  r  e  s  e  n  t’ artefact into one heading."""
    acc, out = [], []
    for itm in items:
        if len(itm["text"]) == 1 and itm["level"] == "H1":
            acc.append(itm["text"])
            continue
        if acc:
            itm["text"] = "".join(acc) + " " + itm["text"].lstrip()
            acc.clear()
        out.append(itm)
    return out

def extract(pdf: str) -> dict:
    doc       = fitz.open(pdf)
    buckets   = font_buckets(doc)
    outline   = []
    title_raw = []

    # build page‑local stop‑sets (duplicate upper‑headers)
    stops = defaultdict(set)
    for pno, pg in enumerate(doc):
        caps = Counter(
            normalise(" ".join(sp["text"] for ln in bl.get("lines", [])
                               for sp in ln["spans"]))
            for bl in pg.get_text("dict")["blocks"]
        )
        for txt, n in caps.items():
            if n >= 2 and 3 <= len(txt.split()) <= 8:
                stops[pno].add(txt.lower())

    for pno, pg in enumerate(doc):
        h_page = pg.rect.height
        blocks = pg.get_text("dict")["blocks"]

        local_hist = Counter(
            round(sp["size"])
            for bl in blocks
            for ln in bl.get("lines", [])
            for sp in ln["spans"]
        )

        for bl in blocks:
            y0 = bl["bbox"][1]
            for ln in bl.get("lines", []):
                spans = ln["spans"]
                if not spans:
                    continue
                size = round(spans[0]["size"])
                if size < MIN_SIZE or local_hist[size] > 15:
                    continue
                text = normalise(" ".join(sp["text"] for sp in spans))
                if not text or is_noise(text) or text.lower() in stops[pno]:
                    continue
                level = lvl(size, buckets)
                if not level:
                    continue

                # candidate title lines on the first page
                if pno == 0 and y0 < h_page * TITLE_BAND:
                    title_raw.append((y0, text))
                    continue

                # numeric prefix (“3.2.1”) → treat as at least H2
                if re.match(r'^\d+(\.\d+)*(\s|[.)])', text):
                    level = "H2"

                outline.append({"level": level, "text": text, "page": pno + 1})

    # ─── build robust title ────────────────────────────────────────────────
    title_raw.sort(key=lambda t: t[0])
    title = normalise("  ".join(t for _, t in title_raw))
    if not title:
        # fallback: biggest centred line on first page
        big_sz = buckets[0]
        for bl in doc[0].get_text("dict")["blocks"]:
            for ln in bl.get("lines", []):
                sp = ln["spans"][0]
                if (round(sp["size"]) == big_sz
                        and 3 <= len(sp["text"].split()) <= 12):
                    cand = normalise(sp["text"])
                    if cand:
                        title = cand
                        break
            if title:
                break

    outline = glue_single_letters(outline)

    # final de‑dup
    seen, clean = set(), []
    for itm in outline:
        key = (itm["level"], itm["text"])
        if key not in seen:
            seen.add(key)
            clean.append(itm)

    return {"title": title, "outline": clean}

# ─── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: extract_outline.py input.pdf output.json")
    res = extract(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as fp:
        json.dump(res, fp, indent=4, ensure_ascii=False)
