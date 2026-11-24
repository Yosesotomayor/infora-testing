# Infora · Demo

App de demostración para prospectos: "tu Excel de hoy" vs. lo que entrega Infora.
Dos giros (Distribuidora y Asesoría de seguros) y cuatro pestañas: Antes, Reporte automático, Tablero y Pronóstico.
Todos los datos son ficticios (semilla fija).

## Correr local
```bash
pip install -r requirements.txt
streamlit run app.py
pytest -q   # pruebas (requiere pytest)
```

## Publicar en Streamlit Cloud
1. Entra a https://share.streamlit.io con tu cuenta de GitHub.
2. **Create app** → repo `Yosesotomayor/infora-testing`, rama `main`, archivo `app.py`.
3. En *Advanced settings* elige Python 3.11 o superior y dale **Deploy**.
