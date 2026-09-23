# Determinantes del precio de la vivienda en Barranquilla

Seminario de investigación, Universidad del Norte · Septiembre de 2026

Este libro es la fase de análisis exploratorio del proyecto *Predicción del precio de
vivienda en Barranquilla mediante Machine Learning*. Antes de entrenar los modelos
necesitamos saber qué parte de la base se puede usar, qué variables se relacionan con el
precio y cómo hay que validar los resultados.

La base reúne compraventas de cuatro fuentes (observatorio inmobiliario, registros
georreferenciados, IGAC y avisos de registro) cruzadas con el catastro. Tiene 68.709
registros, de los que quedan 15.459 viviendas después de la limpieza.

## Capítulos

1. **Los datos.** Diccionario de variables, limpieza, datos faltantes, ajuste por
   inflación, precios por m² fuera de rango y registros duplicados.
2. **Análisis univariado.** Distribución del precio, del área y de las características
   de las viviendas.
3. **Análisis bivariado.** Precio frente a área, estrato, barrio, año y características,
   y comparación con el índice de precios del Banco de la República.
4. **Precio contra avalúo catastral.** Cuánto se paga por encima del avalúo y cómo
   cambia esa diferencia entre zonas y estratos.
5. **Análisis geoespacial.** Mapas de ventas, precios y estratos, y dependencia espacial
   del precio.
6. **Conclusiones.** Resumen de las pruebas estadísticas y hallazgos para el modelo.

## Cómo leerlo

Todos los precios están en pesos de diciembre de 2025. En el texto, M significa millones
de pesos. Los gráficos son interactivos: al pasar el cursor se ven los valores, y se
puede hacer zoom y ocultar series desde la leyenda.
