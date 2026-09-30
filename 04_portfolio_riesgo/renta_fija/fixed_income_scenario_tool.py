from pathlib import Path
import pandas as pd

# ============================================================
# TOOL DE ESCENARIOS DE RENTA FIJA - INVESTCOPILOT (prototipo)
# ============================================================
#
# Calcula el impacto en precio de un shock de tipos (paralelo) o de spread
# de crédito sobre la cartera de renta fija, usando duración modificada y
# DV01 por posición — el enfoque estándar de la industria, sin necesidad de
# reconstruir un motor de pricing de bonos ni series históricas de precios.
#
# Fórmula (aproximación de primer orden, válida para shocks moderados):
#   impacto_precio_pct ≈ -duracion_modificada * shock_decimal
#
# Para shock de tipos, shock_decimal = shock_pb / 10000.
# Para shock de spread de crédito, se usa la misma duración como proxy de
# "duración de spread" (simplificación habitual cuando no se dispone de
# spread duration específica por bono).
#
# Datos: ver README_renta_fija.md. Sintéticos por ahora; mismo formato que
# se espera de un extracto real de Bloomberg (ISIN, peso, duración
# modificada, DV01, OAS, rating, divisa, vencimiento).

BASE_DIR = Path(__file__).resolve().parent

# Datos reales (GBF, generados por generar_cartera_rf_real.py).
# Si no existen, fallback a datos sintéticos para no romper el prototipo.
_CARTERA_REAL = BASE_DIR / "cartera_bonos_real.csv"
_CARTERA_SINTETICA = BASE_DIR / "cartera_bonos_sintetica.csv"
CARTERA_PATH = _CARTERA_REAL if _CARTERA_REAL.exists() else _CARTERA_SINTETICA

BENCHMARK_PATH = BASE_DIR / "benchmark_renta_fija_sintetico.csv"

TIPOS_SHOCK_VALIDOS = ["tipos_paralelo", "spread_credito"]


def _cargar_cartera() -> pd.DataFrame:
    df = pd.read_csv(CARTERA_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def _cargar_benchmark() -> pd.DataFrame:
    df = pd.read_csv(BENCHMARK_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def _duracion_media_ponderada(df: pd.DataFrame, col_peso: str, col_duracion: str) -> float:
    pesos = df[col_peso] / df[col_peso].sum()
    return float((pesos * df[col_duracion]).sum())


def calcular_escenario_renta_fija(tipo_shock: str, magnitud_pb: float) -> dict:
    """
    Calcula el impacto de un shock de tipos paralelo o de spread de crédito
    sobre la cartera de renta fija, comparado con el benchmark.

    Parámetros:
    - tipo_shock: "tipos_paralelo" (shock de la curva de tipos libre de
      riesgo) o "spread_credito" (shock del spread de crédito, OAS).
    - magnitud_pb: magnitud del shock en puntos básicos. Positivo = subida
      de tipos/spreads (negativo para precios). Negativo = bajada.

    Devuelve impacto estimado en precio (%) para la cartera y el benchmark,
    duración/OAS agregados, y el detalle por posición.
    """

    tipo_shock = (tipo_shock or "").strip().lower()

    if tipo_shock not in TIPOS_SHOCK_VALIDOS:
        return {
            "status": "error",
            "message": f"tipo_shock '{tipo_shock}' no reconocido.",
            "tipos_validos": TIPOS_SHOCK_VALIDOS,
        }

    try:
        cartera = _cargar_cartera()
        benchmark = _cargar_benchmark()
    except Exception as e:
        return {
            "status": "error",
            "message": "No se han podido cargar los datos de renta fija.",
            "error": str(e),
        }

    shock_decimal = magnitud_pb / 10000.0

    cartera["impacto_precio_pct"] = -cartera["duracion_modificada"] * shock_decimal * 100
    pesos = cartera["peso_pct"] / cartera["peso_pct"].sum()
    impacto_cartera_pct = float((pesos * cartera["impacto_precio_pct"]).sum())

    duracion_cartera = _duracion_media_ponderada(cartera, "peso_pct", "duracion_modificada")
    oas_cartera = _duracion_media_ponderada(cartera, "peso_pct", "oas_bps")

    duracion_benchmark = _duracion_media_ponderada(benchmark, "peso_pct", "duracion_modificada")
    oas_benchmark = _duracion_media_ponderada(benchmark, "peso_pct", "oas_bps")
    impacto_benchmark_pct = -duracion_benchmark * shock_decimal * 100

    detalle_posiciones = cartera[[
        "nombre_activo", "sector", "rating", "peso_pct",
        "duracion_modificada", "oas_bps", "impacto_precio_pct",
    ]].sort_values("peso_pct", ascending=False).to_dict(orient="records")

    return {
        "status": "success",
        "tipo_shock": tipo_shock,
        "magnitud_pb_solicitada": magnitud_pb,
        "metodologia": (
            "Aproximación de primer orden: impacto_precio_pct ≈ -duración_modificada × shock. "
            "Para spread_credito se usa la duración modificada como proxy de duración de spread "
            "(simplificación habitual sin spread duration específica por bono). "
            "Válida para shocks moderados; no captura convexidad ni efectos de segundo orden."
        ),
        "cartera": {
            "duracion_modificada_media": round(duracion_cartera, 3),
            "oas_medio_bps": round(oas_cartera, 1),
            "impacto_precio_pct_estimado": round(impacto_cartera_pct, 4),
        },
        "benchmark": {
            "duracion_modificada_media": round(duracion_benchmark, 3),
            "oas_medio_bps": round(oas_benchmark, 1),
            "impacto_precio_pct_estimado": round(impacto_benchmark_pct, 4),
        },
        "diferencia_cartera_vs_benchmark_pct": round(impacto_cartera_pct - impacto_benchmark_pct, 4),
        "detalle_por_posicion": detalle_posiciones,
        "fuente_datos": "GBF real (saldos_Inventario_Fondos_20260713)" if _CARTERA_REAL.exists() else "sintética (prototipo)",
        "oas_fuente": "proxy por rating (no Bloomberg real)" if _CARTERA_REAL.exists() else "sintético",
        "advertencia": (
            "Cálculo paramétrico de primer orden. Posiciones reales de GBF (MISV 13/07/2026); "
            "OAS estimado por rating (proxy, no Bloomberg OAS real). Benchmark sintético. "
            "No constituye una métrica oficial de riesgo ni una recomendación de inversión. "
            "La decisión final debe ser revisada por el gestor o el órgano correspondiente."
            if _CARTERA_REAL.exists() else
            "Cálculo paramétrico de primer orden sobre datos sintéticos del prototipo "
            "InvestCopilot. No constituye una métrica oficial de riesgo ni una recomendación "
            "de inversión. La decisión final debe ser revisada por el gestor o el órgano "
            "correspondiente."
        ),
    }
