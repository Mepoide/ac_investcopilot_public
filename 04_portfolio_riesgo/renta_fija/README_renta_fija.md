# Renta Fija - Datos sintéticos (prototipo)

Esta carpeta contiene un dataset **sintético** de renta fija, construido para
validar la arquitectura de la tool de duración/curva antes de tener el
extracto real de Bloomberg.

## Por qué sintético y por qué este enfoque

A diferencia del módulo de riesgo de equity (que reconstruye una serie
histórica de retornos diarios y calcula VaR/volatilidad/drawdown), aquí se
usa el enfoque estándar de la industria para renta fija: **duración
modificada + DV01 por posición**, aplicando shocks paramétricos de tipos o
de spread de crédito directamente sobre esas sensibilidades, en vez de
reconstruir un motor de pricing de bonos desde cero.

Esto significa que, a diferencia de equity, **no se necesita una serie
histórica de precios por bono** para el cálculo básico de impacto de un
shock de tipos o de spread — solo la sensibilidad ya calculada (duración,
DV01, OAS), que normalmente se obtiene directamente de Bloomberg (pantalla
YAS o PORT), no se recalcula desde cero.

## Archivos

- `cartera_bonos_sintetica.csv` — cartera de renta fija de ejemplo (8
  posiciones, distintos ratings/sectores/vencimientos).
- `benchmark_renta_fija_sintetico.csv` — benchmark de ejemplo (proxy de un
  agregado de grado de inversión).

## Campos

| Campo | Descripción |
|---|---|
| `isin` | Identificador del bono |
| `nombre_activo` | Nombre del emisor/emisión |
| `sector` | Sector GICS o sectorial simplificado |
| `rating` | Rating crediticio (S&P/Moody's simplificado) |
| `divisa` | Divisa de denominación |
| `vencimiento` | Fecha de vencimiento |
| `peso_pct` | Peso en la cartera (%) |
| `duracion_modificada` | Sensibilidad a tipos (años) |
| `dv01_pct` | Variación de precio (%) por 1 punto básico de tipos |
| `ytm_pct` | Yield to maturity (%) |
| `oas_bps` | Spread de crédito (Option-Adjusted Spread, en pb) |

## Qué falta para pasar a datos reales

Ver `TOOLS_ROADMAP.md` (raíz del repo) — sustituir estos CSV por un extracto
real de Bloomberg con los mismos campos (ISIN, peso, duración modificada,
DV01, OAS, rating, divisa, vencimiento) por posición real de la cartera de
renta fija, más el benchmark de renta fija oficial del fondo correspondiente.
