import streamlit as st
import requests
import pandas as pd

API = "http://localhost:8000"
st.set_page_config(page_title="Hospital IA", page_icon="🏥", layout="wide")
modulo = st.sidebar.radio("Modulo", ["Interconsultas HCD", "Metricas HCD"])

if modulo == "Interconsultas HCD":
    st.title("Interconsultas detectadas en HCD")
    r = requests.get(f"{API}/hcd/interconsultas")
    if r.status_code == 200:
        for ic in r.json():
            estado = ic["estado_interconsulta"]
            emoji = {"resuelta":"🟢","realizada":"🔵","en_gestion":"🟡"}.get(estado,"⚪")
            with st.expander(f"{emoji} {ic['servicios_detectados'][0].upper()} - {estado}"):
                st.write(f"**Motivo:** {ic['motivo']}")
                st.write(f"**Texto:** {ic['texto_original']}")
    else:
        st.error("Error API")

elif modulo == "Metricas HCD":
    st.title("Metricas del Sistema HCD")
    r = requests.get(f"{API}/hcd/metricas")
    if r.status_code == 200:
        data = r.json()
        st.subheader("Resumen de internacion")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total intervenciones", data["carga_asistencial"]["total_intervenciones"])
        col2.metric("Accuracy del modelo", f"{data['modelo_nlp']['accuracy']:.1%}")
        col3.metric("Dias internacion", data["internacion"]["dias_totales"])
        col4.metric("Reingresos", data["internacion"]["reingresos"])
        col5, col6, col7 = st.columns(3)
        col5.metric("1ra internacion", f"{data['internacion']['primera_estadia_dias']} dias")
        col6.metric("2da internacion", f"{data['internacion']['segunda_estadia_dias']} dias")
        col7.metric("Cambios de cama", data["internacion"]["cambios_cama"])
        st.subheader("Intervenciones por area")
        areas = data["intervenciones_por_area"]
        df = pd.DataFrame({"Area": list(areas.keys()), "Intervenciones": list(areas.values())}).sort_values("Intervenciones", ascending=False)
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("Area"))
        st.subheader("Variables clinicas detectadas")
        vars_cli = list(data["variables_clinicas_detectadas"].keys())
        col_a, col_b = st.columns(2)
        for i, k in enumerate(vars_cli):
            if i % 2 == 0:
                col_a.write(f"✅ {k.replace('_',' ').capitalize()}")
            else:
                col_b.write(f"✅ {k.replace('_',' ').capitalize()}")
    else:
        st.error("Error API")
