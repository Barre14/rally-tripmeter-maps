#!/usr/bin/env python3
"""Snijdt de kaarten uit regions.json uit de wereldkaart van Protomaps en
schrijft catalog.json voor de app.

Gebruik: scripts/build.py <bron.pmtiles of URL> <edition> <uitvoermap>
Vereist het programma `pmtiles` (github.com/protomaps/go-pmtiles).
"""
import hashlib
import json
import os
import subprocess
import sys


def bounds(geojson_path):
    """Zuidwest en noordoost van alle punten in een GeoJSON-bestand."""
    data = json.load(open(geojson_path))
    lons, lats = [], []

    def walk(c):
        if isinstance(c[0], (int, float)):
            lons.append(c[0])
            lats.append(c[1])
        else:
            for x in c:
                walk(x)

    for feature in data["features"]:
        walk(feature["geometry"]["coordinates"])
    return [round(min(lons), 4), round(min(lats), 4), round(max(lons), 4), round(max(lats), 4)]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    source, edition, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    maps = []
    for region in json.load(open("regions.json")):
        name = region["id"] + ".pmtiles"
        target = os.path.join(out, name)
        subprocess.run(["pmtiles", "extract", source, target,
                        "--region=" + region["region"],
                        "--maxzoom=" + str(region["maxzoom"])], check=True)
        maps.append({
            "id": region["id"],
            "name": region["name"],
            "file": name,
            "size": os.path.getsize(target),
            "sha256": sha256(target),
            "bounds": bounds(region["region"]),
        })
        # Op GitHub: de vaste link naar het bestand in deze editie.
        repository = os.environ.get("GITHUB_REPOSITORY")
        if repository:
            maps[-1]["url"] = (f"https://github.com/{repository}/releases/download/"
                               f"edition-{edition}/{name}")
        print(f"{name}: {maps[-1]['size'] / 1e6:.0f} MB")
    catalog = {"format": 1, "edition": edition, "maps": maps}
    with open(os.path.join(out, "catalog.json"), "w") as f:
        json.dump(catalog, f, indent=2)


if __name__ == "__main__":
    main()
