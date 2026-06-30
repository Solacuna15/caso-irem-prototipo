"""
MÓDULO 1: REGISTRO DE PRUEBAS DIAGNÓSTICAS
--------------------------------------------
Digitaliza el Anexo 1 (formato en papel que llenan los ColVol).
Diseñado para que el supervisor digite RÁPIDO: campos mínimos,
listas desplegables en vez de texto libre, valores por defecto
inteligentes (la fecha de hoy, por ejemplo).

Supuesto: el supervisor digita por lotes (varios formatos seguidos)
al llegar a la oficina, no uno por uno en distintos momentos del día.
Por eso el diseño prioriza una tabla acumulativa en pantalla, para
que vea su avance y pueda detectar duplicados o errores antes de guardar.
"""

import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Registro de Pruebas - ColVol", layout="wide")

DATA_FILE = "registros_pruebas.csv"

COLUMNS = [
    "fecha_toma", "localidad_residencia", "codigo_muestra", "motivo",
    "nombre_completo", "identificacion", "nacionalidad", "sexo",
    "fecha_nacimiento", "resultado_pdr", "tipo_busqueda", "tomo_medicamento",
    "medicamento_detalle"
]

# --- Carga de datos existentes (simula la "base" local del supervisor) ---
if "registros" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.registros = pd.read_csv(DATA_FILE)
    else:
        st.session_state.registros = pd.DataFrame(columns=COLUMNS)

st.title("📋 Registro de Pruebas Diagnósticas")
st.caption("Digitaliza el Anexo 1 que llenan los ColVol en papel.")

with st.form("form_registro", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        fecha_toma = st.date_input("Fecha de toma", value=date.today())
        localidad = st.text_input("Localidad de residencia")
        codigo_muestra = st.text_input("Código de muestra")
        motivo = st.selectbox("Motivo", ["Sospechoso", "Conviviente", "Seguimiento"])

    with col2:
        nombre = st.text_input("Nombre completo")
        identificacion = st.text_input("Identificación")
        nacionalidad = st.text_input("Nacionalidad")
        sexo = st.selectbox("Sexo", ["M", "H"])
        fecha_nac = st.date_input("Fecha de nacimiento", value=date(2000, 1, 1),
                                   min_value=date(1900, 1, 1), max_value=date.today())

    with col3:
        resultado_pdr = st.selectbox(
            "Resultado PDR",
            ["P.v (Plasmodium vivax)", "P.f (Plasmodium falciparum)", "Negativa", "Inválida"]
        )
        tipo_busqueda = st.selectbox("Tipo de búsqueda", ["Pasiva", "Proactiva", "Reactiva"])
        tomo_medicamento = st.radio("¿Ha tomado algún medicamento?", ["No", "Sí"], horizontal=True)
        medicamento_detalle = ""
        if tomo_medicamento == "Sí":
            medicamento_detalle = st.text_input("¿Cuál medicamento?")

    submitted = st.form_submit_button("➕ Agregar registro", use_container_width=True)

    if submitted:
        if not nombre or not codigo_muestra:
            st.error("Nombre completo y Código de muestra son obligatorios.")
        else:
            nuevo = pd.DataFrame([{
                "fecha_toma": fecha_toma, "localidad_residencia": localidad,
                "codigo_muestra": codigo_muestra, "motivo": motivo,
                "nombre_completo": nombre, "identificacion": identificacion,
                "nacionalidad": nacionalidad, "sexo": sexo,
                "fecha_nacimiento": fecha_nac, "resultado_pdr": resultado_pdr,
                "tipo_busqueda": tipo_busqueda, "tomo_medicamento": tomo_medicamento,
                "medicamento_detalle": medicamento_detalle
            }])
            st.session_state.registros = pd.concat(
                [st.session_state.registros, nuevo], ignore_index=True
            )
            st.session_state.registros.to_csv(DATA_FILE, index=False)
            st.success(f"Registro de {nombre} agregado correctamente.")

st.divider()
st.subheader(f"Registros digitados en esta sesión ({len(st.session_state.registros)})")

if len(st.session_state.registros) > 0:
    st.dataframe(st.session_state.registros, use_container_width=True, hide_index=True)

    # Alerta simple: casos positivos requieren acción del supervisor (inicio de tratamiento)
    positivos = st.session_state.registros[
        st.session_state.registros["resultado_pdr"].str.contains("P.v|P.f", na=False)
    ]
    if len(positivos) > 0:
        st.warning(f"⚠️ {len(positivos)} caso(s) positivo(s) en esta sesión. "
                   f"Recuerda iniciar el primer tratamiento correspondiente.")

    csv = st.session_state.registros.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar registros (CSV)", csv, "registros_pruebas.csv", "text/csv")
else:
    st.info("Aún no hay registros. Usa el formulario de arriba para agregar el primero.")
