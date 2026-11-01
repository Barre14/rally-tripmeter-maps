"""Gebieden uit regions.json als GeoJSON: een land, eventueel bijgesneden tot
een rechthoek (voor landen die te groot zijn voor één bestand)."""
import json


def clip_ring(ring, box):
    """Sutherland-Hodgman: een ring bijsnijden tot de rechthoek [w, s, e, n]."""
    w, s, e, n = box
    edges = [
        (lambda p: p[0] >= w, lambda a, b: (w, a[1] + (b[1] - a[1]) * (w - a[0]) / (b[0] - a[0]))),
        (lambda p: p[0] <= e, lambda a, b: (e, a[1] + (b[1] - a[1]) * (e - a[0]) / (b[0] - a[0]))),
        (lambda p: p[1] >= s, lambda a, b: (a[0] + (b[0] - a[0]) * (s - a[1]) / (b[1] - a[1]), s)),
        (lambda p: p[1] <= n, lambda a, b: (a[0] + (b[0] - a[0]) * (n - a[1]) / (b[1] - a[1]), n)),
    ]
    points = [tuple(p[:2]) for p in ring]
    for inside, cross in edges:
        if not points:
            break
        out = []
        for i, b in enumerate(points):
            a = points[i - 1]
            if inside(b):
                if not inside(a):
                    out.append(cross(a, b))
                out.append(b)
            elif inside(a):
                out.append(cross(a, b))
        points = out
    if len(points) < 3:
        return None
    return [list(p) for p in points] + [list(points[0])]


def polygons(geometry):
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"]]
    return geometry["coordinates"]


def area(region, margin=0.0):
    """De veelhoeken van een gebied; `margin` vergroot de rechthoek (in graden)."""
    data = json.load(open(region["region"]))
    result = []
    for feature in data["features"]:
        for polygon in polygons(feature["geometry"]):
            if "clip" not in region:
                result.append(polygon)
                continue
            w, s, e, n = region["clip"]
            box = (w - margin, s - margin, e + margin, n + margin)
            rings = [clip_ring(r, box) for r in polygon]
            if rings[0]:
                result.append([r for r in rings if r])
    return result


def write(region, path, margin):
    geometry = {"type": "MultiPolygon", "coordinates": area(region, margin)}
    json.dump({"type": "FeatureCollection",
               "features": [{"type": "Feature", "properties": {}, "geometry": geometry}]},
              open(path, "w"))


def simplify(points, tolerance):
    """Ramer-Douglas-Peucker, voor een lichte omtrek in de catalogus."""
    if len(points) < 4:
        return points
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx, dy = x2 - x1, y2 - y1
    length = (dx * dx + dy * dy) ** 0.5 or 1e-12
    index, distance = 0, 0.0
    for i in range(1, len(points) - 1):
        x, y = points[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / length
        if d > distance:
            index, distance = i, d
    if distance <= tolerance:
        return [points[0], points[-1]]
    return simplify(points[:index + 1], tolerance)[:-1] + simplify(points[index:], tolerance)


def outline(region):
    """Buitenranden van het gebied, vereenvoudigd tot ongeveer 1 km."""
    rings = []
    for polygon in area(region):
        points = [[round(x, 4), round(y, 4)] for x, y in polygon[0]]
        # Een gesloten ring in twee helften, anders valt alles weg (begin = einde).
        far = max(range(len(points)), key=lambda i: (points[i][0] - points[0][0]) ** 2
                  + (points[i][1] - points[0][1]) ** 2)
        ring = simplify(points[:far + 1], 0.01)[:-1] + simplify(points[far:], 0.01)
        if len(ring) >= 4:
            rings.append(ring)
    return rings
