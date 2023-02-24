import streamlit as st

st.set_page_config(page_title="Tidligfasedimensjonering", page_icon="📈")

with open("styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True) 
    
st.title("Tidligfasedimensjonering av energibrønnpark")

    