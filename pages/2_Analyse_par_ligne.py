import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
import os

# Ajouter le répertoire parent au path pour importer utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_data, prepare_ligne_data, display_logo, COLORS_RATP, configure_matplotlib

# Configuration
st.set_page_config(
    page_title="Analyse par ligne - RATP",
    page_icon="assets/RATP.png",
    layout="wide"
)

# Configuration matplotlib
configure_matplotlib()

# Logo
display_logo()

# Chargement des données
df = load_data()
stats_lignes, df_lignes = prepare_ligne_data(df)

# Titre
st.title("Analyse par ligne")
st.markdown("Comparez les performances des différentes lignes du réseau ferré RATP.")

# Filtre par réseau
col_f1, col_f2 = st.columns([1, 3])

with col_f1:
    reseau_filter = st.selectbox("Filtrer par réseau", ['Tous', 'Métro', 'RER'])

if reseau_filter != 'Tous':
    stats_lignes_filtered = stats_lignes[stats_lignes['Réseau'] == reseau_filter].copy()
else:
    stats_lignes_filtered = stats_lignes.copy()

# Trier par trafic total
stats_lignes_filtered = stats_lignes_filtered.sort_values('Trafic_total', ascending=False)

# Tableau récapitulatif
st.subheader("Tableau récapitulatif par ligne")

# Formater le dataframe pour l'affichage
df_display = stats_lignes_filtered.copy()
df_display['Trafic_total'] = df_display['Trafic_total'].apply(lambda x: f"{x:,.0f}")
df_display['Trafic_moyen_station'] = df_display['Trafic_moyen_station'].apply(lambda x: f"{x:,.0f}")
df_display['Part_trafic_pct'] = df_display['Part_trafic_pct'].apply(lambda x: f"{x:.2f}%")

df_display.columns = ['Ligne', 'Trafic total', 'Nb stations', 'Réseau', 'Trafic moyen/station', 'Part du trafic (%)']

st.dataframe(df_display, use_container_width=True, hide_index=True)

st.markdown("---")

# Graphiques
graph_col1, graph_col2 = st.columns(2)

with graph_col1:
    st.subheader("Trafic total par ligne")

    fig, ax = plt.subplots(figsize=(12, 6))
    
    data_plot = stats_lignes_filtered.head(15).copy()
    
    # Créer le graphique avec couleurs par réseau (couleurs RATP)
    colors = data_plot['Réseau'].map({'Métro': COLORS_RATP['bleu'], 'RER': COLORS_RATP['vert']})
    bars = ax.bar(data_plot['Ligne'], data_plot['Trafic_total'], color=colors, alpha=0.85, 
                 edgecolor=COLORS_RATP['noir'], linewidth=1.2)
    
    ax.set_xlabel('Ligne', fontsize=12, fontweight='bold')
    ax.set_ylabel('Trafic total', fontsize=12, fontweight='bold')
    ax.set_title(f'Top 15 des lignes - Trafic total ({reseau_filter})', fontsize=14, fontweight='bold', 
                pad=20, color=COLORS_RATP['bleu'])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
    ax.grid(axis='y', alpha=0.3, linestyle='--', color=COLORS_RATP['noir'])
    plt.xticks(rotation=45, ha='right')
    
    # Légende avec couleurs RATP
    metro_patch = mpatches.Patch(color=COLORS_RATP['bleu'], label='Métro', alpha=0.85)
    rer_patch = mpatches.Patch(color=COLORS_RATP['vert'], label='RER', alpha=0.85)
    ax.legend(handles=[metro_patch, rer_patch], loc='upper right')
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with graph_col2:
    st.subheader("Trafic moyen par station")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    data_plot = stats_lignes_filtered.head(15).copy()
    
    # Créer le graphique avec couleurs par réseau (couleurs RATP)
    colors = data_plot['Réseau'].map({'Métro': COLORS_RATP['jaune'], 'RER': COLORS_RATP['rouge']})
    bars = ax.bar(data_plot['Ligne'], data_plot['Trafic_moyen_station'], color=colors, alpha=0.85, 
                 edgecolor=COLORS_RATP['noir'], linewidth=1.2)
    
    ax.set_xlabel('Ligne', fontsize=12, fontweight='bold')
    ax.set_ylabel('Trafic moyen/station', fontsize=12, fontweight='bold')
    ax.set_title(f'Top 15 des lignes - Trafic moyen/station ({reseau_filter})', fontsize=14, fontweight='bold', 
                pad=20, color=COLORS_RATP['bleu'])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
    ax.grid(axis='y', alpha=0.3, linestyle='--', color=COLORS_RATP['noir'])
    plt.xticks(rotation=45, ha='right')
    
    # Légende avec couleurs RATP
    metro_patch = mpatches.Patch(color=COLORS_RATP['jaune'], label='Métro', alpha=0.85)
    rer_patch = mpatches.Patch(color=COLORS_RATP['rouge'], label='RER', alpha=0.85)
    ax.legend(handles=[metro_patch, rer_patch], loc='upper right')
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# Graphique camembert
st.subheader("Répartition du trafic par ligne")

pie_col1, pie_col2 = st.columns([2, 1])

with pie_col1:
    # Prendre top 10 + "Autres"
    top_n = 10
    stats_top = stats_lignes_filtered.head(top_n).copy()
    
    if len(stats_lignes_filtered) > top_n:
        autres_trafic = stats_lignes_filtered.iloc[top_n:]['Trafic_total'].sum()
        autres_row = pd.DataFrame([{
            'Ligne': 'Autres',
            'Trafic_total': autres_trafic,
            'Réseau': 'Mixte'
        }])
        stats_for_pie = pd.concat([stats_top, autres_row], ignore_index=True)
    else:
        stats_for_pie = stats_top
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Couleurs personnalisées RATP
    color_map = {'Métro': COLORS_RATP['bleu'], 'RER': COLORS_RATP['vert'], 'Mixte': '#95A5A6'}
    colors = [color_map.get(r, '#95A5A6') for r in stats_for_pie['Réseau']]
    
    wedges, texts, autotexts = ax.pie(
        stats_for_pie['Trafic_total'], 
        labels=stats_for_pie['Ligne'],
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 10, 'weight': 'bold', 'color': COLORS_RATP['noir']},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    
    ax.set_title(f'Part du trafic total par ligne (Top {top_n})', fontsize=14, fontweight='bold', 
                pad=20, color=COLORS_RATP['bleu'])
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with pie_col2:
    st.markdown("### Insights")
    
    ligne_max = stats_lignes_filtered.iloc[0]
    st.success(f"**Ligne la plus fréquentée :** {ligne_max['Ligne']}\n\n"
              f"Trafic : {ligne_max['Trafic_total']:,.0f}")
    
    ligne_avg = stats_lignes_filtered.iloc[0]
    st.info(f"**Meilleur trafic moyen/station :** {stats_lignes_filtered.sort_values('Trafic_moyen_station', ascending=False).iloc[0]['Ligne']}")
    
    total_lignes = len(stats_lignes_filtered)
    st.metric("Nombre de lignes", total_lignes)
