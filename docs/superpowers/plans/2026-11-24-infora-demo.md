# Infora Demo App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Streamlit demo that shows a prospect "tu Excel hoy → lo que te entrega Infora" for two giros (Distribuidora, Asesoría de seguros).

**Architecture:** Pure-pandas modules (data, cleaning, report, metrics, forecast) driven by a per-giro config dict; a thin `app.py` renders four tabs. Synthetic data uses a fixed seed so every run looks the same.

**Tech Stack:** Python 3.11, pandas, numpy, openpyxl, streamlit, plotly, pytest.

**Spec:** `docs/2026-11-24-demo-design.md`

## Global Constraints

- All UI text in Spanish; app title "Infora · Demo"; footer "infora.mx · WhatsApp 55 1443 9029".
- Giros exactly: "Distribuidora", "Asesoría de seguros".
- Tab order exactly: "1. Antes", "2. Reporte automático", "3. Tablero", "4. Pronóstico".
- Fixed seed 42; "today" for the demo is a parameter, default `pd.Timestamp("2026-11-24")`.
- Money shown as `$1,234,567` MXN (no decimals).
- No login, no external services; deployable on Streamlit Cloud with `requirements.txt` only.

## Review Focus

- Messy amounts like `"$12,500.00"`, `"12500"`, `" 12 500 "` must all parse to 12500.0.
- Mixed date formats (`"03/11/2026"`, `"2026-11-03"`, `"3-nov-26"`) must parse day-first to 2026-11-03.
- Name variants (`"juan pérez "`, `"Juan Perez"`, `"JUAN PÉREZ"`) must collapse to one person `"Juan Pérez"`.
- Exact duplicate rows and blank rows in the raw sheet must be dropped, not double-counted.
- The downloaded .xlsx must reopen with pandas and keep accents (é, ñ) intact.

---

### Task 1: Giro config + synthetic messy data

**Files:**
- Create: `demo/__init__.py`, `demo/giros.py`, `demo/data.py`, `requirements.txt`
- Test: `tests/test_data.py`

**Interfaces:**
- Produces: `GIROS: dict[str, dict]` with keys per giro: `persona` ("Vendedor"/"Asesor"), `monto` ("Venta"/"Prima"), `cliente` ("Cliente"/"Asegurado"), `alerta` ("Cobranza atrasada"/"Pólizas por vencer (30 días)"), `comision: dict[str, float]` (Distribuidora: `{"default": 0.05}`; Seguros: `{"Vida": 0.30, "Gastos médicos": 0.15, "Autos": 0.10}`).
- Produces: `PERSONAS: list[str]` — 8 canonical names with accents (e.g. "Juan Pérez", "Ana Muñoz").
- Produces: `make_raw(giro: str, seed: int = 42, today: pd.Timestamp = ...) -> pd.DataFrame` — 18 months of rows, 8 personas, columns with messy headers (`"FECHA "`, `"Vendedor/Agente"`, `"Importe"`, `"Cliente"`, `"Producto"`, `"Pagado?"`, `"Vence"`), injected: 3 name variants per persona, mixed date formats, string amounts with `$`/commas, 5 exact duplicates, 4 blank rows.

- [ ] **Step 1: Write failing tests** — `test_raw_is_deterministic` (two calls equal), `test_raw_has_mess` (contains a `"$"` amount, a blank row, ≥5 duplicated rows), `test_giros_keys` (both giros have all keys above).
- [ ] **Step 2:** `pytest tests/test_data.py -v` → FAIL (import error).
- [ ] **Step 3:** Implement `GIROS` and `make_raw` with `numpy.random.default_rng(seed)`; Seguros `Producto` ∈ the three ramos and `Vence` = fecha + 1 year; Distribuidora `Vence` = fecha + 30 days.
- [ ] **Step 4:** `pytest tests/test_data.py -v` → PASS.
- [ ] **Step 5:** `git commit -m "feat: giro config and synthetic messy data"`

### Task 2: Cleaning

**Files:** Create `demo/clean.py`; Test `tests/test_clean.py`

**Interfaces:**
- Consumes: `make_raw`.
- Produces: `clean(raw: pd.DataFrame) -> pd.DataFrame` with columns `fecha (datetime64)`, `persona (str)`, `cliente`, `producto`, `monto (float)`, `pagado (bool)`, `vence (datetime64)`; helpers `parse_amount(s) -> float`, `parse_date(s) -> pd.Timestamp`, `canonical_name(s) -> str`.

