"""Asigna barrio y localidad desde el predio catastral más cercano (≤ 150 m) a las ventas
que no los traen. Marca el origen en `origen_barrio`. Uso: python rellenar_barrio.py <carpeta>"""
import sys
import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

N = sys.argv[1]
PREDIOS = "C:/Users/Juanes Garcia Gomez/Downloads/fr/datos/barranquilla/predios.parquet"
RADIO_M = 150
ruta = N + "/datos/base_final_excel_es.csv"

c = pd.read_csv(ruta, sep=";", dtype=str, keep_default_na=False)
num = lambda s: pd.to_numeric(s.str.replace(",", ".", regex=False), errors="coerce")
lat, lon = num(c.lat), num(c.lon)
vacio = lambda s: s.fillna("").astype(str).str.strip() == ""

pr = pd.read_parquet(PREDIOS, columns=["BARRIO", "LOCALIDAD", "latitud", "longitud"]).dropna(subset=["latitud", "longitud"])
con_punto = (lat.notna() & lon.notna()).to_numpy()
xy = np.radians(np.c_[lat[con_punto], lon[con_punto]])

def vecino(col):
    p = pr[~vacio(pr[col])]
    d, i = BallTree(np.radians(p[["latitud", "longitud"]].to_numpy()), metric="haversine").query(xy, k=1)
    valor = np.full(len(c), "", dtype=object)
    cerca = np.zeros(len(c), dtype=bool)
    valor[con_punto] = p[col].astype(str).str.strip().to_numpy()[i[:, 0]]
    cerca[con_punto] = d[:, 0] * 6_371_000 <= RADIO_M
    return valor, cerca

c["origen_barrio"] = np.where(vacio(c.barrio), "", "original")
for col, src in [("barrio", "BARRIO"), ("localidad", "LOCALIDAD")]:
    valor, cerca = vecino(src)
    llenar = vacio(c[col]).to_numpy() & cerca
    c.loc[llenar, col] = valor[llenar]
    if col == "barrio":
        c.loc[llenar, "origen_barrio"] = "predio_mas_cercano"
    print(f"{col}: rellenadas {llenar.sum():,}; siguen vacías {vacio(c[col]).sum():,}")

c.to_csv(ruta, sep=";", index=False)

b = pd.read_parquet(N + "/datos/enriquecida/base_final.parquet")
assert (b.id.to_numpy() == c.id.to_numpy()).all()
for col in ("barrio", "localidad", "origen_barrio"):
    b[col] = c[col].str.strip().replace("", pd.NA).to_numpy()
b.to_parquet(N + "/datos/enriquecida/base_final.parquet", index=False)
