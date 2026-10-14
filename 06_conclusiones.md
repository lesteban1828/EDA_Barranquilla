# Conclusiones

## Hallazgos

1. De 68.709 compraventas quedan 15.459 viviendas útiles, después de filtrar
   `apto_modelo`, quitar 810 ventas con precio por m² fuera de rango y 3.412 registros
   duplicados.
2. Descontando la inflación no hubo valorización: ajustando por composición, el m² real
   de 2025 está 2% por debajo de 2019, igual que el IPVU real del Banco de la República
   (1% por debajo).
3. La ubicación es lo que más explica el precio. El barrio pesa más que la localidad y
   que el estrato, y el norte cuesta casi el doble que el sur.
4. El precio tiene dependencia espacial (I de Moran = 0,59), así que el modelo debe
   validarse también por zonas.
5. Conviene modelar log(precio). Además de la ubicación, las variables más útiles son el
   área y los baños.
6. El catastro está por debajo del mercado (1,54 veces en la mediana) y la distancia
   depende más del barrio que del estrato.

## Limitaciones

- La vivienda de interés social (VIS) no está incluida: el filtro `apto_modelo` la deja
  por fuera.
- Sector Alameda del Río pesa 16% de la base.
- 2024 tiene pocas ventas y antes de 2019 casi no hay registros.
- El avalúo es de un solo año, así que no se puede estudiar cómo cambia la brecha en el
  tiempo.
- El índice del Banco de la República es nacional; no hay uno publicado solo para
  Barranquilla.
