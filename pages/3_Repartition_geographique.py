import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# Ajouter le répertoire parent au path pour importer utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_data, display_logo, COLORS_RATP, configure_matplotlib

# Configuration
st.set_page_config(
    page_title="Répartition géographique - RATP",
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
st.title("Répartition géographique")
st.markdown("Analysez la distribution géographique du trafic RATP.")

# Choix du mode d'analyse
mode = st.radio(
    "Mode d'analyse :",
    ["Par arrondissement (Paris)", "Par ville", "Par réseau/zone"],
    horizontal=True
)

st.markdown("---")

if mode == "Par arrondissement (Paris)":
    st.subheader("Trafic par arrondissement parisien")

    # Filtrer Paris uniquement
    df_paris = df[df['Ville'] == 'Paris'].copy()
    df_paris = df_paris[df_paris['Arrondissement pour Paris'] != ''].copy()
    
    # Agréger par arrondissement et trier par numéro
    arr_stats = df_paris.groupby('Arrondissement pour Paris')['Trafic'].sum().reset_index()
    arr_stats.columns = ['Arrondissement', 'Trafic_total']
    arr_stats = arr_stats.sort_values('Arrondissement')
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Palette de bleus pour les arrondissements (couleurs RATP)
        n_arr = len(arr_stats)
        colors_arr = sns.light_palette(COLORS_RATP['bleu'], n_colors=n_arr, reverse=True)
        
        bars = ax.bar(arr_stats['Arrondissement'], arr_stats['Trafic_total'], 
                     color=colors_arr, alpha=0.85, edgecolor=COLORS_RATP['noir'], linewidth=1.2)
        
        ax.set_xlabel('Arrondissement', fontsize=12, fontweight='bold')
        ax.set_ylabel('Trafic total', fontsize=12, fontweight='bold')
        ax.set_title('Trafic total par arrondissement de Paris', fontsize=14, fontweight='bold', 
                    pad=20, color=COLORS_RATP['bleu'])
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
        ax.grid(axis='y', alpha=0.3, linestyle='--', color=COLORS_RATP['noir'])
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.markdown("### Top 5 arrondissements")
        arr_stats_sorted = arr_stats.sort_values('Trafic_total', ascending=False)
        for idx, row in arr_stats_sorted.head(5).iterrows():
            st.markdown(f"**{row['Arrondissement']}** : {row['Trafic_total']:,.0f}")
        
        st.markdown("---")
        st.metric("Total arrondissements", len(arr_stats))
        st.metric("Trafic total Paris", f"{arr_stats['Trafic_total'].sum():,.0f}")

elif mode == "Par ville":
    st.subheader("Trafic par ville")
    
    ville_stats = df.groupby('Ville')['Trafic'].sum().reset_index()
    ville_stats.columns = ['Ville', 'Trafic_total']
    ville_stats = ville_stats.sort_values('Trafic_total', ascending=False)
    
    # Top 20
    top_n_villes = st.slider("Nombre de villes à afficher", 10, 50, 20)
    ville_stats_top = ville_stats.head(top_n_villes)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Palette de verts pour les villes (couleurs RATP)
        n_villes = len(ville_stats_top)
        colors_villes = sns.light_palette(COLORS_RATP['vert'], n_colors=n_villes, reverse=True)
        
        bars = ax.barh(ville_stats_top['Ville'], ville_stats_top['Trafic_total'],
                      color=colors_villes, alpha=0.85, edgecolor=COLORS_RATP['noir'], linewidth=1.2)
        
        ax.set_xlabel('Trafic total', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ville', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n_villes} des villes par trafic', fontsize=14, fontweight='bold', 
                    pad=20, color=COLORS_RATP['bleu'])
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
        ax.grid(axis='x', alpha=0.3, linestyle='--', color=COLORS_RATP['noir'])
        ax.invert_yaxis()  # Pour avoir la plus haute valeur en haut
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.markdown("### Top 5 villes")
        for idx, row in ville_stats.head(5).iterrows():
            st.markdown(f"**{row['Ville']}** : {row['Trafic_total']:,.0f}")
        
        st.markdown("---")
        st.metric("Nombre total de villes", len(ville_stats))

else:  # Par réseau/zone
    st.subheader("Répartition par réseau et zone")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Par réseau
        reseau_stats = df.groupby('Réseau')['Trafic'].sum().reset_index()
        reseau_stats.columns = ['Réseau', 'Trafic_total']
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Couleurs RATP pour réseau
        colors_reseau = [COLORS_RATP['bleu'] if r == 'Métro' else COLORS_RATP['vert'] for r in reseau_stats['Réseau']]
        
        wedges, texts, autotexts = ax.pie(
            reseau_stats['Trafic_total'],
            labels=reseau_stats['Réseau'],
            autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*reseau_stats["Trafic_total"].sum()):,})',
            startangle=90,
            colors=colors_reseau,
            textprops={'fontsize': 11, 'weight': 'bold', 'color': 'white'},
            wedgeprops={'edgecolor': 'white', 'linewidth': 3}
        )
        
        ax.set_title('Répartition du trafic par réseau', fontsize=14, fontweight='bold', 
                    pad=20, color=COLORS_RATP['bleu'])
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col2:
        # Par zone (Paris vs Banlieue)
        df_copy = df.copy()
        df_copy['Zone'] = df_copy['Ville'].apply(lambda x: 'Paris' if x == 'Paris' else 'Banlieue')
        zone_stats = df_copy.groupby('Zone')['Trafic'].sum().reset_index()
        zone_stats.columns = ['Zone', 'Trafic_total']
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Couleurs RATP pour zones
        colors_zone = [COLORS_RATP['jaune'] if z == 'Paris' else COLORS_RATP['rouge'] for z in zone_stats['Zone']]
        
        wedges, texts, autotexts = ax.pie(
            zone_stats['Trafic_total'],
            labels=zone_stats['Zone'],
            autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*zone_stats["Trafic_total"].sum()):,})',
            startangle=90,
            colors=colors_zone,
            textprops={'fontsize': 11, 'weight': 'bold', 'color': 'white'},
            wedgeprops={'edgecolor': 'white', 'linewidth': 3}
        )
        
        ax.set_title('Répartition du trafic Paris vs Banlieue', fontsize=14, fontweight='bold', 
                    pad=20, color=COLORS_RATP['bleu'])
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    st.markdown("---")
    
    # Tableau croisé
    st.subheader("Tableau croisé Réseau × Zone")
    
    df_copy['Zone'] = df_copy['Ville'].apply(lambda x: 'Paris' if x == 'Paris' else 'Banlieue')
    cross_stats = df_copy.groupby(['Réseau', 'Zone'])['Trafic'].sum().reset_index()
    pivot_table = cross_stats.pivot(index='Réseau', columns='Zone', values='Trafic').fillna(0)
    
    st.dataframe(pivot_table.style.format("{:,.0f}"), use_container_width=True)
