# Rally Tripmeter maps

Offline maps for the [Rally Tripmeter Classic](https://rallytripmeter.inventico.be) app.

Each release is one edition of the maps. The app reads
`releases/latest/download/catalog.json` and downloads the map files it lists.

## How a release is made

The workflow **Build maps** runs on the first of every month (or by hand under
Actions). It takes the latest world build from
[Protomaps](https://docs.protomaps.com/basemaps/downloads), cuts out every
region in `regions.json` up to zoom 14 and publishes the files with a fresh
`catalog.json`.

To add a country: put its border in `regions/` as GeoJSON and add a line to
`regions.json`.

## Licence

Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright),
available under the Open Database License (ODbL). Borders from
[datasets/geo-countries](https://github.com/datasets/geo-countries) (Natural Earth, public domain).
