# Prototipo: Apoyo digital para supervisores de ColVol

Prototipo de 3 módulos independientes en Streamlit, diseñados para reemplazar
la transcripción manual del Anexo 1 a Excel, y para que la información sirva
a nivel local, regional y nacional.

## Módulos

1. **`1_Registro.py`** — Digitaliza el Anexo 1 (formulario para el supervisor).
2. **`2_Gestion_ColVol.py`** — Catálogo de los ColVol a cargo del supervisor.
3. **`3_Dashboard.py`** — Visualización con filtros por región/distrito/fecha,
   usando datos simulados (no depende de los otros módulos).

Cada módulo se puede ejecutar de forma 100% independiente.

## Cómo correr cada módulo

### Opción A: Local
```bash
pip install -r requirements.txt
streamlit run 1_Registro.py
# o
streamlit run 2_Gestion_ColVol.py
# o
streamlit run 3_Dashboard.py
```

### Opción B: Streamlit Community Cloud (recomendado para compartir el link)
1. Sube esta carpeta a un repositorio de GitHub.
2. Entra a https://share.streamlit.io y conecta tu cuenta de GitHub.
3. Crea una nueva app, selecciona el repo y elige el archivo del módulo
   que quieras desplegar (por ejemplo, `1_Registro.py`).
4. Repite para cada módulo si quieres 3 links separados, o combínalos en
   una sola app multipágina (ver nota abajo).

> Nota: si prefieres una sola app con navegación entre los 3 módulos,
> Streamlit detecta automáticamente cualquier carpeta `pages/` como
> páginas adicionales. Bastaría con renombrar este folder a `pages/` y
> tener un `Home.py` como entrada principal.

## Supuestos de diseño explícitos

- El supervisor digita por lotes, al llegar a la oficina con varios
  formatos en papel acumulados — no registro a registro durante el día.
- Cada ColVol pertenece a una sola localidad, que a su vez pertenece a un
  distrito, región y país (jerarquía fija, sin combinaciones múltiples).
- El catálogo de ColVol se mantiene aparte del registro de pruebas para
  evitar que el supervisor reescriba distrito/región cada vez (reduce
  carga de digitación y errores).
- El dashboard usa datos simulados para poder probarse de forma aislada;
  en producción se alimentaría de la base nacional consolidada (todos
  los supervisores), no solo de los registros de un supervisor.
- Los datos se guardan en CSV local como simulación de persistencia —
  en producción se reemplazaría por una base de datos real, pero esto
  no afecta la lógica de los módulos ni la experiencia del usuario.
- El piloto no requiere autenticación de usuario ni roles — se asume un
  supervisor por sesión, consistente con que es un prototipo, no la
  solución final.
