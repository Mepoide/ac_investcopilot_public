from pathlib import Path
import pandas as pd
import numpy as np

# ============================================================
# HERRAMIENTA DE CALCULO DE ESCENARIOS DE RIESGO - INVESTCOPILOT
# ============================================================
#
# A diferencia de calcular_metricas_riesgo.py (que es un script que solo
# recalcula el escenario fijo "+3pp tecnologia" y escribe archivos), este
# modulo expone una funcion reutilizable para calcular el impacto en riesgo
# de CUALQUIER cambio de peso sectorial (p.ej. "vender 1pp en tecnologia",
# "subir 2pp en salud"), pensada para ser invocada como tool por un LLM
# (function calling) o por el orquestador/MCP server.
#
# Metodologia (la misma que ya usa el prototipo para el escenario +3pp
# tecnologia precalculado, verificada sobre
# escenario_bam_tecnologia_plus3_posiciones.csv):
#
# 1. El peso del sector objetivo se escala proporcionalmente entre sus
#    posiciones para alcanzar el nuevo peso total (actual + delta_pp).
# 2. El hueco de financiacion (o el excedente, si delta_pp es negativo) se
#    reparte proporcionalmente entre TODAS las demas posiciones de la
#    cartera, en funcion de su peso actual.
#
# Esto reproduce el mismo criterio de redistribucion pro-rata que ya se
# uso para construir escenario_bam_tecnologia_plus3_posiciones.csv, en vez
# de inventar un criterio nuevo.

BASE_DIR = Path(__file__).resolve().parents[1]

CARTERAS_DIR = BASE_DIR / "carteras"
SERIES_DIR = BASE_DIR / "series_historicas"
METRICAS_DIR = BASE_DIR / "metricas"

RETS_PATH = SERIES_DIR / "rentabilidades_bam_componentes_enriquecido.csv"
CARTERA_ACTUAL_PATH = CARTERAS_DIR / "cartera_real_fondmapfre_bolsa_america.csv"
MAPPING_PATH = SERIES_DIR / "mapping_isin_ticker_gics.csv"

BENCHMARK_TICKER = "SPX INDEX"
DIAS_ANUALES = 252
NIVEL_VAR = 0.95


# ============================================================
# FUNCIONES AUXILIARES (mismas formulas que calcular_metricas_riesgo.py)
# ============================================================

def _normalizar_ticker(x):
    return (
        str(x)
        .replace("‌", "")
        .strip()
        .upper()
        .replace("  ", " ")
    )


def _max_drawdown(returns):
    indice = (1 + returns).cumprod()
    max_acum = indice.cummax()
    drawdown = indice / max_acum - 1
    return drawdown.min()


def _calcular_metricas(nombre, serie_ret, benchmark=None):
    serie_ret = serie_ret.dropna()

    if len(serie_ret) == 0:
        return {
            "cartera": nombre,
            "num_observaciones": 0,
            "advertencia": "Sin observaciones suficientes para calcular métricas.",
        }

    vol_diaria = serie_ret.std()
    vol_anual = vol_diaria * np.sqrt(DIAS_ANUALES)

    var_diario = -np.percentile(serie_ret, (1 - NIVEL_VAR) * 100)
    var_anual = var_diario * np.sqrt(DIAS_ANUALES)

    mdd = _max_drawdown(serie_ret)

    rent_acum = (1 + serie_ret).prod() - 1
    rent_anualizada = (1 + rent_acum) ** (DIAS_ANUALES / len(serie_ret)) - 1

    metricas = {
        "cartera": nombre,
        "num_observaciones": len(serie_ret),
        "rentabilidad_acumulada": rent_acum,
        "rentabilidad_anualizada": rent_anualizada,
        "volatilidad_diaria": vol_diaria,
        "volatilidad_anualizada": vol_anual,
        "var_historico_diario_95": var_diario,
        "var_historico_anualizado_95": var_anual,
        "max_drawdown": mdd,
    }

    if benchmark is not None:
        df_tmp = pd.concat([serie_ret, benchmark], axis=1).dropna()
        df_tmp.columns = ["cartera", "benchmark"]

        exceso = df_tmp["cartera"] - df_tmp["benchmark"]

        tracking_error_diario = exceso.std()
        tracking_error_anual = tracking_error_diario * np.sqrt(DIAS_ANUALES)

        var_benchmark = np.var(df_tmp["benchmark"])
        beta = (
            np.cov(df_tmp["cartera"], df_tmp["benchmark"])[0, 1] / var_benchmark
            if var_benchmark != 0
            else np.nan
        )

        metricas.update({
            "tracking_error_diario": tracking_error_diario,
            "tracking_error_anualizado": tracking_error_anual,
            "beta_vs_benchmark": beta,
        })

    return metricas


