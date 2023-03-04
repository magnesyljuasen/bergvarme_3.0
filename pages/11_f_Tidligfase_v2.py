import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_extras.chart_container import chart_container

from GHEtool import Borefield, GroundData
import pygfunction as gt
import altair as alt
import numpy as np 
import pandas as pd
from scripts.__utils import st_modified_number_input

st.set_page_config(page_title="Månedssimulering", page_icon="📊")

with open("styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True) 

def cop_or_not():
    selected_input = st.selectbox("Hvordan vil du legge inn energi- og effektdata?", 
                                  options=["Varme/kjøling fra/til bygg (velg SPF og dekningsgrad)",
                                           "Varme/kjøling fra/til varmepumpe (velg SPF)",
                                           "Varme/kjøling fra/til brønner"])
    if selected_input == "Varme/kjøling fra/til brønner":
        COP = 0
    elif selected_input == "Varme/kjøling fra/til varmepumpe (velg SPF)":
        COP = st.number_input("Hva er antatt årsvarmefaktor (SPF) for varmepumpen?", min_value=2.0, value=3.5, max_value=5.0, step=0.1)
    elif selected_input == "Varme/kjøling fra/til bygg (velg SPF og dekningsgrad)":
        COP = st.number_input("Hva er antatt årsvarmefaktor (SPF) for varmepumpen?", min_value=2.0, value=3.5, max_value=5.0, step=0.1)
        COVERAGE = st.number_input("Hva skal energidekningsgraden [%] være?", min_value=70, value=90, max_value=100, step=1)

st.title("Dimensjonering av brønnpark")

tab1, tab2, tab3 = st.tabs(["Timeverdier", "Månedsverdier", "Årsverdier"])
with tab1:
    st.header("Inndata")
    cop_or_not()
    st.subheader("Last opp fil")
    uploaded_array = st.file_uploader("Last opp timeserie i kW")
    if uploaded_array:
        df = pd.read_excel(uploaded_array, header=None)
        demand_array = df.iloc[:,0].to_numpy()
        st.area_chart(demand_array)
        st.line_chart(np.sort(demand_array)[::-1])