# 🚇 Dashboard RATP - Analyse du trafic 2021

Dashboard interactif Streamlit pour l'analyse du trafic annuel des stations du réseau ferré RATP en 2021.

## 📋 Description du projet

Ce projet est une application de visualisation de données développée avec **Streamlit** qui permet d'explorer et d'analyser les données de trafic des stations de métro et RER de la RATP pour l'année 2021.

### Fonctionnalités

L'application comprend **4 onglets** principaux :

1. **📊 Analyse par station**
   - Sélection d'une station par réseau
   - Fiche détaillée de la station (trafic, lignes, ville, arrondissement)
   - Classement national et dans le réseau
   - Comparaison avec la moyenne et la médiane du réseau
   - Graphiques de comparaison

2. **🚉 Analyse par ligne**
   - Tableau récapitulatif par ligne (trafic total, nombre de stations, trafic moyen)
   - Graphiques : trafic total par ligne, trafic moyen par station
   - Diagramme circulaire de répartition du trafic
   - Filtrage par réseau (Métro/RER)

3. **🗺️ Répartition géographique**
   - Analyse par arrondissement parisien
   - Analyse par ville (top N configurable)
   - Répartition par réseau et par zone (Paris vs Banlieue)
   - Tableaux croisés et graphiques interactifs

4. **🔍 Exploration libre**
   - Filtres multiples : réseau, ville, ligne, plage de trafic
   - Recherche textuelle de station
   - Visualisations dynamiques (top 20, histogrammes)
   - Export des données filtrées au format CSV
   - Tableau interactif triable

## 🛠️ Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**

```bash
cd "Z:\BUT 3\Dataviz\app_ratp"
```

2. **Créer un environnement virtuel (recommandé)**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Installer les dépendances**

```powershell
pip install -r requirements.txt
```

## 🚀 Utilisation

### Lancer l'application

```powershell
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut à l'adresse `http://localhost:8501`.

### Navigation

- Utilisez le **menu latéral gauche** pour naviguer entre les différents onglets
- Les **filtres interactifs** permettent d'affiner les analyses
- Les **graphiques** sont interactifs : survolez-les pour plus de détails

## 📁 Structure du projet

```
app_ratp/
│
├── app.py                              # Application Streamlit principale
├── requirements.txt                    # Dépendances Python
├── README.md                           # Ce fichier
│
└── data/
    └── trafic-annuel-entrant-par-station-du-reseau-ferre-2021.csv
```

## 📊 Source des données

- **Fichier** : `trafic-annuel-entrant-par-station-du-reseau-ferre-2021.csv`
- **Source** : RATP / Open Data RATP
- **Année** : 2021
- **Format** : CSV avec séparateur `;`

### Colonnes du dataset

- `Rang` : Classement de la station
- `Réseau` : Type de réseau (Métro, RER)
- `Station` : Nom de la station
- `Trafic` : Nombre de voyageurs annuel
- `Correspondance_1` à `Correspondance_5` : Lignes desservant la station
- `Ville` : Ville de la station
- `Arrondissement pour Paris` : Arrondissement (si Paris)

## 🔧 Technologies utilisées

- **Streamlit** (1.29.0) : Framework web pour applications de data science
- **Pandas** (2.1.4) : Manipulation et analyse de données
- **Matplotlib** (3.8.2) : Visualisations graphiques
- **Seaborn** (0.13.0) : Visualisations statistiques avancées
- **Python** (3.8+)

## 📝 Notes de développement

### Fonctionnalités techniques

- **Cache des données** : Utilisation de `@st.cache_data` pour optimiser le chargement
- **Données agrégées** : Pré-calcul des statistiques par ligne pour de meilleures performances
- **Filtres dynamiques** : Mise à jour en temps réel des visualisations
- **Export CSV** : Téléchargement des données filtrées
- **Responsive design** : Interface adaptative avec colonnes Streamlit

### Améliorations possibles

- [ ] Ajout de coordonnées GPS pour une vraie cartographie
- [ ] Comparaison inter-annuelle (avec données de plusieurs années)
- [ ] Prédictions de trafic avec Machine Learning
- [ ] Analyse temporelle (évolution par mois/trimestre)
- [ ] Export en format Excel avec graphiques
- [ ] Thèmes personnalisables (mode sombre/clair)

## 👨‍💻 Auteur

Projet développé dans le cadre du cours de Dataviz - BUT 3

## 📄 Licence

Projet académique - Données RATP Open Data

## 🐛 Dépannage

### L'application ne démarre pas

Vérifiez que :
- L'environnement virtuel est activé
- Toutes les dépendances sont installées : `pip install -r requirements.txt`
- Le fichier CSV est présent dans `data/`

### Erreur d'encodage

Le fichier CSV utilise l'encodage UTF-8. Si vous rencontrez des problèmes d'affichage des caractères accentués, vérifiez l'encodage du fichier.

### Port déjà utilisé

Si le port 8501 est déjà utilisé, vous pouvez spécifier un autre port :

```powershell
streamlit run app.py --server.port 8502
```

## 📞 Support

Pour toute question ou problème, contactez votre enseignant de Dataviz.

---

**Dernière mise à jour** : Décembre 2025
