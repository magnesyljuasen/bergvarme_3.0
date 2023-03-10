import streamlit as st
import numpy as np
import pandas as pd
from io import BytesIO
import altair as alt
from streamlit_extras.chart_container import chart_container

from scripts.__profet import PROFet
from scripts.__utils import Plotting
from scripts.__energycoverage import EnergyCoverage
from scripts.__costs import Costs
from scripts.__ghetool import GheTool
from scripts.__utils import hour_to_month
from scripts.__peakshaving import peakshaving
from scripts.__pygfunction import Simulation

st.set_page_config(page_title="Tidligfasedimensjonering", page_icon="📈")

with open("styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True) 
    
st.title("Tidligfasedimensjonering av energibrønnpark")
st.caption("Spørsmål til verktøyet? 📧 magne.syljuasen@asplanviak.no ")
with st.expander("Hva er dette?"):
    st.header("Hva er dette?")
    st.write("""Dette verktøyet gir et tidlig estimat for størrelse på brønnpark til et bygg eller område. 
    Beregningene tar utgangspunkt i timeverdier til oppvarming, og kan enten estimeres vha. PROFet eller lastes opp selv som en excel-fil. """)
    st.write(""" PROFet er en temperaturavhengig lastprofilmodell 
    som baserer seg på reelle måledata fra bygg. Modellen gjør det mulig å estimere energibehovet 
    til romoppvarming, varmt tappevann og elektrisitet for bygg.""")
    st.write(""" Deretter dimensjoneres energibrønnparken. Dimensjoneringen går ut på å simulere temperaturnivåene i brønnparken ut ifra
    energi- og effektuttak/tilførsel, og forutsetningene i kapittel Ⅱ). """)
st.markdown("---")
#---
st.header("Ⅰ) Energibehov")
selected_input = st.radio("Hvordan vil du legge inn input?", options=["PROFet", "Last opp"])
if selected_input == "PROFet":
    st.subheader("Termisk energibehov fra PROFet")
    st.info("Foreløpig begrenset til Trondheimsklima", icon="ℹ️")
    energy_demand = PROFet()
    demand_array, selected_array = energy_demand.get_thermal_arrays_from_input()
    data = pd.DataFrame({
        "x" : np.arange(0,8760,1),
        "y" : demand_array
        })
    with chart_container(data):
        st.altair_chart(alt.Chart(data).mark_area(color = '#1d3c34', line = {'color':'#1d3c34'}, opacity = 1).encode(
            x=alt.X("x", axis=alt.Axis(title="Timer i ett år"), scale=alt.Scale(domain=(0,8760))),
            y=alt.Y("y", axis=alt.Axis(title="Timesmidlet effekt [kWh/h]"))), theme="streamlit", use_container_width=True)
    
    data = pd.DataFrame({
        "x" : np.arange(0,8760,1),
        "y" : np.sort(demand_array)[::-1]
        })
    with chart_container(data):
        st.altair_chart(alt.Chart(data).mark_line(color = '#1d3c34', line = {'color':'#1d3c34'}, opacity = 1).encode(
            x=alt.X("x", axis=alt.Axis(title="Timer i ett år"), scale=alt.Scale(domain=(0,8760))),
            y=alt.Y("y", axis=alt.Axis(title="Timesmidlet effekt [kWh/h]"))), theme="streamlit", use_container_width=True)

    #--
    st.subheader("El-spesifikt energibehov fra PROFet")
    with st.expander("El-spesifikt behov"):
        electric_array, selected_array = energy_demand.get_electric_array_()
        data = pd.DataFrame({
        "x" : np.arange(0,8760,1),
        "y" : electric_array
        })
        with chart_container(data):
            st.altair_chart(alt.Chart(data).mark_area(color = '#b7dc8f', line = {'color':'#b7dc8f'}, opacity = 1).encode(
                x=alt.X("x", axis=alt.Axis(title="Timer i ett år"), scale=alt.Scale(domain=(0,8760))),
                y=alt.Y("y", axis=alt.Axis(title="Timesmidlet effekt [kWh/h]"))), theme="streamlit", use_container_width=True)
        data = pd.DataFrame({
        "x" : np.arange(0,8760,1),
        "y" : np.sort(electric_array)[::-1]
        })
        with chart_container(data):
            st.altair_chart(alt.Chart(data).mark_line(color = '#b7dc8f', line = {'color':'#b7dc8f'}, opacity = 1).encode(
                x=alt.X("x", axis=alt.Axis(title="Timer i ett år"), scale=alt.Scale(domain=(0,8760))),
                y=alt.Y("y", axis=alt.Axis(title="Timesmidlet effekt [kWh/h]"))), theme="streamlit", use_container_width=True)
        
else:
    st.subheader("Last opp fil")
    uploaded_array = st.file_uploader("Last opp timeserie i kW")
    if uploaded_array:
        df = pd.read_excel(uploaded_array, header=None)
        demand_array = df.iloc[:,0].to_numpy()
        st.area_chart(demand_array)
        st.line_chart(np.sort(demand_array)[::-1])
    else:
        st.stop()
st.markdown("---")
#--
st.subheader("Kjølebehov")
annual_cooling_demand = st.number_input("Legg inn årlig kjølebehov [kWh]", min_value=0, value=0, step=1000)
cooling_effect = st.number_input("Legg inn kjøleeffekt [kW]", min_value=0, value=0, step=100)
cooling_per_month = annual_cooling_demand * np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
months = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"]
data = pd.DataFrame({
    "x" : months,
    "y" : cooling_per_month
    })
with chart_container(data):
    st.altair_chart(alt.Chart(data).mark_bar(color = '#1d3c34', line = {'color':'#1d3c34'}, opacity = 1).encode(
        x=alt.X("x", axis=alt.Axis(title="Måneder")),
        y=alt.Y("y", axis=alt.Axis(title="Kjølebehov [kWh]"))), theme="streamlit", use_container_width=True)

st.markdown("---")
#--
st.subheader("Dekningsgrad")
energy_coverage = EnergyCoverage(demand_array)
energy_coverage.COVERAGE = st.number_input("Velg energidekningsgrad [%]", min_value=50, value=90, max_value=100, step=2)    
energy_coverage._coverage_calculation()
st.caption(f"**Varmepumpe: {energy_coverage.heat_pump_size} kW | Effektdekningsgrad: {int(round((energy_coverage.heat_pump_size/np.max(demand_array))*100,0))} %**")

data = pd.DataFrame({
    'Timer i ett år' : np.arange(0,8760,1),
    'Spisslast' : energy_coverage.non_covered_arr,
    'a' : energy_coverage.covered_arr, 
    })

with chart_container(data):
    c = alt.Chart(data).transform_fold(
    ['a', 'Spisslast'],
    as_=['key', 'Timesmidlet effekt (kWh/h)']).mark_bar(color = '#b7dc8f', line = {'color':'#b7dc8f'}, opacity=1).encode(
        x=alt.X('Timer i ett år:Q', scale=alt.Scale(domain=[0, 8760])),
        y=alt.Y('Timesmidlet effekt (kWh/h):Q', stack = True),
        color=alt.Color('key:N', scale=alt.Scale(domain=['a', 'Spisslast'], 
        range=['#1d3c34', '#ffdb9a']), legend=alt.Legend(orient='top', direction='vertical', title=None))
    )
    st.altair_chart(c, use_container_width=True)

#Plotting().hourly_stack_plot(energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Grunnvarmedekning", "Spisslast (dekkes ikke av brønnparken)", Plotting().FOREST_GREEN, Plotting().SUN_YELLOW)
#Plotting().hourly_stack_plot(np.sort(energy_coverage.covered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Grunnvarmedekning", "Spisslast (dekkes ikke av brønnparken)", Plotting().FOREST_GREEN, Plotting().SUN_YELLOW)
#--
st.subheader("Årsvarmefaktor")
energy_coverage.COP = st.number_input("Velg årsvarmefaktor (SCOP)", min_value=1.0, value=3.5, max_value=5.0, step=0.2)
energy_coverage._geoenergy_cop_calculation()
data = pd.DataFrame({
    'Timer i ett år' : np.arange(0,8760,1),
    'Spisslast' : energy_coverage.gshp_delivered_arr,
    "Levert fra brønner" : energy_coverage.non_covered_arr,
    'Strøm til varmepumpe' : energy_coverage.gshp_compressor_arr, 
    })
with chart_container(data):
    c = alt.Chart(data).transform_fold(
    ['Spisslast', 'Levert fra brønner', 'Strøm til varmepumpe'],
    as_=['key', 'Timesmidlet effekt (kWh/h)']).mark_bar(color = '#b7dc8f', line = {'color':'#b7dc8f'}, opacity=1).encode(
        x=alt.X('Timer i ett år:Q', scale=alt.Scale(domain=[0, 8760])),
        y=alt.Y('Timesmidlet effekt (kWh/h):Q', stack = True),
        color=alt.Color('key:N', scale=alt.Scale(domain=['Spisslast', 'Levert fra brønner', 'Strøm til varmepumpe'], 
        range=['#1d3c34', '#ffdb9a', '#ffdb3b']), legend=alt.Legend(orient='top', direction='vertical', title=None))
    )
    st.altair_chart(c, use_container_width=True)
#--
data = pd.DataFrame({
    'Varighet (timer)' : np.arange(0,8760,1),
    'Spisslast' : np.sort(energy_coverage.gshp_delivered_arr)[::-1],
    "Levert fra brønner" : np.sort(energy_coverage.non_covered_arr)[::-1],
    'Strøm til varmepumpe' : np.sort(energy_coverage.gshp_compressor_arr)[::-1], 
    })
with chart_container(data):
    c = alt.Chart(data).transform_fold(
    ['Spisslast', 'Levert fra brønner', 'Strøm til varmepumpe'],
    as_=['key', 'Timesmidlet effekt (kWh/h)']).mark_bar(color = '#b7dc8f', line = {'color':'#b7dc8f'}, opacity=1).encode(
        x=alt.X('Varighet (timer):Q', scale=alt.Scale(domain=[0, 8760])),
        y=alt.Y('Timesmidlet effekt (kWh/h):Q', stack = True),
        color=alt.Color('key:N', scale=alt.Scale(domain=['Spisslast', 'Levert fra brønner', 'Strøm til varmepumpe'], 
        range=['#1d3c34', '#ffdb9a', '#ffdb3b']), legend=alt.Legend(orient='top', direction='vertical', title=None))
    )
    st.altair_chart(c, use_container_width=True)

st.markdown("---")
#--
#    st.subheader("Alternativer for Spisslast (dekkes ikke av brønnparken)")
#    with st.expander("Akkumuleringstank"):
#        max_effect_noncovered = max(energy_coverage.non_covered_arr)
#        st.write("**Før akkumulering**")
#        Plotting().hourly_plot(energy_coverage.non_covered_arr, "Spisslast (dekkes ikke av brønnparken)", Plotting().SUN_YELLOW, 0, 1.1*max_effect_noncovered, max_effect_noncovered)
#        #Plotting().hourly_plot(energy_coverage.non_covered_arr, "Spisslast (dekkes ikke av brønnparken)", Plotting().SUN_YELLOW, 0, 1.1*max_effect_noncovered, max_effect_noncovered, winterweek=True)
#        st.write("**Etter akkumulering**")
#        effect_reduction = st.number_input("Ønsket effektreduksjon [kW]", value=int(round(max_effect_noncovered/10,0)), step=10)
#        if effect_reduction > max_effect_noncovered:
#            st.warning("Effektreduksjon kan ikke være høyere enn effekttopp")
#            st.stop()
#        TO_TEMP = st.number_input("Turtemperatur [°C]", value = 60)
#        FROM_TEMP = st.number_input("Returtemperatur [°C]", value = 40)
#        peakshaving_arr, peakshaving_effect = peakshaving(energy_coverage.non_covered_arr, effect_reduction, TO_TEMP, FROM_TEMP)
#        Plotting().hourly_plot(peakshaving_arr, "Spisslast (dekkes ikke av brønnparken)", Plotting().SUN_YELLOW, 0, 1.1*max_effect_noncovered, peakshaving_effect)
#        #Plotting().hourly_plot(energy_coverage.non_covered_arr, "Spisslast (dekkes ikke av brønnparken)", Plotting().SUN_YELLOW, 0, 1.1*max_effect_noncovered, max_effect_noncovered, winterweek=True)
#    st.markdown("---")
st.subheader("Oppsummert")
st.write(f"Totalt energibehov: {int(round(np.sum(demand_array),0)):,} kWh | {int(round(np.max(demand_array),0)):,} kW".replace(',', ' '))
st.write(f"- Dekkes av grunnvarmeanlegget: {int(round(np.sum(energy_coverage.covered_arr),0)):,} kWh | **{int(round(np.max(energy_coverage.covered_arr),0)):,}** kW".replace(',', ' '))
st.write(f"- - Strøm til varmepumpe: {int(round(np.sum(energy_coverage.gshp_compressor_arr),0)):,} kWh | {int(round(np.max(energy_coverage.gshp_compressor_arr),0)):,} kW".replace(',', ' '))
st.write(f"- - Levert fra brønn(er): {int(round(np.sum(energy_coverage.gshp_delivered_arr),0)):,} kWh | {int(round(np.max(energy_coverage.gshp_delivered_arr),0)):,} kW".replace(',', ' '))
st.write(f"- Spisslast (dekkes ikke av brønnparken): {int(round(np.sum(energy_coverage.non_covered_arr),0)):,} kWh | {int(round(np.max(energy_coverage.non_covered_arr),0)):,} kW".replace(',', ' '))
st.markdown("---")
#---
st.header("Ⅱ) Dimensjonering av brønnpark")
st.warning("Under utvikling", icon = "⚠️")
with st.expander("Generelle råd"):
    st.write(""" - Avstanden mellom brønnene bør være minst 15 meter slik at de ikke henter varme fra samme bergvolum. 
    Der det er tilgengelig plass etterstrebes en mest mulig åpen konfigurasjon""")
    st.write(""" - 250 - 300 m er vanlig brønndybde. Noen av de store brønnborerfirmaene kan også bore dypere brønner. 
    Dype brønner kan være aktuelt i områder med lite tilgjengelig plass, eller der løsmassemektigheten er stor. """)
    st.write(""" - Det settes ofte ulike kriterier i prosjekter for når temperaturnivåene er OK. 
    Ofte sier vi at temperaturen ved dellast ikke bør bli lavere enn 1 °C etter 25 års drift.
    Andre ganger kan det være et kriterie at temperaturen inn til varmepumpa ikke skal være lavere enn 1 °C. """)
    st.write(""" - I områder med marine løsmasser (leire) er det kritisk at brønnparken ikke fryser. 
    Gjentatte fryse- og tineprosesser i leire gir setningsskader.""")
#    st.write("""I denne delen simuleres kollektorvæsketemperaturen i energibrønnen(e) 
#    ut ifra energien som skal leveres fra brønnene, størrelsen på varmepumpa og forutsetningene under. 
#    Det er et samspill mellom disse faktorene som bestemmer hvor mange brønner som er nødvendig. """)

simulation_obj = GheTool()
simulation_obj.monthly_load_heating = hour_to_month(energy_coverage.gshp_delivered_arr)
simulation_obj.peak_heating = np.full((1, 12), energy_coverage.heat_pump_size).flatten().tolist()
simulation_obj.monthly_load_cooling = cooling_per_month
simulation_obj.peak_cooling = np.full((1, 12), cooling_effect).flatten().tolist()
well_guess = int(round(np.sum(energy_coverage.gshp_delivered_arr)/80/300,2))
if well_guess == 0:
    well_guess = 1
with st.form("Inndata"):
    c1, c2 = st.columns(2)
    with c1:
        simulation_obj.K_S = st.number_input("Effektiv varmledningsevne [W/m∙K]", min_value=1.0, value=3.5, max_value=10.0, step=1.0) 
        simulation_obj.T_G = st.number_input("Uforstyrret temperatur [°C]", min_value=1.0, value=8.0, max_value=20.0, step=1.0)
        simulation_obj.R_B = st.number_input("Borehullsmotstand [m∙K/W]", min_value=0.0, value=0.10, max_value=2.0, step=0.01) + 0.03
        simulation_obj.N_1= st.number_input("Antall brønner (X)", value=well_guess, step=1) 
        simulation_obj.N_2= st.number_input("Antall brønner (Y)", value=1, step=1)
        #--
        simulation_obj.COP = energy_coverage.COP
    with c2:
        H = st.number_input("Brønndybde [m]", min_value=100, value=300, max_value=500, step=10)
        GWT = st.number_input("Grunnvannsstand [m]", min_value=0, value=5, max_value=100, step=1)
        simulation_obj.H = H - GWT
        simulation_obj.B = st.number_input("Avstand mellom brønner", min_value=1, value=15, max_value=30, step=1)
        simulation_obj.RADIUS = st.number_input("Brønndiameter [mm]", min_value = 80, value=115, max_value=300, step=1) / 2000
        heat_carrier_fluid_types = ["HX24", "HX35", "Kilfrost GEO 24%", "Kilfrost GEO 32%", "Kilfrost GEO 35%"]    
        heat_carrier_fluid = st.selectbox("Type kollektorvæske", options=list(range(len(heat_carrier_fluid_types))), format_func=lambda x: heat_carrier_fluid_types[x])
        simulation_obj.FLOW = 0.5
        #simulation_obj.peak_heating = st.number_input("Varmepumpe [kW]", value = int(round(energy_coverage.heat_pump_size,0)), step=10)
    st.form_submit_button("Kjør simulering")
heat_carrier_fluid_densities = [970.5, 955, 1105.5, 1136.2, 1150.6]
heat_carrier_fluid_capacities = [4.298, 4.061, 3.455, 3.251, 3.156]
simulation_obj.DENSITY = heat_carrier_fluid_densities[heat_carrier_fluid]
simulation_obj.HEAT_CAPACITY = heat_carrier_fluid_capacities[heat_carrier_fluid]
simulation_obj._run_simulation()


st.markdown("---")   
#--
st.header("Ⅲ) Kostnader")
st.warning("Under utvikling", icon = "⚠️")
st.subheader("Forutsetninger")
costs_obj = Costs()
c1, c2 = st.columns(2)
#-- input
with c1:
    costs_obj.ELPRICE = st.number_input("Strømpris inkl. alt [kr/kWh]", min_value=0.0, value=1.0, max_value=10.0, step=1.0)
    costs_obj.LIFETIME = st.number_input("Levetid [år]", min_value=1, value=25, max_value=100, step=5)
with c2:
    costs_obj.METERS = (simulation_obj.N_1 * simulation_obj.N_2) * simulation_obj.H
    costs_obj.gshp_compressor_arr = energy_coverage.gshp_compressor_arr
    costs_obj.non_covered_arr = energy_coverage.non_covered_arr
    costs_obj.demand_array = demand_array
    costs_obj.heat_pump_size = energy_coverage.heat_pump_size
    #--
    costs_obj.DISKONTERINGSRENTE = st.number_input("Diskonteringsrente [%]", min_value=1, value=6, max_value=100, step=2) / 100
    costs_obj.maintenance_cost = st.number_input("Vedlikeholdskostnad [kr/år]", min_value=0, value=10000, max_value=100000, step=1000)     
    #--
    costs_obj._run_cost_calculation()

st.subheader("Resultater")
st.write(f"- Anslått investeringskostnad: {costs_obj.investment_cost:,} kr".replace(',', ' '))
st.write(f"- Driftskostnad (strøm): {costs_obj.operation_cost + costs_obj.maintenance_cost:,} kr/år".replace(',', ' '))
st.write(f"- Levelized cost of electricity (LCOE): {costs_obj.LCOE:,} kr/kWh".replace(',', ' '))

st.markdown("---")
st.header("Oppsummering")
buffer = BytesIO()

df1 = pd.DataFrame({
    "Termisk energibehov" : demand_array, 
    "Strøm til varmepumpe" : energy_coverage.gshp_compressor_arr,
    "Levert energi fra brønner" : energy_coverage.gshp_delivered_arr,
    "Spisslast" : energy_coverage.non_covered_arr
    })

with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    df1.to_excel(writer, sheet_name="Sheet1", index=False)
    writer.save()

    st.write("Her kan du laste ned resultater fra beregningene til excel-format.")
    st.download_button(
        label="Last ned resultater",
        data=buffer,
        file_name="Energibehov.xlsx",
        mime="application/vnd.ms-excel",
    )
st.markdown("---")
st.header("Bistand til grunnvarmeprosjekter?")
st.write("Vi bistår gjerne i alle typer grunnvarmeprosjekter! Ta kontakt med en av oss 😊")
st.write(""" - Johanne Strålberg | johanne.stralberg@asplanviak.no""")
st.write(""" - Sofie Hartvigsen | sofie.hartvigsen@asplanviak.no""")
st.write(""" - Magne Syljuåsen | magne.syljuasen@asplanviak.no""")
st.write(""" - Henrik Holmberg | henrik.holmberg@asplanviak.no""")
st.write(""" - Randi Kalskin Ramstad | randi.kalskin.ramstad@asplanviak.no""")    


