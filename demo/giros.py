"""Textos y reglas de cada giro que maneja el demo."""

GIROS: dict[str, dict] = {
    "Distribuidora": {
        "persona": "Vendedor",
        "monto": "Venta",
        "cliente": "Cliente",
        "alerta": "Cobranza atrasada",
        "comision": {"default": 0.05},
        "pitch": "Ventas, comisiones y cobranza de tu equipo, sin armar reportes a mano.",
    },
    "Asesoría de seguros": {
        "persona": "Asesor",
        "monto": "Prima",
        "cliente": "Asegurado",
        "alerta": "Pólizas por vencer (30 días)",
        "comision": {"Vida": 0.30, "Gastos médicos": 0.15, "Autos": 0.10, "default": 0.10},
        "pitch": "Producción, comisiones y renovaciones de tus asesores en una sola pantalla.",
    },
}


def rate(giro: str, producto: str) -> float:
    tabla = GIROS[giro]["comision"]
    return tabla.get(producto, tabla["default"])
