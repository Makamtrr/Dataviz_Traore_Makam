import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Ajouter le répertoire parent au path pour importer utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_data, display_logo, COLORS_RATP, configure_matplotlib

# Configuration
st.set_page_config(
    page_title="Analyse par station - RATP",
    page_icon="assets/RATP.png",
    layout="wide"
)

# Configuration matplotlib
configure_matplotlib()

# Logo
display_logo()

# Chargement des données
df = load_data()

# Titre
st.title("Analyse par station")
st.markdown("Explorez les détails d'une station et comparez-la aux moyennes du réseau.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Filtres")
    
    # Filtre réseau
    reseaux = ['Tous'] + sorted(df['Réseau'].unique().tolist())
    reseau_choisi = st.selectbox("Réseau", reseaux)
    
    # Filtrer les stations selon le réseau
    if reseau_choisi == 'Tous':
        df_filtre = df.copy()
    else:
        df_filtre = df[df['Réseau'] == reseau_choisi].copy()
    
    # Sélection de la station
    stations = sorted(df_filtre['Station'].unique().tolist())
    station_choisie = st.selectbox("Station", stations, key='station_select')
    
    # Récupérer les infos de la station
    station_data = df_filtre[df_filtre['Station'] == station_choisie].iloc[0]

with col2:
    st.subheader("Fiche station")
    
    # Affichage des informations
    info_col1, info_col2, info_col3 = st.columns(3)
    
    with info_col1:
        st.metric("Trafic annuel", f"{station_data['Trafic']:,.0f}")
    
    with info_col2:
        st.metric("Réseau", station_data['Réseau'])
    
    with info_col3:
        rang = station_data['Rang']
        st.metric("Rang", f"#{int(rang)}")
    
    st.markdown("---")
    
    info_col4, info_col5 = st.columns(2)
    
    with info_col4:
        st.markdown(f"**Lignes desservies :** {station_data['Lignes']}")
        st.markdown(f"**Ville :** {station_data['Ville']}")
    
    with info_col5:
        arr = station_data['Arrondissement pour Paris']
        if arr and str(arr).strip():
            st.markdown(f"**Arrondissement :** {arr}")
        else:
            st.markdown(f"**Arrondissement :** -")

st.markdown("---")

# Calcul des statistiques du réseau
if reseau_choisi == 'Tous':
    reseau_label = "tous réseaux"
    df_stats = df.copy()
else:
    reseau_label = f"réseau {reseau_choisi}"
    df_stats = df[df['Réseau'] == reseau_choisi].copy()

trafic_moyen = df_stats['Trafic'].mean()
trafic_median = df_stats['Trafic'].median()

# Classement dans le réseau
df_stats_sorted = df_stats.sort_values('Trafic', ascending=False).reset_index(drop=True)
rang_reseau = df_stats_sorted[df_stats_sorted['Station'] == station_choisie].index[0] + 1
total_stations_reseau = len(df_stats)

st.subheader(f"Comparaison avec le {reseau_label}")

comp_col1, comp_col2 = st.columns([1, 1])

with comp_col1:
    st.info(f"**Classement dans le {reseau_label} :** #{rang_reseau} sur {total_stations_reseau}")
    
    # Comparaison avec moyenne et médiane
    delta_moyen = ((station_data['Trafic'] - trafic_moyen) / trafic_moyen) * 100
    delta_median = ((station_data['Trafic'] - trafic_median) / trafic_median) * 100
    
    st.metric("Trafic moyen du réseau", f"{trafic_moyen:,.0f}", f"{delta_moyen:+.1f}%")
    st.metric("Trafic médian du réseau", f"{trafic_median:,.0f}", f"{delta_median:+.1f}%")

with comp_col2:
    # Graphique de comparaison
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['Station\nsélectionnée', 'Moyenne\nréseau', 'Médiane\nréseau']
    values = [station_data['Trafic'], trafic_moyen, trafic_median]
    colors = [COLORS_RATP['bleu'], COLORS_RATP['vert'], COLORS_RATP['jaune']]
    
    bars = ax.bar(categories, values, color=colors, alpha=0.85, edgecolor=COLORS_RATP['noir'], linewidth=1.5)
    
    # Ajouter les valeurs sur les barres
    for i, (bar, value) in enumerate(zip(bars, values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{value:,.0f}',
               ha='center', va='bottom', fontsize=11, fontweight='bold', color=COLORS_RATP['noir'])
    
    ax.set_ylabel('Trafic annuel', fontsize=12, fontweight='bold')
    ax.set_title(f'Comparaison du trafic - {station_choisie}', fontsize=14, fontweight='bold', pad=20, color=COLORS_RATP['bleu'])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    ax.grid(axis='y', alpha=0.3, linestyle='--', color=COLORS_RATP['noir'])
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
