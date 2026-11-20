# Conclusiones

## Hallazgos

1. De 68.709 compraventas quedan 34.606 viviendas útiles, después de filtrar
   `apto_modelo`, quitar 814 ventas con precio por m² fuera de rango y 858 registros
   duplicados. Son más del doble que en la versión anterior (15.459), porque el cruce por
   matrícula ubicó el 97,6% de las ventas del IGAC. El IGAC es ahora la fuente principal
   (62% de la base) y casi todas sus ventas nuevas son apartamentos.
2. Descontando la inflación, el m² casi no se valorizó: la mediana pasó de 3,2 M en 2019 a
   3,3 M en 2025 (pesos de 2025), con una caída hasta 2,8 M en 2022. En pesos corrientes
   parecía subir 48% entre 2022 y 2025. Parte de esos movimientos no es cambio de precio
   sino de qué se vendió cada año.
3. La ubicación es lo que más explica el precio. El barrio pesa más que la localidad y
   que el estrato, y el norte cuesta 1,7 veces el m² del sur.
4. El precio tiene dependencia espacial (I de Moran = 0,58), así que el modelo debe
   validarse también por zonas.
5. Conviene modelar log(precio). Además de la ubicación, las variables más útiles son el
   área y los baños. La fuente del dato solo se usa para entrenar; al valorar una
   vivienda nueva se fija en el observatorio.
6. El catastro está por debajo del mercado: la vivienda típica se vende a 1,44 veces su
   avalúo. La distancia depende más del barrio y de la fuente que del estrato.
7. El precio de la escritura no siempre es lo que se pagó: en el IGAC, el 57% de las casas y el
   30% de los apartamentos con avalúo declaran un precio a menos de 10% del avalúo catastral.
   Esas ventas se quitan del modelo. Como la fuente entra al entrenamiento, el modelo corrige el
   nivel de precio más bajo del IGAC: al valorar una vivienda nueva, con la fuente fijada en el
   observatorio, la predicción de las ventas del IGAC sube un 10,5%.

## Limitaciones

- La vivienda de interés social (VIS) no está incluida: el filtro `apto_modelo` la deja
  por fuera.
- Sector Alameda del Río pesa 13% de la base.
- Antes de 2019 casi no hay registros, y 2024 y 2025 solo tienen datos del observatorio.
- El avalúo es de un solo año, así que no se puede estudiar cómo cambia la brecha en el
  tiempo. Lo tiene el 68% de las viviendas; en el IGAC se recuperó buscando el número
  predial vigente o su número de origen en el historial del catastro (columna
  `origen_avaluo`), pero el 39% de sus ventas sigue sin avalúo y no se puede revisar si
  declaran el avalúo en lugar del precio.
- La coordenada de las ventas del IGAC es la del edificio, no la del apartamento.
- En el 13% de las viviendas el catastro no tiene la unidad vendida: el área, las habitaciones,
  los baños y el año son la mediana del edificio (`origen_caract = edificio`) y el piso queda
  vacío, salvo cuando la dirección dice el número de apartamento (`origen_piso`). En total,
  el 12% de las viviendas no tiene piso.
- El barrio del 59% de las viviendas se asignó desde el predio catastral más cercano
  (acierto de 98,9% donde se pudo comparar). Está marcado en `origen_barrio`.
- Las características de las unidades (área, habitaciones, baños, año) se consultan al
  servicio del Distrito por `objectid`, y el Distrito renumeró la capa entre agosto y
  noviembre de 2026. En esta versión se consultaron con la capa al día; en la versión
  anterior, las del IGAC y las georreferenciadas estaban desalineadas.
