import io

import pandas as pd

from demo.report import commission_report, to_xlsx


def _df(rows):
    return pd.DataFrame(rows, columns=["fecha", "persona", "cliente", "producto", "monto", "pagado", "vence"])


NOV = pd.Period("2026-11", "M")


def test_distribuidora_commission():
    d = pd.Timestamp("2026-11-05")
    df = _df([[d, "Juan Pérez", "A", "X", 1000.0, True, d], [d, "Juan Pérez", "B", "X", 1000.0, True, d]])
    rep = commission_report(df, "Distribuidora", NOV)
    row = rep[rep["persona"] == "Juan Pérez"].iloc[0]
    assert row["operaciones"] == 2 and row["total"] == 2000.0 and row["comision"] == 100.0


def test_seguros_commission_and_total_row():
    d = pd.Timestamp("2026-11-05")
    df = _df([
        [d, "Juan Pérez", "A", "Vida", 1000.0, True, d],
        [d, "Juan Pérez", "B", "Autos", 1000.0, True, d],
        [d, "Ana Muñoz", "C", "Gastos médicos", 1000.0, True, d],
        [pd.Timestamp("2026-10-05"), "Ana Muñoz", "C", "Vida", 9999.0, True, d],
    ])
    rep = commission_report(df, "Asesoría de seguros", NOV)
    assert rep.iloc[0]["persona"] == "Juan Pérez"
    assert rep[rep["persona"] == "Juan Pérez"].iloc[0]["comision"] == 400.0
    total = rep.iloc[-1]
    assert total["persona"] == "TOTAL"
    assert total["total"] == 3000.0 and total["comision"] == 550.0


def test_xlsx_roundtrip_keeps_accents():
    df = pd.DataFrame({"persona": ["Juan Pérez", "Ana Muñoz"], "total": [1.0, 2.0]})
    back = pd.read_excel(io.BytesIO(to_xlsx({"Comisiones": df})), sheet_name="Comisiones")
    assert list(back["persona"]) == ["Juan Pérez", "Ana Muñoz"]
