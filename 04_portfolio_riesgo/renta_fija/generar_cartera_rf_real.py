"""
Genera cartera_bonos_real.csv a partir de datos reales del inventario de saldos.

Fuente: data/saldos_Inventario_Fondos_20260713.xlsx
Fondo:  GBF (mayor duración modificada del universo — ~8 años, buen ejemplo
        de riesgo de tipos para la demo de InvestCopilot).

OAS proxy: no disponible directamente en MISV; se estima por rating/sector
siguiendo convenciones estándar de mercado. Marcado como sintético en la columna
oas_fuente para no confundirlo con datos reales de Bloomberg.

Ejecutar:
    python3 04_portfolio_riesgo/renta_fija/generar_cartera_rf_real.py
"""

from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parents[2]
SALDOS_PATH = PROJECT_DIR / "data" / "saldos_Inventario_Fondos_20260713.xlsx"
OUT_PATH = Path(__file__).resolve().parent / "cartera_bonos_real.csv"

FONDO = "GBF"

# Proxy de OAS (pb) por rating, en ausencia de Bloomberg OAS real.
# Nivel conservador mid-2026, curva EUR.
OAS_BY_RATING = {
    "AAA": 5, "AA+": 10, "AA": 15, "AA-": 20,
    "A+": 40, "A": 55, "A-": 70,
    "BBB+": 100, "BBB": 130, "BBB-": 170,
    "BB+": 230, "BB": 300, "BB-": 380,
    "B+": 480, "B": 600,
}
OAS_DEFAULT = 50  # cuando rating no disponible o no mapeado


def _oas_proxy(rating_val) -> int:
    if pd.isna(rating_val) or not str(rating_val).strip():
        return OAS_DEFAULT
    r = str(rating_val).strip().upper()
    return OAS_BY_RATING.get(r, OAS_DEFAULT)


def _sector_label(row) -> str:
    s2 = str(row.get("Sector N2", "")).strip()
    s1 = str(row.get("Sector N1", "")).strip()
    return s2 if s2 and s2 not in ("nan", "NDES") else (s1 if s1 and s1 not in ("nan",) else "Other")


def run():
    print(f"Leyendo saldos desde {SALDOS_PATH}...")
    df = pd.read_excel(SALDOS_PATH)

    # Solo fondo seleccionado, solo RF, con ISIN y duración válida
    mask = (
        (df["Código cartera MISV"] == FONDO) &
        (df["Tipo de Renta Operacional"] == "FI") &
        (df["ISIN de la Emisión"].notna()) &
        (df["Duración Modificada"].notna()) &
        (df["Duración Modificada"] > 0) &
        (df["Valor de Mercado Contravalorado"] > 0)
    )
    sub = df[mask].copy()
    print(f"Posiciones RF {FONDO}: {len(sub)}")

    if sub.empty:
        print("ERROR: No hay posiciones válidas.")
        return

    total_vm = sub["Valor de Mercado Contravalorado"].sum()
    sub["peso_pct"] = (sub["Valor de Mercado Contravalorado"] / total_vm * 100).round(4)

    # DV01 como porcentaje del valor de cartera
    sub["dv01_pct"] = (sub["peso_pct"] / 100 * sub["Duración Modificada"] / 100).round(6)

    sub["oas_bps"] = sub["Rating SP de la Emisión"].apply(_oas_proxy)
    sub["sector"] = sub.apply(_sector_label, axis=1)

    # Formato de fecha
    sub["vencimiento"] = pd.to_datetime(
        sub["Fecha de Vencimiento"], errors="coerce"
    ).dt.strftime("%Y-%m-%d").fillna("N/D")

    rating_col = sub["Rating SP de la Emisión"].fillna(
        sub["Rating MISV de la Emisión"]
    ).fillna("NR")

    out = pd.DataFrame({
        "isin":               sub["ISIN de la Emisión"].values,
        "nombre_activo":      sub["Descripción de la Emisión"].values,
        "sector":             sub["sector"].values,
        "rating":             rating_col.values,
        "divisa":             sub["Divisa del activo N0"].values,
        "vencimiento":        sub["vencimiento"].values,
        "peso_pct":           sub["peso_pct"].values,
        "duracion_modificada":sub["Duración Modificada"].round(3).values,
        "dv01_pct":           sub["dv01_pct"].values,
        "ytm_pct":            (sub["TIR Mercado"] * 100).round(4).values,
        "oas_bps":            sub["oas_bps"].values,
        "vm_eur":             sub["Valor de Mercado Contravalorado"].round(0).values,
        "oas_fuente":         "proxy_rating",   # no Bloomberg real
    })

    out = out.sort_values("peso_pct", ascending=False).reset_index(drop=True)

    print(f"\nTop 5 posiciones:")
    print(out[["isin","nombre_activo","peso_pct","duracion_modificada","oas_bps"]].head(5).to_string(index=False))

    dur_media = float((out["peso_pct"] / out["peso_pct"].sum() * out["duracion_modificada"]).sum())
    oas_media = float((out["peso_pct"] / out["peso_pct"].sum() * out["oas_bps"]).sum())
    print(f"\nDuración media ponderada: {dur_media:.2f}")
    print(f"OAS medio ponderado:      {oas_media:.0f} pb  (proxy por rating)")
    print(f"VM total {FONDO} RF:      {total_vm/1e6:.1f} M EUR")
    print(f"Posiciones:               {len(out)}")

    out.to_csv(OUT_PATH, index=False)
    print(f"\nGuardado en {OUT_PATH}")


if __name__ == "__main__":
    run()
