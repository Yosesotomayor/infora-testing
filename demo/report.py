"""Reporte de comisiones y exportación a Excel."""

import io

import pandas as pd
from openpyxl.styles import Font

from demo.giros import rate

DINERO = {"total", "comision", "monto", "Total", "Comisión", "Venta", "Prima"}


def commission_report(df: pd.DataFrame, giro: str, month: pd.Period) -> pd.DataFrame:
    mes = df[df["fecha"].dt.to_period("M") == month].copy()
    mes["comision"] = mes["monto"] * mes["producto"].map(lambda p: rate(giro, p))
    rep = (
        mes.groupby("persona")
        .agg(operaciones=("monto", "size"), total=("monto", "sum"), comision=("comision", "sum"))
        .reset_index()
        .sort_values("total", ascending=False)
    )
    rep["comision"] = rep["comision"].round(2)
    total = pd.DataFrame([{
        "persona": "TOTAL",
        "operaciones": rep["operaciones"].sum(),
        "total": rep["total"].sum(),
        "comision": round(rep["comision"].sum(), 2),
    }])
    return pd.concat([rep, total], ignore_index=True)


def to_xlsx(sheets: dict[str, pd.DataFrame]) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        for nombre, df in sheets.items():
            df.to_excel(xw, sheet_name=nombre, index=False)
            ws = xw.sheets[nombre]
            for j, col in enumerate(df.columns, start=1):
                ws.cell(1, j).font = Font(bold=True)
                ws.column_dimensions[ws.cell(1, j).column_letter].width = max(14, len(str(col)) + 4)
                if col in DINERO:
                    for i in range(2, len(df) + 2):
                        ws.cell(i, j).number_format = "$#,##0"
    return buf.getvalue()
