#!/usr/bin/env python3
"""Bygger ett butikspaket för Kalejdo och för in det i store/catalog.json.

Användning (från mappen där index.html ligger):

    python3 tools/build_pack.py <källmapp>                 # gratispaket
    python3 tools/build_pack.py <källmapp> --code KOD      # betalt paket, krypteras med KOD
    KALEJDO_CODE=KOD python3 tools/build_pack.py <källmapp>

Källmappen innehåller SVG-filerna (en per pryl) och en pack.json, t.ex.

    {
      "id": "ocean",                 // unikt, ändras aldrig
      "name": "Ocean",               // visas i butiken och som kategori
      "description": "Fish, coral and bubbles",
      "price": 0,                    // 0 = gratis; annars pris, t.ex. 19
      "currency": "kr",
      "version": 1,                  // höj när innehållet ändras, så får användarna "Update"
      "buyUrl": "",                  // betallänk som öppnas av knappen Buy (t.ex. Stripe Payment Link)
      "keepColours": false,          // true = Mix colours rör aldrig färgerna
      "preview": ["clownfish", "coral", "jellyfish", "shell"]   // upp till 4 filnamn utan .svg
    }

Betalda paket krypteras med AES-256-GCM. Nyckeln tas fram ur koden med PBKDF2-SHA256
(samma som index.html gör med WebCrypto). Koden normaliseras: versaler, bara A–Z och 0–9,
så "space-2026" och "SPACE 2026" är samma kod. Kräver paketet `cryptography`
(pip install cryptography).

VIKTIGT: Lägg aldrig källmappen till ett betalt paket i det publika GitHub-repot eller på webbservern.
Bara den krypterade filen i store/packs/ ska publiceras.
"""
import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
STORE = os.path.join(ROOT, "store")
ITER = 200_000


def norm_code(code):
    return re.sub(r"[^A-Z0-9]", "", code.upper())


def minify(svg):
    svg = re.sub(r"<\?xml[^>]*>", "", svg)
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<metadata.*?</metadata>", "", svg, flags=re.S)  # t.ex. inbäddad ursprungsinfo
    return re.sub(r">\s+<", "><", svg).strip()


def encrypt(plain: bytes, code: str):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        sys.exit("Betalda paket kräver paketet 'cryptography':  pip install cryptography")
    salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
    key = hashlib.pbkdf2_hmac("sha256", norm_code(code).encode(), salt, ITER, 32)
    data = AESGCM(key).encrypt(iv, plain, None)  # chiffertext + 16 byte tagg, som WebCrypto vill ha
    b = lambda x: base64.b64encode(x).decode()
    return {"alg": "AES-GCM/PBKDF2-SHA256", "iter": ITER, "salt": b(salt), "iv": b(iv), "data": b(data)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="källmapp med pack.json och SVG-filer")
    ap.add_argument("--code", default=os.environ.get("KALEJDO_CODE", ""), help="upplåsningskod (betalda paket)")
    a = ap.parse_args()

    with open(os.path.join(a.src, "pack.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    pid = meta["id"]
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", pid):
        sys.exit("id får bara innehålla a-z, 0-9, - och _")
    files = sorted(f for f in os.listdir(a.src) if f.lower().endswith(".svg"))
    if not files:
        sys.exit("Inga SVG-filer i " + a.src)
    items = []
    for f in files:
        with open(os.path.join(a.src, f), encoding="utf-8") as fh:
            items.append({"name": f[:-4], "svg": minify(fh.read())})

    price = meta.get("price", 0) or 0
    payload = json.dumps({"id": pid, "items": items}, ensure_ascii=False, separators=(",", ":")).encode()
    if price > 0:
        if not norm_code(a.code):
            sys.exit("Betalt paket: ange --code (eller KALEJDO_CODE)")
        out = {"id": pid, "encrypted": encrypt(payload, a.code)}
    else:
        out = json.loads(payload)

    os.makedirs(os.path.join(STORE, "packs"), exist_ok=True)
    rel = f"packs/{pid}.json"
    with open(os.path.join(STORE, rel), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))

    by_name = {it["name"]: it["svg"] for it in items}
    preview = [by_name[n] for n in meta.get("preview", []) if n in by_name][:4] or [it["svg"] for it in items[:4]]
    entry = {
        "id": pid, "name": meta["name"], "description": meta.get("description", ""),
        "price": price, "currency": meta.get("currency", "kr"), "version": meta.get("version", 1),
        "items": len(items), "file": rel, "buyUrl": meta.get("buyUrl", ""),
        "keepColours": bool(meta.get("keepColours", False)), "preview": preview,
    }
    cat_path = os.path.join(STORE, "catalog.json")
    catalog = {"packs": []}
    if os.path.exists(cat_path):
        with open(cat_path, encoding="utf-8") as fh:
            catalog = json.load(fh)
    packs = catalog.setdefault("packs", [])
    for i, p in enumerate(packs):
        if p["id"] == pid:
            packs[i] = entry
            break
    else:
        packs.append(entry)
    with open(cat_path, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    kind = f"betalt ({price} {entry['currency']}), krypterat" if price > 0 else "gratis"
    print(f"{meta['name']}: {len(items)} prylar, {kind} -> store/{rel}")


if __name__ == "__main__":
    main()
