# Validación mapping ISIN / ticker / GICS

Archivo principal generado: `mapping_isin_ticker_gics.csv`.

## Resumen

- Filas totales: 78
- Equities: 54
- Índices: 24
- ISINs de las carteras BAM/modelo cubiertos: 54 de 54

## ISINs de cartera no cubiertos

Todos los ISINs de cartera están cubiertos.

## Nota

El ISIN `US3143521058` aparece en la cartera como `FEDEX FREIGHT HOLDING COMPANY INC`, pero en la tabla enviada no aparece un ticker Bloomberg claro. Lo he preservado usando el propio ISIN como identificador temporal y marcando la fuente como `inferido_desde_cartera_usuario_sin_ticker_en_mapping`.

## Uso recomendado

Guarda estos archivos en:

`<ruta_repo>\04_portfolio_riesgo\series_historicas`
