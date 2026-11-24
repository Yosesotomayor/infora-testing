"""Limpieza: lo que Infora hace automáticamente con el Excel del cliente."""

import re
import unicodedata

import pandas as pd

from demo.data import MESES, PERSONAS


def _clave(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


_CANON = {_clave(p): p for p in PERSONAS}


def canonical_name(s) -> str:
    k = _clave(s)
    return _CANON.get(k, k.title())


def parse_amount(s) -> float:
    if isinstance(s, (int, float)):
        return float(s)
    return float(re.sub(r"[\s$,]", "", str(s)))


def parse_date(s) -> pd.Timestamp:
    if isinstance(s, pd.Timestamp):
        return s
    s = str(s).strip().lower()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return pd.Timestamp(s)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        d, mo, y = map(int, m.groups())
        return pd.Timestamp(year=y, month=mo, day=d)
    m = re.fullmatch(r"(\d{1,2})-([a-z]{3})-(\d{2})", s)
    if m:
        d, mes, y = m.groups()
        return pd.Timestamp(year=2000 + int(y), month=MESES.index(mes) + 1, day=int(d))
    raise ValueError(f"Fecha no reconocida: {s!r}")


def _pagado(s) -> bool:
    s = _clave(s) if isinstance(s, str) else ""
    return s.startswith("s") or s == "x"


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.dropna(how="all").drop_duplicates().copy()
    df.columns = [c.strip() for c in df.columns]
    return pd.DataFrame({
        "fecha": df["FECHA"].map(parse_date).astype("datetime64[ns]"),
        "persona": df["Vendedor/Agente"].map(canonical_name),
        "cliente": df["Cliente"].str.strip(),
        "producto": df["Producto"].str.strip(),
        "monto": df["Importe"].map(parse_amount).astype(float),
        "pagado": df["Pagado?"].map(_pagado),
        "vence": df["Vence"].map(parse_date).astype("datetime64[ns]"),
    }).sort_values("fecha").reset_index(drop=True)
