import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).parent

PKL_PATH = BASE_DIR / "precios_valores.pkl"

MAPPING_PATH = BASE_DIR / "mapping_isin_ticker_gics.csv"

PRECIOS_LARGO_PATH = BASE_DIR / "precios_bam_componentes.csv"
RENTABILIDADES_LARGO_PATH = BASE_DIR / "rentabilidades_bam_componentes.csv"

PRECIOS_ANCHO_PATH = BASE_DIR / "precios_bam_componentes_formato_ancho.csv"
RENTABILIDADES_ANCHO_PATH = BASE_DIR / "rentabilidades_bam_componentes_formato_ancho.csv"

PRECIOS_ENRIQUECIDOS_PATH = BASE_DIR / "precios_bam_componentes_enriquecido.csv"
RENTABILIDADES_ENRIQUECIDAS_PATH = BASE_DIR / "rentabilidades_bam_componentes_enriquecido.csv"

VALIDACION_TICKERS_SIN_MAPPING_PATH = BASE_DIR / "validacion_tickers_sin_mapping.csv"


# ============================================================
# 1. CARGAR PKL
# ============================================================

df = pd.read_pickle(PKL_PATH)

print("Archivo .pkl cargado correctamente.")
print("Dimensiones originales:", df.shape)
print("Tipo de columnas:", type(df.columns))
print("Primeras columnas:")
print(df.columns[:5])


# ============================================================
# 2. TRATAR COLUMNAS MULTIINDEX
# ============================================================

if isinstance(df.columns, pd.MultiIndex):
    print("\nColumnas MultiIndex detectadas.")

    print("Niveles del MultiIndex:")
    print(df.columns.names)

    # Si las columnas son tipo ('AAPL US Equity', 'PX_LAST'),
    # nos quedamos solo con el primer nivel: el ticker.
    df.columns = df.columns.get_level_values(0)

    print("Columnas aplanadas usando el primer nivel del MultiIndex.")
    print("Primeras columnas tras aplanar:")
    print(df.columns[:5])

else:
    print("\nLas columnas no son MultiIndex. Se continúa sin aplanar.")


# ============================================================
# 3. PASAR ÍNDICE DE FECHA A COLUMNA
# ============================================================

# La fecha está en el índice, así que la pasamos a columna
df = df.reset_index()

# La primera columna tras reset_index será la fecha
col_fecha = df.columns[0]
df = df.rename(columns={col_fecha: "fecha"})

df["fecha"] = pd.to_datetime(df["fecha"])

# Ordenar por fecha
df = df.sort_values("fecha")


# ============================================================
# 4. LIMPIAR COLUMNAS / TICKERS
# ============================================================

# Limpiar nombres de columnas
df.columns = [
    str(c).replace("\u200c", "").strip()
    for c in df.columns
]

# Identificar columnas de tickers
ticker_cols = [c for c in df.columns if c != "fecha"]

# Normalizar nombres de tickers en columnas
rename_tickers = {
    c: " ".join(str(c).replace("\u200c", "").strip().split())
    for c in ticker_cols
}

df = df.rename(columns=rename_tickers)

ticker_cols = [c for c in df.columns if c != "fecha"]

print("\nNúmero de tickers detectados:", len(ticker_cols))
print("Primeros tickers detectados:")
print(ticker_cols[:10])


# ============================================================
# 5. GUARDAR PRECIOS EN FORMATO ANCHO
# ============================================================

