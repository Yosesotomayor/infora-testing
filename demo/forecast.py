"""Pronóstico sencillo y explicable: tendencia lineal de los últimos 12 meses."""

import numpy as np
import pandas as pd


def forecast(df: pd.DataFrame, today: pd.Timestamp, months: int = 3) -> pd.DataFrame:
    actual = today.to_period("M")
    m = df.groupby(df["fecha"].dt.to_period("M"))["monto"].sum()
    m = m[m.index < actual].sort_index().tail(12)
    y = m.to_numpy(dtype=float)
    if len(y) >= 3:
        x = np.arange(len(y))
        a, b = np.polyfit(x, y, 1)
        sd = float(np.std(y - (a * x + b)))
        fut = a * np.arange(len(y), len(y) + months) + b
    else:
        sd = 0.0
        fut = np.full(months, y.mean() if len(y) else 0.0)
    hist = pd.DataFrame({"mes": m.index, "real": y, "pronostico": np.nan, "bajo": np.nan, "alto": np.nan})
    futuro = pd.DataFrame({
        "mes": pd.period_range(start=actual, periods=months, freq="M"),
        "real": np.nan,
        "pronostico": fut,
        "bajo": np.maximum(fut - sd, 0),
        "alto": fut + sd,
    })
    return pd.concat([hist, futuro], ignore_index=True)
