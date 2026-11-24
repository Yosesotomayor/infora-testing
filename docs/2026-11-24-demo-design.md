# Infora demo app — short design (approved 2026-11-24)

**Intent:** show prospects in ~5 min "your Excel today vs. what Infora gives you". Wed 25 Nov 17:00 (contadoras, distribuidora) and Fri 27 Nov 12:00 (InverVÁ, asesoría de seguros).

**Approaches considered:** (1) one Streamlit app with a "giro" selector — picked: one deploy, shared code, shows versatility; (2) two separate apps — duplicated work; (3) Power BI — only shows a dashboard, not the automation, and sharing needs licenses.

**Design:**
- Streamlit, Spanish UI, Infora branding. Sidebar selector: Distribuidora / Asesoría de seguros.
- Tabs: Antes (messy Excel preview + download) → Reporte automático (button generates commissions report per vendedor/asesor, .xlsx download) → Tablero (KPIs, ranking, cobranza atrasada / pólizas por vencer, mobile-friendly) → Pronóstico (next 3 months flujo / primas).
- Synthetic data with pandas, fixed seed.
- Deploy: GitHub repo → Streamlit Cloud.
- Non-goals: AlvaManager (shown separately), real integrations, login.
- Builder's calls: chart library, exact column names, forecast method (simple, explainable).
