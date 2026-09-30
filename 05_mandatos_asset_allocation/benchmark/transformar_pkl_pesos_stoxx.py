import pickle
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

BENCHMARK_DIR = Path(__file__).resolve().parent
PROJECT_DIR = Path(__file__).resolve().parents[2]

PKL_PATH = BENCHMARK_DIR / "pesos_sx90up.pkl"

MAPPING_PATH = PROJECT_DIR / "04_portfolio_riesgo" / "series_historicas" / "mapping_isin_ticker_gics.csv"
BAM_PATH = PROJECT_DIR / "04_portfolio_riesgo" / "carteras" / "cartera_real_fondmapfre_bolsa_america.csv"

OUTPUT_BENCHMARK = BENCHMARK_DIR / "benchmark_stoxx_usa_900_tr_pesos.csv"
OUTPUT_BENCHMARK_SECTOR = BENCHMARK_DIR / "benchmark_stoxx_usa_900_tr_pesos_sector.csv"
OUTPUT_COMPARATIVA_BAM = BENCHMARK_DIR / "comparativa_bam_vs_stoxx_usa_900_tr.csv"
OUTPUT_COMPARATIVA_SECTOR = BENCHMARK_DIR / "comparativa_bam_vs_stoxx_usa_900_tr_sector.csv"
OUTPUT_VALIDACION = BENCHMARK_DIR / "validacion_benchmark_stoxx_usa_900_tr.md"
OUTPUT_DEBUG = BENCHMARK_DIR / "debug_columnas_benchmark.csv"

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def normalizar_texto(x):
    return (
        str(x)
        .replace("\u200c", "")
        .replace("\xa0", " ")
        .strip()
    )

def normalizar_ticker(x):
    return (
        normalizar_texto(x)
        .upper()
        .replace("  ", " ")
    )

def ticker_root(x):
    x = normalizar_ticker(x)
    if x == "" or x == "NAN":
        return ""
    return x.split()[0]

def limpiar_columna(x):
    return (
        normalizar_texto(x)
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "")
    )

def convertir_a_porcentaje(s):
    s = pd.to_numeric(s, errors="coerce")
    total = s.dropna().sum()
    if total <= 2:
        return s * 100
    return s

def detectar_columna_peso(df):
    candidatos_nombre = []
    for c in df.columns:
        c_clean = limpiar_columna(c)
        if (
            "weight" in c_clean
            or "peso" in c_clean
            or "percent" in c_clean
            or "pct" in c_clean
            or "mweight" in c_clean
        ):
            candidatos_nombre.append(c)

    candidatos_numericos = [
        c for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c])
    ]

    if candidatos_nombre:
        return candidatos_nombre[0]

    if candidatos_numericos:
        # Elegimos la columna numérica cuya suma sea más razonable como peso.
        # Normalmente suma cerca de 1 o de 100.
        mejor_col = None
        mejor_score = 10**9

        for c in candidatos_numericos:
            suma = pd.to_numeric(df[c], errors="coerce").dropna().sum()
            score = min(abs(suma - 1), abs(suma - 100))
            if score < mejor_score:
                mejor_score = score
                mejor_col = c

        return mejor_col

    return None

def detectar_columna_ticker(df, col_peso):
    candidatos_nombre = []
    for c in df.columns:
        if c == col_peso:
            continue
        c_clean = limpiar_columna(c)
        if (
            "ticker" in c_clean
            or "security" in c_clean
            or "member" in c_clean
            or "index_member" in c_clean
            or "name" in c_clean
        ):
            candidatos_nombre.append(c)

    if candidatos_nombre:
        return candidatos_nombre[0]

    # Si no detecta por nombre, buscamos columna object con pinta de ticker.
    columnas_objeto = [
        c for c in df.columns
        if c != col_peso and not pd.api.types.is_numeric_dtype(df[c])
    ]

    for c in columnas_objeto:
        muestra = df[c].dropna().astype(str).head(20).tolist()
        texto = " ".join(muestra).upper()
        if "EQUITY" in texto or "INDEX" in texto:
            return c

    if columnas_objeto:
        return columnas_objeto[0]

    return None

# ============================================================
# 1. CARGAR PKL
# ============================================================

if not PKL_PATH.exists():
    raise FileNotFoundError(f"No se encuentra el archivo: {PKL_PATH}")

with open(PKL_PATH, "rb") as f:
    obj = pickle.load(f)

print("PKL cargado correctamente.")
print("Tipo de objeto:", type(obj))

# ============================================================
# 2. EXTRAER TABLA Y FECHA
# ============================================================

fecha_benchmark = None

