import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

CARTERAS_DIR = BASE_DIR / "carteras"
METRICAS_DIR = BASE_DIR / "metricas"
SERIES_DIR = BASE_DIR / "series_historicas"

RETS_PATH = SERIES_DIR / "rentabilidades_bam_componentes_enriquecido.csv"

CARTERA_ACTUAL_PATH = CARTERAS_DIR / "cartera_real_fondmapfre_bolsa_america.csv"
ESCENARIO_PATH = METRICAS_DIR / "escenario_bam_tecnologia_plus3_posiciones.csv"

OUTPUT_METRICAS_PATH = METRICAS_DIR / "metricas_riesgo_bam_vs_escenario.csv"
OUTPUT_SERIES_CARTERAS_PATH = METRICAS_DIR / "series_rentabilidad_bam_vs_escenario.csv"
OUTPUT_DRAWDOWN_PATH = METRICAS_DIR / "drawdown_bam_vs_escenario.csv"
OUTPUT_CORRELACIONES_PATH = METRICAS_DIR / "matriz_correlaciones_componentes.csv"
OUTPUT_RESUMEN_MD_PATH = METRICAS_DIR / "resumen_metricas_riesgo_bam_vs_escenario.md"

BENCHMARK_TICKER = "SPX INDEX"
DIAS_ANUALES = 252
NIVEL_VAR = 0.95


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def normalizar_ticker(x):
    return (
        str(x)
        .replace("\u200c", "")
        .strip()
        .upper()
        .replace("  ", " ")
    )


def max_drawdown(returns):
    indice = (1 + returns).cumprod()
    max_acum = indice.cummax()
    drawdown = indice / max_acum - 1
    return drawdown.min(), drawdown


def calcular_metricas(nombre, serie_ret, benchmark=None):
    serie_ret = serie_ret.dropna()

    vol_diaria = serie_ret.std()
    vol_anual = vol_diaria * np.sqrt(DIAS_ANUALES)

    var_diario = -np.percentile(serie_ret, (1 - NIVEL_VAR) * 100)
    var_anual = var_diario * np.sqrt(DIAS_ANUALES)

    mdd, dd_series = max_drawdown(serie_ret)

    rent_acum = (1 + serie_ret).prod() - 1
    rent_anualizada = (1 + rent_acum) ** (DIAS_ANUALES / len(serie_ret)) - 1 if len(serie_ret) > 0 else np.nan

    metricas = {
        "cartera": nombre,
        "num_observaciones": len(serie_ret),
        "rentabilidad_acumulada": rent_acum,
        "rentabilidad_anualizada": rent_anualizada,
        "volatilidad_diaria": vol_diaria,
        "volatilidad_anualizada": vol_anual,
        "var_historico_diario_95": var_diario,
        "var_historico_anualizado_95": var_anual,
        "max_drawdown": mdd
    }

    if benchmark is not None:
        df_tmp = pd.concat([serie_ret, benchmark], axis=1).dropna()
        df_tmp.columns = ["cartera", "benchmark"]

        exceso = df_tmp["cartera"] - df_tmp["benchmark"]

        tracking_error_diario = exceso.std()
        tracking_error_anual = tracking_error_diario * np.sqrt(DIAS_ANUALES)

        beta = (
            np.cov(df_tmp["cartera"], df_tmp["benchmark"])[0, 1]
            / np.var(df_tmp["benchmark"])
            if np.var(df_tmp["benchmark"]) != 0
            else np.nan
        )

        metricas.update({
            "tracking_error_diario": tracking_error_diario,
            "tracking_error_anualizado": tracking_error_anual,
            "beta_vs_benchmark": beta
        })
    else:
        metricas.update({
            "tracking_error_diario": np.nan,
            "tracking_error_anualizado": np.nan,
            "beta_vs_benchmark": np.nan
        })

    return metricas, dd_series


def construir_serie_cartera(retornos_ancho, pesos, nombre_peso):
    cols_disponibles = [c for c in pesos.index if c in retornos_ancho.columns]

    pesos_ok = pesos.loc[cols_disponibles].copy()
    pesos_ok = pesos_ok / pesos_ok.sum()

    retornos_ok = retornos_ancho[cols_disponibles].copy()

    serie = retornos_ok.mul(pesos_ok, axis=1).sum(axis=1)
    serie.name = nombre_peso

    tickers_faltantes = sorted(set(pesos.index) - set(cols_disponibles))

    return serie, tickers_faltantes


# ============================================================
# 1. CARGAR RENTABILIDADES
# ============================================================

rets = pd.read_csv(RETS_PATH)
rets["fecha"] = pd.to_datetime(rets["fecha"])

rets["ticker_normalizado"] = rets["ticker_normalizado"].apply(normalizar_ticker)

rets_ancho = rets.pivot_table(
    index="fecha",
    columns="ticker_normalizado",
    values="retorno_diario",
    aggfunc="first"
).sort_index()

