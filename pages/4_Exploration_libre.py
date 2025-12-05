import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
import os

# Ajouter le répertoire parent au path pour importer utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_data, display_logo, COLORS_RATP, configure_matplotlib

# Configuration
st.set_page_config(
    page_title="Exploration libre - RATP",
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
st.title("Exploration libre des données")
st.markdown("Filtrez et explorez les données selon vos critères.")

# Sidebar de filtres
with st.sidebar:
    st.markdown("---")
    st.subheader("Filtres")
    
    # Filtre réseau
    reseaux_selected = st.multiselect(
        "Réseau",
        options=df['Réseau'].unique().tolist(),
        default=df['Réseau'].unique().tolist()
    )
    
    # Filtre ville
    villes_selected = st.multiselect(
        "Ville",
        options=sorted(df['Ville'].unique().tolist()),
        default=None
    )
    
    # Filtre par ligne
    toutes_lignes = []
    correspondances_cols = ['Correspondance_1', 'Correspondance_2', 'Correspondance_3', 
                           'Correspondance_4', 'Correspondance_5']
    for col in correspondances_cols:
        lignes = df[col].dropna().unique().tolist()
        toutes_lignes.extend([str(l).strip() for l in lignes if str(l).strip() != ''])
    
    toutes_lignes = sorted(list(set(toutes_lignes)))
    
    lignes_selected = st.multiselect(
        "Ligne(s)",
        options=toutes_lignes,
        default=None
    )
    
    # Filtre trafic
    trafic_min, trafic_max = st.slider(
        "Plage de trafic",
        min_value=int(df['Trafic'].min()),
        max_value=int(df['Trafic'].max()),
        value=(int(df['Trafic'].min()), int(df['Trafic'].max())),
        format="%d"
    )
    
    # Recherche textuelle
    search_station = st.text_input("Rechercher une station")

# Appliquer les filtres
df_filtered = df.copy()

if reseaux_selected:
    df_filtered = df_filtered[df_filtered['Réseau'].isin(reseaux_selected)]

if villes_selected:
    df_filtered = df_filtered[df_filtered['Ville'].isin(villes_selected)]

if lignes_selected:
    # Filtrer les stations qui ont au moins une des lignes sélectionnées
    mask = df_filtered[correspondances_cols].isin(lignes_selected).any(axis=1)
    df_filtered = df_filtered[mask]

df_filtered = df_filtered[
    (df_filtered['Trafic'] >= trafic_min) & 
    (df_filtered['Trafic'] <= trafic_max)
]

if search_station:
    df_filtered = df_filtered[
        df_filtered['Station'].str.contains(search_station, case=False, na=False)
    ]

# Affichage des résultats
st.subheader(f"Résultats : {len(df_filtered)} stations")

if len(df_filtered) > 0:
    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Stations", len(df_filtered))
    
    with col2:
        st.metric("Trafic total", f"{df_filtered['Trafic'].sum():,.0f}")
    
    with col3:
        st.metric("Trafic moyen", f"{df_filtered['Trafic'].mean():,.0f}")
    
    with col4:
        st.metric("Trafic médian", f"{df_filtered['Trafic'].median():,.0f}")
    
    st.markdown("---")
    
    # Graphique dynamique
    graph_type = st.selectbox(
        "Type de graphique",
        ["Top 20 stations", "Histogramme de distribution"]
    )
    
    if graph_type == "Top 20 stations":
        df_top20 = df_filtered.nlargest(20, 'Trafic')
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Couleurs par réseau (couleurs RATP)
        colors = df_top20['Réseau'].map({'Métro': COLORS_RATP['bleu'], 'RER': COLORS_RATP['vert']})
        bars = ax.barh(df_top20['Station'], df_top20['Trafic'], color=colors, alpha=0.85, 
                      edgecolor=COLORS_RATP['noir'], linewidth=1.2)
        
        ax.set_xlabel('Trafic annuel', fontsize=12, fontweight='bold')
        ax.set_ylabel('Station', fontsize=12, fontweight='bold')
        ax.set_title('Top 20 des stations (données filtrées)', fontsize=14, fontweight='bold', 
                    pad=20, color=COLORS_RATP['bleu'])
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
        ax.grid(axis='x', alpha=0.3, linestyle='--', color=COLORS_RATP['noir'])
        ax.invert_yaxis()
        
        # Légende avec couleurs RATP
        metro_patch = mpatches.Patch(color=COLORS_RATP['bleu'], label='Métro', alpha=0.85)
        rer_patch = mpatches.Patch(color=COLORS_RATP['vert'], label='RER', alpha=0.85)
        ax.legend(handles=[metro_patch, rer_patch], loc='lower right')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    else:  # Histogramme
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Créer un histogramme avec couleurs RATP
        if 'Réseau' in df_filtered.columns and len(df_filtered['Réseau'].unique()) > 1:
            for reseau in df_filtered['Réseau'].unique():
                data = df_filtered[df_filtered['Réseau'] == reseau]['Trafic']
                color = COLORS_RATP['bleu'] if reseau == 'Métro' else COLORS_RATP['vert']
                ax.hist(data, bins=30, alpha=0.7, label=reseau, color=color, 
                       edgecolor=COLORS_RATP['noir'], linewidth=0.8)
            ax.legend(loc='upper right', fontsize=11)
        else:
            ax.hist(df_filtered['Trafic'], bins=30, alpha=0.75, color=COLORS_RATP['bleu'], 
                   edgecolor=COLORS_RATP['noir'], linewidth=0.8)
        
        ax.set_xlabel('Trafic annuel', fontsize=12, fontweight='bold')
        ax.set_ylabel('Nombre de stations', fontsize=12, fontweight='bold')
        ax.set_title('Distribution du trafic (données filtrées)', fontsize=14, fontweight='bold', 
                    pad=20, color=COLORS_RATP['bleu'])
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
        ax.grid(axis='y', alpha=0.3, linestyle='--', color=COLORS_RATP['noir'])
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    st.markdown("---")
    
    # Tableau de données
    st.subheader("Données filtrées")
    
    # Colonnes à afficher
    colonnes_affichage = ['Rang', 'Réseau', 'Station', 'Trafic', 'Lignes', 'Ville', 'Arrondissement pour Paris']
    df_display = df_filtered[colonnes_affichage].copy()
    
    # Trier par trafic
    df_display = df_display.sort_values('Trafic', ascending=False)
    
    st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)
    
    # Export CSV
    st.markdown("---")
    st.subheader("Export des données")
    
    csv = df_display.to_csv(index=False, sep=';').encode('utf-8')
    
    st.download_button(
        label="Télécharger les données filtrées (CSV)",
        data=csv,
        file_name='ratp_data_filtered.csv',
        mime='text/csv',
    )

else:
    st.warning("Aucune station ne correspond à vos critères de filtrage.")