if isinstance(obj, dict):
    print("El PKL contiene un diccionario.")
    print("Claves disponibles:", list(obj.keys()))

    fecha_benchmark = obj.get("fecha", None)

    if "tabla" not in obj:
        raise KeyError("El diccionario no contiene la clave 'tabla'.")

    tabla = obj["tabla"]

else:
    print("El PKL no contiene diccionario. Se asume que el objeto es directamente la tabla.")
    tabla = obj

if not isinstance(tabla, pd.DataFrame):
    raise TypeError(f"La tabla extraída no es un DataFrame. Tipo detectado: {type(tabla)}")

df = tabla.copy()

print("Fecha benchmark:", fecha_benchmark)
print("Dimensiones tabla:", df.shape)
print("Columnas originales:")
print(df.columns)

# Guardar debug de columnas
pd.DataFrame({"columnas_originales": [str(c) for c in df.columns]}).to_csv(
    OUTPUT_DEBUG,
    index=False,
    encoding="utf-8-sig"
)

# ============================================================
# 3. LIMPIAR FORMATO DE TABLA
# ============================================================

if isinstance(df.columns, pd.MultiIndex):
    print("Columnas MultiIndex detectadas. Se aplanan.")
    df.columns = [
        "_".join([str(x) for x in col if str(x) != ""])
        for col in df.columns
    ]

df.columns = [normalizar_texto(c) for c in df.columns]

# Si el índice parece contener tickers, lo pasamos a columna
if not isinstance(df.index, pd.RangeIndex):
    df = df.reset_index()

print("Columnas tras limpieza:")
print(df.columns)

# ============================================================
# 4. DETECTAR COLUMNAS TICKER Y PESO
# ============================================================

col_peso = detectar_columna_peso(df)

if col_peso is None:
    raise ValueError("No se ha podido detectar la columna de peso del benchmark.")

col_ticker = detectar_columna_ticker(df, col_peso)

if col_ticker is None:
    raise ValueError("No se ha podido detectar la columna de ticker / miembro del índice.")

print("Columna ticker detectada:", col_ticker)
print("Columna peso detectada:", col_peso)

# ============================================================
# 5. NORMALIZAR BENCHMARK
# ============================================================

df_benchmark = df[[col_ticker, col_peso]].copy()
df_benchmark.columns = ["ticker", "peso_benchmark"]

df_benchmark["ticker"] = df_benchmark["ticker"].apply(normalizar_texto)
df_benchmark["ticker_normalizado"] = df_benchmark["ticker"].apply(normalizar_ticker)
df_benchmark["ticker_root"] = df_benchmark["ticker"].apply(ticker_root)

df_benchmark["peso_benchmark"] = pd.to_numeric(
    df_benchmark["peso_benchmark"],
    errors="coerce"
)

df_benchmark = df_benchmark.dropna(subset=["peso_benchmark"])
df_benchmark = df_benchmark[df_benchmark["ticker_normalizado"] != ""]

df_benchmark["peso_benchmark"] = convertir_a_porcentaje(df_benchmark["peso_benchmark"])

df_benchmark = (
    df_benchmark
    .groupby(["ticker_normalizado", "ticker_root"], as_index=False)
    .agg(
        ticker=("ticker", "first"),
        peso_benchmark=("peso_benchmark", "sum")
    )
)

df_benchmark = df_benchmark.sort_values(
    "peso_benchmark",
    ascending=False
).reset_index(drop=True)

print("")
print("Benchmark normalizado.")
print("Número de componentes:", len(df_benchmark))
print("Suma de pesos:", df_benchmark["peso_benchmark"].sum())
print(df_benchmark.head(10).to_string(index=False))

# ============================================================
# 6. ENRIQUECER CON MAPPING
# ============================================================

