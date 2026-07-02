"""
MÓDULO 1: REGISTRO DE PRUEBAS DIAGNÓSTICAS
--------------------------------------------
Digitaliza el Anexo 1 (formato en papel que llenan los ColVol).
Diseñado para que el supervisor digite RAPIDO: campos mínimos,
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
COLVOL_FILE = "colvol_catalogo.csv"

COLUMNS = [
    "fecha_toma", "colvol", "localidad_residencia", "distrito", "region", "pais",
    "codigo_muestra", "motivo", "nombre_completo", "identificacion",
    "nacionalidad", "sexo", "fecha_nacimiento", "resultado_pdr",
    "tipo_busqueda", "tomo_medicamento", "medicamento_detalle"
]

PAISES = ["País X", "País Y", "País Z"]

# --- Carga del catálogo de ColVol ---
if os.path.exists(COLVOL_FILE):
    df_colvol = pd.read_csv(COLVOL_FILE)
    df_colvol = df_colvol[df_colvol["activo"] == True]
else:
    df_colvol = pd.DataFrame([
        {"nombre_colvol": "Juana Pérez", "localidad": "San Martín",
         "distrito": "Distrito Norte", "region": "Región A", "pais": "País X"},
        {"nombre_colvol": "Carlos Ríos", "localidad": "Las Palmas",
         "distrito": "Distrito Norte", "region": "Región A", "pais": "País X"},
    ])

# --- Carga de registros existentes ---
if "registros" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.registros = pd.read_csv(DATA_FILE)
    else:
        st.session_state.registros = pd.DataFrame(columns=COLUMNS)

st.title("📋 Registro de Pruebas Diagnósticas")
st.caption("Digitaliza el Anexo 1 que llenan los ColVol en papel.")

# --- Selector de ColVol FUERA del form para autorrelleno en tiempo real ---
nombres_colvol = ["— Selecciona un ColVol —"] + list(df_colvol["nombre_colvol"].values)
colvol_sel = st.selectbox("ColVol que realizó la prueba", nombres_colvol)

if colvol_sel != "— Selecciona un ColVol —":
    fila_colvol = df_colvol[df_colvol["nombre_colvol"] == colvol_sel].iloc[0]
    localidad_auto = fila_colvol["localidad"]
    distrito_auto  = fila_colvol["distrito"]
    region_auto    = fila_colvol["region"]
    pais_auto      = fila_colvol["pais"]
    st.info(f"📍 **{colvol_sel}** — {localidad_auto}, {distrito_auto}, {region_auto}, {pais_auto}")
else:
    localidad_auto = distrito_auto = region_auto = pais_auto = ""

st.divider()

with st.form("form_registro", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        fecha_toma     = st.date_input("Fecha de toma", value=date.today())
        codigo_muestra = st.text_input("Código de muestra")
        motivo         = st.selectbox("Motivo", ["Sospechoso", "Conviviente", "Seguimiento"])

    with col2:
        nombre         = st.text_input("Nombre completo del paciente")
        identificacion = st.text_input("Identificación")
        nacionalidad   = st.selectbox("Nacionalidad", PAISES)
        sexo           = st.selectbox("Sexo", ["Masculino", "Femenino"])
        fecha_nac      = st.date_input(
            "Fecha de nacimiento",
            value=date(2000, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )

    with col3:
        resultado_pdr = st.selectbox(
            "Resultado PDR",
            ["P.v (Plasmodium vivax)", "P.f (Plasmodium falciparum)", "Negativa", "Inválida"]
        )
        tipo_busqueda = st.selectbox("Tipo de búsqueda", ["Pasiva", "Proactiva", "Reactiva"])

    st.divider()
    tomo_medicamento   = st.radio(
        "¿Ha tomado algún medicamento?", ["No", "Sí"], horizontal=True
    )
    medicamento_detalle = st.text_input(
        "Anota cuál medicamento: (deja vacío si no aplica)"
    )

    submitted = st.form_submit_button("➕ Agregar registro", use_container_width=True)

    if submitted:
        errores = []
        if colvol_sel == "— Selecciona un ColVol —":
            errores.append("Debes seleccionar un ColVol.")
        if not nombre:
            errores.append("El nombre completo del paciente es obligatorio.")
        if not codigo_muestra:
            errores.append("El código de muestra es obligatorio.")
        if codigo_muestra and len(st.session_state.registros) > 0:
            if codigo_muestra in st.session_state.registros["codigo_muestra"].values:
                errores.append(f"⚠️ El código '{codigo_muestra}' ya fue registrado antes.")

        if errores:
            for e in errores:
                st.error(e)
        else:
            nuevo = pd.DataFrame([{
                "fecha_toma": fecha_toma,
                "colvol": colvol_sel,
                "localidad_residencia": localidad_auto,
                "distrito": distrito_auto,
                "region": region_auto,
                "pais": pais_auto,
                "codigo_muestra": codigo_muestra,
                "motivo": motivo,
                "nombre_completo": nombre,
                "identificacion": identificacion,
                "nacionalidad": nacionalidad,
                "sexo": sexo,
                "fecha_nacimiento": fecha_nac,
                "resultado_pdr": resultado_pdr,
                "tipo_busqueda": tipo_busqueda,
                "tomo_medicamento": tomo_medicamento,
                "medicamento_detalle": medicamento_detalle
            }])
            st.session_state.registros = pd.concat(
                [st.session_state.registros, nuevo], ignore_index=True
            )
            st.session_state.registros.to_csv(DATA_FILE, index=False)
            st.success(f"✅ Registro de {nombre} agregado correctamente.")

st.divider()
st.subheader(f"Registros digitados en esta sesión ({len(st.session_state.registros)})")

if len(st.session_state.registros) > 0:
    st.dataframe(st.session_state.registros, use_container_width=True, hide_index=True)

    positivos = st.session_state.registros[
        st.session_state.registros["resultado_pdr"].str.contains("P.v|P.f", na=False)
    ]
    if len(positivos) > 0:
        st.warning(
            f"⚠️ {len(positivos)} caso(s) positivo(s) en esta sesión. "
            f"Recuerda iniciar el primer tratamiento correspondiente."
        )

    csv = st.session_state.registros.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar registros (CSV)", csv, "registros_pruebas.csv", "text/csv"
    )
else:
    st.info("Aún no hay registros. Usa el formulario de arriba para agregar el primero.")