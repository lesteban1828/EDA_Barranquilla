"""Descarga de OpenStreetMap los elementos del entorno que usa el capítulo 7.

Se corre una sola vez y guarda datos/entorno_osm.csv con una fila por punto:
categoria, nombre, lat, lon. Las líneas (río y vías) se guardan como puntos cada ~25 m
para poder medir distancias con las mismas herramientas que los puntos.

Datos © colaboradores de OpenStreetMap, licencia ODbL.
"""
import json, math, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

import pandas as pd

URL = "https://overpass-api.de/api/interpreter"
CAJA = "10.88,-74.93,11.08,-74.74"          # sur, oeste, norte, este: área de Barranquilla
SALIDA = Path(__file__).parent / "datos" / "entorno_osm.csv"

# categoría -> (filtros de Overpass, es línea)
CONSULTAS = {
    "rio":             (['way["waterway"="river"]', 'way["natural"="water"]["water"="river"]'], True),
    "via_principal":   (['way["highway"~"^(trunk|primary)$"]'], True),
    "transmetro":      (['node["public_transport"="station"]', 'way["public_transport"="station"]',
                         'node["highway"="bus_stop"]["network"~"Transmetro",i]',
                         'node["amenity"="bus_station"]'], False),
    "colegio":         (['nwr["amenity"="school"]'], False),
    "universidad":     (['nwr["amenity"~"^(university|college)$"]'], False),
    "salud":           (['nwr["amenity"~"^(hospital|clinic)$"]'], False),
    "parque":          (['nwr["leisure"="park"]'], False),
    "centro_comercial": (['nwr["shop"="mall"]'], False),
    "supermercado":    (['nwr["shop"="supermarket"]'], False),
}


def consultar(filtros, linea):
    cuerpo = "".join(f"{f}({CAJA});" for f in filtros)
    salida = "out geom;" if linea else "out center;"
    q = f"[out:json][timeout:120];({cuerpo});{salida}"
    pedido = urllib.request.Request(URL, data=urllib.parse.urlencode({"data": q}).encode(),
                                    headers={"User-Agent": "EDA-seminario-vivienda-barranquilla/1.0"})
    for intento in range(5):                       # el servidor público a veces responde 502/504
        try:
            return json.load(urllib.request.urlopen(pedido, timeout=180))["elements"]
        except urllib.error.HTTPError as error:
            if error.code not in (429, 502, 503, 504) or intento == 4:
                raise
            time.sleep(15 * (intento + 1))


def densificar(geom, paso_m=25):
    """Puntos cada ~paso_m metros a lo largo de una línea."""
    puntos = []
    for a, b in zip(geom[:-1], geom[1:]):
        dlat = (b["lat"] - a["lat"]) * 111_320
        dlon = (b["lon"] - a["lon"]) * 111_320 * math.cos(math.radians(a["lat"]))
        n = max(1, int(math.hypot(dlat, dlon) // paso_m))
        puntos += [(a["lat"] + (b["lat"] - a["lat"]) * k / n, a["lon"] + (b["lon"] - a["lon"]) * k / n)
                   for k in range(n)]
    return puntos + [(geom[-1]["lat"], geom[-1]["lon"])]


filas = []
for categoria, (filtros, linea) in CONSULTAS.items():
    elementos = consultar(filtros, linea)
    for e in elementos:
        nombre = e.get("tags", {}).get("name", "")
        if linea and "geometry" in e:
            filas += [(categoria, nombre, la, lo) for la, lo in densificar(e["geometry"])]
        elif "lat" in e:
            filas.append((categoria, nombre, e["lat"], e["lon"]))
        elif "center" in e:
            filas.append((categoria, nombre, e["center"]["lat"], e["center"]["lon"]))
    print(f"{categoria:17s} {len(elementos):5d} elementos")
    time.sleep(2)                                  # pausa entre consultas para no saturar el servidor

tabla = pd.DataFrame(filas, columns=["categoria", "nombre", "lat", "lon"]).drop_duplicates()
tabla.to_csv(SALIDA, index=False)
print(f"\nGuardado {SALIDA} con {len(tabla):,} puntos")
print(tabla.categoria.value_counts().to_string())