print("Rentabilidades cargadas:")
print(rets_ancho.shape)


# ============================================================
# 2. CARGAR CARTERA ACTUAL BAM
# ============================================================

cartera = pd.read_csv(CARTERA_ACTUAL_PATH)

cartera.columns = [c.strip().lower() for c in cartera.columns]

# Esperado: sector,nombre_activo,isin,peso_bam
if "peso_bam" not in cartera.columns:
    raise ValueError("No encuentro la columna 'peso_bam' en cartera_real_fondmapfre_bolsa_america.csv")

mapping = pd.read_csv(SERIES_DIR / "mapping_isin_ticker_gics.csv")
mapping["ticker_normalizado"] = mapping["ticker_normalizado"].apply(normalizar_ticker)
mapping["isin"] = mapping["isin"].astype(str).str.strip()

cartera["isin"] = cartera["isin"].astype(str).str.strip()

cartera = cartera.merge(
    mapping[["isin", "ticker_normalizado"]],
    on="isin",
    how="left"
)

cartera["peso_bam"] = cartera["peso_bam"] / 100

pesos_actual = cartera.set_index("ticker_normalizado")["peso_bam"].dropna()


# ============================================================
# 3. CARGAR ESCENARIO TECNOLOGÍA +3
# ============================================================

escenario = pd.read_csv(ESCENARIO_PATH)

escenario.columns = [c.strip().lower() for c in escenario.columns]

# Esperado: sector,nombre_activo,isin,peso_actual,peso_escenario_tecnologia_plus3,...
if "peso_escenario_tecnologia_plus3" not in escenario.columns:
    raise ValueError("No encuentro la columna 'peso_escenario_tecnologia_plus3' en escenario_bam_tecnologia_plus3_posiciones.csv")

escenario["isin"] = escenario["isin"].astype(str).str.strip()

escenario = escenario.merge(
    mapping[["isin", "ticker_normalizado"]],
    on="isin",
    how="left"
)

escenario["peso_escenario_tecnologia_plus3"] = escenario["peso_escenario_tecnologia_plus3"] / 100

pesos_escenario = escenario.set_index("ticker_normalizado")["peso_escenario_tecnologia_plus3"].dropna()


# ============================================================
# 4. CONSTRUIR SERIES DE CARTERA
# ============================================================

serie_bam, faltantes_bam = construir_serie_cartera(
    rets_ancho,
    pesos_actual,
    "BAM_actual"
)

serie_escenario, faltantes_escenario = construir_serie_cartera(
    rets_ancho,
    pesos_escenario,
    "BAM_tecnologia_plus3"
)

df_series = pd.concat([serie_bam, serie_escenario], axis=1).dropna(how="all")

benchmark = None

if BENCHMARK_TICKER in rets_ancho.columns:
    benchmark = rets_ancho[BENCHMARK_TICKER].rename(BENCHMARK_TICKER)
    df_series[BENCHMARK_TICKER] = benchmark
else:
    print(f"No se ha encontrado benchmark {BENCHMARK_TICKER} en las series.")

df_series.to_csv(
    OUTPUT_SERIES_CARTERAS_PATH,
    encoding="utf-8-sig"
)

print("Series de cartera guardadas en:")
print(OUTPUT_SERIES_CARTERAS_PATH)


# ============================================================
# 5. CALCULAR MÉTRICAS
# ============================================================

metricas_bam, dd_bam = calcular_metricas(
    "BAM_actual",
    df_series["BAM_actual"],
    benchmark=benchmark
)

metricas_escenario, dd_escenario = calcular_metricas(
    "BAM_tecnologia_plus3",
    df_series["BAM_tecnologia_plus3"],
    benchmark=benchmark
)

df_metricas = pd.DataFrame([metricas_bam, metricas_escenario])

# Diferenciales escenario - actual
diferencial = {
    "cartera": "diferencia_escenario_menos_actual"
}

for col in df_metricas.columns:
    if col != "cartera":
        try:
            diferencial[col] = (
                df_metricas.loc[df_metricas["cartera"] == "BAM_tecnologia_plus3", col].values[0]
                - df_metricas.loc[df_metricas["cartera"] == "BAM_actual", col].values[0]
            )
        except Exception:
            diferencial[col] = np.nan

df_metricas = pd.concat(
    [df_metricas, pd.DataFrame([diferencial])],
    ignore_index=True
)

