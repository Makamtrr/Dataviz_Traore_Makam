import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches

# Configuration de matplotlib et seaborn
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10

# Configuration de la page
st.set_page_config(
    page_title="Dashboard RATP 2021",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction de chargement et préparation des données
@st.cache_data
def load_data():
    """Charge et prépare les données RATP"""
    df = pd.read_csv('data/trafic-annuel-entrant-par-station-du-reseau-ferre-2021.csv', sep=';')
    
    # Créer une colonne avec toutes les lignes concaténées
    correspondances_cols = ['Correspondance_1', 'Correspondance_2', 'Correspondance_3', 
                           'Correspondance_4', 'Correspondance_5']
    
    def get_lignes(row):
        lignes = []
        for col in correspondances_cols:
            if pd.notna(row[col]) and str(row[col]).strip() != '':
                lignes.append(str(row[col]).strip())
        return ', '.join(lignes) if lignes else '-'
    
    df['Lignes'] = df.apply(get_lignes, axis=1)
    
    # Nettoyer les colonnes
    df['Trafic'] = pd.to_numeric(df['Trafic'], errors='coerce')
    df['Arrondissement pour Paris'] = df['Arrondissement pour Paris'].fillna('')
    
    return df

@st.cache_data
def prepare_ligne_data(df):
    """Prépare les données agrégées par ligne"""
    rows = []
    correspondances_cols = ['Correspondance_1', 'Correspondance_2', 'Correspondance_3', 
                           'Correspondance_4', 'Correspondance_5']
    
    for idx, row in df.iterrows():
        for col in correspondances_cols:
            if pd.notna(row[col]) and str(row[col]).strip() != '':
                ligne = str(row[col]).strip()
                rows.append({
                    'Ligne': ligne,
                    'Station': row['Station'],
                    'Réseau': row['Réseau'],
                    'Trafic': row['Trafic']
                })
    
    df_lignes = pd.DataFrame(rows)
    
    # Agréger par ligne
    stats_lignes = df_lignes.groupby('Ligne').agg({
        'Trafic': 'sum',
        'Station': 'nunique',
        'Réseau': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]
    }).reset_index()
    
    stats_lignes.columns = ['Ligne', 'Trafic_total', 'Nb_stations', 'Réseau']
    stats_lignes['Trafic_moyen_station'] = stats_lignes['Trafic_total'] / stats_lignes['Nb_stations']
    stats_lignes['Part_trafic_pct'] = (stats_lignes['Trafic_total'] / stats_lignes['Trafic_total'].sum()) * 100
    
    return stats_lignes, df_lignes

# Chargement des données
try:
    df = load_data()
    stats_lignes, df_lignes = prepare_ligne_data(df)
except Exception as e:
    st.error(f"Erreur lors du chargement des données : {e}")
    st.stop()

# Sidebar avec navigation
st.sidebar.title("🚇 Navigation")
page = st.sidebar.radio(
    "Choisir une page :",
    ["📊 Analyse par station", "🚉 Analyse par ligne", "🗺️ Répartition géographique", "🔍 Exploration libre"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"**{len(df)}** stations\n\n**{df['Trafic'].sum():,.0f}** voyageurs total")

# ========== PAGE 1 : ANALYSE PAR STATION ==========
if page == "📊 Analyse par station":
    st.title("📊 Analyse par station")
    st.markdown("Explorez les détails d'une station et comparez-la aux moyennes du réseau.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🔍 Filtres")
        
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
        st.subheader("📋 Fiche station")
        
        # Affichage des informations
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.metric("Trafic annuel", f"{station_data['Trafic']:,.0f}")
        
        with info_col2:
            st.metric("Réseau", station_data['Réseau'])
        
        with info_col3:
            rang = station_data['Rang']
            st.metric("Rang national", f"#{int(rang)}")
        
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
    
    st.subheader(f"📈 Comparaison avec le {reseau_label}")
    
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
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)
        
        # Ajouter les valeurs sur les barres
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:,.0f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_ylabel('Trafic annuel', fontsize=12, fontweight='bold')
        ax.set_title(f'Comparaison du trafic - {station_choisie}', fontsize=14, fontweight='bold', pad=20)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

