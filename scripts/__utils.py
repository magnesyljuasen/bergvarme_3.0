import requests
import streamlit.components.v1 as components
import streamlit as st

#  Hjelpefunksjon - Load Lottie
def load_lottie(url: str):
    r = requests.get(url)
    if r.status_code!= 200:
        return None
    return r.json()

#  Modifisert number input
def st_modified_number_input(text):
    number = st.text_input(text, value="")
    if number == "" or number == "":
        number = None
    elif number.isdecimal():
        number = int(number)
    else:
        st.error("Input må være et tall!")
    return number