- [ ] **Step 1: Write failing tests** — the five Review Focus cases as asserts (e.g. `parse_amount("$12,500.00") == 12500.0`, `parse_date("3-nov-26") == pd.Timestamp("2026-11-03")`, `canonical_name("JUAN PÉREZ") == canonical_name("juan perez ") == "Juan Pérez"`), plus `test_clean_drops_dupes_and_blanks` (`len(clean(raw)) == len(raw) - 5 - 4`).
- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3:** Implement. `canonical_name`: match accent-stripped, lowercased, trimmed key against the canonical list from `GIROS`-independent `PERSONAS` in `data.py`; `parse_date`: try ISO, then `dayfirst=True`, then Spanish month abbreviations map.
- [ ] **Step 4:** run → PASS. **Step 5:** commit `feat: cleaning`.

### Task 3: Commission report + xlsx export

**Files:** Create `demo/report.py`; Test `tests/test_report.py`

**Interfaces:**
- Consumes: `clean`, `GIROS`.
- Produces: `commission_report(df, giro: str, month: pd.Period) -> pd.DataFrame` columns `[persona, operaciones, total, comision]` sorted by `total` desc, plus a final `"TOTAL"` row; `to_xlsx(sheets: dict[str, pd.DataFrame]) -> bytes`.

- [ ] **Step 1: Failing tests** — tiny hand-made df: Distribuidora 2 sales of 1000 → comision 100.0; Seguros Vida 1000 + Autos 1000 → 400.0; TOTAL row equals column sums; `pd.read_excel(io.BytesIO(to_xlsx({"Comisiones": df})))` round-trips `"Pérez"`.
- [ ] **Step 2:** FAIL. **Step 3:** implement (openpyxl engine, header bold, money format `$#,##0`). **Step 4:** PASS. **Step 5:** commit.

### Task 4: Dashboard metrics

**Files:** Create `demo/metrics.py`; Test `tests/test_metrics.py`

**Interfaces:**
- Produces: `kpis(df, today) -> dict` keys `mes_actual`, `mes_anterior`, `variacion_pct`, `por_cobrar`, `alertas`; `ranking(df, today) -> pd.DataFrame [persona, total]` for current month; `alert_table(df, giro, today) -> pd.DataFrame` — Distribuidora: unpaid with `vence < today`, column `dias_atraso`; Seguros: `today <= vence <= today+30d`, column `dias_para_vencer`.

- [ ] **Step 1: Failing tests** on a hand-made df with known answers for each function (including `variacion_pct` when previous month is 0 → `None`, not an exception).
- [ ] **Step 2–4:** FAIL → implement → PASS. **Step 5:** commit.

### Task 5: Forecast

**Files:** Create `demo/forecast.py`; Test `tests/test_forecast.py`

**Interfaces:**
- Produces: `forecast(df, today, months: int = 3) -> pd.DataFrame [mes (Period), real (float|NaN), pronostico (float|NaN), bajo, alto]` — history rows have `real`, future rows have `pronostico/bajo/alto`.
- Method: monthly totals of complete months; linear trend via `numpy.polyfit(deg=1)` on the last 12; band = ±1 std of residuals. Fewer than 3 months → flat mean, band 0.

- [ ] **Step 1: Failing tests** — perfectly linear history 100,200,…,1200 → next month 1300 ± 0; history of 2 months → flat mean; output has exactly `months` future rows.
- [ ] **Step 2–4:** FAIL → implement → PASS. **Step 5:** commit.

### Task 6: Streamlit app + deploy files

**Files:** Create `app.py`, `.streamlit/config.toml` (theme: primary `#1E3A5F`, base light), `README.md` (deploy steps for Streamlit Cloud).

**Interfaces:** Consumes everything above.

- Sidebar: giro radio, short pitch line, footer contact.
- Tab 1: `st.dataframe(raw.head(40))` + caption "Así llega hoy: nombres repetidos, fechas mezcladas, importes como texto." + download raw .xlsx.
- Tab 2: month select, button "Generar reporte" → spinner, report table, download button "reporte_comisiones.xlsx", caption with row counts cleaned.
- Tab 3: 4 `st.metric` (MXN format), plotly bar ranking, monthly line, alert table.
- Tab 4: plotly line real vs. pronóstico with shaded band, one-sentence explanation.
- [ ] **Step 1:** `streamlit run app.py` locally; check every tab for both giros; check width 390px (phone).
- [ ] **Step 2:** `pytest -q` → all PASS.
- [ ] **Step 3:** commit `feat: streamlit demo app`.