def _construir_serie_cartera(retornos_ancho, pesos, nombre_peso):
    cols_disponibles = [c for c in pesos.index if c in retornos_ancho.columns]

    pesos_ok = pesos.loc[cols_disponibles].copy()
    pesos_ok = pesos_ok / pesos_ok.sum()

    retornos_ok = retornos_ancho[cols_disponibles].copy()

    serie = retornos_ok.mul(pesos_ok, axis=1).sum(axis=1)
    serie.name = nombre_peso

    tickers_faltantes = sorted(set(pesos.index) - set(cols_disponibles))

    return serie, tickers_faltantes


def _cargar_datos_base():
    rets = pd.read_csv(RETS_PATH)
    rets["fecha"] = pd.to_datetime(rets["fecha"])
    rets["ticker_normalizado"] = rets["ticker_normalizado"].apply(_normalizar_ticker)

    rets_ancho = rets.pivot_table(
        index="fecha",
        columns="ticker_normalizado",
        values="retorno_diario",
        aggfunc="first",
    ).sort_index()

    cartera = pd.read_csv(CARTERA_ACTUAL_PATH)
    cartera.columns = [c.strip().lower() for c in cartera.columns]

    mapping = pd.read_csv(MAPPING_PATH)
    mapping["ticker_normalizado"] = mapping["ticker_normalizado"].apply(_normalizar_ticker)
    mapping["isin"] = mapping["isin"].astype(str).str.strip()

    cartera["isin"] = cartera["isin"].astype(str).str.strip()
    cartera = cartera.merge(mapping[["isin", "ticker_normalizado"]], on="isin", how="left")

    benchmark = rets_ancho[BENCHMARK_TICKER] if BENCHMARK_TICKER in rets_ancho.columns else None

    return rets_ancho, cartera, benchmark


# ============================================================
# FUNCION PRINCIPAL: ESCENARIO SECTORIAL AD-HOC
# ============================================================

