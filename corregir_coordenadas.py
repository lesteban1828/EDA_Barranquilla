"""Corrige las coordenadas que caen fuera de Barranquilla en la base final.

Reemplaza cada una por la coordenada del edificio en el terreno LADM (código predial, o
predio matriz `[:21] + "900000000"`). Si no la encuentra, la deja vacía. Debe correrse
antes de `rellenar_barrio.py`, que usa la coordenada.

    python corregir_coordenadas.py <carpeta del libro>
"""
import sys

import numpy as np
import pandas as pd

N = sys.argv[1]
LAT, LON = (10.85, 11.15), (-74.95, -74.70)
ruta = N + "/datos/base_final_excel_es.csv"

c = pd.read_csv(ruta, sep=";", dtype=str, keep_default_na=False)
num = lambda s: pd.to_numeric(s.str.replace(",", ".", regex=False), errors="coerce")
lat, lon = num(c.lat), num(c.lon)
fuera = lat.notna() & ~(lat.between(*LAT) & lon.between(*LON))

ter = pd.read_parquet(N + "/datos/enriquecida/terreno_ladm_coordenadas.parquet").set_index("name")
cod = c.codigo_predial.str.replace('="', "", regex=False).str.replace('"', "", regex=False).str.strip()
nueva_lat = cod.map(ter.latitud).fillna((cod.str[:21] + "900000000").map(ter.latitud))
nueva_lon = cod.map(ter.longitud).fillna((cod.str[:21] + "900000000").map(ter.longitud))

coma = lambda x: "" if pd.isna(x) else repr(float(x)).replace(".", ",")
for i in np.where(fuera)[0]:
    print(f"{c.id[i]}: ({lat[i]}, {lon[i]}) -> ({nueva_lat[i]}, {nueva_lon[i]})")
    c.loc[i, "lat"], c.loc[i, "lon"] = coma(nueva_lat[i]), coma(nueva_lon[i])
print(f"Coordenadas fuera de Barranquilla corregidas: {fuera.sum()}")
c.to_csv(ruta, sep=";", index=False)

b = pd.read_parquet(N + "/datos/enriquecida/base_final.parquet")
assert (b.id.to_numpy() == c.id.to_numpy()).all()
b["lat"], b["lon"] = num(c.lat).to_numpy(), num(c.lon).to_numpy()
b.to_parquet(N + "/datos/enriquecida/base_final.parquet", index=False)
