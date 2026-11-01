# Rally Tripmeter maps

Offline maps for the [Rally Tripmeter Classic](https://rallytripmeter.inventico.be) app.

Each release is one edition of the maps. The app reads
`releases/latest/download/catalog.json` and downloads the map files it lists.

## How a release is made

The workflow **Build maps** runs on the first of every month (or by hand under
Actions). It takes the latest world build from
[Protomaps](https://docs.protomaps.com/basemaps/downloads), cuts out every
region in `regions.json` up to zoom 14 and publishes the files with a fresh
`catalog.json`. Only the two newest editions are kept, and `latest.json` in
this repo records the current one.

To add a country: put its border in `regions/` as GeoJSON and add a line to
`regions.json`. A release file may be at most 2 GB, so large countries are
split with a `clip` rectangle `[west, south, east, north]`: France in four
parts, Germany in two. The parts overlap a little at the seams.

## Maps

| Map | Size |
|---|---|
| Belgium | 340 MB |
| Netherlands | 485 MB |
| Luxembourg | 40 MB |
| France (4 parts) | 570–725 MB each |
| Germany (2 parts) | 1.3–1.4 GB each |
| Switzerland | 294 MB |
| Austria | 554 MB |
| Italy | 1.3 GB |
| Spain | 1.2 GB |
| Portugal | 298 MB |
| United Kingdom | 1.3 GB |
| Denmark | 286 MB |
| Czechia | 553 MB |

## Licence

Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright),
available under the Open Database License (ODbL). Borders from
[datasets/geo-countries](https://github.com/datasets/geo-countries) (Natural Earth, public domain).
