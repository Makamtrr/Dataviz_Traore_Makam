import streamlit as st
from utils import display_logo, configure_matplotlib

st.set_page_config(
    page_title="Dashboard RATP",
    page_icon="assets/RATP.png",
    layout="wide"
)

configure_matplotlib()
display_logo()

st.switch_page("pages/1_Analyse_par_station.py")
