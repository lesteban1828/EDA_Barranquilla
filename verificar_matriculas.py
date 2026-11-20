"""Verificación manual, paso a paso, de cada venta contra las REST API del catastro.

Para cada venta del IGAC elegida arma las cuatro consultas al servicio público del
Distrito (miciudad.barranquilla.gov.co, ArcGIS REST) y el valor que debe salir en cada
una, para comparar a mano lo que tiene nuestra base con lo que dice el catastro hoy:

  Paso 1  Predio (500)          matrícula        → número predial, condición, estrato
  Paso 2  Unidad (305)          número predial   → objectid de la unidad, piso, área del polígono
  Paso 3  Características (505) objectid (paso 2) → área construida, habitaciones, baños, año
  Paso 4  Terreno (315)         código del lote  → polígono; nuestra coordenada debe caer dentro

Uso:
    python verificar_matriculas.py                       # 10 ventas al azar
    python verificar_matriculas.py 20                    # 20 al azar
    python verificar_matriculas.py 040-615314 040-412    # matrículas concretas
    python verificar_matriculas.py sospechosas           # predio en otra manzana que la vía anterior
    python verificar_matriculas.py poligono terreno.geojson 10.990247 -74.84772
        # paso 4: ¿cae el punto dentro del polígono que guardaste desde el navegador?

Escribe `datos/enriquecida/verificacion_matriculas.html` (enlaces que se pueden pulsar) y
`verificacion_matriculas.csv` (con columnas para anotar el resultado de cada paso).

Ojo con el paso 3: el `objectid` es un número interno que el Distrito renumera al
republicar la capa (pasó entre agosto y noviembre de 2026). Úsalo siempre tal como lo
devuelve el paso 2 hoy; si no coincide con el de la ficha, vale el del servicio.
"""
import html
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).parent
FR = Path("C:/Users/Juanes Garcia Gomez/Downloads/fr/datos")
BASE_URL = "https://miciudad.barranquilla.gov.co/gis/rest/services/catastro/datosabiertos/FeatureServer"


def poligono(ruta: str, lat: float, lon: float) -> None:
    """Paso 4 sin transcribir vértices: ¿el punto cae dentro del GeoJSON guardado?"""
    from matplotlib.path import Path as Trazo
    g = json.load(open(ruta, encoding="utf-8"))
    anillos = []
    for f in g.get("features", [g]):
        geo = f.get("geometry", f)
        partes = geo["coordinates"] if geo["type"] == "Polygon" else [r for p in geo["coordinates"] for r in p]
        anillos += [np.array(r) for r in partes]
    dentro = any(Trazo(r).contains_point((lon, lat)) for r in anillos)
    v = np.vstack(anillos)
    print(f"Polígono: longitud {v[:, 0].min():.6f} a {v[:, 0].max():.6f} · "
          f"latitud {v[:, 1].min():.6f} a {v[:, 1].max():.6f}")
    print(f"Punto ({lat}, {lon}): {'DENTRO del terreno ✔' if dentro else 'FUERA del terreno ✘'}")


args = sys.argv[1:]
if args[:1] == ["poligono"]:
    poligono(args[1], float(args[2]), float(args[3]))
    sys.exit()

a = pd.read_parquet(AQUI / "datos/enriquecida/tabla_a_enriquecida.parquet")
a = a[(a.fuente == "igac") & (a.origen_predio == "matricula")].copy()
a["motivo"] = "muestra al azar"
if args == ["sospechosas"]:
    viejo = pd.read_parquet(AQUI / "datos/enriquecida/tabla_a_enriquecida_anterior_14sep.parquet",
                            columns=["id", "CODIGO"]).rename(columns={"CODIGO": "codigo_via_anterior"})
    a = a.merge(viejo, on="id", how="left")
    otra = (a.codigo_via_anterior.notna()
            & (a.codigo_via_anterior.astype(str).str[:17] != a.CODIGO.astype(str).str[:17]))
    a.loc[otra, "motivo"] = "otra manzana que la vía anterior (" + a.codigo_via_anterior.astype(str) + ")"
    muestra = a[otra]
    print(f"Sospechosas: {len(muestra)} ventas con el predio en otra manzana que la vía anterior")
elif args and not args[0].isdigit():
    muestra = a[a.matricula.isin(args)]
    faltan = set(args) - set(muestra.matricula)
    if faltan:
        print("No cruzaron por matrícula (o no existen):", ", ".join(sorted(faltan)))
else:
    muestra = a.sample(int(args[0]) if args else 10)

# capas locales para armar las consultas y los valores esperados
unidades = pd.read_parquet(FR / "miciudad/unidad_construccion.parquet",
                           columns=["objectid", "local_id", "planta_ubicacion", "Shape__Area"])
unidades["local_id"] = unidades.local_id.astype(str).str.strip()
unidades = unidades[unidades.local_id.isin(set(muestra.CODIGO.astype(str)))]
terrenos = set(pd.read_parquet(AQUI / "datos/enriquecida/terreno_ladm_coordenadas.parquet").name)
predio = pd.read_parquet(FR / "miciudad/predio.parquet", columns=["numero_predial_nacional", "globalid"])
predio["numero_predial_nacional"] = predio.numero_predial_nacional.astype(str).str.strip()
guid = predio.drop_duplicates("numero_predial_nacional").set_index("numero_predial_nacional").globalid
direc = pd.read_parquet(FR / "miciudad/direccion.parquet",
                        columns=["cr_predio_guid", "nombre_predio", "es_direccion_principal"])
