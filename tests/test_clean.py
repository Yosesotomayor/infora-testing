import pandas as pd

from demo.clean import canonical_name, clean, parse_amount, parse_date
from demo.data import make_raw


def test_parse_amount_variants():
    for s in ["$12,500.00", "12500", " 12 500 ", 12500]:
        assert parse_amount(s) == 12500.0


def test_parse_date_variants():
    for s in ["03/11/2026", "2026-11-03", "3-nov-26"]:
        assert parse_date(s) == pd.Timestamp("2026-11-03")


def test_canonical_name_variants():
    assert canonical_name("JUAN PÉREZ") == canonical_name("juan perez ") == canonical_name("Juan Perez") == "Juan Pérez"


def test_clean_drops_dupes_and_blanks():
    for giro in ["Distribuidora", "Asesoría de seguros"]:
        raw = make_raw(giro)
        out = clean(raw)
        assert len(out) == len(raw) - 5 - 4
        assert out["persona"].nunique() == 8
        assert out["monto"].dtype == float
        assert pd.api.types.is_datetime64_any_dtype(out["fecha"])
