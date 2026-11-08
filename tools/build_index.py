#!/usr/bin/env python3
"""Bygger props/index.json från alla SVG-filer i props/<kategori>/.

Lägg en ny pryl genom att släppa en .svg-fil i en kategorimapp (eller i en ny mapp,
så blir det en ny kategori). GitHub Actions kör det här skriptet före varje bygge,
så APK:n får alltid med allt. Kör det själv om du vill uppdatera webbversionen.

Valfritt: en fil props/<kategori>/_category.txt med kategorins visningsnamn
på första raden.
"""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "props")

# kategorier i den här ordningen först, övriga i bokstavsordning efter
ORDER = ["glass", "gems", "shapes", "nature", "food", "critters", "things"]
NAMES = {
    "glass": "Glass & beads",
    "gems": "Gems",
    "shapes": "Shapes",
    "nature": "Nature",
    "food": "Food",
    "critters": "Critters",
    "things": "Things",
}


def pretty(stem):
    s = re.sub(r"[_\-]+", " ", stem).strip()
    return s[:1].upper() + s[1:]


def main():
    cats = []
    dirs = [d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)) and not d.startswith(".")]
    dirs.sort(key=lambda d: (ORDER.index(d) if d in ORDER else len(ORDER), d))
    for d in dirs:
        files = sorted(f for f in os.listdir(os.path.join(ROOT, d)) if f.lower().endswith(".svg"))
        if not files:
            continue
        name = NAMES.get(d, pretty(d))
        label = os.path.join(ROOT, d, "_category.txt")
        if os.path.exists(label):
            with open(label, encoding="utf-8") as fh:
                name = fh.readline().strip() or name
        cats.append({
            "id": d,
            "name": name,
            "items": [{"id": f"{d}/{f[:-4]}", "name": pretty(f[:-4]), "file": f"props/{d}/{f}"} for f in files],
        })
    with open(os.path.join(ROOT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump({"categories": cats}, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(sum(len(c["items"]) for c in cats), "props in", len(cats), "categories")


if __name__ == "__main__":
    main()
