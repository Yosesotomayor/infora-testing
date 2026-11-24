from demo.data import make_raw, PERSONAS
from demo.giros import GIROS

KEYS = {"persona", "monto", "cliente", "alerta", "comision"}


def test_giros_keys():
    assert set(GIROS) == {"Distribuidora", "Asesoría de seguros"}
    for cfg in GIROS.values():
        assert KEYS <= set(cfg)


def test_raw_is_deterministic():
    for giro in GIROS:
        assert make_raw(giro).equals(make_raw(giro))


def test_raw_has_mess():
    raw = make_raw("Distribuidora")
    assert raw["Importe"].astype(str).str.contains(r"\$").any()
    assert raw.isna().all(axis=1).sum() == 4
    assert raw.dropna(how="all").duplicated().sum() >= 5
    assert len(PERSONAS) == 8
