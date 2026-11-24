"""Infora · Demo — tu Excel de hoy vs. lo que te entrega Infora."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from demo.clean import clean
from demo.data import TODAY, make_raw
from demo.forecast import forecast
from demo.giros import GIROS
from demo.metrics import alert_table, kpis, monthly, ranking
from demo.report import commission_report, to_xlsx

AZUL = "#1E3A5F"
VERDE = "#2E8B57"
MESES_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

st.set_page_config(page_title="Infora · Demo", page_icon="📊", layout="wide")


def dinero(x: float) -> str:
    return f"${x:,.0f}"


def mes_es(p: pd.Period) -> str:
    return f"{MESES_ES[p.month - 1]} {p.year}"


@st.cache_data
def cargar(giro: str):
    raw = make_raw(giro)
    return raw, clean(raw)


with st.sidebar:
    st.markdown("## Infora")
    giro = st.radio("Tipo de negocio", list(GIROS))
    cfg = GIROS[giro]
    st.caption(cfg["pitch"])
    st.divider()
    st.caption("Datos ficticios para demostración.")
    st.caption("infora.mx · WhatsApp 55 1443 9029")

raw, df = cargar(giro)
P, M, C = cfg["persona"], cfg["monto"], cfg["cliente"]

st.title("Infora · Demo")
st.caption(f"{giro} · corte al {TODAY.day} de {MESES_ES[TODAY.month - 1]} de {TODAY.year}")

t1, t2, t3, t4 = st.tabs(["1. Antes", "2. Reporte automático", "3. Tablero", "4. Pronóstico"])

with t1:
    st.subheader("Así llega hoy tu información")
    st.write(
        "Nombres escritos de varias formas, fechas mezcladas, importes como texto, "
        "renglones duplicados y vacíos. Alguien pasa horas limpiándolo cada mes."
    )
    st.dataframe(raw.head(40), width="stretch", hide_index=True)
    st.download_button(
        "Descargar Excel original", to_xlsx({"Operaciones": raw}),
        "excel_original.xlsx", width="stretch",
    )

with t2:
    st.subheader("Reporte de comisiones en segundos")
    meses = sorted(df["fecha"].dt.to_period("M").unique(), reverse=True)
    mes = st.selectbox("Mes", meses, index=1, format_func=mes_es)
    if st.button("Generar reporte", type="primary", width="stretch"):
        with st.spinner("Limpiando y calculando..."):
            rep = commission_report(df, giro, mes)
        st.success(
            f"Listo: {len(raw):,} renglones revisados, {len(raw) - len(df)} duplicados o vacíos "
            f"eliminados y {raw['Vendedor/Agente'].nunique()} formas de escribir nombres unificadas "
            f"en {df['persona'].nunique()} {P.lower()}es."
        )
        vista = rep.rename(columns={"persona": P, "operaciones": "Operaciones", "total": M, "comision": "Comisión"})
        st.dataframe(
            vista.style.format({M: dinero, "Comisión": dinero}),
            width="stretch", hide_index=True,
        )
        st.download_button(
            "Descargar reporte en Excel", to_xlsx({"Comisiones": vista}),
            f"comisiones_{mes}.xlsx", width="stretch",
        )

with t3:
    k = kpis(df, giro, TODAY)
    a, b = st.columns(2)
    var = f"{k['variacion_pct']:+.1f}% vs. mismo corte del mes pasado" if k["variacion_pct"] is not None else None
    a.metric(f"{M}s del mes", dinero(k["mes_actual"]), var)
    b.metric(f"{'Por cobrar' if giro == 'Distribuidora' else 'Primas por cobrar'}", dinero(k["por_cobrar"]))
    c, d = st.columns(2)
    c.metric(cfg["alerta"], k["alertas"])
    c2 = ranking(df, TODAY)
    d.metric(f"Mejor {P.lower()} del mes", c2.iloc[0]["persona"] if len(c2) else "—")

    st.markdown(f"**{M}s por {P.lower()} (mes actual)**")
    fig = go.Figure(go.Bar(x=c2["total"], y=c2["persona"], orientation="h", marker_color=AZUL,
                           text=[dinero(v) for v in c2["total"]], textposition="auto"))
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, width="stretch")

    st.markdown(f"**{M}s por mes (meses cerrados)**")
    mm = monthly(df)
    mm = mm[mm["mes"] < TODAY.to_period("M")]
    fig = go.Figure(go.Scatter(x=[mes_es(p) for p in mm["mes"]], y=mm["monto"], mode="lines+markers",
                               line=dict(color=AZUL, width=3)))
    fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width="stretch")

    st.markdown(f"**{cfg['alerta']}**")
    al = alert_table(df, giro, TODAY).rename(columns={
        "cliente": C, "persona": P, "producto": "Producto", "monto": M, "vence": "Vence",
        "dias_atraso": "Días de atraso", "dias_para_vencer": "Días para vencer",
    })
    st.dataframe(al.style.format({M: dinero, "Vence": lambda x: x.strftime("%d/%m/%Y")}),
                 width="stretch", hide_index=True)

with t4:
    st.subheader(f"{M}s de los próximos 3 meses")
    fc = forecast(df, TODAY)
    hist, fut = fc[fc["real"].notna()], fc[fc["pronostico"].notna()]
    x_h, x_f = [mes_es(p) for p in hist["mes"]], [mes_es(p) for p in fut["mes"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_f + x_f[::-1], y=list(fut["alto"]) + list(fut["bajo"])[::-1],
                             fill="toself", fillcolor="rgba(46,139,87,0.18)", line=dict(width=0), mode="lines",
                             name="Rango probable", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=x_h, y=hist["real"], mode="lines+markers", name="Real",
                             line=dict(color=AZUL, width=3)))
    fig.add_trace(go.Scatter(x=[x_h[-1]] + x_f, y=[hist["real"].iloc[-1]] + list(fut["pronostico"]),
                             mode="lines+markers", name="Pronóstico", line=dict(color=VERDE, width=3, dash="dash")))
    fig.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.2),
                      xaxis=dict(categoryorder="array", categoryarray=x_h + x_f))
    st.plotly_chart(fig, width="stretch")
    cols = st.columns(len(fut))
    for col, (_, r) in zip(cols, fut.iterrows()):
        col.metric(mes_es(r["mes"]), dinero(r["pronostico"]))
        col.caption(f"Entre {dinero(r['bajo'])} y {dinero(r['alto'])}")
    st.caption(
        "Se calcula con la tendencia de tus últimos 12 meses. El rango sombreado muestra "
        "qué tanto puede variar, para que planees con un escenario bajo y uno alto."
    )

st.divider()
st.caption("¿Quieres verlo con tus datos? Escríbenos: WhatsApp 55 1443 9029 · infora.mx")
