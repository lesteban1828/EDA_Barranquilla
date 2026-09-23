# Conclusiones

## Resumen de pruebas

Con más de 15 mil datos casi todo resulta significativo, así que la columna que importa
es el tamaño del efecto.

| Pregunta | Prueba | p-valor | Tamaño del efecto |
|---|---|---|---|
| ¿El precio cambia cuando falta el avalúo? | Mann-Whitney | < 0,001 | P(sin dato > con dato) = 0,58 |
| ¿El precio cambia cuando falta el año de construcción? | Mann-Whitney | < 0,001 | P(sin dato > con dato) = 0,59 |
| ¿El precio sube con el área? | Correlación de Spearman | < 0,001 | rho = 0,48 (IC 95%: 0,47 a 0,49) |
| ¿El precio por m² difiere entre estratos? | Kruskal-Wallis | < 0,001 | épsilon² = 0,36 |
| ¿El estrato 5 es más caro por m² que el 4? | Mann-Whitney | 0,094 | medianas de 4,6 M y 4,3 M |
| ¿El precio por m² difiere entre barrios? | Kruskal-Wallis | < 0,001 | épsilon² = 0,58 |
| ¿El precio por m² difiere entre localidades? | Kruskal-Wallis | < 0,001 | épsilon² = 0,46 |
| ¿El m² real cambia entre 2019 y 2025? | Kruskal-Wallis | < 0,001 | épsilon² = 0,05 |
| ¿Se paga por encima del avalúo? | Wilcoxon de rangos con signo | < 0,001 | mediana = 1,54 |
| ¿La razón precio/avalúo cambia con el estrato? | Kruskal-Wallis | < 0,001 | épsilon² = 0,01 |
| ¿A mayor estrato, mayor subvaloración? | Correlación de Spearman | < 0,001 | rho = 0,08 |
| ¿El estrato depende de la localidad? | Chi-cuadrado de independencia | < 0,001 | V de Cramér = 0,53 |
| ¿El precio por m² depende del de las vecinas? | I de Moran (999 permutaciones) | 0,001 | I = 0,59 |

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
