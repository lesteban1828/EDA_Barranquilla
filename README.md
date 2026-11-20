# Determinantes del precio de la vivienda en Barranquilla

Análisis exploratorio de compraventas, ubicación y valor catastral (2016-2025).

Luis Esteban Mariño Bornacelli · Juan Esteban García · Camilo González
Universidad del Norte, Seminario de investigación

> **Versión 2: georreferenciación por matrícula (noviembre 2026).** Es una copia de
> `eda-vivienda-barranquilla` con una base nueva. Las ventas del IGAC se cruzan con la
> capa de predios del LADM por la matrícula inmobiliaria de la unidad, y el IGAC pasa de
> 13 % a 97,6 % de ventas con coordenada. Ver `00_base_enriquecida.ipynb`.
>
> Cambios frente a la versión 1:
> - `datos/base_final_excel_es.csv`: base regenerada con `enriquecer_a.py` y
>   `base_final.py` del proyecto `fr`. Incluye la marca VIS corregida (tolerancia de $1.000)
>   y la columna nueva `origen_barrio`: el barrio y la localidad de las ventas que no los
>   traían salen del predio catastral más cercano con barrio (≤ 150 m; acierto de 98,9 % en
>   barrio y 100 % en localidad, medido sobre las ventas que sí lo traían). En la base
>   original y en la capa de predios, muchos barrios vienen como un espacio en blanco; se
>   tratan como vacíos. El script es `rellenar_barrio.py`.
> - `datos/enriquecida/`: los parquet de la tabla A antes y después del cruce, la base final
>   y las coordenadas de los terrenos LADM.
> - `eda_utils.py` y `01_datos.ipynb`: el ajuste por IPC incluye 2015 (6,77 %, DANE).
> - `corregir_coordenadas.py`: una venta del IGAC traía la longitud igual a la latitud
>   (error heredado de `tabla_consolidada.parquet`); se reemplaza por la coordenada del
>   edificio en el LADM. Esa sola fila hacía que la regresión lineal diera R² = −1,9.
> - **Características de las unidades al día.** El área, las habitaciones, los baños y el año
>   se consultan al servicio del Distrito por `objectid`, y el Distrito renumeró la capa de
>   unidades de construcción (305) entre agosto y noviembre de 2026: el 90% de los
>   `objectid` de la copia de agosto apuntaban a otra unidad. Se volvió a bajar la capa, se
>   consultaron otra vez las características y `tabla_ladm.py` (en `Downloads/fr`; los
>   archivos anteriores están en `fr/respaldo_2026-11-16/`) ahora verifica una muestra
>   de `objectid` contra el servicio antes de consultar. Con esto, el
>   área coincide con el polígono de su unidad en el 76% de las ventas, frente al 55%
>   anterior. En la versión 1, las características del IGAC y de las georreferenciadas
>   estaban afectadas; las del observatorio no.
> - **Solo matrículas del círculo 040.** El catastro guarda la matrícula sin el círculo
>   registral y solo tiene folios de Barranquilla (040), así que una matrícula `041-…`
>   encontraba un predio equivocado. `enriquecer_a.py` ya no cruza las de otros círculos
>   (35 ventas; 13 se habían cruzado mal y 9 entraban al modelo).
> - **Avalúo por número predial.** La capa de 2022 (la única con avalúo) usa los números
>   prediales de ese año, y el catastro renumeró muchos predios desde entonces.
>   `enriquecer_a.py::avaluo_por_codigo` (en `Downloads/fr`; respaldo de lo anterior en
>   `fr/respaldo_2026-11-17/`) busca el avalúo por el número predial vigente y, si no está, por su
>   número de origen en el historial (capa 540). El avalúo de las viviendas pasa de 41% a
>   68%; el área de 2022 coincide con la nuestra en el 92% de los recuperados. Columna
>   `origen_avaluo`. Con esto se vio que el 30% de los apartamentos del IGAC con avalúo
>   también declara el avalúo en la escritura; el capítulo 8 compara el modelo con y sin
>   el IGAC.
> - **Piso de las ventas sin unidad propia.** Cuando el catastro no tiene la unidad vendida,
>   las características salen de la mediana del edificio, pero el piso ya no: la mediana de
>   los vecinos acertaba el piso real en menos del 5%. Queda vacío, salvo cuando la dirección
>   trae el número de apartamento («AP 413» → piso 4; validado: 97,5% de acierto). Columna
>   `origen_piso`. Random Forest (cap. 7) ya no rellena los vacíos con la mediana.
> - **Zona de Expansión Riomar.** El catastro de 2022 llama «ZONA NO DESARROLLADA» a la manzana
>   716 de Riomar (calles 96 a 99C, carreras 64 a 72), hoy llena de torres de obra nueva.
>   `eda_utils.py` la renombra y ya no la excluye de los análisis por barrio.
> - **La fuente solo para entrenar.** El modelo de los caps. 7 y 8 usa la fuente del dato para
>   corregir el nivel de precio de cada fuente, pero al valorar una vivienda nueva la fija en
>   el observatorio (`REFERENCIA`), así que nadie tiene que darla. Ver «Cómo se valora una
>   vivienda nueva» en el cap. 7.
> - `verificar_matriculas.py`: fichas para verificar a mano el cruce matrícula → número
>   predial → terreno → coordenada contra el servicio del catastro.
> - `08_evaluacion.ipynb` usa los hiperparámetros que elige el capítulo 7 con esta base
>   (en la versión 1 estaban escritos a mano con los de la base anterior).
> - Los notebooks se volvieron a ejecutar y los textos, la introducción y las conclusiones
>   citan las cifras nuevas.
>
> Para regenerar la base desde la de `fr`: copiar `base_final_excel_es.csv` y
> `base_final.parquet` a `datos/` y `datos/enriquecida/`, y correr
> `python corregir_coordenadas.py .` y después `python rellenar_barrio.py .`.

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
├── 06_conclusiones.md       Hallazgos y limitaciones
├── eda_utils.py             Preparación de la base que comparten los capítulos
├── datos/
│   ├── base_final_excel_es.csv       Base de compraventas
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
- Mapa de fondo: © colaboradores de OpenStreetMap.
