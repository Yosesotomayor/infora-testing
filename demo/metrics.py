"""Números del tablero."""

import pandas as pd


def _mes(df: pd.DataFrame, periodo: pd.Period, today: pd.Timestamp) -> pd.DataFrame:
    return df[(df["fecha"].dt.to_period("M") == periodo) & (df["fecha"] <= today)]


def alert_table(df: pd.DataFrame, giro: str, today: pd.Timestamp) -> pd.DataFrame:
    if giro == "Distribuidora":
        t = df[~df["pagado"] & (df["vence"] < today)].copy()
        t["dias_atraso"] = (today - t["vence"]).dt.days
        orden = "dias_atraso"
    else:
        t = df[(df["vence"] >= today) & (df["vence"] <= today + pd.Timedelta(days=30))].copy()
        t["dias_para_vencer"] = (t["vence"] - today).dt.days
        orden = "dias_para_vencer"
    cols = ["cliente", "persona", "producto", "monto", "vence", orden]
    return t[cols].sort_values(orden, ascending=(orden == "dias_para_vencer")).reset_index(drop=True)


def kpis(df: pd.DataFrame, giro: str, today: pd.Timestamp) -> dict:
    actual = today.to_period("M")
    cur = _mes(df, actual, today)["monto"].sum()
    # Mismo periodo del mes anterior (del 1 al mismo día), para comparar parejo.
    prev = _mes(df, actual - 1, today - pd.DateOffset(months=1))["monto"].sum()
    return {
        "mes_actual": float(cur),
        "mes_anterior": float(prev),
        "variacion_pct": float(round((cur / prev - 1) * 100, 1)) if prev else None,
        "por_cobrar": float(df.loc[~df["pagado"], "monto"].sum()),
        "alertas": len(alert_table(df, giro, today)),
    }


def ranking(df: pd.DataFrame, today: pd.Timestamp) -> pd.DataFrame:
    return (
        _mes(df, today.to_period("M"), today)
        .groupby("persona", as_index=False)["monto"].sum()
        .rename(columns={"monto": "total"})
        .sort_values("total", ascending=False)
        .reset_index(drop=True)
    )


def monthly(df: pd.DataFrame) -> pd.DataFrame:
    m = df.groupby(df["fecha"].dt.to_period("M"))["monto"].sum()
    return m.rename_axis("mes").reset_index()
