"""Pruebas de optimización del capítulo 8 sobre XGBoost con pérdida MAE y área del lote.

Compara variantes en las mismas 20 divisiones por zonas del entrenamiento que usa 08_evaluacion.ipynb.
El ajuste de hiperparámetros usa otras 10 divisiones (semillas 100 a 109), para no elegir y evaluar
con las mismas. Tarda cerca de una hora. LightGBM es opcional: si no está instalado, se omite.

Uso, desde la carpeta del libro:  python optimizar_modelo.py [resultados.csv]
"""
import json
import sys
import matplotlib
matplotlib.use("Agg")
nb = json.load(open("07_modelos.ipynb", encoding="utf-8"))
code = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
g = {}
for i in [0, 1, 2, 3]:
    exec(code[i], g)
globals().update(g)
try:
    from lightgbm import LGBMRegressor
except ImportError:
    LGBMRegressor = None

SALIDA = sys.argv[1] if len(sys.argv) > 1 else "optimizacion_resultados.csv"
TERRENO = "datos/terreno_casas.csv"
MEJORES = dict(n_estimators=600, learning_rate=0.05, max_depth=6, subsample=0.6,
               colsample_bytree=0.8, min_child_weight=30, reg_lambda=10.0)
MAE = dict(objective="reg:absoluteerror")

# área del lote (solo casas) y coordenadas rotadas
t = pd.read_csv(TERRENO, dtype={"name": str}).set_index("name").Shape__Area
lat0, lon0 = d.lat.mean(), d.lon.mean()
ANGULOS = [15, 30, 45, 60, 75, 105, 120, 135, 150, 165]
for x in (ent, prueba):
    casa = (x.tipo_NPH == 1).to_numpy()
    x["log_terreno"] = np.log10(x.codigo_predial.astype(str).map(t).astype(float).where(casa))
    yy, xx = x.lat - lat0, (x.lon - lon0) * np.cos(np.radians(lat0))
    for a in ANGULOS:
        x[f"rot_{a}"] = xx * np.cos(np.radians(a)) + yy * np.sin(np.radians(a))
LOTE = BASE + ["log_terreno"]
ROT = LOTE + [f"rot_{a}" for a in ANGULOS]


def metricas(y, p):
    real, pred = 10.0 ** y, 10.0 ** p
    err = pred / real - 1
    ae = np.abs(err)
    r = pred / real
    med = np.median(r)
    return {"R2_log": 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum(),
            "R2_pesos": 1 - ((real - pred) ** 2).sum() / ((real - real.mean()) ** 2).sum(),
            "MdAPE": np.median(ae) * 100, "MAPE": ae.mean() * 100,
            "PPE10": (ae <= 0.1).mean() * 100, "PPE20": (ae <= 0.2).mean() * 100,
            "sesgo": np.median(err) * 100,
            "COD": 100 * np.mean(np.abs(r - med)) / med, "PRD": r.mean() / (pred.sum() / real.sum())}


def divisiones(datos, semillas, frac=0.2):
    bl = datos.groupby("bloque").agg(ventas=("bloque", "size"),
                                     alameda=("barrio", lambda s: (s == "SECTOR ALAMEDA DEL RIO").mean()))
    cand = bl[bl.alameda < 0.5]
    for s in semillas:
        c = cand.sample(frac=1, random_state=s)
        yield s, datos.bloque.isin(c.index[c.ventas.cumsum() <= frac * len(datos)]).to_numpy()


def xgb_(tr, te, cols, params=MEJORES, peso=None, semilla=42):
    m = XGBRegressor(n_jobs=4, random_state=semilla, **{**params, **MAE})
    return m.fit(tr[cols], tr.log_precio, sample_weight=peso).predict(te[cols]).astype(float)


def pesos_bloque(tr, tope):
    """Cada bloque aporta como máximo `tope` ventas efectivas."""
    n = tr.bloque.map(tr.bloque.value_counts())
    return np.minimum(1.0, tope / n).to_numpy()


def lgbm(tr, te, cols):
    m = LGBMRegressor(objective="l1", n_estimators=600, learning_rate=0.05, num_leaves=31, min_child_samples=30,
                      subsample=0.6, subsample_freq=1, colsample_bytree=0.8, reg_lambda=10.0,
                      n_jobs=4, random_state=42, verbose=-1)
    return m.fit(tr[cols], tr.log_precio).predict(te[cols])