if MAPPING_PATH.exists():
    mapping = pd.read_csv(MAPPING_PATH)

    mapping["ticker_normalizado"] = mapping["ticker_normalizado"].apply(normalizar_ticker)
    mapping["ticker_root"] = mapping["ticker_normalizado"].apply(ticker_root)

    columnas_mapping = [
        "ticker_normalizado",
        "ticker_root",
        "isin",
        "gics_industry_group_name",
        "descripcion",
        "tipo_instrumento",
        "es_indice"
    ]

    columnas_mapping = [c for c in columnas_mapping if c in mapping.columns]

    # 6.1 Merge exacto por ticker normalizado
    df_benchmark = df_benchmark.merge(
        mapping[columnas_mapping],
        on="ticker_normalizado",
        how="left",
        suffixes=("", "_map")
    )

    # 6.2 Fallback por ticker_root para casos tipo AAPL UW Equity vs AAPL US Equity
    sin_mapping = df_benchmark["isin"].isna() | (df_benchmark["isin"].astype(str).str.strip() == "")

    if sin_mapping.any():
        mapping_root = (
            mapping[columnas_mapping]
            .dropna(subset=["ticker_root"])
            .drop_duplicates(subset=["ticker_root"], keep="first")
        )

        fallback = df_benchmark.loc[sin_mapping, ["ticker_normalizado", "ticker_root"]].merge(
            mapping_root,
            on="ticker_root",
            how="left",
            suffixes=("", "_fallback")
        )

        fallback = fallback.set_index("ticker_normalizado")

        for col in ["isin", "gics_industry_group_name", "descripcion", "tipo_instrumento", "es_indice"]:
            if col in df_benchmark.columns and col in fallback.columns:
                mask = sin_mapping & (
                    df_benchmark[col].isna()
                    | (df_benchmark[col].astype(str).str.strip() == "")
                )
                df_benchmark.loc[mask, col] = (
                    df_benchmark.loc[mask, "ticker_normalizado"]
                    .map(fallback[col])
                )

else:
    print("No se encuentra mapping_isin_ticker_gics.csv. Se genera benchmark sin enriquecer.")
    df_benchmark["isin"] = ""
    df_benchmark["gics_industry_group_name"] = ""

# Añadir fecha
df_benchmark["fecha_benchmark"] = fecha_benchmark

# ============================================================
# 7. GUARDAR BENCHMARK LIMPIO
# ============================================================

df_benchmark.to_csv(
    OUTPUT_BENCHMARK,
    index=False,
    encoding="utf-8-sig"
)

print("")
print("Benchmark guardado en:")
print(OUTPUT_BENCHMARK)

# ============================================================
# 8. PESOS POR SECTOR / GICS
# ============================================================

if "gics_industry_group_name" in df_benchmark.columns:
    df_sector = (
        df_benchmark
        .fillna({"gics_industry_group_name": "Sin mapping"})
        .groupby("gics_industry_group_name", as_index=False)["peso_benchmark"]
        .sum()
        .sort_values("peso_benchmark", ascending=False)
    )
else:
    df_sector = pd.DataFrame()

df_sector.to_csv(
    OUTPUT_BENCHMARK_SECTOR,
    index=False,
    encoding="utf-8-sig"
)

print("Pesos sectoriales benchmark guardados en:")
print(OUTPUT_BENCHMARK_SECTOR)

# ============================================================
# 9. COMPARAR BAM VS BENCHMARK
# ============================================================

if BAM_PATH.exists() and MAPPING_PATH.exists():
    bam = pd.read_csv(BAM_PATH)
    bam.columns = [limpiar_columna(c) for c in bam.columns]

    if "peso_bam" not in bam.columns:
        raise ValueError("No encuentro la columna 'peso_bam' en cartera_real_fondmapfre_bolsa_america.csv")

    if "isin" not in bam.columns:
        raise ValueError("No encuentro la columna 'isin' en cartera_real_fondmapfre_bolsa_america.csv")

    bam["isin"] = bam["isin"].astype(str).str.strip()
    bam["peso_bam"] = pd.to_numeric(bam["peso_bam"], errors="coerce")

    mapping = pd.read_csv(MAPPING_PATH)
    mapping["isin"] = mapping["isin"].astype(str).str.strip()
    mapping["ticker_normalizado"] = mapping["ticker_normalizado"].apply(normalizar_ticker)
    mapping["ticker_root"] = mapping["ticker_normalizado"].apply(ticker_root)

    bam = bam.merge(
        mapping[["isin", "ticker_normalizado", "ticker_root", "gics_industry_group_name"]],
        on="isin",
        how="left"
    )

    comp = bam.merge(
        df_benchmark[["ticker_normalizado", "ticker_root", "peso_benchmark"]],
        on="ticker_normalizado",
        how="outer",
        suffixes=("", "_bench")
    )

    # Fallback por ticker_root para posiciones no casadas exacto
    if "peso_benchmark" in comp.columns:
        sin_bench = comp["peso_benchmark"].isna()
    else:
        sin_bench = pd.Series(False, index=comp.index)

    if sin_bench.any():
        bench_root = (
            df_benchmark[["ticker_root", "peso_benchmark"]]
            .drop_duplicates(subset=["ticker_root"], keep="first")
        )

        comp = comp.merge(
            bench_root,
            on="ticker_root",
            how="left",
            suffixes=("", "_root")
        )

        comp["peso_benchmark"] = comp["peso_benchmark"].fillna(comp["peso_benchmark_root"])
        comp = comp.drop(columns=[c for c in ["peso_benchmark_root"] if c in comp.columns])

    for col in ["peso_bam", "peso_benchmark"]:
        if col not in comp.columns:
            comp[col] = 0
        comp[col] = pd.to_numeric(comp[col], errors="coerce").fillna(0)

    comp["diferencia_bam_menos_benchmark"] = comp["peso_bam"] - comp["peso_benchmark"]
    comp["abs_diferencia"] = comp["diferencia_bam_menos_benchmark"].abs()

    comp = comp.sort_values("abs_diferencia", ascending=False)

    comp.to_csv(
        OUTPUT_COMPARATIVA_BAM,
        index=False,
        encoding="utf-8-sig"
    )

    print("Comparativa BAM vs benchmark guardada en:")
    print(OUTPUT_COMPARATIVA_BAM)

    # Comparativa sectorial
    bam_sector = (
        bam
        .fillna({"gics_industry_group_name": "Sin mapping"})
        .groupby("gics_industry_group_name", as_index=False)["peso_bam"]
        .sum()
    )

    comp_sector = bam_sector.merge(
        df_sector,
        on="gics_industry_group_name",
        how="outer"
    ).fillna(0)

    comp_sector["diferencia_bam_menos_benchmark"] = (
        comp_sector["peso_bam"] - comp_sector["peso_benchmark"]
    )

    comp_sector["abs_diferencia"] = comp_sector["diferencia_bam_menos_benchmark"].abs()

    comp_sector = comp_sector.sort_values("abs_diferencia", ascending=False)

    comp_sector.to_csv(
        OUTPUT_COMPARATIVA_SECTOR,
        index=False,
        encoding="utf-8-sig"
    )

    print("Comparativa sectorial BAM vs benchmark guardada en:")
    print(OUTPUT_COMPARATIVA_SECTOR)

