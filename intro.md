---
authors:
  - Luis Esteban Mariño Bornacelli
  - Juan Esteban García
  - Camilo González
---
# Determinantes del precio de la vivienda en Barranquilla

Seminario de investigación, Universidad del Norte · Noviembre de 2026 (versión 2)

Este libro es la fase de análisis exploratorio del proyecto *Predicción del precio de
vivienda en Barranquilla mediante Machine Learning*. Antes de entrenar los modelos
necesitamos saber qué parte de la base se puede usar, qué variables se relacionan con el
precio y cómo hay que validar los resultados.

La base reúne compraventas de cuatro fuentes (observatorio inmobiliario, registros
georreferenciados, IGAC y avisos de registro) cruzadas con el catastro. Tiene 68.709
registros, de los que quedan 34.606 viviendas después de la limpieza.

En esta versión, las ventas del IGAC se cruzan con el catastro por la matrícula
inmobiliaria de la unidad, y el 97,6% queda ubicado (antes, el 13%). Por eso la base de
análisis tiene el doble de viviendas que la versión anterior.

## Capítulos

0. **La base enriquecida.** Cómo se cruzó cada venta con el catastro y de dónde sale su
   coordenada, con la validación del cruce.
1. **Los datos.** Diccionario de variables, limpieza, datos faltantes, ajuste por
   inflación, precios por m² fuera de rango y registros duplicados.
2. **Análisis univariado.** Distribución del precio, del área y de las características
   de las viviendas.
3. **Análisis bivariado.** Precio frente a área, estrato, barrio, año y características.
4. **Precio contra avalúo catastral.** Cuánto se paga por encima del avalúo y cómo
   cambia esa diferencia entre zonas y estratos.
5. **Análisis geoespacial.** Mapas de ventas, precios y estratos, y dependencia espacial
   del precio.
6. **Conclusiones.** Hallazgos para el modelo y limitaciones de la base.
7. **Modelos de predicción.** Comparación de modelos con validación por zonas, ajuste de
   hiperparámetros y prueba final.
8. **Evaluación del modelo y variantes.** Métricas completas, sensibilidad al azar y
   variantes del modelo.

## Cómo leerlo

Todos los precios están en pesos de diciembre de 2025. En el texto, M significa millones
de pesos. Los gráficos son interactivos: al pasar el cursor se ven los valores, y se
puede hacer zoom y ocultar series desde la leyenda.