direc = (direc.sort_values("es_direccion_principal", ascending=False)
              .drop_duplicates("cr_predio_guid").set_index("cr_predio_guid").nombre_predio)

fichas = []
for _, r in muestra.iterrows():
    npn = str(r.CODIGO)
    num = int(r.matricula.split("-")[1])
    lote = npn if npn in terrenos else npn[:21] + "900000000"
    u = unidades[unidades.local_id == npn].sort_values("Shape__Area", ascending=False)
    oids = ",".join(str(int(x)) for x in u.objectid)
    fichas.append({
        "matricula": r.matricula, "motivo": r.motivo, "precio": r.precio, "anio": r.anio,
        "direccion": direc.get(guid.get(npn), ""),
        "p1_url": (f"{BASE_URL}/500/query?where=matricula_inmobiliaria%3D{num}"
                   "&outFields=matricula_inmobiliaria,numero_predial_nacional,condicion_predio,estrato"
                   "&returnGeometry=false&f=html"),
        "p1_esperado": f"numero_predial_nacional = {npn} · condicion_predio = {r.condicion_predio} · estrato = {r.estrato}",
        "p2_url": (f"{BASE_URL}/305/query?where=local_id%3D%27{npn}%27"
                   "&outFields=objectid,local_id,planta_ubicacion,Shape__Area&returnGeometry=false&f=html"),
        "p2_esperado": (f"{len(u)} unidad(es): " + "; ".join(
            f"objectid {int(x.objectid)}, piso {x.planta_ubicacion}, {x.Shape__Area:.1f} m²" for x in u.itertuples())),
        "p3_url": (f"{BASE_URL}/305/queryRelatedRecords?objectIds={oids}"
                   "&relationshipId=6&outFields=*&returnGeometry=false&f=html"),
        "p3_esperado": (f"area_construida = {r.area_unidad_principal:g} (la unidad de vivienda) · "
                        f"total_habitaciones = {r.total_habitaciones:g} · total_banios = {r.total_banios:g} · "
                        f"anio_construccion = {r.anio_construccion:g} · origen: {r.origen_caract}"),
        "p4_url": (f"{BASE_URL}/315/query?where=name%3D%27{lote}%27"
                   "&outFields=name,Shape__Area&returnGeometry=true&outSR=4326&f=geojson"),
        "p4_esperado": f"terreno {lote} · nuestra coordenada (lat {r.lat:.6f}, lon {r.lon:.6f}) dentro del polígono",
        "lat": r.lat, "lon": r.lon,
        "ok_p1": "", "ok_p2": "", "ok_p3": "", "ok_p4": "", "notas": "",
    })

for f in fichas:
    print("\n" + "=" * 100)
    print(f"Matrícula {f['matricula']}  ·  {f['direccion'] or '(sin dirección)'}  ·  "
          f"${f['precio']:,.0f} ({f['anio']})  [{f['motivo']}]")
    for p in ("p1", "p2", "p3", "p4"):
        print(f"  {p.upper()}  {f[p + '_url']}\n       debe dar: {f[p + '_esperado']}")

t = pd.DataFrame(fichas)
t.to_csv(AQUI / "datos/enriquecida/verificacion_matriculas.csv", sep=";", decimal=",",
         index=False, encoding="utf-8-sig")

# la misma información con enlaces que se pueden pulsar
PASOS = {"p1": "Paso 1 · Predio (500): matrícula → número predial",
         "p2": "Paso 2 · Unidad (305): número predial → objectid y área del polígono",
         "p3": "Paso 3 · Características: objectid → área, habitaciones, baños",
         "p4": "Paso 4 · Terreno (315): polígono del lote (GeoJSON)"}
filas_html = []
for f in fichas:
    pasos = "".join(
        f"<li><a href='{html.escape(f[p + '_url'])}' target='_blank'>{PASOS[p]}</a>"
        f"<br><span>Debe dar: {html.escape(f[p + '_esperado'])}</span></li>" for p in PASOS)
    filas_html.append(
        f"<section><h2>{f['matricula']}</h2><p>{html.escape(str(f['direccion']))} · "
        f"${f['precio']:,.0f} ({f['anio']}) · {html.escape(f['motivo'])}</p><ol>{pasos}</ol></section>")
(AQUI / "datos/enriquecida/verificacion_matriculas.html").write_text(
    "<!doctype html><meta charset='utf-8'><title>Verificación de matrículas</title>"
    "<style>body{font-family:Segoe UI,Arial;max-width:900px;margin:24px auto;padding:0 16px;color:#222}"
    "section{border-top:2px solid #24384C;margin-top:24px}li{margin:10px 0}span{color:#3C546B;font-size:14px}"
    "</style><h1>Verificación paso a paso contra el catastro</h1>"
    "<p>En el paso 3 usa el <b>objectid que devuelva el paso 2 hoy</b>; el Distrito lo renumera. "
    "Para el paso 4 guarda el GeoJSON (Ctrl+S) y corre "
    "<code>python verificar_matriculas.py poligono archivo.geojson lat lon</code>.</p>"
    + "".join(filas_html), encoding="utf-8")
print(f"\n{len(t)} ventas -> datos/enriquecida/verificacion_matriculas.html y .csv")
