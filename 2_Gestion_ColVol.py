"""
MÓDULO 2: GESTIÓN DE COLVOL
-----------------------------
Catálogo simple de los ColVol a cargo del supervisor (5 a 15 según el brief).

¿Por qué este módulo? El Anexo 1 no identifica qué ColVol hizo la prueba como
campo explícito, pero el supervisor SÍ necesita saber qué colaborador reportó
qué, para fines de seguimiento y para que la data sirva a nivel distrital/
regional/nacional sin ambigüedad. Mantener este catálogo aparte evita que el
supervisor reescriba localidad/distrito/región cada vez que registra una
prueba (eso es trabajo duplicado y fuente de errores de transcripción).

Supuesto: un ColVol pertenece a una sola localidad, que a su vez pertenece a
un distrito, región y país. Esta jerarquía es la que permite los filtros del
Dashboard (Módulo 3).
"""

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestión de ColVol", layout="wide")

DATA_FILE = "colvol_catalogo.csv"
COLUMNS = ["nombre_colvol", "localidad", "distrito", "region", "pais", "activo"]

if "colvol" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.colvol = pd.read_csv(DATA_FILE)
    else:
        # Catálogo de ejemplo para que el módulo se pueda probar de inmediato
        st.session_state.colvol = pd.DataFrame([
            {"nombre_colvol": "Juana Pérez", "localidad": "San Martín", "distrito": "Distrito Norte",
             "region": "Región A", "pais": "País X", "activo": True},
            {"nombre_colvol": "Carlos Ríos", "localidad": "Las Palmas", "distrito": "Distrito Norte",
             "region": "Región A", "pais": "País X", "activo": True},
        ], columns=COLUMNS)

st.title("👥 Gestión de ColVol")
st.caption("Catálogo de los colaboradores voluntarios a tu cargo.")

with st.expander("➕ Agregar nuevo ColVol", expanded=False):
    with st.form("form_colvol", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del ColVol")
            localidad = st.text_input("Localidad")
        with col2:
            distrito = st.text_input("Distrito")
            region = st.text_input("Región")
        pais = st.text_input("País", value="País X")
        activo = st.checkbox("Activo", value=True)

        if st.form_submit_button("Guardar ColVol"):
            if not nombre:
                st.error("El nombre del ColVol es obligatorio.")
            else:
                nuevo = pd.DataFrame([{
                    "nombre_colvol": nombre, "localidad": localidad,
                    "distrito": distrito, "region": region, "pais": pais, "activo": activo
                }])
                st.session_state.colvol = pd.concat(
                    [st.session_state.colvol, nuevo], ignore_index=True
                )
                st.session_state.colvol.to_csv(DATA_FILE, index=False)
                st.success(f"{nombre} agregado al catálogo.")

st.divider()
st.subheader(f"ColVol a cargo ({len(st.session_state.colvol)})")
st.caption("Edita directamente en la tabla (por ejemplo, para desactivar un ColVol que dejó de participar).")

edited = st.data_editor(
    st.session_state.colvol,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    column_config={"activo": st.column_config.CheckboxColumn("Activo")}
)

if st.button("💾 Guardar cambios"):
    st.session_state.colvol = edited
    edited.to_csv(DATA_FILE, index=False)
    st.success("Catálogo actualizado.")

activos = st.session_state.colvol[st.session_state.colvol["activo"] == True]
st.metric("ColVol activos", len(activos))
if len(activos) > 15:
    st.warning("Tienes más de 15 ColVol activos — el rango esperado es de 5 a 15 por supervisor.")