df_metricas.to_csv(
    OUTPUT_METRICAS_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("Métricas guardadas en:")
print(OUTPUT_METRICAS_PATH)


# ============================================================
# 6. DRAWDOWNS
# ============================================================

df_drawdown = pd.concat(
    [
        dd_bam.rename("drawdown_BAM_actual"),
        dd_escenario.rename("drawdown_BAM_tecnologia_plus3")
    ],
    axis=1
)

df_drawdown.to_csv(
    OUTPUT_DRAWDOWN_PATH,
    encoding="utf-8-sig"
)

print("Drawdowns guardados en:")
print(OUTPUT_DRAWDOWN_PATH)


# ============================================================
# 7. MATRIZ DE CORRELACIONES
# ============================================================

# Solo componentes con datos suficientes
correlaciones = rets_ancho.corr()

correlaciones.to_csv(
    OUTPUT_CORRELACIONES_PATH,
    encoding="utf-8-sig"
)

print("Matriz de correlaciones guardada en:")
print(OUTPUT_CORRELACIONES_PATH)


# ============================================================
# 8. RESUMEN MARKDOWN
# ============================================================

m_actual = df_metricas[df_metricas["cartera"] == "BAM_actual"].iloc[0]
m_esc = df_metricas[df_metricas["cartera"] == "BAM_tecnologia_plus3"].iloc[0]
m_diff = df_metricas[df_metricas["cartera"] == "diferencia_escenario_menos_actual"].iloc[0]

resumen_md = f"""# Resumen métricas de riesgo - BAM vs tecnología +3 p.p.

## 1. Propósito

Este documento resume las métricas históricas calculadas para la cartera BAM actual y para el escenario de incremento de tecnología estadounidense en +3 p.p.

Los cálculos se basan en las series históricas disponibles en el prototipo y deben interpretarse como análisis preliminar, no como métricas oficiales de riesgo.

---

## 2. Datos utilizados

- Rentabilidades: `rentabilidades_bam_componentes_enriquecido.csv`
- Cartera actual: `cartera_real_fondmapfre_bolsa_america.csv`
- Escenario: `escenario_bam_tecnologia_plus3_posiciones.csv`
- Mapping: `mapping_isin_ticker_gics.csv`

---

## 3. Cobertura de tickers

### Tickers faltantes en BAM actual

{faltantes_bam if faltantes_bam else "No hay tickers faltantes relevantes."}

### Tickers faltantes en escenario

{faltantes_escenario if faltantes_escenario else "No hay tickers faltantes relevantes."}

---

## 4. Métricas principales

| Métrica | BAM actual | Escenario tecnología +3 | Diferencia |
|---|---:|---:|---:|
| Rentabilidad anualizada | {m_actual['rentabilidad_anualizada']:.4%} | {m_esc['rentabilidad_anualizada']:.4%} | {m_diff['rentabilidad_anualizada']:.4%} |
| Volatilidad anualizada | {m_actual['volatilidad_anualizada']:.4%} | {m_esc['volatilidad_anualizada']:.4%} | {m_diff['volatilidad_anualizada']:.4%} |
| VaR histórico diario 95% | {m_actual['var_historico_diario_95']:.4%} | {m_esc['var_historico_diario_95']:.4%} | {m_diff['var_historico_diario_95']:.4%} |
| VaR histórico anualizado 95% | {m_actual['var_historico_anualizado_95']:.4%} | {m_esc['var_historico_anualizado_95']:.4%} | {m_diff['var_historico_anualizado_95']:.4%} |
| Máximo drawdown | {m_actual['max_drawdown']:.4%} | {m_esc['max_drawdown']:.4%} | {m_diff['max_drawdown']:.4%} |
| Tracking error anualizado | {m_actual['tracking_error_anualizado']:.4%} | {m_esc['tracking_error_anualizado']:.4%} | {m_diff['tracking_error_anualizado']:.4%} |
| Beta vs benchmark | {m_actual['beta_vs_benchmark']:.4f} | {m_esc['beta_vs_benchmark']:.4f} | {m_diff['beta_vs_benchmark']:.4f} |

---

## 5. Lectura preliminar

El escenario tecnología +3 p.p. debe analizarse comparando el cambio de volatilidad, VaR, drawdown, tracking error y beta frente a BAM actual.

Si las métricas aumentan, el Agente Riesgo debería señalar que el escenario incrementa el riesgo histórico estimado.

Si las métricas se mantienen estables, el agente debe recordar que el análisis sigue dependiendo del periodo histórico, la calidad de las series y la metodología utilizada.

---

## 6. Advertencia metodológica

Estos cálculos forman parte del prototipo InvestCopilot.

No constituyen métricas oficiales de riesgo ni una recomendación de inversión.

La decisión final debe ser revisada por el gestor o por el órgano correspondiente.
"""

with open(OUTPUT_RESUMEN_MD_PATH, "w", encoding="utf-8") as f:
    f.write(resumen_md)

print("Resumen markdown guardado en:")
print(OUTPUT_RESUMEN_MD_PATH)


# ============================================================
# 9. FIN
# ============================================================

print("\nProceso terminado correctamente.")
print("Archivos generados:")
print("-", OUTPUT_METRICAS_PATH.name)
print("-", OUTPUT_SERIES_CARTERAS_PATH.name)
print("-", OUTPUT_DRAWDOWN_PATH.name)
print("-", OUTPUT_CORRELACIONES_PATH.name)
print("-", OUTPUT_RESUMEN_MD_PATH.name)