df.to_csv(
    PRECIOS_ANCHO_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("\nPrecios en formato ancho guardados en:")
print(PRECIOS_ANCHO_PATH)


# ============================================================
# 6. CONVERTIR PRECIOS A FORMATO LARGO
# ============================================================

df_largo = df.melt(
    id_vars="fecha",
    var_name="ticker",
    value_name="precio"
)

df_largo = df_largo.dropna(subset=["precio"])

df_largo["ticker"] = (
    df_largo["ticker"]
    .astype(str)
    .str.replace("\u200c", "", regex=False)
    .str.strip()
)

df_largo["ticker_normalizado"] = (
    df_largo["ticker"]
    .str.upper()
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

df_largo = df_largo.sort_values(["ticker_normalizado", "fecha"])

df_largo.to_csv(
    PRECIOS_LARGO_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("\nPrecios en formato largo guardados en:")
print(PRECIOS_LARGO_PATH)


# ============================================================
# 7. CALCULAR RENTABILIDADES
# ============================================================

df_ret = df.copy()
df_ret = df_ret.sort_values("fecha")

# Calcular rentabilidades diarias por ticker
df_ret[ticker_cols] = df_ret[ticker_cols].pct_change()

# Eliminar filas donde todos los retornos sean NaN
df_ret = df_ret.dropna(how="all", subset=ticker_cols)

df_ret.to_csv(
    RENTABILIDADES_ANCHO_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("\nRentabilidades en formato ancho guardadas en:")
print(RENTABILIDADES_ANCHO_PATH)

# Pasar rentabilidades a formato largo
df_ret_largo = df_ret.melt(
    id_vars="fecha",
    var_name="ticker",
    value_name="retorno_diario"
)

df_ret_largo = df_ret_largo.dropna(subset=["retorno_diario"])

df_ret_largo["ticker"] = (
    df_ret_largo["ticker"]
    .astype(str)
    .str.replace("\u200c", "", regex=False)
    .str.strip()
)

df_ret_largo["ticker_normalizado"] = (
    df_ret_largo["ticker"]
    .str.upper()
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

df_ret_largo = df_ret_largo.sort_values(["ticker_normalizado", "fecha"])

df_ret_largo.to_csv(
    RENTABILIDADES_LARGO_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("\nRentabilidades en formato largo guardadas en:")
print(RENTABILIDADES_LARGO_PATH)


# ============================================================
# 8. ENRIQUECER CON MAPPING ISIN / TICKER / GICS
# ============================================================

if MAPPING_PATH.exists():
    mapping = pd.read_csv(MAPPING_PATH)

    mapping["ticker_normalizado"] = (
        mapping["ticker_normalizado"]
        .astype(str)
        .str.upper()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    columnas_mapping = [
        "ticker_normalizado",
        "isin",
        "gics_industry_group_name",
        "descripcion",
        "tipo_instrumento",
        "es_indice"
    ]

    columnas_mapping = [c for c in columnas_mapping if c in mapping.columns]

    # Enriquecer precios
    df_largo_enriquecido = df_largo.merge(
        mapping[columnas_mapping],
        on="ticker_normalizado",
        how="left"
    )

    df_largo_enriquecido.to_csv(
        PRECIOS_ENRIQUECIDOS_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    # Enriquecer rentabilidades
    df_ret_largo_enriquecido = df_ret_largo.merge(
        mapping[columnas_mapping],
        on="ticker_normalizado",
        how="left"
    )

    df_ret_largo_enriquecido.to_csv(
        RENTABILIDADES_ENRIQUECIDAS_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nArchivos enriquecidos guardados en:")
    print(PRECIOS_ENRIQUECIDOS_PATH)
    print(RENTABILIDADES_ENRIQUECIDAS_PATH)

    # Validación de tickers sin mapping
    tickers_sin_mapping = (
        df_largo_enriquecido
        .loc[df_largo_enriquecido["isin"].isna(), "ticker_normalizado"]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    pd.DataFrame({
        "ticker_normalizado_sin_mapping": tickers_sin_mapping
    }).to_csv(
        VALIDACION_TICKERS_SIN_MAPPING_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nNúmero de tickers sin mapping:", len(tickers_sin_mapping))
    print("Validación guardada en:")
    print(VALIDACION_TICKERS_SIN_MAPPING_PATH)

else:
    print("\nNo se ha encontrado mapping_isin_ticker_gics.csv.")
    print("Se han generado precios y rentabilidades sin enriquecer.")


# ============================================================
# 9. RESUMEN FINAL
# ============================================================

print("\nProceso terminado correctamente.")
print("Archivos principales generados:")
print("-", PRECIOS_LARGO_PATH.name)
print("-", RENTABILIDADES_LARGO_PATH.name)
print("-", PRECIOS_ENRIQUECIDOS_PATH.name)
print("-", RENTABILIDADES_ENRIQUECIDAS_PATH.name)