# Determinantes del precio de la vivienda en Barranquilla

Análisis exploratorio de compraventas, ubicación y valor catastral (2016-2025).

Luis Esteban Mariño Bornacelli · Juan Esteban García · Camilo González
Universidad del Norte, Seminario de investigación

Este repositorio contiene el análisis exploratorio del proyecto *Predicción del precio
de vivienda en Barranquilla mediante Machine Learning*, organizado como un Jupyter Book.

## Contenido

```
├── intro.md                 Presentación del libro
├── 01_datos.ipynb           Diccionario, limpieza, faltantes, inflación y duplicados
├── 02_univariado.ipynb      Distribución del precio y de las características
├── 03_bivariado.ipynb       Precio frente a área, estrato, barrio, año y características
├── 04_avaluo.ipynb          Precio contra avalúo catastral
├── 05_geoespacial.ipynb     Mapas y dependencia espacial
├── 06_conclusiones.md       Resumen de pruebas, hallazgos y limitaciones
├── eda_utils.py             Preparación de la base que comparten los capítulos
├── datos/
│   ├── base_final_excel_es.csv       Base de compraventas
│   ├── ipvu_nacional_banrep.csv      Índice de precios de vivienda usada (Banco de la República)
│   └── mapa_base_barranquilla.png    Mapa de fondo (© colaboradores de OpenStreetMap)
├── myst.yml                 Configuración del libro
├── requirements.txt
└── .github/workflows/deploy.yml   Publicación automática en GitHub Pages
```

Los notebooks están ejecutados, así que se pueden leer en GitHub o en el libro sin correr
nada.

## Ver el libro

Cada vez que se sube un cambio a la rama `main`, GitHub Actions construye el libro y lo
publica en GitHub Pages. Para activarlo la primera vez: en el repositorio, ir a
**Settings → Pages** y en **Source** elegir **GitHub Actions**.

## Ejecutar los notebooks

```bash
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace 0*.ipynb
```

El capítulo 1 muestra paso a paso la preparación de la base. Los demás capítulos empiezan
con `from eda_utils import *`, que repite esa preparación sin mostrar nada.

## Construir el libro en el computador

Se necesita Node.js instalado.

```bash
jupyter book build --html
```

El sitio queda en `_build/html`. Para verlo mientras se edita: `jupyter book start`.

## Fuentes

- Compraventas: observatorio inmobiliario, registros georreferenciados, IGAC y avisos de
  registro, cruzados con el catastro de Barranquilla.
- Inflación: variación anual del IPC, DANE.
- Índice de precios de la vivienda usada (IPVU): Banco de la República.
- Mapa de fondo: © colaboradores de OpenStreetMap.