def evaluar(variantes, semillas, etiqueta):
    filas = []
    for s, es_val in divisiones(ent, semillas):
        tr, te = ent[~es_val].reset_index(drop=True), ent[es_val].reset_index(drop=True)
        y = te.log_precio.to_numpy()
        casa = (te.tipo_NPH == 1).to_numpy()
        for nombre, f in variantes.items():
            p = f(tr, te)
            assert 5 < p.min() and p.max() < 12, (nombre, p.min(), p.max())
            for gr, m in [("todas", np.ones(len(y), bool)), ("casas", casa), ("aptos", ~casa)]:
                filas.append({"etapa": etiqueta, "division": s, "modelo": nombre, "grupo": gr, **metricas(y[m], p[m])})
        print(etiqueta, s, flush=True)
    return pd.DataFrame(filas)


# 1) ajuste de hiperparámetros para MAE + lote, en divisiones aparte
espacio = {"learning_rate": [0.02, 0.03, 0.05, 0.08], "max_depth": [4, 6, 8, 10],
           "min_child_weight": [3, 10, 30, 60], "subsample": [0.5, 0.6, 0.8],
           "colsample_bytree": [0.5, 0.7, 0.8, 1.0], "reg_lambda": [1.0, 10.0, 30.0],
           "reg_alpha": [0.0, 1.0], "n_estimators": [400, 800, 1200]}
configs = [MEJORES] + list(ParameterSampler(espacio, n_iter=30, random_state=7))
aj = evaluar({f"cfg{i}": (lambda c: lambda a, b: xgb_(a, b, LOTE, c))(c) for i, c in enumerate(configs)},
             range(100, 110), "ajuste")
r = aj[aj.grupo == "todas"].groupby("modelo")[["MdAPE", "R2_log"]].mean().sort_values("MdAPE")
print(r.head(8).round(3))
mejor = configs[int(r.index[0][3:])]
mejor = {k: (int(v) if k in ("n_estimators", "max_depth", "min_child_weight") else float(v)) for k, v in mejor.items()}
print("configuracion elegida:", mejor, flush=True)
json.dump(mejor, open(SALIDA.replace(".csv", "_mejor.json"), "w"))

# 2) comparación en las 20 divisiones de evaluación
variantes = {
    "base: MAE + lote": lambda a, b: xgb_(a, b, LOTE),
    "hiperparametros reajustados": lambda a, b: xgb_(a, b, LOTE, mejor),
    "coordenadas rotadas": lambda a, b: xgb_(a, b, ROT),
    "peso por bloque (tope 300)": lambda a, b: xgb_(a, b, LOTE, peso=pesos_bloque(a, 300)),
    "peso por bloque (tope 600)": lambda a, b: xgb_(a, b, LOTE, peso=pesos_bloque(a, 600)),
    "promedio 5 semillas": lambda a, b: np.mean([xgb_(a, b, LOTE, semilla=s) for s in range(5)], axis=0),
    "LightGBM (L1)": lambda a, b: lgbm(a, b, LOTE),
    "promedio XGB + LightGBM": lambda a, b: 0.5 * (xgb_(a, b, LOTE) + lgbm(a, b, LOTE)),
    "reajustado + rotadas": lambda a, b: xgb_(a, b, ROT, mejor),
    "peso por bloque (tope 150)": lambda a, b: xgb_(a, b, LOTE, peso=pesos_bloque(a, 150)),
    "peso 300 + 5 semillas": lambda a, b: np.mean([xgb_(a, b, LOTE, peso=pesos_bloque(a, 300), semilla=s)
                                                   for s in range(5)], axis=0),
}
if LGBMRegressor is None:
    variantes = {k: v for k, v in variantes.items() if "LightGBM" not in k}
ev = evaluar(variantes, range(20), "evaluacion")
pd.concat([aj, ev]).to_csv(SALIDA, index=False)

pd.set_option("display.width", 220); pd.set_option("display.max_columns", 30)
todas = ev[ev.grupo == "todas"]
print(todas.groupby("modelo")[["MdAPE", "R2_log", "R2_pesos", "MAPE", "PPE10", "PPE20", "sesgo", "COD", "PRD"]].mean()
      .sort_values("MdAPE").round(3))
print(ev[ev.grupo != "todas"].pivot_table(index="modelo", columns="grupo", values=["MdAPE", "R2_log"]).round(2))
for met in ["MdAPE", "R2_log"]:
    a = todas.pivot(index="division", columns="modelo", values=met)
    dif = a.sub(a["base: MAE + lote"], axis=0).drop(columns="base: MAE + lote")
    e = 2.093 * dif.std() / np.sqrt(len(dif))
    print(f"\n{met}: diferencia frente a la base")
    print(pd.DataFrame({"media": dif.mean(), "IC_inf": dif.mean() - e, "IC_sup": dif.mean() + e,
                        "mejora_en": (dif < 0).sum() if met == "MdAPE" else (dif > 0).sum()}).sort_values("media").round(3))
print("listo")