def calcular_escenario_sectorial(sector: str, delta_pp: float) -> dict:
    """
    Calcula el impacto en métricas de riesgo de cambiar el peso de un sector
    en +/- delta_pp puntos porcentuales (p.ej. delta_pp=-1.0 para "vender 1pp",
    delta_pp=2.5 para "subir 2.5pp"), financiando el cambio proporcionalmente
    con el resto de la cartera (misma metodología que el escenario +3pp
    tecnología ya existente en el prototipo).

    Devuelve un dict con status, métricas actuales, métricas del escenario,
    diferencias, y los pesos resultantes. No escribe ni modifica ningún
    archivo: es una función pura de cálculo bajo demanda.
    """

    try:
        rets_ancho, cartera, benchmark = _cargar_datos_base()
    except Exception as e:
        return {
            "status": "error",
            "message": "No se han podido cargar los datos base (rentabilidades / cartera / mapping).",
            "error": str(e),
        }

    sectores_disponibles = sorted(cartera["sector"].dropna().unique().tolist())

    sector_match = next(
        (s for s in sectores_disponibles if s.strip().lower() == sector.strip().lower()),
        None,
    )

    if sector_match is None:
        return {
            "status": "error",
            "message": f"Sector '{sector}' no reconocido en la cartera BAM.",
            "sectores_disponibles": sectores_disponibles,
        }

    sector = sector_match

    cartera["peso_bam_pct"] = cartera["peso_bam"]
    peso_sector_actual = cartera.loc[cartera["sector"] == sector, "peso_bam_pct"].sum()
    peso_sector_escenario = peso_sector_actual + delta_pp

    if peso_sector_escenario < 0:
        return {
            "status": "error",
            "message": (
                f"El delta solicitado ({delta_pp:+.2f} p.p.) dejaría el peso de "
                f"'{sector}' en {peso_sector_escenario:.2f}%, por debajo de 0%. "
                "No es un escenario válido."
            ),
            "peso_sector_actual_pct": peso_sector_actual,
        }

    resto_actual = 100.0 - peso_sector_actual

    if resto_actual <= 0:
        return {
            "status": "error",
            "message": "No hay resto de cartera disponible para financiar el cambio (el sector ya pesa ~100%).",
        }

    resto_escenario = resto_actual - delta_pp

    if resto_escenario < 0:
        return {
            "status": "error",
            "message": (
                f"El delta solicitado ({delta_pp:+.2f} p.p.) requeriría financiarse con más peso "
                "del que existe fuera del sector. No es un escenario válido."
            ),
        }

    factor_sector = (peso_sector_escenario / peso_sector_actual) if peso_sector_actual > 0 else 0.0
    factor_resto = resto_escenario / resto_actual

    pesos_escenario_pct = cartera["peso_bam_pct"].where(
        cartera["sector"] != sector,
        cartera["peso_bam_pct"] * factor_sector,
    )
    pesos_escenario_pct = pesos_escenario_pct.where(
        cartera["sector"] == sector,
        cartera["peso_bam_pct"] * factor_resto,
    )

    cartera["peso_escenario_pct"] = pesos_escenario_pct

    pesos_actual = cartera.set_index("ticker_normalizado")["peso_bam_pct"].dropna() / 100
    pesos_escenario = cartera.set_index("ticker_normalizado")["peso_escenario_pct"].dropna() / 100

    serie_actual, faltantes_actual = _construir_serie_cartera(rets_ancho, pesos_actual, "BAM_actual")
    serie_escenario, faltantes_escenario = _construir_serie_cartera(rets_ancho, pesos_escenario, "BAM_escenario")

    metricas_actual = _calcular_metricas("BAM_actual", serie_actual, benchmark=benchmark)
    metricas_escenario = _calcular_metricas("BAM_escenario", serie_escenario, benchmark=benchmark)

    claves_numericas = [
        k for k in metricas_actual
        if k not in ("cartera", "num_observaciones") and isinstance(metricas_actual.get(k), (int, float))
    ]

    diferencias = {
        k: (metricas_escenario.get(k) - metricas_actual.get(k))
        for k in claves_numericas
        if isinstance(metricas_escenario.get(k), (int, float))
    }

    sector_top_posiciones = (
        cartera.loc[cartera["sector"] == sector, ["nombre_activo", "peso_bam_pct", "peso_escenario_pct"]]
        .sort_values("peso_bam_pct", ascending=False)
        .head(10)
        .to_dict(orient="records")
    )

    return {
        "status": "success",
        "sector": sector,
        "delta_pp_solicitado": delta_pp,
        "peso_sector_actual_pct": round(peso_sector_actual, 4),
        "peso_sector_escenario_pct": round(peso_sector_escenario, 4),
        "metodologia": (
            "El peso del sector se escala proporcionalmente entre sus posiciones hasta "
            "alcanzar el nuevo peso total. El hueco (o excedente) se financia repartiéndolo "
            "proporcionalmente entre el resto de posiciones de la cartera, según su peso actual. "
            "Misma metodología que el escenario tecnología +3pp ya existente en el prototipo."
        ),
        "metricas_actual": metricas_actual,
        "metricas_escenario": metricas_escenario,
        "diferencias_escenario_menos_actual": diferencias,
        "principales_posiciones_del_sector": sector_top_posiciones,
        "tickers_sin_serie_de_precios": sorted(set(faltantes_actual) | set(faltantes_escenario)),
        "advertencia": (
            "Cálculo bajo demanda del prototipo InvestCopilot a partir de datos históricos "
            "simplificados. No constituye una métrica oficial de riesgo ni una recomendación "
            "de inversión. La decisión final debe ser revisada por el gestor o el órgano "
            "correspondiente."
        ),
    }


# ============================================================
# FUNCION PRINCIPAL: ESCENARIO MULTI-SECTORIAL AD-HOC
# ============================================================