else:
    print("No se genera comparativa BAM vs benchmark porque falta BAM o mapping.")

# ============================================================
# 10. VALIDACIÓN
# ============================================================

tickers_sin_mapping = []

if "isin" in df_benchmark.columns:
    tickers_sin_mapping = (
        df_benchmark
        .loc[
            df_benchmark["isin"].isna()
            | (df_benchmark["isin"].astype(str).str.strip() == ""),
            "ticker_normalizado"
        ]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

total_peso = df_benchmark["peso_benchmark"].sum()

texto_validacion = (
    "# Validación benchmark STOXX USA 900 TR\n\n"
    "## 1. Archivos generados\n\n"
    "- benchmark_stoxx_usa_900_tr_pesos.csv\n"
    "- benchmark_stoxx_usa_900_tr_pesos_sector.csv\n"
    "- comparativa_bam_vs_stoxx_usa_900_tr.csv\n"
    "- comparativa_bam_vs_stoxx_usa_900_tr_sector.csv\n"
    "- debug_columnas_benchmark.csv\n\n"
    "## 2. Resumen del benchmark\n\n"
    f"- Fecha benchmark incluida en el PKL: {fecha_benchmark}\n"
    f"- Número de componentes detectados: {len(df_benchmark)}\n"
    f"- Suma de pesos detectada: {total_peso:.4f} %\n\n"
    "## 3. Tickers sin mapping\n\n"
    f"{tickers_sin_mapping if tickers_sin_mapping else 'No se detectan tickers sin mapping.'}\n\n"
    "## 4. Uso en InvestCopilot\n\n"
    "Este benchmark se utilizará como referencia del DFI para Fondmapfre Bolsa América en el prototipo.\n\n"
    "La cartera BAM se comparará frente al benchmark para identificar sobreponderaciones, infraponderaciones, desviaciones sectoriales, desviaciones por posición y posibles alertas de concentración.\n\n"
    "## 5. Advertencia\n\n"
    "Este archivo procede de la transformación de un .pkl proporcionado para el prototipo. Debe validarse que los pesos corresponden efectivamente al STOXX USA 900 TR y a la fecha correcta antes de utilizarlo como referencia definitiva.\n"
)

with open(OUTPUT_VALIDACION, "w", encoding="utf-8") as f:
    f.write(texto_validacion)

print("")
print("Validación guardada en:")
print(OUTPUT_VALIDACION)

print("")
print("Proceso terminado correctamente.")
print("Archivos generados:")
print("-", OUTPUT_BENCHMARK.name)
print("-", OUTPUT_BENCHMARK_SECTOR.name)
print("-", OUTPUT_COMPARATIVA_BAM.name)
print("-", OUTPUT_COMPARATIVA_SECTOR.name)
print("-", OUTPUT_VALIDACION.name)
print("-", OUTPUT_DEBUG.name)