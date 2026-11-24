import numpy as np
import pandas as pd

from demo.forecast import forecast
from demo.metrics import alert_table, kpis, ranking

TODAY = pd.Timestamp("2026-11-24")
COLS = ["fecha", "persona", "cliente", "producto", "monto", "pagado", "vence"]


def _df(rows):
    return pd.DataFrame(rows, columns=COLS)


def test_kpis_and_ranking():
    df = _df([
        [pd.Timestamp("2026-11-02"), "A", "c", "x", 300.0, False, pd.Timestamp("2026-11-10")],
        [pd.Timestamp("2026-11-03"), "B", "c", "x", 100.0, True, pd.Timestamp("2026-12-10")],
        [pd.Timestamp("2026-10-03"), "B", "c", "x", 200.0, True, pd.Timestamp("2026-11-03")],
    ])
    k = kpis(df, "Distribuidora", TODAY)
    assert k["mes_actual"] == 400.0 and k["mes_anterior"] == 200.0
    assert k["variacion_pct"] == 100.0
    assert k["por_cobrar"] == 300.0 and k["alertas"] == 1
    r = ranking(df, TODAY)
    assert list(r["persona"]) == ["A", "B"]


def test_variacion_none_when_no_previous_month():
    df = _df([[pd.Timestamp("2026-11-02"), "A", "c", "x", 300.0, True, TODAY]])
    assert kpis(df, "Distribuidora", TODAY)["variacion_pct"] is None


def test_alert_tables():
    df = _df([
        [TODAY, "A", "c1", "Vida", 1.0, False, TODAY - pd.Timedelta(days=5)],
        [TODAY, "A", "c2", "Vida", 1.0, True, TODAY + pd.Timedelta(days=10)],
        [TODAY, "A", "c3", "Vida", 1.0, True, TODAY + pd.Timedelta(days=60)],
    ])
    dist = alert_table(df, "Distribuidora", TODAY)
    assert list(dist["cliente"]) == ["c1"] and dist.iloc[0]["dias_atraso"] == 5
    seg = alert_table(df, "Asesoría de seguros", TODAY)
    assert list(seg["cliente"]) == ["c2"] and seg.iloc[0]["dias_para_vencer"] == 10


def _monthly(values, end="2026-10"):
    months = pd.period_range(end=end, periods=len(values), freq="M")
    return _df([[m.to_timestamp() + pd.Timedelta(days=4), "A", "c", "x", float(v), True, TODAY] for m, v in zip(months, values)])


def test_forecast_linear():
    out = forecast(_monthly(range(100, 1300, 100)), TODAY, months=3)
    fut = out[out["pronostico"].notna()]
    assert len(fut) == 3
    assert np.isclose(fut.iloc[0]["pronostico"], 1300.0)
    assert np.isclose(fut.iloc[0]["alto"], fut.iloc[0]["bajo"])


def test_forecast_few_months_is_flat():
    out = forecast(_monthly([100, 300]), TODAY, months=3)
    fut = out[out["pronostico"].notna()]
    assert np.allclose(fut["pronostico"], 200.0)
