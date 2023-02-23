import streamlit as st 
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.chart_container import chart_container
import pandas as pd
import numpy as np
from PIL import Image

st.set_page_config(page_title="Utregninger", page_icon="🔢")

with open("styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

st.title("Utregninger")
selected_method = selectbox(
    "Velg metode",
    ["Beregning av ΔT", "Beregning av uforstyrret temperatur"],
    no_selection_label="-",
)

st.markdown("---")
if selected_method == "Beregning av ΔT":
    st.header("Beregning av ΔT")
    st.subheader("Inndata")
    heat_carrier_fluid_types = ["HX24", "HX35", "Kilfrost GEO 24%", "Kilfrost GEO 32%", "Kilfrost GEO 35%"]
    heat_carrier_fluid_densities = [970.5, 955, 1105.5, 1136.2, 1150.6]
    heat_carrier_fluid_capacities = [4.298, 4.061, 3.455, 3.251, 3.156]
    c1, c2 = st.columns(2)
    with c1:
        number_of_wells = st.number_input("Antall brønner", value=1, step=1, min_value=1)
        COP = st.number_input("Årsvarmefaktor (SPF)", value=3.5, min_value=2.0, max_value=5.0, step=0.1)
        heat_pump_size = st.number_input("Varmepumpestørrelse [kW]", value=10, step=10)
        peak_average_minimum_temperature = st.number_input("Gjennomsnittlig minimumstemperatur [°C]", value=0.0, step=1.0)
    with c2:
        flow = st.number_input("Flow [l/min]", value=0.5, step=0.1)
        heat_carrier_fluid = st.selectbox("Type kollektorvæske", options=list(range(len(heat_carrier_fluid_types))), format_func=lambda x: heat_carrier_fluid_types[x])
        density = st.number_input("Tetthet [kg/m3]", value=heat_carrier_fluid_densities[heat_carrier_fluid])
        heat_capacity = st.number_input("Spesifikk varmekapasitet [kJ/kg∙K]", value=heat_carrier_fluid_capacities[heat_carrier_fluid])
    st.markdown("---")
    #--
    st.subheader("Resultater")
    #st.caption(f"Levert effekt fra brønnpark: {round(heat_pump_size-heat_pump_size/COP,1)} kW")
    Q = (heat_pump_size-heat_pump_size/COP)/number_of_wells
    st.caption(f"Levert effekt fra brønnpark: {round(heat_pump_size-heat_pump_size/COP,1)} kW | Levert effekt per brønn (Q): {round(Q,1)} kW")
    delta_T = round((Q*1000)/(density*flow*heat_capacity),1)
    st.write(f"ΔT = {delta_T} °C")
    peak_max_temperature = round(peak_average_minimum_temperature + delta_T/2,1)
    peak_min_temperature = round(peak_average_minimum_temperature - delta_T/2,1)
    st.write(f"Maksimal kollektorvæsketemperatur: {peak_average_minimum_temperature} °C + {delta_T/2} °C = **{peak_max_temperature} °C**")
    st.write(f"Minimum kollektorvæsketemperatur: {peak_average_minimum_temperature} °C - {delta_T/2} °C = **{peak_min_temperature} °C**")
    st.markdown("---")
    #--
    st.subheader("Til rapport")
    st.write(f""" Ved maksimal varmeeffekt fra varmepumpen på {heat_pump_size} kW kommer temperaturen til og fra energibrønnene til å være henholdsvis ca. {round(delta_T/2,1)} grader høyere og lavere enn den gjennomsnittlige temperaturen (ΔT = {delta_T} °C). Dette betyr at den laveste kollektorvæsketemperaturen til og fra varmepumpens fordampere i vintermånedene år 25 vil være henholdsvis {peak_max_temperature} °C og {peak_min_temperature} °C. """)

if selected_method == "Beregning av uforstyrret temperatur":
    st.header("Beregning av uforstyrret temperatur")
    st.subheader("Inndata")
    uploaded_file = st.file_uploader("Last opp fil (excel)")
    with st.expander("Hvordan skal filen se ut?"):
        image = Image.open("src/data/img/uforstyrretTemperaturInput.PNG")
        st.image(image)  
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.subheader("Data")
        groundwater_table = st.number_input("Grunnvannstand [m]", value=5, min_value=0, max_value=100, step=1)
        df = df[df["Dybde"] >= groundwater_table]
        with chart_container(df):
            st.line_chart(data = df, x = "Dybde", y = "Temperatur")
        df.reset_index(inplace=True)
        with st.spinner("Beregner uforstyrret temperatur..."):
            mean_value = df["Temperatur"].mean()
            positive_deviation = 0
            negative_deviation = 0
            for i in range(0, 1000):
                #--
                for i in range(0, len(df)-1):
                    if df["Temperatur"].iloc[i] > mean_value:
                        x1 = df["Temperatur"].iloc[i] - mean_value
                        x2 = df["Temperatur"].iloc[i+1] - mean_value
                        delta_y = df["Dybde"].iloc[i+1] - df["Dybde"].iloc[i]
                        areal_trekant = delta_y*abs(x1-x2)/2
                        if x1 > x2:
                            langside = x1 - abs(x1-x2)
                        elif x2 < x1:
                            langside = x2 - abs(x1-x2)
                        else:
                            langside = x1
                        areal_rektangel = delta_y*langside
                        totalt_areal = areal_rektangel + areal_trekant
                        positive_deviation += totalt_areal
                    elif df["Temperatur"].iloc[i] < mean_value:
                        x1 = mean_value - df["Temperatur"].iloc[i] 
                        x2 = mean_value - df["Temperatur"].iloc[i+1] 
                        delta_y = df["Dybde"].iloc[i+1] - df["Dybde"].iloc[i]
                        areal_trekant = delta_y*abs(x1-x2)/2
                        if x1 > x2:
                            langside = x1 - abs(x1-x2)
                        elif x2 < x1:
                            langside = x2 - abs(x1-x2)
                        else:
                            langside = x1
                        areal_rektangel = delta_y*langside
                        totalt_areal = areal_rektangel + areal_trekant
                        negative_deviation += totalt_areal
                trigger_value = round(float(positive_deviation/negative_deviation),2)
                if trigger_value > 1:
                    mean_value = mean_value + 0.1
                if trigger_value < 1:
                    mean_value = mean_value - 0.1
            st.subheader(f"Uforstyrret temperatur = {round(float(mean_value),2)} °C")


                
                

