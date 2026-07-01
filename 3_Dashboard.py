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

Notificación de positivos: se usa mailto (link de email pre-rellenado) porque
no requiere APIs de pago, no necesita mantenimiento técnico, es trazable y es
el canal formal apropiado para comunicación interinstitucional con Ministerios.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import urllib.parse

st.set_page_config(page_title="Dashboard de Vigilancia", layout="wide")

# --- Generación de datos simulados ---
@st.cache_data
def generar_datos_simulados(n=400, seed=42):
    rng = np.random.default_rng(seed)

    paises_regiones_distritos = {
        "País X": {"Región A": ["Distrito Norte", "Distrito Sur"],
                   "Región B": ["Distrito Centro", "Distrito Este"]},
        "País Y": {"Región C": ["Distrito Oeste", "Distrito Costa"]},
        "País Z": {"Región D": ["Distrito Sierra", "Distrito Selva"]},
    }

    nombres = ["Ana López", "Carlos Ríos", "María Torres", "Juan Pérez",
               "Lucía Mamani", "Pedro Quispe", "Rosa Flores", "Miguel Huanca"]

    filas = []
    for _ in range(n):
        pais = rng.choice(list(paises_regiones_distritos.keys()))
        region = rng.choice(list(paises_regiones_distritos[pais].keys()))
        distrito = rng.choice(paises_regiones_distritos[pais][region])
        fecha = date.today() - timedelta(days=int(rng.integers(0, 60)))
        resultado = rng.choice(
            ["P.v", "P.f", "Negativa", "Inválida"],
            p=[0.12, 0.08, 0.75, 0.05]
        )
        tipo_busqueda = rng.choice(["Pasiva", "Proactiva", "Reactiva"], p=[0.5, 0.3, 0.2])
        sexo = rng.choice(["Masculino", "Femenino"])
        nombre = rng.choice(nombres)
        filas.append({
            "pais": pais,
            "region": region,
            "distrito": distrito,
            "fecha_toma": fecha,
            "resultado_pdr": resultado,
            "tipo_busqueda": tipo_busqueda,
            "nombre_completo": nombre,
            "sexo": sexo,
        })
    return pd.DataFrame(filas)

df = generar_datos_simulados()

st.title("📊 Dashboard de Vigilancia de Malaria")
st.caption("Datos simulados para fines de prototipo — en producción se alimentaría de la base nacional consolidada.")

# --- Filtros jerárquicos: país > región > distrito ---
col_f1, col_f2, col_f3, col_f4 = st.columns(4)
with col_f1:
    paises_sel = st.multiselect("País", sorted(df["pais"].unique()), default=list(df["pais"].unique()))
with col_f2:
    regiones_disponibles = sorted(df[df["pais"].isin(paises_sel)]["region"].unique())
    regiones_sel = st.multiselect("Región", regiones_disponibles, default=regiones_disponibles)
with col_f3:
    distritos_disponibles = sorted(
        df[(df["pais"].isin(paises_sel)) & (df["region"].isin(regiones_sel))]["distrito"].unique()
    )
    distritos_sel = st.multiselect("Distrito", distritos_disponibles, default=distritos_disponibles)
with col_f4:
    rango_fechas = st.date_input(
        "Rango de fechas",
        value=(date.today() - timedelta(days=30), date.today())
    )

df_filtrado = df[
    (df["pais"].isin(paises_sel)) &
    (df["region"].isin(regiones_sel)) &
    (df["distrito"].isin(distritos_sel))
]
if len(rango_fechas) == 2:
    df_filtrado = df_filtrado[
        (df_filtrado["fecha_toma"] >= rango_fechas[0]) &
        (df_filtrado["fecha_toma"] <= rango_fechas[1])
    ]

st.divider()

# --- Métricas clave ---
total = len(df_filtrado)
positivos_n = df_filtrado["resultado_pdr"].isin(["P.v", "P.f"]).sum()
positividad = (positivos_n / total * 100) if total > 0 else 0
invalidas = (df_filtrado["resultado_pdr"] == "Inválida").sum()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Pruebas realizadas", total)
m2.metric("Casos positivos", positivos_n)
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

# --- Tabla de casos positivos con alerta y notificación por email ---
df_positivos = df_filtrado[df_filtrado["resultado_pdr"].isin(["P.v", "P.f"])].copy()
df_positivos = df_positivos.sort_values("fecha_toma", ascending=False)

st.subheader(f"🔴 Detalle de registros positivos ({len(df_positivos)} casos)")

if len(df_positivos) > 0:
    st.dataframe(df_positivos, use_container_width=True, hide_index=True)

    # --- Notificación por email (mailto: no requiere API ni costo) ---
    st.markdown("**📧 Notificar casos positivos al Programa de Malaria**")
    email_destino = st.text_input(
        "Correo del funcionario del Ministerio de Salud",
        placeholder="funcionario@minsa.gob.xx"
    )

    if email_destino:
        # Armar el cuerpo del email con la lista de positivos
        filas_email = []
        for _, r in df_positivos.iterrows():
            filas_email.append(
                f"- {r['nombre_completo']} | {r['resultado_pdr']} | "
                f"{r['distrito']}, {r['region']}, {r['pais']} | Fecha: {r['fecha_toma']}"
            )
        cuerpo = (
            f"Estimado/a,\n\n"
            f"Se reportan {len(df_positivos)} caso(s) positivo(s) de malaria "
            f"en el período {rango_fechas[0]} al {rango_fechas[1]}:\n\n"
            + "\n".join(filas_email) +
            "\n\nEste reporte fue generado automáticamente desde el sistema de vigilancia ColVol."
        )
        asunto = f"Reporte casos positivos malaria — {date.today()}"
        mailto = (
            f"mailto:{email_destino}"
            f"?subject={urllib.parse.quote(asunto)}"
            f"&body={urllib.parse.quote(cuerpo)}"
        )
        st.link_button("📨 Abrir correo pre-rellenado", mailto, use_container_width=True)
        st.caption(
            "Al hacer clic se abre tu cliente de correo (Outlook, Gmail, etc.) "
            "con el asunto y la lista de positivos ya escritos. Solo tienes que enviar."
        )
else:
    st.success("✅ No hay casos positivos en el período y filtros seleccionados.")

st.divider()

# --- Tabla completa de todos los registros ---
st.subheader("Detalle de todos los registros filtrados")
st.dataframe(df_filtrado.sort_values("fecha_toma", ascending=False),
             use_container_width=True, hide_index=True)