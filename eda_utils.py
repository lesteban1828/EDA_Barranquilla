"""Preparación compartida de la base de análisis.

Repite, sin mostrar tablas ni gráficos, los pasos del capítulo 1 (01_datos.ipynb):
carga, filtro apto_modelo, ajuste por inflación, precio por m² fuera de rango y
registros duplicados. Cada capítulo empieza con `from eda_utils import *`.
"""
import io, math, urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from PIL import Image
from scipy import stats
from sklearn.neighbors import NearestNeighbors, KNeighborsClassifier
from sklearn.model_selection import GroupKFold, cross_val_score

pd.set_option("display.max_columns", 60)
pd.set_option("display.width", 160)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

AZUL, ROJO, VERDE, GRIS = "#2F6F9F", "#C7522A", "#6A9B4F", "#9FB8CC"
ORDEN_ESTRATO = ["Bajo_Bajo_1", "Bajo_2", "Medio_Bajo_3", "Medio_4", "Medio_Alto_5", "Alto_6", "No_Aplica", "Otro"]
ESTRATOS = ORDEN_ESTRATO[:6]
NOMBRES_ESTRATO = [f"Estrato {i}" for i in range(1, 7)]
COLORES_ESTRATO = ["#253494", "#2C7FB8", "#41B6C4", "#FDAE61", "#F46D43", "#A50026"]
NO_BARRIOS = ["RURAL", "ZONA NO DESARROLLADA", "SIN LOCALIDAD"]

# Gráficos interactivos: el formato que lee VS Code y HTML para Jupyter
pio.renderers.default = "plotly_mimetype+notebook_connected"
pio.templates["eda"] = go.layout.Template(layout=dict(
    font=dict(family="Segoe UI, Arial", size=13, color="#222"),
    colorway=[AZUL, ROJO, VERDE, "#E0A030", "#7B5EA7", "#3BA3A3"],
    title=dict(x=0.01, font=dict(size=17)),
    margin=dict(l=60, r=30, t=80, b=50),
    xaxis=dict(gridcolor="#EEEEEE", zeroline=False),
    yaxis=dict(gridcolor="#EEEEEE", zeroline=False),
    hoverlabel=dict(font_family="Segoe UI, Arial"),
))
pio.templates.default = "plotly_white+eda"

def cop(x):
    """Plata en formato legible."""
    if pd.isna(x):
        return "-"
    if abs(x) >= 1e9:
        return f"${x/1e9:,.2f} mil M"
    if abs(x) >= 1e6:
        return f"${x/1e6:,.1f} M"
    if abs(x) >= 1e3:
        return f"${x/1e3:,.0f} mil"
    return f"${x:,.0f}"

def mostrar(fig, titulo, alto=450):
    fig.update_layout(title=titulo, height=alto)
    fig.show()

# Herramientas para las pruebas estadísticas. Cada prueba que hacemos queda
# guardada en PRUEBAS y al final se muestran todas juntas (sección 8).
PRUEBAS = []

def p_texto(p):
    return "< 0,001" if p < 0.001 else f"{p:.3f}".replace(".", ",")

def anotar(pregunta, prueba, estadistico, p, efecto=""):
    PRUEBAS.append({"Pregunta": pregunta, "Prueba": prueba,
                    "Estadístico": round(float(estadistico), 3), "p-valor": p_texto(p),
                    "Tamaño del efecto": efecto})
    print(f"{prueba}: estadístico = {estadistico:,.3f}   p = {p_texto(p)}   {efecto}")

def holm(pvalores):
    """Corrección de Holm para comparaciones múltiples."""
    p = np.asarray(pvalores, dtype=float)
    orden = np.argsort(p)
    ajustado = np.empty_like(p)
    acumulado = 0
    for rango, i in enumerate(orden):
        acumulado = max(acumulado, (len(p) - rango) * p[i])
        ajustado[i] = min(acumulado, 1)
    return ajustado

def kruskal_por_grupo(datos, variable, grupo, grupos):
    """Kruskal-Wallis y su épsilon² (proporción de la variación en rangos que explica el grupo)."""
    muestras = [datos.loc[datos[grupo] == g, variable].dropna() for g in grupos]
    muestras = [m for m in muestras if len(m) > 0]
    H, p = stats.kruskal(*muestras)
    n = sum(len(m) for m in muestras)
    return H, p, H / (n - 1)

def v_de_cramer(tabla):
    chi2, p, gl, _ = stats.chi2_contingency(tabla)
    n = tabla.to_numpy().sum()
    return chi2, p, gl, np.sqrt(chi2 / (n * (min(tabla.shape) - 1)))

import contextlib as _contextlib
import io as _io

_mostrar = mostrar
mostrar = lambda *args, **kwargs: None      # no mostrar gráficos al preparar la base

