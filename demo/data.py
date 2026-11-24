"""Datos ficticios con los errores típicos de un Excel hecho a mano."""

import numpy as np
import pandas as pd

TODAY = pd.Timestamp("2026-11-24")
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

PERSONAS = [
    "Juan Pérez", "Ana Muñoz", "Luis Hernández", "María González",
    "Jorge Ramírez", "Sofía Martínez", "Ricardo Núñez", "Lucía Ortiz",
]
PESOS = [0.2, 0.17, 0.15, 0.13, 0.11, 0.1, 0.08, 0.06]

CLIENTES_DIST = [
    "Abarrotes La Esperanza", "Ferretería El Clavo", "Comercial Sánchez", "Minisúper Doña Lupe",
    "Papelería Central", "Tienda La Güera", "Distribuidora Norte", "Farmacia San Rafael",
    "Abarrotes El Sol", "Cremería Los Pinos", "Ferremateriales Ruiz", "Vinos y Licores Toño",
    "Tlapalería La Única", "Super Express Roma", "Comercializadora Vega", "Miscelánea Carmelita",
]
CLIENTES_SEG = [
    "Roberto Aguilar", "Patricia Lozano", "Fernando Cruz", "Gabriela Reyes", "Arturo Mendoza",
    "Claudia Navarro", "Héctor Salinas", "Verónica Ibarra", "Eduardo Rivas", "Mónica Castañeda",
    "Alejandro Fuentes", "Daniela Peña", "Sergio Campos", "Adriana Villalobos", "Raúl Delgado",
    "Silvia Cortés", "Manuel Escobar", "Laura Pacheco", "Óscar Medina", "Teresa Rangel",
]
RAMOS = {"Vida": (20_000, 0.5), "Gastos médicos": (35_000, 0.4), "Autos": (11_000, 0.3)}
PRODUCTOS_DIST = ["Abarrotes", "Bebidas", "Limpieza", "Botanas"]

COLUMNAS = ["FECHA ", "Vendedor/Agente", "Cliente", "Producto", "Importe", "Pagado?", "Vence"]


def _sin_acentos(s: str) -> str:
    return s.translate(str.maketrans("áéíóúñÁÉÍÓÚÑ", "aeiounAEIOUN"))


def _nombre_feo(nombre: str, rng) -> str:
    opciones = [nombre, nombre.upper(), nombre.lower() + " ", _sin_acentos(nombre)]
    return opciones[rng.integers(len(opciones))]


def _fecha_fea(f: pd.Timestamp, rng) -> str:
    k = rng.integers(3)
    if k == 0:
        return f.strftime("%Y-%m-%d")
    if k == 1:
        return f.strftime("%d/%m/%Y")
    return f"{f.day}-{MESES[f.month - 1]}-{f.strftime('%y')}"


def _importe_feo(x: float, rng) -> str:
    k = rng.integers(3)
    if k == 0:
        return f"${x:,.2f}"
    if k == 1:
        return f"{x:.0f}"
    return " " + f"{x:,.0f}".replace(",", " ") + " "


def make_raw(giro: str, seed: int = 42, today: pd.Timestamp = TODAY) -> pd.DataFrame:
    """Hoja 'como llega hoy': 18 meses de operaciones con errores de captura."""
    rng = np.random.default_rng(seed)
    meses = pd.period_range(end=today.to_period("M"), periods=18, freq="M")
    filas = []
    for i, mes in enumerate(meses):
        estacional = 1.25 if mes.month == 12 else (0.9 if mes.month in (1, 2) else 1.0)
        n = int(45 * (1 + 0.025 * i) * estacional)
        ultimo = min(mes.days_in_month, today.day) if mes == today.to_period("M") else mes.days_in_month
        if mes == today.to_period("M"):
            n = int(n * ultimo / mes.days_in_month)
        for _ in range(n):
            fecha = mes.to_timestamp() + pd.Timedelta(days=int(rng.integers(ultimo)))
            persona = PERSONAS[rng.choice(len(PERSONAS), p=PESOS)]
            if giro == "Distribuidora":
                cliente = CLIENTES_DIST[rng.integers(len(CLIENTES_DIST))]
                producto = PRODUCTOS_DIST[rng.integers(len(PRODUCTOS_DIST))]
                monto = round(float(rng.lognormal(np.log(15_000), 0.5)), -1)
                vence = fecha + pd.Timedelta(days=30)
                dias = (today - fecha).days
                pagado = rng.random() < (0.97 if dias > 75 else 0.75 if dias > 30 else 0.35)
            else:
                cliente = CLIENTES_SEG[rng.integers(len(CLIENTES_SEG))]
                producto = list(RAMOS)[rng.integers(len(RAMOS))]
                base, sigma = RAMOS[producto]
                monto = round(float(rng.lognormal(np.log(base), sigma)), -1)
                vence = fecha + pd.DateOffset(years=1)
                pagado = rng.random() < (0.97 if (today - fecha).days > 30 else 0.7)
            filas.append([
                _fecha_fea(fecha, rng), _nombre_feo(persona, rng), cliente, producto,
                _importe_feo(monto, rng), ["Sí", "si", "x"][rng.integers(3)] if pagado else ["NO", "no", ""][rng.integers(3)],
                _fecha_fea(vence, rng),
            ])
    raw = pd.DataFrame(filas, columns=COLUMNAS)
    dupes = raw.sample(5, random_state=seed)
    raw = pd.concat([raw, dupes], ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)
    blancos = pd.DataFrame([[np.nan] * len(COLUMNAS)] * 4, columns=COLUMNAS)
    for pos in sorted(rng.choice(len(raw), 4, replace=False), reverse=True):
        raw = pd.concat([raw.iloc[:pos], blancos.iloc[[0]], raw.iloc[pos:]], ignore_index=True)
    return raw