# ========== PAGE 2 : ANALYSE PAR LIGNE ==========
elif page == "🚉 Analyse par ligne":
    st.title("🚉 Analyse par ligne")
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
    st.subheader("📋 Tableau récapitulatif par ligne")
    
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
        st.subheader("📊 Trafic total par ligne")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        data_plot = stats_lignes_filtered.head(15).copy()
        
        # Créer le graphique avec couleurs par réseau
        colors = data_plot['Réseau'].map({'Métro': '#4ECDC4', 'RER': '#FF6B6B'})
        bars = ax.bar(data_plot['Ligne'], data_plot['Trafic_total'], color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        ax.set_xlabel('Ligne', fontsize=12, fontweight='bold')
        ax.set_ylabel('Trafic total', fontsize=12, fontweight='bold')
        ax.set_title(f'Top 15 des lignes - Trafic total ({reseau_filter})', fontsize=14, fontweight='bold', pad=20)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        plt.xticks(rotation=45, ha='right')
        
        # Légende
        metro_patch = mpatches.Patch(color='#4ECDC4', label='Métro', alpha=0.8)
        rer_patch = mpatches.Patch(color='#FF6B6B', label='RER', alpha=0.8)
        ax.legend(handles=[metro_patch, rer_patch], loc='upper right')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with graph_col2:
        st.subheader("📊 Trafic moyen par station")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        data_plot = stats_lignes_filtered.head(15).copy()
        
        # Créer le graphique avec couleurs par réseau
        colors = data_plot['Réseau'].map({'Métro': '#45B7D1', 'RER': '#FFA07A'})
        bars = ax.bar(data_plot['Ligne'], data_plot['Trafic_moyen_station'], color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        ax.set_xlabel('Ligne', fontsize=12, fontweight='bold')
        ax.set_ylabel('Trafic moyen/station', fontsize=12, fontweight='bold')
        ax.set_title(f'Top 15 des lignes - Trafic moyen/station ({reseau_filter})', fontsize=14, fontweight='bold', pad=20)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        plt.xticks(rotation=45, ha='right')
        
        # Légende
        metro_patch = mpatches.Patch(color='#45B7D1', label='Métro', alpha=0.8)
        rer_patch = mpatches.Patch(color='#FFA07A', label='RER', alpha=0.8)
        ax.legend(handles=[metro_patch, rer_patch], loc='upper right')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    st.markdown("---")
    
    # Graphique camembert
    st.subheader("🥧 Répartition du trafic par ligne")
    
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
        
        # Couleurs personnalisées
        color_map = {'Métro': '#4ECDC4', 'RER': '#FF6B6B', 'Mixte': '#95A5A6'}
        colors = [color_map.get(r, '#95A5A6') for r in stats_for_pie['Réseau']]
        
        wedges, texts, autotexts = ax.pie(
            stats_for_pie['Trafic_total'], 
            labels=stats_for_pie['Ligne'],
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 10, 'weight': 'bold'}
        )
        
        ax.set_title(f'Part du trafic total par ligne (Top {top_n})', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with pie_col2:
        st.markdown("### 📌 Insights")
        
        ligne_max = stats_lignes_filtered.iloc[0]
        st.success(f"**Ligne la plus fréquentée :** {ligne_max['Ligne']}\n\n"
                  f"Trafic : {ligne_max['Trafic_total']:,.0f}")
        
        ligne_avg = stats_lignes_filtered.iloc[0]
        st.info(f"**Meilleur trafic moyen/station :** {stats_lignes_filtered.sort_values('Trafic_moyen_station', ascending=False).iloc[0]['Ligne']}")
        
        total_lignes = len(stats_lignes_filtered)
        st.metric("Nombre de lignes", total_lignes)

# ========== PAGE 3 : RÉPARTITION GÉOGRAPHIQUE ==========
elif page == "🗺️ Répartition géographique":
    st.title("🗺️ Répartition géographique")
    st.markdown("Analysez la distribution géographique du trafic RATP.")
    
    # Choix du mode d'analyse
    mode = st.radio(
        "Mode d'analyse :",
        ["Par arrondissement (Paris)", "Par ville", "Par réseau/zone"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if mode == "Par arrondissement (Paris)":
        st.subheader("📍 Trafic par arrondissement parisien")
        
        # Filtrer Paris uniquement
        df_paris = df[df['Ville'] == 'Paris'].copy()
        df_paris = df_paris[df_paris['Arrondissement pour Paris'] != ''].copy()
        
        # Agréger par arrondissement
        arr_stats = df_paris.groupby('Arrondissement pour Paris')['Trafic'].sum().reset_index()
        arr_stats.columns = ['Arrondissement', 'Trafic_total']
        arr_stats = arr_stats.sort_values('Trafic_total', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            bars = ax.bar(arr_stats['Arrondissement'], arr_stats['Trafic_total'], 
                         color=sns.color_palette('Blues_r', len(arr_stats)), 
                         alpha=0.8, edgecolor='black', linewidth=1)
            
            ax.set_xlabel('Arrondissement', fontsize=12, fontweight='bold')
            ax.set_ylabel('Trafic total', fontsize=12, fontweight='bold')
            ax.set_title('Trafic total par arrondissement de Paris', fontsize=14, fontweight='bold', pad=20)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.markdown("### 🏆 Top 5 arrondissements")
            for idx, row in arr_stats.head(5).iterrows():
                st.markdown(f"**{row['Arrondissement']}** : {row['Trafic_total']:,.0f}")
            
            st.markdown("---")
            st.metric("Total arrondissements", len(arr_stats))
            st.metric("Trafic total Paris", f"{arr_stats['Trafic_total'].sum():,.0f}")
    
    elif mode == "Par ville":
        st.subheader("🏙️ Trafic par ville")
        
        ville_stats = df.groupby('Ville')['Trafic'].sum().reset_index()
        ville_stats.columns = ['Ville', 'Trafic_total']
        ville_stats = ville_stats.sort_values('Trafic_total', ascending=False)
        
        # Top 20
        top_n_villes = st.slider("Nombre de villes à afficher", 10, 50, 20)
        ville_stats_top = ville_stats.head(top_n_villes)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(12, 10))
            
            bars = ax.barh(ville_stats_top['Ville'], ville_stats_top['Trafic_total'],
                          color=sns.color_palette('viridis', len(ville_stats_top)),
                          alpha=0.8, edgecolor='black', linewidth=1)
            
            ax.set_xlabel('Trafic total', fontsize=12, fontweight='bold')
            ax.set_ylabel('Ville', fontsize=12, fontweight='bold')
            ax.set_title(f'Top {top_n_villes} des villes par trafic', fontsize=14, fontweight='bold', pad=20)
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            ax.invert_yaxis()  # Pour avoir la plus haute valeur en haut
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.markdown("### 🏆 Top 5 villes")
            for idx, row in ville_stats.head(5).iterrows():
                st.markdown(f"**{row['Ville']}** : {row['Trafic_total']:,.0f}")
            
            st.markdown("---")
            st.metric("Nombre total de villes", len(ville_stats))
    
    else:  # Par réseau/zone
        st.subheader("🚇 Répartition par réseau et zone")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Par réseau
            reseau_stats = df.groupby('Réseau')['Trafic'].sum().reset_index()
            reseau_stats.columns = ['Réseau', 'Trafic_total']
            
            fig, ax = plt.subplots(figsize=(8, 8))
            
            colors_reseau = ['#4ECDC4' if r == 'Métro' else '#FF6B6B' for r in reseau_stats['Réseau']]
            
            wedges, texts, autotexts = ax.pie(
                reseau_stats['Trafic_total'],
                labels=reseau_stats['Réseau'],
                autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*reseau_stats["Trafic_total"].sum()):,})',
                startangle=90,
                colors=colors_reseau,
                textprops={'fontsize': 11, 'weight': 'bold'}
            )
            
            ax.set_title('Répartition du trafic par réseau', fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col2:
            # Par zone (Paris vs Banlieue)
            df['Zone'] = df['Ville'].apply(lambda x: 'Paris' if x == 'Paris' else 'Banlieue')
            zone_stats = df.groupby('Zone')['Trafic'].sum().reset_index()
            zone_stats.columns = ['Zone', 'Trafic_total']
            
            fig, ax = plt.subplots(figsize=(8, 8))
            
            colors_zone = ['#E74C3C' if z == 'Paris' else '#3498DB' for z in zone_stats['Zone']]
            
            wedges, texts, autotexts = ax.pie(
                zone_stats['Trafic_total'],
                labels=zone_stats['Zone'],
                autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*zone_stats["Trafic_total"].sum()):,})',
                startangle=90,
                colors=colors_zone,
                textprops={'fontsize': 11, 'weight': 'bold'}
            )
            
            ax.set_title('Répartition du trafic Paris vs Banlieue', fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        st.markdown("---")
        
        # Tableau croisé
        st.subheader("📊 Tableau croisé Réseau × Zone")
        
        cross_stats = df.groupby(['Réseau', 'Zone'])['Trafic'].sum().reset_index()
        pivot_table = cross_stats.pivot(index='Réseau', columns='Zone', values='Trafic').fillna(0)
        
        st.dataframe(pivot_table.style.format("{:,.0f}"), use_container_width=True)

# ========== PAGE 4 : EXPLORATION LIBRE ==========
else:  # Exploration libre
    st.title("🔍 Exploration libre des données")
    st.markdown("Filtrez et explorez les données selon vos critères.")
    
    # Sidebar de filtres
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔧 Filtres")
        
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
        search_station = st.text_input("🔎 Rechercher une station")
    
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
    st.subheader(f"📊 Résultats : {len(df_filtered)} stations")
    
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
            
            # Couleurs par réseau
            colors = df_top20['Réseau'].map({'Métro': '#4ECDC4', 'RER': '#FF6B6B'})
            bars = ax.barh(df_top20['Station'], df_top20['Trafic'], color=colors, alpha=0.8, edgecolor='black', linewidth=1)
            
            ax.set_xlabel('Trafic annuel', fontsize=12, fontweight='bold')
            ax.set_ylabel('Station', fontsize=12, fontweight='bold')
            ax.set_title('Top 20 des stations (données filtrées)', fontsize=14, fontweight='bold', pad=20)
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            ax.invert_yaxis()
            
            # Légende
            metro_patch = mpatches.Patch(color='#4ECDC4', label='Métro', alpha=0.8)
            rer_patch = mpatches.Patch(color='#FF6B6B', label='RER', alpha=0.8)
            ax.legend(handles=[metro_patch, rer_patch], loc='lower right')
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        else:  # Histogramme
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Créer un histogramme avec seaborn pour plus de style
            if 'Réseau' in df_filtered.columns and len(df_filtered['Réseau'].unique()) > 1:
                for reseau in df_filtered['Réseau'].unique():
                    data = df_filtered[df_filtered['Réseau'] == reseau]['Trafic']
                    color = '#4ECDC4' if reseau == 'Métro' else '#FF6B6B'
                    ax.hist(data, bins=30, alpha=0.6, label=reseau, color=color, edgecolor='black', linewidth=0.5)
                ax.legend(loc='upper right', fontsize=11)
            else:
                ax.hist(df_filtered['Trafic'], bins=30, alpha=0.7, color='#4ECDC4', edgecolor='black', linewidth=0.5)
            
            ax.set_xlabel('Trafic annuel', fontsize=12, fontweight='bold')
            ax.set_ylabel('Nombre de stations', fontsize=12, fontweight='bold')
            ax.set_title('Distribution du trafic (données filtrées)', fontsize=14, fontweight='bold', pad=20)
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6):.1f}M' if x >= 1e6 else f'{int(x/1e3):.0f}K'))
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        st.markdown("---")
        
        # Tableau de données
        st.subheader("📋 Données filtrées")
        
        # Colonnes à afficher
        colonnes_affichage = ['Rang', 'Réseau', 'Station', 'Trafic', 'Lignes', 'Ville', 'Arrondissement pour Paris']
        df_display = df_filtered[colonnes_affichage].copy()
        
        # Trier par trafic
        df_display = df_display.sort_values('Trafic', ascending=False)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)
        
        # Export CSV
        st.markdown("---")
        st.subheader("💾 Export des données")
        
        csv = df_display.to_csv(index=False, sep=';').encode('utf-8')
        
        st.download_button(
            label="📥 Télécharger les données filtrées (CSV)",
            data=csv,
            file_name='ratp_data_filtered.csv',
            mime='text/csv',
        )
    
    else:
        st.warning("⚠️ Aucune station ne correspond à vos critères de filtrage.")