with _contextlib.redirect_stdout(_io.StringIO()):
    df = pd.read_csv("datos/base_final_excel_es.csv", sep=";", decimal=",", low_memory=False)
    n_total = len(df)

    for col in ["manzana", "codigo_predial"]:
        df[col] = (df[col].astype("string").str.replace('="', "", regex=False)
                          .str.replace('"', "", regex=False).str.strip())
    # estas dos banderas traen vacíos y pandas las lee como texto
    for col in ["area_es_suma_pisos", "area_confiable"]:
        df[col] = df[col].map({True: True, False: False, "True": True, "False": False}).astype("boolean")
    for col in [c for c in df.columns if str(df[c].dtype) in ("object", "str", "string")]:
        df[col] = df[col].astype("string").str.strip().replace({"": pd.NA})

    cobertura = (df.assign(con_coordenadas=df.lat.notna(), con_area=df.area.notna(), con_estrato=df.estrato.notna())
                   .groupby("fuente")[["con_coordenadas", "con_area", "con_estrato"]].mean().mul(100).round(1))
    cobertura.insert(0, "registros", df.fuente.value_counts())
    cobertura

    df = df[df.apto_modelo].copy().reset_index(drop=True)

    # códigos del catastro que no son mediciones: se pasan a vacío sin borrar la fila
    df.loc[df.piso >= 90, "piso"] = np.nan                     # código de sótano
    df.loc[~df.anio_construccion.between(1900, 2025), "anio_construccion"] = np.nan
    df.loc[df.avaluo <= 0, "avaluo"] = np.nan                   # sin avalúo
    df.loc[df.habitaciones > 20, "habitaciones"] = np.nan       # totales de edificio
    df.loc[df.banios > 20, "banios"] = np.nan

    df["edad"] = df.anio - df.anio_construccion
    df.loc[df.edad < 0, "edad"] = np.nan
    df["razon_precio_avaluo"] = df.precio / df.avaluo
    df.loc[df.localidad == "SIN LOCALIDAD", "localidad"] = pd.NA
    df["estrato"] = pd.Categorical(df.estrato, categories=ORDEN_ESTRATO, ordered=True)

    print(f"Base completa: {n_total:,}   apto_modelo: {len(df):,} ({len(df)/n_total:.0%})")

    # Variación anual del IPC (diciembre a diciembre, %), DANE
    VARIACION_IPC = {2016: 5.75, 2017: 4.09, 2018: 3.18, 2019: 3.80, 2020: 1.61,
                     2021: 5.62, 2022: 13.12, 2023: 9.28, 2024: 5.20, 2025: 5.10}

    # índice de diciembre con base diciembre 2018 = 100
    ipc_dic = {2018: 100.0}
    for a in range(2019, 2026):
        ipc_dic[a] = ipc_dic[a - 1] * (1 + VARIACION_IPC[a] / 100)
    for a in range(2017, 2014, -1):
        ipc_dic[a] = ipc_dic[a + 1] / (1 + VARIACION_IPC[a + 1] / 100)

    # nivel medio de cada año: media geométrica entre el diciembre anterior y el del año
    ipc_anio = pd.Series({a: np.sqrt(ipc_dic[a - 1] * ipc_dic[a]) for a in range(2016, 2026)})
    factor = ipc_dic[2025] / ipc_anio

    df["precio_real"] = df.precio * df.anio.map(factor)
    df["precio_m2_real"] = df.precio_m2 * df.anio.map(factor)
    df["log_precio"] = np.log10(df.precio_real)

    pd.DataFrame({"inflación del año (%)": pd.Series(VARIACION_IPC),
                  "IPC medio (dic 2018 = 100)": ipc_anio.round(1),
                  "multiplicar por": factor.round(3)})

    viv0 = df[df.clase_unidad_principal == "vivienda"]
    fuera = viv0[~viv0.precio_m2_en_rango]
    bien = viv0[viv0.precio_m2_en_rango]

    # Rango que acepta la bandera de la base
    print(f"Rango aceptado: de {cop(bien.precio_m2.min())} a {cop(bien.precio_m2.max())} por m²")
    print(f"Viviendas fuera de rango: {len(fuera):,} de {len(viv0):,} ({len(fuera)/len(viv0):.1%})")

    baratas = fuera[fuera.precio_m2 < bien.precio_m2.min()]
    caras = fuera[fuera.precio_m2 > bien.precio_m2.max()]
    pd.DataFrame({
        "ventas": [len(baratas), len(caras)],
        "precio mediano": [cop(baratas.precio.median()), cop(caras.precio.median())],
        "área mediana (m²)": [baratas.area.median(), caras.area.median()],
        "área > 150 m²": [(baratas.area > 150).sum(), (caras.area > 150).sum()],
        "área = suma de pisos": [int(baratas.area_es_suma_pisos.sum()), int(caras.area_es_suma_pisos.sum())],
        "precio < 20 M": [(baratas.precio < 20e6).sum(), (caras.precio < 20e6).sum()],
    }, index=["muy baratas por m²", "muy caras por m²"])

    COLS = [c for c in df.columns if c != "id"]
    copias = bien.duplicated(subset=COLS)
    viv = bien[~copias].copy()

    alameda = bien.barrio == "SECTOR ALAMEDA DEL RIO"
    print(f"Copias quitadas: {copias.sum():,}  ({alameda[copias].mean():.0%} de Alameda del Río)")
    print(f"Peso de Alameda del Río: {alameda.mean():.1%} con copias, {alameda[~copias].mean():.1%} sin copias")

    # columnas de apoyo para los gráficos
    viv["estrato_txt"] = viv.estrato.astype(str).map(dict(zip(ESTRATOS, NOMBRES_ESTRATO))).fillna("Sin estrato")
    viv["barrio_txt"] = viv.barrio.fillna("sin barrio").str.title()
    viv["precio_txt"] = viv.precio_real.map(cop)
    viv["precio_M"] = viv.precio_real / 1e6
    viv["pm2_M"] = viv.precio_m2_real / 1e6

    pasos = pd.Series({"Base completa": n_total, "apto_modelo": len(df), "Viviendas": len(viv0),
                       "Precio por m² en rango": len(bien), "Sin copias": len(viv)})
    fig = go.Figure(go.Funnel(y=pasos.index, x=pasos.values, textinfo="value+percent initial",
                              marker_color=[GRIS, GRIS, AZUL, AZUL, ROJO]))
    mostrar(fig, "De la base completa a la base de análisis", alto=380)

mostrar = _mostrar
PRUEBAS = []