def calcular_escenario_multisector(cambios: list) -> dict:
    """
    Calcula el impacto en métricas de riesgo de mover varios sectores a la vez.

    cambios: lista de dicts con claves 'sector' y 'delta_pp'.
    Ejemplo: [{"sector": "Health Care", "delta_pp": -2.0},
               {"sector": "Information Technology", "delta_pp": 1.5}]

    El resto de la cartera (sectores no mencionados) financia/absorbe el
    net de todos los cambios, repartido proporcionalmente a sus pesos actuales.
    Si el net de cambios es 0 (lo que sumas lo quitas), la cartera sigue
    sumando 100% sin tocar el resto.
    """

    try:
        rets_ancho, cartera, benchmark = _cargar_datos_base()
    except Exception as e:
        return {
            "status": "error",
            "message": "No se han podido cargar los datos base.",
            "error": str(e),
        }

    sectores_disponibles = sorted(cartera["sector"].dropna().unique().tolist())

    cambios_validados = []
    for c in cambios:
        sector_raw = c.get("sector", "")
        delta = float(c.get("delta_pp", 0.0))
        sector_match = next(
            (s for s in sectores_disponibles if s.strip().lower() == sector_raw.strip().lower()),
            None,
        )
        if sector_match is None:
            return {
                "status": "error",
                "message": f"Sector '{sector_raw}' no reconocido en la cartera BAM.",
                "sectores_disponibles": sectores_disponibles,
            }
        cambios_validados.append({"sector": sector_match, "delta_pp": delta})

    sectores_afectados = {c["sector"] for c in cambios_validados}

    cartera["peso_bam_pct"] = cartera["peso_bam"]
    cartera["peso_escenario_pct"] = cartera["peso_bam_pct"].copy()

    for c in cambios_validados:
        sector = c["sector"]
        delta = c["delta_pp"]
        peso_sector_actual = cartera.loc[cartera["sector"] == sector, "peso_escenario_pct"].sum()
        peso_sector_nuevo = peso_sector_actual + delta

        if peso_sector_nuevo < 0:
            return {
                "status": "error",
                "message": (
                    f"El delta solicitado ({delta:+.2f} p.p.) dejaría el sector "
                    f"'{sector}' en {peso_sector_nuevo:.2f}%, por debajo de 0%."
                ),
            }

        if peso_sector_actual > 0:
            factor = peso_sector_nuevo / peso_sector_actual
            cartera.loc[cartera["sector"] == sector, "peso_escenario_pct"] *= factor
        else:
            return {
                "status": "error",
                "message": f"El sector '{sector}' tiene peso actual 0%, no se puede escalar.",
            }

    delta_neto = sum(c["delta_pp"] for c in cambios_validados)
    peso_resto_actual = cartera.loc[~cartera["sector"].isin(sectores_afectados), "peso_escenario_pct"].sum()

    if abs(delta_neto) > 1e-9:
        peso_resto_nuevo = peso_resto_actual - delta_neto
        if peso_resto_nuevo < 0:
            return {
                "status": "error",
                "message": (
                    f"El delta neto ({delta_neto:+.2f} p.p.) excede el peso disponible "
                    f"fuera de los sectores afectados ({peso_resto_actual:.2f}%)."
                ),
            }
        if peso_resto_actual > 0:
            factor_resto = peso_resto_nuevo / peso_resto_actual
            cartera.loc[~cartera["sector"].isin(sectores_afectados), "peso_escenario_pct"] *= factor_resto

    pesos_actual = cartera.set_index("ticker_normalizado")["peso_bam_pct"].dropna() / 100
    pesos_escenario = cartera.set_index("ticker_normalizado")["peso_escenario_pct"].dropna() / 100

    serie_actual, _ = _construir_serie_cartera(rets_ancho, pesos_actual, "BAM_actual")
    serie_escenario, faltantes = _construir_serie_cartera(rets_ancho, pesos_escenario, "BAM_escenario")

    metricas_actual = _calcular_metricas("BAM_actual", serie_actual, benchmark=benchmark)
    metricas_escenario = _calcular_metricas("BAM_escenario", serie_escenario, benchmark=benchmark)

    claves_numericas = [
        k for k in metricas_actual
        if k not in ("cartera", "num_observaciones") and isinstance(metricas_actual.get(k), (int, float))
    ]
    diferencias = {
        k: (metricas_escenario.get(k) - metricas_actual.get(k))
        for k in claves_numericas
        if isinstance(metricas_escenario.get(k), (int, float))
    }

    resumen_cambios = [
        {
            "sector": c["sector"],
            "delta_pp": c["delta_pp"],
            "peso_actual_pct": round(cartera.loc[cartera["sector"] == c["sector"], "peso_bam_pct"].sum(), 4),
            "peso_escenario_pct": round(cartera.loc[cartera["sector"] == c["sector"], "peso_escenario_pct"].sum(), 4),
        }
        for c in cambios_validados
    ]

    return {
        "status": "success",
        "cambios_aplicados": resumen_cambios,
        "delta_neto_pp": round(delta_neto, 4),
        "metricas_actual": metricas_actual,
        "metricas_escenario": metricas_escenario,
        "diferencias_escenario_menos_actual": diferencias,
        "tickers_sin_serie_de_precios": sorted(faltantes),
        "advertencia": (
            "Cálculo bajo demanda del prototipo InvestCopilot a partir de datos históricos "
            "simplificados. No constituye una métrica oficial de riesgo ni una recomendación "
            "de inversión. La decisión final debe ser revisada por el gestor o el órgano "
            "correspondiente."
        ),
    }
