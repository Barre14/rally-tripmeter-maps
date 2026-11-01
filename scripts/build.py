#!/usr/bin/env python3
"""Snijdt de kaarten uit regions.json uit de wereldkaart van Protomaps en
schrijft catalog.json voor de app.

Gebruik: scripts/build.py <bron.pmtiles of URL> <edition> <uitvoermap> [release-tag]

Met een release-tag gaat elk bestand meteen naar die (concept)release op
GitHub en daarna van de schijf: alle landen samen passen niet op de
bouwmachine. Vereist `pmtiles` (github.com/protomaps/go-pmtiles) en, met een
tag, `gh`.
"""
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import regions  # noqa: E402

# Overlap tussen de delen van een gesplitst land (graden), zodat er op de
# grens geen gat valt.
MARGIN = 0.05


def bounds(rings):
    lons = [p[0] for ring in rings for p in ring]
    lats = [p[1] for ring in rings for p in ring]
    return [round(min(lons), 4), round(min(lats), 4), round(max(lons), 4), round(max(lats), 4)]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    source, edition, out = sys.argv[1], sys.argv[2], sys.argv[3]
    tag = sys.argv[4] if len(sys.argv) > 4 else None
    repository = os.environ.get("GITHUB_REPOSITORY")
    os.makedirs(out, exist_ok=True)
    maps = []
    for region in json.load(open("regions.json")):
        name = region["id"] + ".pmtiles"
        target = os.path.join(out, name)
        area = os.path.join(out, region["id"] + ".geojson")
        regions.write(region, area, MARGIN)
        subprocess.run(["pmtiles", "extract", source, target, "--region=" + area,
                        "--maxzoom=" + str(region["maxzoom"])], check=True)
        outline = regions.outline(region)
        entry = {
            "id": region["id"],
            "name": region["name"],
            "file": name,
            "size": os.path.getsize(target),
            "sha256": sha256(target),
            "bounds": bounds(outline),
            # Omtrek van het gebied: de app kiest daarmee de kaart voor je positie.
            "area": outline,
        }
        if repository and tag:
            entry["url"] = f"https://github.com/{repository}/releases/download/{tag}/{name}"
        maps.append(entry)
        print(f"{name}: {entry['size'] / 1e6:.0f} MB", flush=True)
        os.remove(area)
        if tag:
            subprocess.run(["gh", "release", "upload", tag, target, "--clobber"], check=True)
            os.remove(target)
    maps.sort(key=lambda m: m["name"])
    catalog = {"format": 1, "edition": edition, "maps": maps}
    path = os.path.join(out, "catalog.json")
    with open(path, "w") as f:
        json.dump(catalog, f, separators=(",", ":"))
    if tag:
        subprocess.run(["gh", "release", "upload", tag, path, "--clobber"], check=True)


if __name__ == "__main__":
    main()
