"""
Fonctions utilitaires communes pour le dashboard RATP
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import os

# Couleurs RATP officielles
COLORS_RATP = {
    'bleu': '#100FAA',
    'vert': '#00C0AF',
    'jaune': '#FFCD00',
    'rouge': '#DC143C',
    'metro': "#197972",
    'rer': '#FF6B6B',
    'noir': '#1D1D1B'
}

# Configuration matplotlib
def configure_matplotlib():
    """Configure matplotlib avec les couleurs RATP"""
    plt.style.use('seaborn-v0_8-whitegrid')
    custom_palette = [COLORS_RATP['bleu'], COLORS_RATP['vert'], COLORS_RATP['jaune'], 
                      COLORS_RATP['rouge'], COLORS_RATP['metro'], COLORS_RATP['rer']]
    sns.set_palette(custom_palette)
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelcolor'] = COLORS_RATP['noir']
    plt.rcParams['text.color'] = COLORS_RATP['noir']
    plt.rcParams['xtick.color'] = COLORS_RATP['noir']
    plt.rcParams['ytick.color'] = COLORS_RATP['noir']

def display_logo():
    """Affiche le logo RATP au-dessus de la navigation"""
    logo_path = 'assets/logo_ratp.png'
    if os.path.exists(logo_path):
        try:
            st.logo(logo_path, icon_image=logo_path)
        except:
            pass

@st.cache_data
def load_data():
    """Charge et prepare les donnees RATP"""
    df = pd.read_csv('data/trafic-annuel-entrant-par-station-du-reseau-ferre-2021.csv', sep=';')
    
    correspondances_cols = ['Correspondance_1', 'Correspondance_2', 'Correspondance_3', 
                           'Correspondance_4', 'Correspondance_5']
    
    def get_lignes(row):
        lignes = []
        for col in correspondances_cols:
            if pd.notna(row[col]) and str(row[col]).strip() != '':
                lignes.append(str(row[col]).strip())
        return ', '.join(lignes) if lignes else '-'
    
    df['Lignes'] = df.apply(get_lignes, axis=1)
    
    df['Trafic'] = pd.to_numeric(df['Trafic'], errors='coerce')
    
    df['Arrondissement pour Paris'] = df['Arrondissement pour Paris'].apply(
        lambda x: int(x) if pd.notna(x) and str(x).strip() != '' else ''
    )
    
    return df

@st.cache_data
def prepare_ligne_data(df):
    """Prepare les donnees agregees par ligne"""
    rows = []
    correspondances_cols = ['Correspondance_1', 'Correspondance_2', 'Correspondance_3', 
                           'Correspondance_4', 'Correspondance_5']
    
    for idx, row in df.iterrows():
        for col in correspondances_cols:
            if pd.notna(row[col]) and str(row[col]).strip() != '':
                ligne = str(row[col]).strip()
                
                try:
                    ligne = str(int(float(ligne)))
                except (ValueError, TypeError):
                    pass
                
                rows.append({
                    'Ligne': ligne,
                    'Station': row['Station'],
                    'Réseau': row['Réseau'],
                    'Trafic': row['Trafic']
                })
    
    df_lignes = pd.DataFrame(rows)
    
    stats_lignes = df_lignes.groupby('Ligne').agg({
        'Trafic': 'sum',
        'Station': 'nunique',
        'Réseau': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]
    }).reset_index()
    
    stats_lignes.columns = ['Ligne', 'Trafic_total', 'Nb_stations', 'Réseau']
    stats_lignes['Trafic_moyen_station'] = stats_lignes['Trafic_total'] / stats_lignes['Nb_stations']
    stats_lignes['Part_trafic_pct'] = (stats_lignes['Trafic_total'] / stats_lignes['Trafic_total'].sum()) * 100
    
    return stats_lignes, df_lignes
