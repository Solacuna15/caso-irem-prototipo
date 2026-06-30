"""
MÓDULO 3: DASHBOARD DE VIGILANCIA
------------------------------------
Convierte los registros digitados (Módulo 1) en información útil para tomar
decisiones a nivel local (el propio supervisor), regional y nacional.

Este módulo usa DATOS SIMULADOS para que se pueda abrir y probar de forma
100% independiente, sin depender de que existan registros previos de los
otros módulos (tal como pide el brief). En producción, este dashboard se
alimentaría de la base consolidada nacional (suma de todos los supervisores),
no solo de la sesión de un supervisor individual.

Supuesto de diseño: el supervisor necesita ver SU propio desempeño/avance,
pero los niveles regional y nacional necesitan agregados comparables entre
distritos. Por eso el filtro va de lo general (país) a lo específico
(distrito), permitiendo "drill-down".
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta

st.set_page_config(page_title="Dashboard de Vigilancia", layout="wide")

# --- Generación de datos simulados ---
@st.cache_data
def generar_datos_simulados(n=400, seed=42):
    rng = np.random.default_rng(seed)

    regiones_distritos = {
        "Región A": ["Distrito Norte", "Distrito Sur"],
        "Región B": ["Distrito Centro", "Distrito Este"],
        "Región C": ["Distrito Oeste"],
    }

    filas = []
    for _ in range(n):
        region = rng.choice(list(regiones_distritos.keys()))
        distrito = rng.choice(regiones_distritos[region])
        fecha = date.today() - timedelta(days=int(rng.integers(0, 60)))
        resultado = rng.choice(
            ["P.v", "P.f", "Negativa", "Inválida"],
            p=[0.12, 0.08, 0.75, 0.05]
        )
        tipo_busqueda = rng.choice(["Pasiva", "Proactiva", "Reactiva"], p=[0.5, 0.3, 0.2])
        filas.append({
            "pais": "País X",
            "region": region,
            "distrito": distrito,
            "fecha_toma": fecha,
            "resultado_pdr": resultado,
            "tipo_busqueda": tipo_busqueda,
        })
    return pd.DataFrame(filas)

df = generar_datos_simulados()

st.title("📊 Dashboard de Vigilancia de Malaria")
st.caption("Datos simulados para fines de prototipo — en producción se alimentaría de la base nacional consolidada.")

# --- Filtros jerárquicos: país > región > distrito ---
col_f1, col_f2, col_f3, col_f4 = st.columns(4)
with col_f1:
    regiones_sel = st.multiselect("Región", sorted(df["region"].unique()), default=list(df["region"].unique()))
with col_f2:
    distritos_disponibles = sorted(df[df["region"].isin(regiones_sel)]["distrito"].unique())
    distritos_sel = st.multiselect("Distrito", distritos_disponibles, default=distritos_disponibles)
with col_f3:
    rango_fechas = st.date_input(
        "Rango de fechas",
        value=(date.today() - timedelta(days=30), date.today())
    )
with col_f4:
    tipo_sel = st.multiselect("Tipo de búsqueda", sorted(df["tipo_busqueda"].unique()),
                               default=list(df["tipo_busqueda"].unique()))

df_filtrado = df[
    (df["region"].isin(regiones_sel)) &
    (df["distrito"].isin(distritos_sel)) &
    (df["tipo_busqueda"].isin(tipo_sel))
]
if len(rango_fechas) == 2:
    df_filtrado = df_filtrado[
        (df_filtrado["fecha_toma"] >= rango_fechas[0]) &
        (df_filtrado["fecha_toma"] <= rango_fechas[1])
    ]

st.divider()

# --- Métricas clave ---
total = len(df_filtrado)
positivos = df_filtrado["resultado_pdr"].isin(["P.v", "P.f"]).sum()
positividad = (positivos / total * 100) if total > 0 else 0
invalidas = (df_filtrado["resultado_pdr"] == "Inválida").sum()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Pruebas realizadas", total)
m2.metric("Casos positivos", positivos)
m3.metric("Tasa de positividad", f"{positividad:.1f}%")
m4.metric("Pruebas inválidas", invalidas,
          help="Pruebas inválidas suelen indicar problemas de insumos o capacitación del ColVol.")

st.divider()

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Casos positivos por distrito")
    casos_distrito = (
        df_filtrado[df_filtrado["resultado_pdr"].isin(["P.v", "P.f"])]
        .groupby("distrito").size().reset_index(name="casos")
        .sort_values("casos", ascending=False)
    )
    st.bar_chart(casos_distrito.set_index("distrito"))

with col_g2:
    st.subheader("Tipo de búsqueda")
    busqueda = df_filtrado["tipo_busqueda"].value_counts()
    st.bar_chart(busqueda)

st.subheader("Tendencia de pruebas en el tiempo")
tendencia = df_filtrado.groupby("fecha_toma").size().reset_index(name="pruebas")
st.line_chart(tendencia.set_index("fecha_toma"))

st.divider()
st.subheader("Detalle de registros filtrados")
st.dataframe(df_filtrado.sort_values("fecha_toma", ascending=False), use_container_width=True, hide_index=True)
