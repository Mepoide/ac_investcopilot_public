import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

CARTERAS_DIR = Path(__file__).resolve().parent

COMPARATIVA_PATH = CARTERAS_DIR / "comparativa_modelo_vs_bam.csv"
OUTPUT_PATH = CARTERAS_DIR / "comparativa_modelo_vs_bam_pesos_sector.csv"

# ============================================================
# CARGAR COMPARATIVA
# ============================================================

if not COMPARATIVA_PATH.exists():
    raise FileNotFoundError(f"No se encuentra el archivo: {COMPARATIVA_PATH}")

df = pd.read_csv(COMPARATIVA_PATH)

# Normalizar columnas
df.columns = [str(c).strip() for c in df.columns]

print("Columnas encontradas:")
print(df.columns.tolist())

# ============================================================
# DETECTAR COLUMNAS
# ============================================================

# Posibles nombres de sector
posibles_sector = [
    "sector",
    "gics_industry_group_name",
    "GICS Industry Group",
    "industry_group",
    "grupo_sectorial"
]

col_sector = None
for c in posibles_sector:
    if c in df.columns:
        col_sector = c
        break

if col_sector is None:
    raise ValueError(
        "No encuentro columna de sector. Revisa si existe 'sector' o 'gics_industry_group_name' en comparativa_modelo_vs_bam.csv"
    )

# Posibles nombres de pesos
posibles_peso_modelo = [
    "peso_modelo",
    "peso_cartera_modelo",
    "peso_modelo_rv_usa"
]

posibles_peso_bam = [
    "peso_bam",
    "peso_real",
    "peso_fondmapfre_bolsa_america"
]

col_peso_modelo = None
for c in posibles_peso_modelo:
    if c in df.columns:
        col_peso_modelo = c
        break

col_peso_bam = None
for c in posibles_peso_bam:
    if c in df.columns:
        col_peso_bam = c
        break

if col_peso_modelo is None:
    raise ValueError("No encuentro columna de peso modelo en comparativa_modelo_vs_bam.csv")

if col_peso_bam is None:
    raise ValueError("No encuentro columna de peso BAM en comparativa_modelo_vs_bam.csv")

# ============================================================
# LIMPIAR Y AGRUPAR
# ============================================================

df[col_sector] = df[col_sector].astype(str).str.strip()

df[col_peso_modelo] = pd.to_numeric(df[col_peso_modelo], errors="coerce").fillna(0)
df[col_peso_bam] = pd.to_numeric(df[col_peso_bam], errors="coerce").fillna(0)

sector = (
    df
    .groupby(col_sector, as_index=False)
    .agg(
        peso_modelo=(col_peso_modelo, "sum"),
        peso_bam=(col_peso_bam, "sum")
    )
)

sector["diferencia_bam_menos_modelo"] = sector["peso_bam"] - sector["peso_modelo"]
sector["abs_diferencia"] = sector["diferencia_bam_menos_modelo"].abs()

sector = sector.sort_values("abs_diferencia", ascending=False)

# Renombrar columna sector a nombre estándar
sector = sector.rename(columns={col_sector: "sector"})

# ============================================================
# GUARDAR
# ============================================================

sector.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("Archivo generado correctamente:")
print(OUTPUT_PATH)

print("\nVista previa:")
print(sector.to_string(index=False))