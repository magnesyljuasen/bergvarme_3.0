import streamlit as st
from PIL import Image
import requests
from streamlit_lottie import st_lottie
import streamlit_authenticator as stauth
import yaml

st.set_page_config(
    page_title="Grunnvarme",
    page_icon="♨️",
)

with open("styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

with open('src/login/config.yaml') as file:
    config = yaml.load(file, Loader=stauth.SafeLoader)

authenticator = stauth.Authenticate(config['credentials'],config['cookie']['name'],config['cookie']['key'],config['cookie']['expiry_days'])
name, authentication_status, username = authenticator.login('Asplan Viak🌱 Innlogging for grunnvarme', 'main')

if authentication_status == False:
    st.error('Ugyldig brukernavn/passord')
elif authentication_status == None:
    st_lottie(requests.get("https://assets3.lottiefiles.com/packages/lf20_szeieqx5.json").json())
elif authentication_status:
    with st.sidebar:
        authenticator.logout('Logg ut', 'sidebar')
    #--
    col1, col2, col3 = st.columns(3)
    with col1:
        image = Image.open('src/data/img/logo.png')
        st.image(image)  
    with col2:
        st.title("Grunnvarme")
        st.write('♨️ Internside')
        
    #--
    st.header("🗺️ Kart")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("[• GRANADA](%s)" % "https://geo.ngu.no/kart/granada_mobil/")
        st.subheader("[• NADAG](%s)" % "https://geo.ngu.no/kart/nadag-avansert/")
        st.subheader("[• Løsmasser](%s)" % "https://geo.ngu.no/kart/losmasse_mobil/")
        st.subheader("[• Berggrunn](%s)" % "https://geo.ngu.no/kart/berggrunn_mobil/")
        st.subheader("[• Høydedata](%s)" % "https://hoydedata.no/LaserInnsyn2/")
    with c2:
        st.subheader("[• InSAR](%s)" % "https://insar.ngu.no/")
        st.subheader("[• AV-kartet](%s)" % "https://kart.asplanviak.no/")
        st.subheader("[• Saksinnsyn](%s)" % "https://od2.pbe.oslo.kommune.no/kart/")
        st.subheader("[• UnderOslo](%s)" % "https://kart4.nois.no/underoslo/Content/login.aspx?standalone=true&onsuccess=restart&layout=underoslo&time=637883136354120798&vwr=asv")
    st.markdown("""---""")
    #--
    st.header("🌍 Egne kart")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("[• Sammenstilling](%s)" % "https://asplanviak.maps.arcgis.com/apps/instant/basic/index.html?appid=901e9d0f94b24ec186bd4e1f7ce426c6")
        st.subheader("[• 3D kart](%s)" % "https://asplanviak.maps.arcgis.com/apps/webappviewer3d/index.html?id=66d6a06bc9a84510a4db7262411ffda7")

    with c2:
        st.subheader("[• Grunnvarmekartet](%s)" % "https://asplanviak.maps.arcgis.com/apps/mapviewer/index.html?webmap=466de4612e0a443f85f413fda02857b5")
        st.subheader("[• Melhus HUB](%s)" % "https://melhus-asplanviak.hub.arcgis.com/")
    st.markdown("""---""")
    #--
    st.header("📙 Internt")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("[• Sysselsetting](%s)" % "https://asplanviak.sharepoint.com/:x:/r/sites/10333-03/_layouts/15/Doc.aspx?sourcedoc=%7B16A5245E-E536-4A50-B78A-79AC4835A40F%7D&file=Sysselsetting%20grunnvarme.xlsx&action=default&mobileredirect=true&cid=421904ae-05a4-4426-bbcd-bfb2f0c56fad") 
        st.subheader("[• Prosess & miljø](%s)" % "https://asplanviak.sharepoint.com/:x:/r/sites/10362-00-50/_layouts/15/Doc.aspx?sourcedoc=%7B3ED0AE0B-BFC1-4F98-9887-951FE5DD3AAF%7D&file=Prosess%20og%20milj%C3%B8_%20Sysselsetting_proto.xlsm&action=default&mobileredirect=true&cid=ca932ba5-c9a9-43d7-8ed9-47e6365ec6eb") 
        st.subheader("[• TRT's](%s)" % "https://asplanviak.sharepoint.com/sites/10333-03/Delte%20dokumenter/General/Termisk%20responstest/Testoversikt.xlsx") 
    with c2:
        st.subheader("[• Ebooks](%s)" % "https://asplanviak.sharepoint.com/sites/10333-03")
        st.subheader("[• Gamle Ebooks](%s)" % "http://bikube/Oppdrag/8492/default.aspx")
        st.subheader("[• Maler](%s)" % "https://asplanviak.sharepoint.com/sites/10333-03/Delte%20dokumenter/General/Maler") 
    st.markdown("""---""")
    #--
    st.header("🔗 Andre")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("[• Nord Pool](%s)" % "https://www.nordpoolgroup.com/en/Market-data1/#/nordic/table")
        st.subheader("[• Profilmanual](%s)" % "https://profil.asplanviak.no/")
        
    with c2:
        st.subheader("[• GeoNorge](%s)" % "https://www.geonorge.no/")
        st.subheader("[• COPCALC](%s)" % "https://www.copcalc.com/tangix/index.php/desktop/index/live/norwegian")
    st.markdown(""" --- """)
    #--
    st.header("✂️ Symboler")
    c1, c2 = st.columns(2)
    with c1:
        st.code("°C")
        st.code("W/m∙K")
        st.code("m∙K/W")
        st.code("Δ")
    with c2:
        st.code("á")
        st.code("∙")
        st.code("±")
        st.code("λ")
    #--
    st_lottie(requests.get("https://assets1.lottiefiles.com/packages/lf20_l22gyrgm.json").json())

