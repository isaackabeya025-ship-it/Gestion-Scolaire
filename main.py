import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu
import base64
from io import BytesIO
import os
import yaml
import hashlib
import time
import datetime
from datetime import datetime as dt
import numpy as np
import plotly.subplots as sp

# === PAGE DE CONNEXION ===
def check_authentication():
    """Vérifier si l'utilisateur est authentifié"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.login_attempts = 0
        st.session_state.last_attempt_time = 0
    
    if not st.session_state.authenticated:
        return False
    return True

def login_form():
    """Afficher le formulaire de connexion"""
    # CSS pour la page de connexion
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 50px auto;
        padding: 30px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .login-title {
        text-align: center;
        color: white;
        margin-bottom: 30px;
        font-size: 28px;
    }
    .stButton > button {
        width: 100%;
        margin-top: 20px;
        background-color: #720B07;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #8a0d08;
    }
    .login-header {
        text-align: center;
        margin-bottom: 40px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Conteneur principal
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Titre
        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        
        # Logo (si disponible)
        try:
            # Correction: utiliser __file__ correctement
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            except:
                base_dir = os.getcwd()
                
            image_path = os.path.join(base_dir, "images", "j..jpg")
            if os.path.exists(image_path):
                image = Image.open(image_path)
                st.image(image, width=100, use_container_width=False)
        except Exception as e:
            pass
        
        st.markdown('<h2 class="login-title">COMPLEXE SCOLAIRE<br>DU JOURDAIN 1</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#ccc; font-size:18px;">GESTION DE SUIVI DE FRAIS SCOLAIRE</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Vérifier si bloqué
        current_time = time.time()
        if (st.session_state.login_attempts >= 3 and 
            current_time - st.session_state.last_attempt_time < 300):
            remaining_time = int(300 - (current_time - st.session_state.last_attempt_time))
            st.error(f"Trop de tentatives échouées. Veuillez réessayer dans {remaining_time} secondes.")
            st.markdown('</div>', unsafe_allow_html=True)
            return False
        
        # Formulaire de connexion
        with st.form(key='login_form'):
            username = st.text_input("Nom d'utilisateur", placeholder="Entrez votre nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe")
            
            submit_button = st.form_submit_button(label="Se connecter")
            
            if submit_button:
                if username and password:
                    if username == "admin" and password == "admin123":
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.login_attempts = 0
                        st.success("Connexion réussie!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.session_state.last_attempt_time = time.time()
                        st.error("Nom d'utilisateur ou mot de passe incorrect")
                        
                        if st.session_state.login_attempts == 3:
                            st.warning("Après 3 tentatives échouées, vous devrez attendre 5 minutes.")
                else:
                    st.warning("Veuillez remplir tous les champs")
        
        # Informations de connexion (pour test)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-top:20px; color:#888; font-size:12px;'>
        <b>Pour test:</b><br>
        Nom d'utilisateur: admin<br>
        Mot de passe: admin123
        </div>
        """, unsafe_allow_html=True)

# Vérifier l'authentification
if not check_authentication():
    login_form()
    st.stop()

# === CONFIGURATION DE BASE ===
# Obtenir le chemin du répertoire de base
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
except:
    base_dir = os.getcwd()

# Chemin de l'image
image_path = os.path.join(base_dir, "images", "j..jpg")

# Créer une image par défaut au cas où
try:
    if os.path.exists(image_path):
        image = Image.open(image_path)
    else:
        # Créer une image bleue par défaut
        image = Image.new('RGB', (100, 100), color='blue')
except Exception as e:
    # Si erreur, créer une image rouge simple
    image = Image.new('RGB', (100, 100), color='red')

# Configuration Streamlit
st.set_page_config(
    page_title="COMPLEXE SCOLAIRE DU JOURDAIN 1",
    page_icon=image,
    layout="wide"
)

# Variable pour le thème
theme_plotly = None

# CSS Style
try:
    css_path = os.path.join(base_dir, "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# CSS Style supplémentaire
hide_st_style = """
<style>
.stAppDeployButton[data-testid="stAppDeployButton"] {
    visibility: hidden;
}
header [data-testid="stHeader"] > div:first-child button {
    display: none;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

def image_to_base64(image):
    """Convertir une image en base64"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# === FONCTIONS DE GESTION DES DONNÉES ===
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data_isaac.xlsx")
        
        # Vérifier et créer les colonnes nécessaires si elles n'existent pas
        required_columns = ['NOMS', 'SEXE', 'PROMOTION', 'VACATION', 'ANNEE', 
                           'INSCRIPTION', 'MINERVAL', 'TRANCHE1', 'TRANCHE2']
        
        for col in required_columns:
            if col not in df.columns:
                if col in ['INSCRIPTION', 'MINERVAL', 'TRANCHE1', 'TRANCHE2']:
                    df[col] = 0
                else:
                    df[col] = ""
        
        # Ajouter colonne pour historique des paiements si elle n'existe pas
        if 'HISTORIQUE_PAIEMENTS' not in df.columns:
            df['HISTORIQUE_PAIEMENTS'] = ""
        
        if 'DATE_DERNIER_PAIEMENT' not in df.columns:
            df['DATE_DERNIER_PAIEMENT'] = ""
            
        if 'HEURE_DERNIER_PAIEMENT' not in df.columns:
            df['HEURE_DERNIER_PAIEMENT'] = ""
            
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

def save_data(df):
    try:
        df.to_excel("data_isaac.xlsx", index=False)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde: {e}")
        return False

# Charger les données globalement
df = load_data()

# Définir les classes
classes_secondaires = ["7ème", "8ème", "1ère", "2ème", "3ème", "4ème"]
options_secondaires = ["Pédagogie Générale", "Coupe Couture", "Biologie Chimie", "Commercial & Gestion"]
classes_primaires = ["1ère Primaire", "2ème Primaire", "3ème Primaire", "4ème Primaire", "5ème Primaire", "6ème Primaire"]

# Taux de change
TAUX_CHANGE = 2300

# === HEADER AVEC LOGO ET DÉCONNEXION ===
col_header1, col_header2, col_header3 = st.columns([0.8, 0.1, 0.1])

with col_header1:
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1], vertical_alignment="top", gap="large")
    
    with col1:
        st.image(image, caption="", width=140)
    
    with col2:
        st.markdown(
            "<h1 style='font-size: 35px; color: white; text-align:center'>GESTION DE SUIVI DE FRAIS SCOLAIRE</h1>",
            unsafe_allow_html=True,
        )
    
    with col3:
        st.image(image, caption="", width=140)

with col_header3:
    if st.button("Déconnexion", key="logout_button"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()

st.divider()

# Affichage de l'utilisateur connecté
st.sidebar.markdown(f"Connecté en tant que : *{st.session_state.username}*")
st.sidebar.markdown("---")

# === SIDEBAR FILTRES ===
st.sidebar.header("Filtres des Données")

# Type d'école
type_ecole = st.sidebar.selectbox(
    "Type d'école",
    ["Tous", "Secondaire", "Primaire"],
    index=0
)

# Filtres communs
genre = st.sidebar.multiselect(
    "Par Genre",
    options=df["SEXE"].unique() if not df.empty else [],
    default=df["SEXE"].unique() if not df.empty else [],
)

# Filtres selon type d'école
if type_ecole in ["Tous", "Secondaire"]:
    option = st.sidebar.multiselect(
        "Par Option (Secondaire)",
        options=df["OPTION"].unique() if "OPTION" in df.columns and not df.empty else [],
        default=df["OPTION"].unique() if "OPTION" in df.columns and not df.empty else []
    )
else:
    option = []

if type_ecole == "Secondaire":
    classes_disponibles = classes_secondaires
elif type_ecole == "Primaire":
    classes_disponibles = classes_primaires
else:
    classes_disponibles = classes_secondaires + classes_primaires

classeFilter = st.sidebar.multiselect(
    "Par Classe",
    options=classes_disponibles,
    default=classes_disponibles,
)

vacation = st.sidebar.multiselect(
    "Par Vacation",
    options=df["VACATION"].unique() if not df.empty else [],
    default=df["VACATION"].unique() if not df.empty else [],
)

annee = st.sidebar.multiselect(
    "Par Année scolaire",
    options=df["ANNEE"].unique() if not df.empty else [],
    default=df["ANNEE"].unique() if not df.empty else [],
)

# === MENU PRINCIPAL ===
with st.sidebar:
    st.markdown("## Menu Principal")
    selectedRendu = option_menu(
        menu_title=None,
        options=["STATISTIQUE", "GRAPHIQUE", "TABLEAU", 
                 "NOUVEAU PAIEMENT", "CONTRÔLE ÉLÈVE"],
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0!important", "background-color": "#262730"},
            "icon": {"color": "orange", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
            "nav-link-selected": {"background-color": "#720B07"},
        }
    )

# Menu Horizontal
hselected = option_menu(
    menu_title=None,
    options=["GLOBALE", "OPTIONS", "LISTES PAR CLASSE", "PRIMAIRE"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    key="horizontal_menu"
)

# === FONCTIONS UTILITAIRES ===
def convertir_dollars_en_fc(montant_dollars):
    """Convertir un montant en dollars en FC"""
    if pd.isna(montant_dollars):
        return 0
    return float(montant_dollars) * TAUX_CHANGE

def formater_montant(montant, devise="FC"):
    """Formater un montant pour l'affichage"""
    if pd.isna(montant):
        montant = 0
    return f"{int(montant):,} {devise}"

def ajouter_historique_paiement(df, index, type_paiement, montant_fc, montant_dollars=0, date=None, heure=None):
    """Ajouter un paiement à l'historique avec date et heure"""
    if date is None:
        date = dt.now().strftime("%d/%m/%Y")
    if heure is None:
        heure = dt.now().strftime("%H:%M")
    
    date_complete = f"{date} {heure}"
    
    historique = df.at[index, 'HISTORIQUE_PAIEMENTS']
    if pd.isna(historique):
        historique = ""
    
    nouveau_paiement = f"{date_complete} - {type_paiement}: {montant_fc:,.0f} FC"
    if montant_dollars > 0:
        nouveau_paiement += f" ({montant_dollars:,.0f} $)"
    
    if historique:
        historique = f"{nouveau_paiement}\n{historique}"
    else:
        historique = nouveau_paiement
    
    df.at[index, 'HISTORIQUE_PAIEMENTS'] = historique
    df.at[index, 'DATE_DERNIER_PAIEMENT'] = date
    df.at[index, 'HEURE_DERNIER_PAIEMENT'] = heure
    
    return df

def generer_reçu_paiement(eleve_info, paiement_info):
    """Générer un reçu de paiement COMPACT sur une seule page"""
    # Échapper les accolades doubles pour le JavaScript
    js_scale_code = '@media print { body { transform: scale(0.95); transform-origin: top left; } }'
    
    # Créer le HTML
    html_parts = []
    
    html_parts.append(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Reçu de Paiement</title>
    <style>
        @media print {{
            @page {{
                size: A4 portrait;
                margin: 0.5cm;
            }}
            body {{
                margin: 0;
                padding: 0;
                font-size: 10px;
            }}
            .no-print {{
                display: none !important;
            }}
        }}
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
            font-size: 10px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 10px;
            border-bottom: 1px solid #720B07;
            padding-bottom: 5px;
        }}
        .title {{
            font-size: 16px;
            font-weight: bold;
            color: #720B07;
            margin-bottom: 2px;
        }}
        .subtitle {{
            font-size: 12px;
            margin-bottom: 5px;
            color: #333;
        }}
        .school-info {{
            font-size: 9px;
            color: #666;
            margin-bottom: 5px;
        }}
        .compact-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 5px 0;
            font-size: 9px;
        }}
        .compact-table th, .compact-table td {{
            border: 1px solid #ddd;
            padding: 3px;
            text-align: left;
        }}
        .compact-table th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        .amount {{
            font-size: 14px;
            font-weight: bold;
            color: #006400;
            text-align: center;
            margin: 15px 0;
            padding: 8px;
            background-color: #f0fff0;
            border-radius: 3px;
            border: 1px solid #006400;
        }}
        .footer {{
            margin-top: 20px;
            border-top: 1px solid #000;
            padding-top: 8px;
            text-align: center;
            font-size: 8px;
            color: #666;
        }}
        .signature {{
            margin-top: 25px;
            display: flex;
            justify-content: space-between;
        }}
        .signature-box {{
            width: 45%;
            text-align: center;
            font-size: 9px;
        }}
        .signature-line {{
            border-top: 1px solid #000;
            width: 80%;
            margin: 5px auto;
            padding-top: 3px;
        }}
        .receipt-number {{
            text-align: right;
            font-size: 8px;
            color: #999;
            margin-bottom: 10px;
        }}
        .datetime {{
            font-size: 9px;
            color: #666;
            text-align: right;
            margin-bottom: 10px;
        }}
        .print-button {{
            text-align: center;
            margin-top: 10px;
            margin-bottom: 10px;
        }}
        .button {{
            background-color: #720B07;
            color: white;
            padding: 5px 10px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 10px;
        }}
        .button:hover {{
            background-color: #8a0d08;
        }}
        .total-row {{
            font-weight: bold;
            background-color: #e8f4ff;
        }}
    </style>
</head>
<body>
    <div class="no-print print-button">
        <button class="button" onclick="window.print()">Imprimer ce reçu</button>
        <button class="button" onclick="window.close()" style="margin-left: 5px; background-color: #666;">Fermer</button>
    </div>
    
    <div class="receipt-number">
        Reçu N°: {dt.now().strftime('%Y%m%d%H%M%S')}
    </div>
    
    <div class="datetime">
        Émis le: {paiement_info.get('date', dt.now().strftime('%d/%m/%Y'))} à {paiement_info.get('heure', dt.now().strftime('%H:%M'))}
    </div>
    
    <div class="header">
        <div class="title">COMPLEXE SCOLAIRE DU JOURDAIN 1</div>
        <div class="subtitle">Reçu de Paiement de Frais Scolaires</div>
        <div class="school-info">
            Matricule: CSJ-001 | Téléphone: +243 XX XXX XXXX<br>
            Kinshasa, RDC
        </div>
    </div>
    
    <table class="compact-table">
        <tr>
            <th colspan="2">INFORMATIONS DE L'ÉLÈVE</th>
        </tr>
        <tr>
            <td width="40%"><strong>Nom complet:</strong></td>
            <td>{eleve_info['NOMS']}</td>
        </tr>
        <tr>
            <td><strong>Classe:</strong></td>
            <td>{eleve_info.get('PROMOTION', 'N/A')}</td>
        </tr>
        <tr>
            <td><strong>Sexe:</strong></td>
            <td>{eleve_info.get('SEXE', 'N/A')}</td>
        </tr>""")
    
    if 'OPTION' in eleve_info and eleve_info['OPTION']:
        html_parts.append(f"""
        <tr>
            <td><strong>Option:</strong></td>
            <td>{eleve_info.get('OPTION', 'N/A')}</td>
        </tr>""")
    
    html_parts.append(f"""
        <tr>
            <td><strong>Année scolaire:</strong></td>
            <td>{eleve_info.get('ANNEE', 'N/A')}</td>
        </tr>
    </table>
    
    <table class="compact-table">
        <tr>
            <th colspan="2">DÉTAILS DU PAIEMENT</th>
        </tr>
        <tr>
            <td width="40%"><strong>Date du paiement:</strong></td>
            <td>{paiement_info.get('date', dt.now().strftime('%d/%m/%Y'))}</td>
        </tr>
        <tr>
            <td><strong>Heure du paiement:</strong></td>
            <td>{paiement_info.get('heure', dt.now().strftime('%H:%M'))}</td>
        </tr>
        <tr>
            <td><strong>Type de paiement:</strong></td>
            <td>{paiement_info.get('type', 'N/A')}</td>
        </tr>
        <tr>
            <td><strong>Mode de paiement:</strong></td>
            <td>{paiement_info.get('mode', 'Espèces')}</td>
        </tr>""")
    
    if paiement_info.get('montant_dollars', 0) > 0:
        html_parts.append(f"""
        <tr>
            <td><strong>Montant en dollars:</strong></td>
            <td>{paiement_info.get('montant_dollars', 0):,.0f} USD</td>
        </tr>
        <tr>
            <td><strong>Taux de change:</strong></td>
            <td>1 USD = {TAUX_CHANGE} FC</td>
        </tr>""")
    
    html_parts.append(f"""
        <tr class="total-row">
            <td><strong>Montant en francs congolais:</strong></td>
            <td><strong>{paiement_info.get('montant_fc', 0):,.0f} FC</strong></td>
        </tr>""")
    
    if paiement_info.get('notes', ''):
        html_parts.append(f"""
        <tr>
            <td><strong>Notes:</strong></td>
            <td>{paiement_info.get('notes', '')}</td>
        </tr>""")
    
    montant_dollars = paiement_info.get('montant_dollars', 0)
    montant_dollars_text = f"({montant_dollars:,.0f} USD)" if montant_dollars > 0 else ""
    
    html_parts.append(f"""
    </table>
    
    <div class="amount">
        TOTAL PAYÉ: {paiement_info.get('montant_fc', 0):,.0f} FRANCS CONGOLAIS {montant_dollars_text}
    </div>
    
    <div class="signature">
        <div class="signature-box">
            <div>Signature du caissier</div>
            <div class="signature-line"></div>
            <div style="font-size: 7px; color: #666;">Nom et cachet</div>
        </div>
        <div class="signature-box">
            <div>Signature du parent/tuteur</div>
            <div class="signature-line"></div>
            <div style="font-size: 7px; color: #666;">Nom et cachet</div>
        </div>
    </div>
    
    <div class="footer">
        <div style="font-weight: bold; margin-bottom: 3px;">IMPORTANT</div>
        <div>• Ce reçu est valable comme justificatif de paiement.</div>
        <div>• Conservez ce reçu pour toute réclamation.</div>
        <div style="margin-top: 5px; font-style: italic;">"L'éducation est l'arme la plus puissante pour changer le monde."</div>
    </div>
    
    <script>
        window.onload = function() {{
            // Ajustement pour impression
            const style = document.createElement('style');
            style.innerHTML = '{js_scale_code}';
            document.head.appendChild(style);
        }};
    </script>
</body>
</html>""")
    
    return ''.join(html_parts)

# === FONCTION POUR AFFICHER LES GRAPHIQUES PRIMAIRES ===
def graphiques_primaire():
    """Afficher les graphiques spécifiques au primaire"""
    if df_selection.empty:
        st.warning("Aucune donnée primaire à afficher avec les filtres sélectionnés.")
        return
    
    # Filtrer seulement les primaires
    df_primaire = df_selection[df_selection['PROMOTION'].isin(classes_primaires)]
    
    if df_primaire.empty:
        st.warning("Aucune donnée primaire disponible.")
        return
    
    st.markdown("## GRAPHIQUES DU PRIMAIRE")
    
    # Créer des onglets pour chaque classe primaire
    tabs = st.tabs(["TOUTES CLASSES", "1ère Primaire", "2ème Primaire", 
                   "3ème Primaire", "4ème Primaire", "5ème Primaire", "6ème Primaire"])
    
    with tabs[0]:  # Toutes classes
        st.markdown("### Statistiques Globales du Primaire")
        
        # 1. Nombre d'élèves par classe
        eleves_par_classe = df_primaire.groupby('PROMOTION').size().reset_index(name='Nombre')
        
        fig1 = px.bar(
            eleves_par_classe,
            x='PROMOTION',
            y='Nombre',
            title="Nombre d'élèves par classe (Primaire)",
            color='PROMOTION',
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis_title="Classe",
            yaxis_title="Nombre d'élèves"
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # 2. Répartition par genre
        df_primaire['count'] = 1
        genre_primaire = df_primaire.groupby('SEXE')['count'].sum().reset_index()
        
        fig2 = px.pie(
            genre_primaire,
            values='count',
            names='SEXE',
            title='Répartition par genre (Primaire)',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4'],
            hole=0.3
        )
        fig2.update_traces(textinfo="percent+label+value")
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white")
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # 3. Total des paiements par classe
        paiements_par_classe = df_primaire.groupby('PROMOTION').agg({
            'INSCRIPTION': 'sum',
            'MINERVAL': 'sum'
        }).reset_index()
        
        paiements_par_classe['TOTAL_FC'] = paiements_par_classe['INSCRIPTION'] + paiements_par_classe['MINERVAL']
        
        fig3 = px.bar(
            paiements_par_classe,
            x='PROMOTION',
            y='TOTAL_FC',
            title='Total des paiements par classe (Primaire)',
            color='PROMOTION',
            color_discrete_sequence=px.colors.sequential.Greens
        )
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis_title="Classe",
            yaxis_title="Total FC"
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # 4. Détail des paiements (Inscription vs Minerval)
        paiements_detail = paiements_par_classe.melt(
            id_vars='PROMOTION',
            value_vars=['INSCRIPTION', 'MINERVAL'],
            var_name='Type',
            value_name='Montant_FC'
        )
        
        paiements_detail['Type'] = paiements_detail['Type'].map({
            'INSCRIPTION': 'Inscription',
            'MINERVAL': 'Minerval'
        })
        
        fig4 = px.bar(
            paiements_detail,
            x='PROMOTION',
            y='Montant_FC',
            color='Type',
            title='Détail des paiements par classe (Primaire)',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4'],
            barmode='group'
        )
        fig4.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis_title="Classe",
            yaxis_title="Montant (FC)"
        )
        st.plotly_chart(fig4, use_container_width=True)
        
        # 5. Paiements par élève (Top 15)
        df_primaire['TOTAL_PAYE'] = df_primaire['INSCRIPTION'] + df_primaire['MINERVAL']
        paiements_eleves = df_primaire.sort_values('TOTAL_PAYE', ascending=False).head(15)
        
        fig5 = px.bar(
            paiements_eleves,
            x='NOMS',
            y='TOTAL_PAYE',
            color='PROMOTION',
            title='Top 15 des paiements par élève (Primaire)',
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig5.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis_title="Élève",
            yaxis_title="Total payé (FC)",
            xaxis_tickangle=45
        )
        st.plotly_chart(fig5, use_container_width=True)
    
    # Graphiques par classe individuelle
    for i, classe in enumerate(classes_primaires, 1):
        with tabs[i]:
            df_classe = df_primaire[df_primaire['PROMOTION'] == classe]
            
            if df_classe.empty:
                st.info(f"Aucun élève en {classe}")
                continue
            
            st.markdown(f"### Statistiques pour la {classe}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Nombre d'élèves
                nb_eleves = len(df_classe)
                st.metric(f"Nombre d'élèves", nb_eleves)
                
                # Répartition par genre
                genre_classe = df_classe.groupby('SEXE').size().reset_index(name='Nombre')
                if not genre_classe.empty:
                    fig_genre = px.pie(
                        genre_classe,
                        values='Nombre',
                        names='SEXE',
                        title=f'Répartition par genre - {classe}',
                        color_discrete_sequence=['#FF6B6B', '#4ECDC4'],
                        hole=0.4
                    )
                    fig_genre.update_traces(textinfo="percent+label")
                    fig_genre.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color="white"),
                        showlegend=True
                    )
                    st.plotly_chart(fig_genre, use_container_width=True)
            
            with col2:
                # Totaux des paiements
                total_inscription = df_classe['INSCRIPTION'].sum()
                total_minerval = df_classe['MINERVAL'].sum()
                total_fc = total_inscription + total_minerval
                
                st.metric(f"Inscription totale", formater_montant(total_inscription))
                st.metric(f"Minerval total", formater_montant(total_minerval))
                st.metric(f"Total général", formater_montant(total_fc))
                
                # Graphique des paiements
                paiements_data = pd.DataFrame({
                    'Type': ['Inscription', 'Minerval'],
                    'Montant': [total_inscription, total_minerval]
                })
                
                fig_paiements = px.bar(
                    paiements_data,
                    x='Type',
                    y='Montant',
                    title=f'Paiements - {classe}',
                    color='Type',
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4']
                )
                fig_paiements.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="white"),
                    xaxis_title="Type de paiement",
                    yaxis_title="Montant (FC)",
                    showlegend=False
                )
                st.plotly_chart(fig_paiements, use_container_width=True)
            
            # Liste des élèves avec leurs paiements
            with st.expander(f"Liste des élèves de {classe}"):
                display_df = df_classe[['NOMS', 'SEXE', 'VACATION', 'ANNEE', 'INSCRIPTION', 'MINERVAL']].copy()
                display_df['TOTAL'] = display_df['INSCRIPTION'] + display_df['MINERVAL']
                display_df = display_df.rename(columns={
                    'INSCRIPTION': 'INSCRIPTION (FC)',
                    'MINERVAL': 'MINERVAL (FC)',
                    'TOTAL': 'TOTAL (FC)'
                })
                
                # Formater les montants
                display_df['INSCRIPTION (FC)'] = display_df['INSCRIPTION (FC)'].apply(lambda x: f"{int(x):,} FC" if pd.notnull(x) else "0 FC")
                display_df['MINERVAL (FC)'] = display_df['MINERVAL (FC)'].apply(lambda x: f"{int(x):,} FC" if pd.notnull(x) else "0 FC")
                display_df['TOTAL (FC)'] = display_df['TOTAL (FC)'].apply(lambda x: f"{int(x):,} FC" if pd.notnull(x) else "0 FC")
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=300
                )

# === NOUVELLE FONCTIONNALITÉ: CONTRÔLE ÉLÈVE AMÉLIORÉ ===
def controle_eleve():
    """Fonction de contrôle des élèves"""
    global df
    
    st.markdown("## CONTRÔLE DES ÉLÈVES")
    
    if 'df' not in globals() or df is None or df.empty:
        st.warning("Aucune donnée disponible. Veuillez d'abord charger des données.")
        return
    
    tab1, tab2, tab3 = st.tabs(["FILTRES ÉLÈVES", "MODIFIER", "SUPPRIMER"])
    
    with tab1:
        st.markdown("### Filtrer les élèves")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            type_recherche = st.selectbox(
                "Type d'école",
                ["Tous", "Secondaire", "Primaire"],
                key="recherche_type"
            )
            
            if type_recherche == "Secondaire":
                classes_options = ["Toutes"] + classes_secondaires
            elif type_recherche == "Primaire":
                classes_options = ["Toutes"] + classes_primaires
            else:
                classes_options = ["Toutes"] + classes_secondaires + classes_primaires
            
            classe_recherche = st.selectbox(
                "Classe",
                classes_options,
                key="recherche_classe"
            )
        
        with col2:
            if type_recherche in ["Tous", "Secondaire"]:
                options_dispo = ["Toutes"] + options_secondaires
                option_recherche = st.selectbox(
                    "Option",
                    options_dispo,
                    key="recherche_option"
                )
            else:
                option_recherche = "Non applicable"
            
            nom_recherche = st.text_input(
                "Nom de l'élève",
                placeholder="Entrez tout ou partie du nom",
                key="recherche_nom"
            )
        
        with col3:
            if not df.empty and 'VACATION' in df.columns:
                vacation_options = ["Toutes"] + list(df['VACATION'].unique())
            else:
                vacation_options = ["Toutes"]
            
            vacation_recherche = st.selectbox(
                "Vacation",
                vacation_options,
                key="recherche_vacation"
            )
            
            if not df.empty and 'ANNEE' in df.columns:
                annee_options = ["Toutes"] + list(df['ANNEE'].unique())
            else:
                annee_options = ["Toutes"]
            
            annee_recherche = st.selectbox(
                "Année scolaire",
                annee_options,
                key="recherche_annee"
            )
        
        resultats = df.copy()
        
        if type_recherche == "Secondaire":
            resultats = resultats[resultats['PROMOTION'].isin(classes_secondaires)]
        elif type_recherche == "Primaire":
            resultats = resultats[resultats['PROMOTION'].isin(classes_primaires)]
        
        if classe_recherche != "Toutes":
            resultats = resultats[resultats['PROMOTION'] == classe_recherche]
        
        if option_recherche != "Toutes" and option_recherche != "Non applicable" and 'OPTION' in resultats.columns:
            resultats = resultats[resultats['OPTION'] == option_recherche]
        
        if nom_recherche:
            resultats = resultats[resultats['NOMS'].str.contains(nom_recherche, case=False, na=False)]
        
        if vacation_recherche != "Toutes":
            resultats = resultats[resultats['VACATION'] == vacation_recherche]
        
        if annee_recherche != "Toutes":
            resultats = resultats[resultats['ANNEE'] == annee_recherche]
        
        if not resultats.empty:
            st.success(f"{len(resultats)} élève(s) trouvé(s)")
            
            eleve_selectionne = st.selectbox(
                "Sélectionnez un élève pour voir les détails",
                resultats['NOMS'].values,
                key="selection_details"
            )
            
            if eleve_selectionne:
                eleve_info = resultats[resultats['NOMS'] == eleve_selectionne].iloc[0]
                
                st.markdown("### Détails de l'élève")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"**Nom complet:** {eleve_info['NOMS']}")
                    st.info(f"**Sexe:** {eleve_info['SEXE']}")
                    st.info(f"**Classe:** {eleve_info['PROMOTION']}")
                    if 'OPTION' in eleve_info and eleve_info['OPTION']:
                        st.info(f"**Option:** {eleve_info['OPTION']}")
                
                with col2:
                    st.info(f"**Vacation:** {eleve_info['VACATION']}")
                    st.info(f"**Année scolaire:** {eleve_info['ANNEE']}")
                    
                    # Date et heure du dernier paiement
                    date_paiement = eleve_info.get('DATE_DERNIER_PAIEMENT', '')
                    heure_paiement = eleve_info.get('HEURE_DERNIER_PAIEMENT', '')
                    if date_paiement and heure_paiement:
                        st.info(f"**Dernier paiement:** {date_paiement} à {heure_paiement}")
                    
                    total_fc = eleve_info['INSCRIPTION'] + eleve_info['MINERVAL']
                    total_dollars = eleve_info['TRANCHE1'] + eleve_info['TRANCHE2'] + eleve_info.get('TRANCHE3', 0)
                    total_fc += convertir_dollars_en_fc(total_dollars)
                    st.info(f"**Total payé:** {formater_montant(total_fc)}")
                
                st.markdown("### Détails des paiements")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Inscription", value=formater_montant(eleve_info['INSCRIPTION']))
                    st.metric("Minerval", value=formater_montant(eleve_info['MINERVAL']))
                
                with col2:
                    st.metric("Tranche 1", value=formater_montant(eleve_info['TRANCHE1'], "$"))
                    st.metric("Tranche 2", value=formater_montant(eleve_info['TRANCHE2'], "$"))
                
                with col3:
                    if 'TRANCHE3' in eleve_info and eleve_info['TRANCHE3'] > 0:
                        st.metric("Tranche 3", value=formater_montant(eleve_info['TRANCHE3'], "$"))
                    
                    total_dollars = eleve_info['TRANCHE1'] + eleve_info['TRANCHE2'] + eleve_info.get('TRANCHE3', 0)
                    st.metric("Total $", value=formater_montant(total_dollars, "$"))
                
                if 'HISTORIQUE_PAIEMENTS' in eleve_info and pd.notna(eleve_info['HISTORIQUE_PAIEMENTS']) and eleve_info['HISTORIQUE_PAIEMENTS']:
                    st.markdown("### Historique des paiements")
                    st.text_area(
                        "Historique",
                        value=eleve_info['HISTORIQUE_PAIEMENTS'],
                        height=150,
                        disabled=True
                    )
        else:
            st.warning("Aucun élève trouvé avec ces critères.")
    
    with tab2:
        st.markdown("### Modifier un élève")
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                eleve_a_modifier = st.selectbox(
                    "Sélectionnez l'élève à modifier",
                    df['NOMS'].values,
                    key="modifier_select"
                )
            
            if eleve_a_modifier:
                eleve_idx = df[df['NOMS'] == eleve_a_modifier].index[0]
                eleve_data = df.loc[eleve_idx]
                
                with st.form(key="form_modification"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nouveau_nom = st.text_input("Nom complet", value=eleve_data['NOMS'], key="mod_nom")
                        nouveau_sexe = st.selectbox("Sexe", ["Masculin", "Féminin"], 
                                                   index=0 if eleve_data['SEXE'] == "Masculin" else 1,
                                                   key="mod_sexe")
                        
                        if eleve_data['PROMOTION'] in classes_secondaires:
                            classe_options = classes_secondaires
                        else:
                            classe_options = classes_primaires
                        
                        nouvelle_classe = st.selectbox("Classe", classe_options, 
                                                     index=classe_options.index(eleve_data['PROMOTION']) if eleve_data['PROMOTION'] in classe_options else 0,
                                                     key="mod_classe")
                    
                    with col2:
                        if 'OPTION' in eleve_data and eleve_data['PROMOTION'] in classes_secondaires:
                            option_val = eleve_data.get('OPTION', options_secondaires[0])
                            nouvelle_option = st.selectbox("Option", options_secondaires, 
                                                         index=options_secondaires.index(option_val) if option_val in options_secondaires else 0,
                                                         key="mod_option")
                        nouvelle_vacation = st.selectbox("Vacation", ["JOUR", "SOIR"], 
                                                       index=0 if eleve_data['VACATION'] == "JOUR" else 1,
                                                       key="mod_vacation")
                        nouvelle_annee = st.text_input("Année scolaire", value=eleve_data['ANNEE'], key="mod_annee")
                    
                    st.markdown("### Modifier les informations financières")
                    col3, col4, col5 = st.columns(3)
                    
                    with col3:
                        nouvelle_inscription = st.number_input("Inscription (FC)", 
                                                              value=float(eleve_data['INSCRIPTION']),
                                                              min_value=0.0, step=1000.0, key="mod_inscription")
                        nouveau_minerval = st.number_input("Minerval (FC)", 
                                                          value=float(eleve_data['MINERVAL']),
                                                          min_value=0.0, step=1000.0, key="mod_minerval")
                    
                    with col4:
                        nouvelle_tranche1 = st.number_input("Tranche 1 ($)", 
                                                           value=float(eleve_data['TRANCHE1']),
                                                           min_value=0.0, step=5.0, key="mod_t1")
                        nouvelle_tranche2 = st.number_input("Tranche 2 ($)", 
                                                           value=float(eleve_data['TRANCHE2']),
                                                           min_value=0.0, step=5.0, key="mod_t2")
                    
                    with col5:
                        if 'TRANCHE3' in eleve_data:
                            nouvelle_tranche3 = st.number_input("Tranche 3 ($)", 
                                                              value=float(eleve_data['TRANCHE3']),
                                                              min_value=0.0, step=5.0, key="mod_t3")
                    
                    if st.form_submit_button("SAUVEGARDER LES MODIFICATIONS"):
                        df.at[eleve_idx, 'NOMS'] = nouveau_nom
                        df.at[eleve_idx, 'SEXE'] = nouveau_sexe
                        df.at[eleve_idx, 'PROMOTION'] = nouvelle_classe
                        df.at[eleve_idx, 'VACATION'] = nouvelle_vacation
                        df.at[eleve_idx, 'ANNEE'] = nouvelle_annee
                        
                        if 'OPTION' in df.columns and nouvelle_classe in classes_secondaires:
                            df.at[eleve_idx, 'OPTION'] = nouvelle_option
                        
                        df.at[eleve_idx, 'INSCRIPTION'] = nouvelle_inscription
                        df.at[eleve_idx, 'MINERVAL'] = nouveau_minerval
                        df.at[eleve_idx, 'TRANCHE1'] = nouvelle_tranche1
                        df.at[eleve_idx, 'TRANCHE2'] = nouvelle_tranche2
                        
                        if 'TRANCHE3' in df.columns:
                            df.at[eleve_idx, 'TRANCHE3'] = nouvelle_tranche3
                        
                        if save_data(df):
                            st.success("Élève modifié avec succès!")
                            st.rerun()
    
    with tab3:
        st.markdown("### Supprimer un élève")
        
        if not df.empty:
            eleve_a_supprimer = st.selectbox(
                "Sélectionnez l'élève à supprimer",
                df['NOMS'].values,
                key="supprimer_select"
            )
            
            if eleve_a_supprimer:
                eleve_info = df[df['NOMS'] == eleve_a_supprimer].iloc[0]
                
                st.warning(f"Vous êtes sur le point de supprimer: **{eleve_a_supprimer}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"Classe: {eleve_info['PROMOTION']}")
                    st.info(f"Sexe: {eleve_info['SEXE']}")
                    if 'OPTION' in eleve_info and eleve_info['OPTION']:
                        st.info(f"Option: {eleve_info['OPTION']}")
                
                with col2:
                    total_fc = eleve_info['INSCRIPTION'] + eleve_info['MINERVAL']
                    total_dollars = eleve_info['TRANCHE1'] + eleve_info['TRANCHE2'] + eleve_info.get('TRANCHE3', 0)
                    total_fc += convertir_dollars_en_fc(total_dollars)
                    st.info(f"Total payé: {formater_montant(total_fc)}")
                    st.info(f"Année: {eleve_info['ANNEE']}")
                
                confirmation = st.checkbox("Je confirme la suppression de cet élève", key="confirm_suppression")
                
                if confirmation and st.button("SUPPRIMER DÉFINITIVEMENT L'ÉLÈVE", type="primary"):
                    df = df[df['NOMS'] != eleve_a_supprimer]
                    if save_data(df):
                        st.success(f"Élève {eleve_a_supprimer} supprimé avec succès!")
                        st.rerun()

# === NOUVELLE FONCTIONNALITÉ: NOUVEAU PAIEMENT AMÉLIORÉ ===
def nouveau_paiement():
    """Fonction pour enregistrer un nouveau paiement"""
    global df
    
    st.markdown("## ENREGISTRER UN NOUVEAU PAIEMENT")
    
    if df.empty:
        st.warning("Aucun élève dans la base de données.")
        return
    
    # Créer une variable de session pour stocker le reçu généré
    if 'paiement_reussi' not in st.session_state:
        st.session_state.paiement_reussi = False
        st.session_state.reçu_html = ""
        st.session_state.eleve_info = None
        st.session_state.paiement_info = None
    
    # Si un paiement a réussi, afficher les options de téléchargement
    if st.session_state.paiement_reussi:
        st.markdown("### Reçu de paiement généré avec succès!")
        
        # Afficher le reçu dans un iframe (plus petit)
        st.components.v1.html(st.session_state.reçu_html, height=600, scrolling=True)
        
        # Options de téléchargement (EN DEHORS DU FORMULAIRE)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Télécharger le reçu HTML
            st.download_button(
                label="Télécharger le reçu (HTML)",
                data=st.session_state.reçu_html.encode(),
                file_name=f"reçu_{st.session_state.eleve_info['NOMS'].replace(' ', '_')}_{st.session_state.paiement_info['date'].replace('/', '_')}.html",
                mime="text/html"
            )
        
        with col2:
            # Télécharger le reçu PDF (simulation)
            st.download_button(
                label="Télécharger le reçu (PDF)",
                data=st.session_state.reçu_html.encode(),
                file_name=f"reçu_{st.session_state.eleve_info['NOMS'].replace(' ', '_')}_{st.session_state.paiement_info['date'].replace('/', '_')}.pdf",
                mime="application/pdf"
            )
        
        with col3:
            # Bouton pour réinitialiser le formulaire
            if st.button("Nouveau paiement"):
                st.session_state.paiement_reussi = False
                st.rerun()
        
        # Information pour impression
        st.info("Conseil: Vous pouvez imprimer directement depuis le navigateur en utilisant Ctrl+P ou le bouton d'impression dans le reçu.")
        
        # Ne pas afficher le formulaire de paiement si un reçu a été généré
        return
    
    # Étape 1: Recherche de l'élève
    st.markdown("### Étape 1: Rechercher l'élève")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        type_paiement = st.selectbox(
            "Type d'école",
            ["Secondaire", "Primaire"],
            key="paiement_type"
        )
        
        if type_paiement == "Secondaire":
            classe_options = ["Sélectionnez"] + classes_secondaires
        else:
            classe_options = ["Sélectionnez"] + classes_primaires
        
        classe_selection = st.selectbox(
            "Classe",
            classe_options,
            key="paiement_classe"
        )
    
    with col2:
        if type_paiement == "Secondaire" and classe_selection != "Sélectionnez":
            option_options = ["Sélectionnez"] + options_secondaires
            option_selection = st.selectbox(
                "Option",
                option_options,
                key="paiement_option"
            )
        else:
            option_selection = "Non applicable"
        
        nom_recherche = st.text_input(
            "Nom de l'élève",
            placeholder="Entrez le nom de l'élève",
            key="paiement_nom"
        )
    
    with col3:
        vacation_options = ["Sélectionnez"] + list(df['VACATION'].unique()) if not df.empty else ["Sélectionnez"]
        vacation_selection = st.selectbox(
            "Vacation",
            vacation_options,
            key="paiement_vacation"
        )
        
        annee_options = ["Sélectionnez"] + list(df['ANNEE'].unique()) if not df.empty else ["Sélectionnez"]
        annee_selection = st.selectbox(
            "Année scolaire",
            annee_options,
            key="paiement_annee"
        )
    
    eleves_filtres = df.copy()
    
    if classe_selection != "Sélectionnez":
        eleves_filtres = eleves_filtres[eleves_filtres['PROMOTION'] == classe_selection]
    
    if option_selection != "Sélectionnez" and option_selection != "Non applicable" and 'OPTION' in eleves_filtres.columns:
        eleves_filtres = eleves_filtres[eleves_filtres['OPTION'] == option_selection]
    
    if nom_recherche:
        eleves_filtres = eleves_filtres[eleves_filtres['NOMS'].str.contains(nom_recherche, case=False, na=False)]
    
    if vacation_selection != "Sélectionnez":
        eleves_filtres = eleves_filtres[eleves_filtres['VACATION'] == vacation_selection]
    
    if annee_selection != "Sélectionnez":
        eleves_filtres = eleves_filtres[eleves_filtres['ANNEE'] == annee_selection]
    
    if not eleves_filtres.empty:
        st.success(f"{len(eleves_filtres)} élève(s) trouvé(s)")
        
        eleve_selectionne = st.selectbox(
            "Sélectionnez l'élève pour le paiement",
            eleves_filtres['NOMS'].values,
            key="paiement_selection"
        )
        
        if eleve_selectionne:
            eleve_info = df[df['NOMS'] == eleve_selectionne].iloc[0]
            eleve_index = df[df['NOMS'] == eleve_selectionne].index[0]
            
            with st.expander("Informations de l'élève sélectionné", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"**Nom:** {eleve_info['NOMS']}")
                    st.info(f"**Classe:** {eleve_info['PROMOTION']}")
                    st.info(f"**Sexe:** {eleve_info['SEXE']}")
                
                with col2:
                    if 'OPTION' in eleve_info and eleve_info['OPTION']:
                        st.info(f"**Option:** {eleve_info['OPTION']}")
                    st.info(f"**Vacation:** {eleve_info['VACATION']}")
                    st.info(f"**Année:** {eleve_info['ANNEE']}")
                
                st.markdown("#### État des paiements")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Inscription", value=formater_montant(eleve_info['INSCRIPTION']))
                    st.metric("Minerval", value=formater_montant(eleve_info['MINERVAL']))
                
                with col2:
                    st.metric("Tranche 1", value=formater_montant(eleve_info['TRANCHE1'], "$"))
                    st.metric("Tranche 2", value=formater_montant(eleve_info['TRANCHE2'], "$"))
                
                with col3:
                    if 'TRANCHE3' in eleve_info and eleve_info['TRANCHE3'] > 0:
                        st.metric("Tranche 3", value=formater_montant(eleve_info['TRANCHE3'], "$"))
                    
                    total_dollars = eleve_info['TRANCHE1'] + eleve_info['TRANCHE2'] + eleve_info.get('TRANCHE3', 0)
                    total_fc = eleve_info['INSCRIPTION'] + eleve_info['MINERVAL'] + convertir_dollars_en_fc(total_dollars)
                    st.metric("Total payé", value=formater_montant(total_fc))
            
            # Étape 2: Détails du paiement
            st.markdown("### Étape 2: Détails du paiement")
            
            with st.form(key="form_paiement"):
                col1, col2 = st.columns(2)
                
                with col1:
                    type_paiement = st.selectbox(
                        "Type de paiement",
                        ["Inscription", "Minerval", "Tranche 1", "Tranche 2", "Tranche 3", "Autre"],
                        key="type_paiement"
                    )
                    
                    date_paiement = st.date_input(
                        "Date du paiement",
                        value=dt.now(),
                        key="date_paiement"
                    )
                    
                    # Heure du paiement
                    heure_paiement = st.time_input(
                        "Heure du paiement",
                        value=dt.now().time(),
                        key="heure_paiement"
                    )
                    
                    mode_paiement = st.selectbox(
                        "Mode de paiement",
                        ["Espèces", "Mobile Money", "Virement bancaire", "Chèque"],
                        key="mode_paiement"
                    )
                
                with col2:
                    if type_paiement in ["Inscription", "Minerval", "Autre"]:
                        devise = "FC"
                        montant = st.number_input(
                            f"Montant en {devise}",
                            min_value=0,
                            value=10000 if type_paiement == "Inscription" else 10000 if type_paiement == "Minerval" else 0,
                            step=1000,
                            key="montant_fc"
                        )
                        montant_dollars = 0
                        montant_fc = montant
                    else:  # Tranches (en dollars)
                        devise = "$"
                        montant_dollars = st.number_input(
                            f"Montant en {devise}",
                            min_value=0,
                            value=20 if "Tranche" in type_paiement else 0,
                            step=5,
                            key="montant_dollars"
                        )
                        montant_fc = convertir_dollars_en_fc(montant_dollars)
                        montant = montant_fc
                    
                    if montant_dollars > 0:
                        st.info(f"**Équivalent en FC:** {formater_montant(montant_fc)}")
                
                notes = st.text_area(
                    "Notes (optionnel)", 
                    placeholder="Ajoutez des notes si nécessaire...",
                    key="notes_paiement"
                )
                
                col3, col4, col5 = st.columns([1, 2, 1])
                with col4:
                    submit_paiement = st.form_submit_button("ENREGISTRER LE PAIEMENT")
                
                if submit_paiement:
                    if montant == 0:
                        st.error("Le montant doit être supérieur à 0")
                        return
                    
                    if type_paiement == "Inscription":
                        df.at[eleve_index, 'INSCRIPTION'] += montant
                    elif type_paiement == "Minerval":
                        df.at[eleve_index, 'MINERVAL'] += montant
                    elif type_paiement == "Tranche 1":
                        df.at[eleve_index, 'TRANCHE1'] += montant_dollars
                    elif type_paiement == "Tranche 2":
                        df.at[eleve_index, 'TRANCHE2'] += montant_dollars
                    elif type_paiement == "Tranche 3":
                        if 'TRANCHE3' not in df.columns:
                            df['TRANCHE3'] = 0
                        df.at[eleve_index, 'TRANCHE3'] += montant_dollars
                    
                    date_str = date_paiement.strftime("%d/%m/%Y")
                    heure_str = heure_paiement.strftime("%H:%M")
                    
                    historique_texte = f"{date_str} {heure_str} - {type_paiement}: {montant_fc:,.0f} FC"
                    if montant_dollars > 0:
                        historique_texte += f" ({montant_dollars:,.0f} $)"
                    if mode_paiement:
                        historique_texte += f" - Mode: {mode_paiement}"
                    if notes:
                        historique_texte += f" - Note: {notes}"
                    
                    df = ajouter_historique_paiement(
                        df, eleve_index, type_paiement, montant_fc, montant_dollars, date_str, heure_str
                    )
                    
                    if save_data(df):
                        st.success(f"Paiement de {montant_fc:,.0f} FC enregistré avec succès!")
                        
                        paiement_info = {
                            'type': type_paiement,
                            'montant_fc': montant_fc,
                            'montant_dollars': montant_dollars,
                            'date': date_str,
                            'heure': heure_str,
                            'mode': mode_paiement,
                            'notes': notes,
                            'historique': historique_texte
                        }
                        
                        reçu_html = generer_reçu_paiement(eleve_info, paiement_info)
                        
                        # Stocker dans la session pour affichage après le formulaire
                        st.session_state.paiement_reussi = True
                        st.session_state.reçu_html = reçu_html
                        st.session_state.eleve_info = eleve_info
                        st.session_state.paiement_info = paiement_info
                        
                        st.rerun()
    else:
        st.warning("Aucun élève trouvé avec ces critères. Veuillez ajuster vos filtres.")

# === FONCTIONS D'AFFICHAGE AMÉLIORÉES AVEC GRAPHIQUES DÉTAILLÉS ===
def graphiqueGLobal():
    if df_selection.empty:
        st.warning("Aucune donnée à afficher avec les filtres sélectionnés.")
        return
    
    df_temp = df_selection.copy()
    df_temp['count'] = 1
    
    fig_genre = px.pie(
        df_temp.groupby("SEXE")['count'].sum().reset_index(),
        values="count",
        names="SEXE",
        title="RÉPARTITION PAR GENRE",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_genre.update_traces(textinfo="percent+label", textposition="inside", 
                          marker=dict(line=dict(color='#000000', width=2)))
    fig_genre.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white")
    )
    
    eleves_par_classe = df_temp.groupby(by=["PROMOTION"])['count'].sum().reset_index()
    fig_classe = px.bar(
        eleves_par_classe,
        x="PROMOTION",
        y="count",
        title="ÉLÈVES PAR CLASSE",
        color="PROMOTION",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig_classe.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        xaxis=dict(title="Classe"),
        yaxis=dict(title="Nombre d'élèves")
    )
    
    paiements_par_eleve = df_temp.copy()
    paiements_par_eleve['TOTAL_PAYE'] = paiements_par_eleve.apply(
        lambda row: row['INSCRIPTION'] + 
                   row['MINERVAL'] + 
                   convertir_dollars_en_fc(row['TRANCHE1'] + row['TRANCHE2'] + row.get('TRANCHE3', 0)),
        axis=1
    )
    
    paiements_par_eleve = paiements_par_eleve.sort_values('TOTAL_PAYE', ascending=False).head(20)
    
    fig_paiements_eleve = px.bar(
        paiements_par_eleve,
        x='NOMS',
        y='TOTAL_PAYE',
        title='TOTAL PAYÉ PAR ÉLÈVE (Top 20)',
        color='PROMOTION',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig_paiements_eleve.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        xaxis=dict(tickangle=45, title="Élève"),
        yaxis=dict(title="Montant total payé (FC)")
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_genre, use_container_width=True)
        st.plotly_chart(fig_classe, use_container_width=True)
    
    with col2:
        st.plotly_chart(fig_paiements_eleve, use_container_width=True)
        
        if hselected == "OPTIONS" and 'OPTION' in df_selection.columns and not df_selection.empty:
            paiements_par_option = df_selection.groupby('OPTION').agg({
                'INSCRIPTION': 'sum',
                'MINERVAL': 'sum',
                'TRANCHE1': 'sum',
                'TRANCHE2': 'sum'
            }).reset_index()
            
            paiements_par_option['TOTAL_TRANCHES_FC'] = paiements_par_option.apply(
                lambda row: convertir_dollars_en_fc(row['TRANCHE1'] + row['TRANCHE2']),
                axis=1
            )
            
            paiements_par_option['TOTAL_FC'] = (
                paiements_par_option['INSCRIPTION'] + 
                paiements_par_option['MINERVAL'] + 
                paiements_par_option['TOTAL_TRANCHES_FC']
            )
            
            fig_options = px.bar(
                paiements_par_option,
                x='OPTION',
                y='TOTAL_FC',
                title='TOTAL PAYÉ PAR OPTION',
                color='OPTION',
                color_discrete_sequence=px.colors.sequential.Rainbow
            )
            fig_options.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white")
            )
            st.plotly_chart(fig_options, use_container_width=True)

# === NOUVEAUX GRAPHIQUES DÉTAILLÉS ===
def graphiques_detailles():
    if df_selection.empty:
        st.warning("Aucune donnée à afficher avec les filtres sélectionnés.")
        return
    
    # Vérifier si les colonnes nécessaires existent
    required_columns = ['PROMOTION', 'INSCRIPTION', 'MINERVAL', 'TRANCHE1', 'TRANCHE2']
    missing_columns = [col for col in required_columns if col not in df_selection.columns]
    
    if missing_columns:
        st.warning(f"Certaines colonnes sont manquantes: {', '.join(missing_columns)}")
        return
    
    st.markdown("## GRAPHIQUES DÉTAILLÉS")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "PAR CLASSE", "PAR OPTION", "PAR TYPE DE PAIEMENT", 
        "PÉDAGOGIE GÉNÉRALE", "COMMERCIAL & GESTION", "BIOLOGIE CHIMIE",
        "COUPE COUTURE"
    ])
    
    with tab1:
        st.markdown("### Graphiques par Classe")
        
        eleves_par_classe = df_selection.groupby('PROMOTION').size().reset_index(name='Nombre')
        
        fig1 = px.bar(
            eleves_par_classe,
            x='PROMOTION',
            y='Nombre',
            title="Nombre d'élèves par classe",
            color='PROMOTION',
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis_title="Classe",
            yaxis_title="Nombre d'élèves"
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        paiements_par_classe = df_selection.groupby('PROMOTION').agg({
            'INSCRIPTION': 'sum',
            'MINERVAL': 'sum',
            'TRANCHE1': 'sum',
            'TRANCHE2': 'sum',
            'TRANCHE3': 'sum' if 'TRANCHE3' in df_selection.columns else pd.Series([0])
        }).reset_index()
        
        paiements_par_classe['TOTAL_DOLLARS'] = paiements_par_classe['TRANCHE1'] + paiements_par_classe['TRANCHE2'] + paiements_par_classe['TRANCHE3']
        paiements_par_classe['TOTAL_DOLLARS_FC'] = paiements_par_classe.apply(
            lambda row: convertir_dollars_en_fc(row['TOTAL_DOLLARS']), axis=1
        )
        paiements_par_classe['TOTAL_FC'] = paiements_par_classe['INSCRIPTION'] + paiements_par_classe['MINERVAL'] + paiements_par_classe['TOTAL_DOLLARS_FC']
        
        fig2 = px.bar(
            paiements_par_classe,
            x='PROMOTION',
            y='TOTAL_FC',
            title='Total des paiements par classe (FC)',
            color='PROMOTION',
            color_discrete_sequence=px.colors.sequential.Greens
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis_title="Classe",
            yaxis_title="Total FC"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        paiements_detail = paiements_par_classe.melt(
            id_vars='PROMOTION',
            value_vars=['INSCRIPTION', 'MINERVAL', 'TOTAL_DOLLARS_FC'],
            var_name='Type',
            value_name='Montant_FC'
        )
        
        paiements_detail['Type'] = paiements_detail['Type'].map({
            'INSCRIPTION': 'Inscription',
            'MINERVAL': 'Minerval',
            'TOTAL_DOLLARS_FC': 'Frais scolaire ($)'
        })
        
        fig3 = px.bar(
            paiements_detail,
            x='PROMOTION',
            y='Montant_FC',
            color='Type',
            title='Détail des paiements par classe',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
        )
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis_title="Classe",
            yaxis_title="Montant (FC)",
            barmode='stack'
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab2:
        st.markdown("### Graphiques par Option")
        
        if 'OPTION' in df_selection.columns and not df_selection[df_selection['OPTION'].notna()].empty:
            df_secondaire = df_selection[df_selection['PROMOTION'].isin(classes_secondaires)]
            
            if not df_secondaire.empty:
                eleves_par_option = df_secondaire.groupby('OPTION').size().reset_index(name='Nombre')
                
                fig1 = px.pie(
                    eleves_par_option,
                    values='Nombre',
                    names='OPTION',
                    title='Répartition des élèves par option',
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.3
                )
                fig1.update_traces(textinfo="percent+label+value")
                fig1.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="white")
                )
                st.plotly_chart(fig1, use_container_width=True)
                
                paiements_par_option = df_secondaire.groupby('OPTION').agg({
                    'INSCRIPTION': 'sum',
                    'MINERVAL': 'sum',
                    'TRANCHE1': 'sum',
                    'TRANCHE2': 'sum'
                }).reset_index()
                
                paiements_par_option['TOTAL_DOLLARS'] = paiements_par_option['TRANCHE1'] + paiements_par_option['TRANCHE2']
                paiements_par_option['TOTAL_DOLLARS_FC'] = paiements_par_option.apply(
                    lambda row: convertir_dollars_en_fc(row['TOTAL_DOLLARS']), axis=1
                )
                paiements_par_option['TOTAL_FC'] = paiements_par_option['INSCRIPTION'] + paiements_par_option['MINERVAL'] + paiements_par_option['TOTAL_DOLLARS_FC']
                
                fig2 = px.bar(
                    paiements_par_option,
                    x='OPTION',
                    y='TOTAL_FC',
                    title='Total des paiements par option (FC)',
                    color='OPTION',
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="white"),
                    xaxis_title="Option",
                    yaxis_title="Total FC"
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("Aucune donnée secondaire disponible.")
        else:
            st.warning("Aucune donnée d'option disponible.")
    
    with tab3:
        st.markdown("### Graphiques par Type de Paiement")
        
        total_inscription = df_selection['INSCRIPTION'].sum()
        total_minerval = df_selection['MINERVAL'].sum()
        total_tranche1 = df_selection['TRANCHE1'].sum()
        total_tranche2 = df_selection['TRANCHE2'].sum()
        total_tranche3 = df_selection['TRANCHE3'].sum() if 'TRANCHE3' in df_selection.columns else 0
        
        paiements_fc = pd.DataFrame({
            'Type': ['Inscription', 'Minerval'],
            'Montant_FC': [total_inscription, total_minerval]
        })
        
        fig1 = px.pie(
            paiements_fc,
            values='Montant_FC',
            names='Type',
            title='Répartition des paiements en FC',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4'],
            hole=0.4
        )
        fig1.update_traces(textinfo="percent+label+value")
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white")
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        frais_dollars = pd.DataFrame({
            'Tranche': ['Tranche 1', 'Tranche 2', 'Tranche 3'],
            'Montant_$': [total_tranche1, total_tranche2, total_tranche3]
        })
        
        fig2 = px.bar(
            frais_dollars,
            x='Tranche',
            y='Montant_$',
            title='Frais scolaires par tranche ($)',
            color='Tranche',
            color_discrete_sequence=['#45B7D1', '#96C37D', '#FEB144']
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis_title="Tranche",
            yaxis_title="Montant ($)"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        total_tranches_fc = convertir_dollars_en_fc(total_tranche1 + total_tranche2 + total_tranche3)
        
        paiements_totaux = pd.DataFrame({
            'Type': ['Inscription', 'Minerval', 'Frais scolaire'],
            'Montant_FC': [total_inscription, total_minerval, total_tranches_fc]
        })
        
        fig3 = px.bar(
            paiements_totaux,
            x='Type',
            y='Montant_FC',
            title='Total des paiements par type',
            color='Type',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
        )
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis_title="Type de paiement",
            yaxis_title="Montant (FC)"
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab4:
        st.markdown("### Pédagogie Générale")
        if 'OPTION' in df_selection.columns:
            df_pedagogie = df_selection[df_selection['OPTION'] == 'Pédagogie Générale']
            if not df_pedagogie.empty:
                afficher_graphiques_option(df_pedagogie, "Pédagogie Générale")
            else:
                st.warning("Aucune donnée pour Pédagogie Générale.")
    
    with tab5:
        st.markdown("### Commercial & Gestion")
        if 'OPTION' in df_selection.columns:
            df_commercial = df_selection[df_selection['OPTION'] == 'Commercial & Gestion']
            if not df_commercial.empty:
                afficher_graphiques_option(df_commercial, "Commercial & Gestion")
            else:
                st.warning("Aucune donnée pour Commercial & Gestion.")
    
    with tab6:
        st.markdown("### Biologie Chimie")
        if 'OPTION' in df_selection.columns:
            df_biologie = df_selection[df_selection['OPTION'] == 'Biologie Chimie']
            if not df_biologie.empty:
                afficher_graphiques_option(df_biologie, "Biologie Chimie")
            else:
                st.warning("Aucune donnée pour Biologie Chimie.")
    
    with tab7:
        st.markdown("### Coupe Couture")
        if 'OPTION' in df_selection.columns:
            df_coupe = df_selection[df_selection['OPTION'] == 'Coupe Couture']
            if not df_coupe.empty:
                afficher_graphiques_option(df_coupe, "Coupe Couture")
            else:
                st.warning("Aucune donnée pour Coupe Couture.")

def afficher_graphiques_option(df_option, nom_option):
    """Afficher les graphiques spécifiques à une option"""
    
    eleves_classe = df_option.groupby('PROMOTION').size().reset_index(name='Nombre')
    
    fig1 = px.bar(
        eleves_classe,
        x='PROMOTION',
        y='Nombre',
        title=f'Élèves par classe - {nom_option}',
        color='PROMOTION',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        xaxis_title="Classe",
        yaxis_title="Nombre d'élèves"
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    total_inscription = df_option['INSCRIPTION'].sum()
    total_minerval = df_option['MINERVAL'].sum()
    total_tranche1 = df_option['TRANCHE1'].sum()
    total_tranche2 = df_option['TRANCHE2'].sum()
    total_tranches_fc = convertir_dollars_en_fc(total_tranche1 + total_tranche2)
    
    paiements_data = pd.DataFrame({
        'Type': ['Inscription', 'Minerval', 'Frais scolaire'],
        'Montant': [total_inscription, total_minerval, total_tranches_fc]
    })
    
    fig2 = px.pie(
        paiements_data,
        values='Montant',
        names='Type',
        title=f'Répartition des paiements - {nom_option}',
        hole=0.5,
        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
    )
    fig2.update_traces(textinfo="percent+label+value")
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white")
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    frais_data = pd.DataFrame({
        'Tranche': ['Tranche 1', 'Tranche 2'],
        'Montant_$': [total_tranche1, total_tranche2]
    })
    
    fig3 = px.bar(
        frais_data,
        x='Tranche',
        y='Montant_$',
        title=f'Frais scolaires par tranche - {nom_option}',
        color='Tranche',
        color_discrete_sequence=['#96C37D', '#FEB144']
    )
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        xaxis_title="Tranche",
        yaxis_title="Montant ($)"
    )
    st.plotly_chart(fig3, use_container_width=True)

# === FONCTIONS RESTANTES ===
def metricsGLobal():
    if df_selection.empty:
        st.warning("Aucune donnée à afficher avec les filtres sélectionnés.")
        return
    
    totalStudent = df_selection["NOMS"].count()
    totalInscriptionPaye = df_selection["INSCRIPTION"].sum()
    totalMinervalPaye = df_selection["MINERVAL"].sum() if "MINERVAL" in df_selection.columns else 0
    
    totalT1Paye = df_selection["TRANCHE1"].sum()
    totalT2Paye = df_selection["TRANCHE2"].sum()
    totalT3Paye = df_selection["TRANCHE3"].sum() if "TRANCHE3" in df_selection.columns else 0
    
    totalT1PayeFC = convertir_dollars_en_fc(totalT1Paye)
    totalT2PayeFC = convertir_dollars_en_fc(totalT2Paye)
    totalT3PayeFC = convertir_dollars_en_fc(totalT3Paye)
    
    totalScolairePayeFC = totalT1PayeFC + totalT2PayeFC + totalT3PayeFC
    totalScolairePayeDollars = totalT1Paye + totalT2Paye + totalT3Paye
    
    col1, col2 = st.columns(2, vertical_alignment="center")
    with col1:
        st.metric("ÉLÈVES", value=f"{totalStudent}")
    
    with col2:
        sommeTotalFC = totalInscriptionPaye + totalMinervalPaye + totalScolairePayeFC
        sommeTotalDollars = totalScolairePayeDollars
        st.metric("TOTAL FC", value=f"{sommeTotalFC:,.0f} FC")
        st.metric("TOTAL $", value=f"{sommeTotalDollars:,.0f} $")
    
    col1, col2, col3 = st.columns(3, vertical_alignment="center")
    with col1:
        st.metric("INSCRIPTION", value=f"{totalInscriptionPaye:,.0f} FC")
        st.metric("MINERVAL", value=f"{totalMinervalPaye:,.0f} FC")
    
    with col2:
        st.metric("FRAIS SCOLAIRE", value=f"{totalScolairePayeFC:,.0f} FC")
        st.metric("(T1+T2+T3)", value=f"{totalScolairePayeDollars:,.0f} $")
    
    with col3:
        st.metric("TRANCHE 1", value=f"{totalT1Paye:,.0f} $")
        st.metric("TRANCHE 2", value=f"{totalT2Paye:,.0f} $")
        if totalT3Paye > 0:
            st.metric("TRANCHE 3", value=f"{totalT3Paye:,.0f} $")
    
    style_metric_cards(background_color="#1E4466", border_left_color="#720B07")

def tableauGLobal():
    if df_selection.empty:
        st.warning("Aucune donnée à afficher avec les filtres sélectionnés.")
        return
    
    display_df = df_selection.copy()
    
    display_df['FRAIS_SCOLAIRE_TOTAL_$'] = (
        display_df['TRANCHE1'] + 
        display_df['TRANCHE2'] + 
        display_df.get('TRANCHE3', 0)
    )
    
    display_df['FRAIS_SCOLAIRE_TOTAL_FC'] = display_df['FRAIS_SCOLAIRE_TOTAL_$'].apply(convertir_dollars_en_fc)
    
    columns_to_show = [
        'NOMS', 'SEXE', 'PROMOTION', 'VACATION', 'ANNEE',
        'INSCRIPTION', 'MINERVAL', 'FRAIS_SCOLAIRE_TOTAL_FC', 'FRAIS_SCOLAIRE_TOTAL_$'
    ]
    
    if 'OPTION' in display_df.columns:
        columns_to_show.insert(2, 'OPTION')
    
    display_df = display_df[columns_to_show]
    display_df = display_df.rename(columns={
        'INSCRIPTION': 'INSCRIPTION (FC)',
        'MINERVAL': 'MINERVAL (FC)',
        'FRAIS_SCOLAIRE_TOTAL_FC': 'FRAIS SCOLAIRE (FC)',
        'FRAIS_SCOLAIRE_TOTAL_$': 'FRAIS SCOLAIRE ($)'
    })
    
    for col in display_df.columns:
        if col.endswith('(FC)'):
            display_df[col] = display_df[col].apply(lambda x: f"{int(x):,} FC" if pd.notnull(x) else "0 FC")
        elif col.endswith('($)'):
            display_df[col] = display_df[col].apply(lambda x: f"{int(x):,} $" if pd.notnull(x) else "0 $")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )

# === FILTRAGE DES DONNÉES ===
if not df.empty:
    df_selection = df.copy()
    
    if type_ecole == "Secondaire":
        df_selection = df_selection[df_selection['PROMOTION'].isin(classes_secondaires)]
    elif type_ecole == "Primaire":
        df_selection = df_selection[df_selection['PROMOTION'].isin(classes_primaires)]
    
    if genre:
        df_selection = df_selection[df_selection['SEXE'].isin(genre)]
    
    if option and 'OPTION' in df_selection.columns:
        df_selection = df_selection[df_selection['OPTION'].isin(option)]
    
    if classeFilter:
        df_selection = df_selection[df_selection['PROMOTION'].isin(classeFilter)]
    
    if vacation:
        df_selection = df_selection[df_selection['VACATION'].isin(vacation)]
    
    if annee:
        df_selection = df_selection[df_selection['ANNEE'].isin(annee)]
else:
    df_selection = pd.DataFrame()

# === ROUTAGE DES FONCTIONNALITÉS ===
if selectedRendu == "NOUVEAU PAIEMENT":
    nouveau_paiement()

elif selectedRendu == "CONTRÔLE ÉLÈVE":
    controle_eleve()

elif selectedRendu == "STATISTIQUE":
    if hselected == "GLOBALE":
        metricsGLobal()
    elif hselected == "OPTIONS":
        if type_ecole in ["Tous", "Secondaire"] and not df_selection.empty:
            if 'OPTION' in df_selection.columns and df_selection['OPTION'].notna().any():
                st.markdown("## STATISTIQUES PAR OPTION")
                metricsGLobal()
            else:
                st.warning("Aucune donnée d'option disponible pour le secondaire.")
        else:
            st.warning("Aucune donnée à afficher. Sélectionnez 'Secondaire' dans les filtres.")
    
    elif hselected == "PRIMAIRE":
        if type_ecole in ["Tous", "Primaire"] and not df_selection.empty:
            metricsGLobal()
        else:
            st.warning("Aucune donnée à afficher. Sélectionnez 'Primaire' dans les filtres.")

elif selectedRendu == "GRAPHIQUE":
    if hselected == "GLOBALE":
        col1, col2 = st.columns([1, 1])
        with col1:
            graphiqueGLobal()
        with col2:
            # Ajoutez un expander pour les graphiques détaillés
            with st.expander("GRAPHIQUES DÉTAILLÉS", expanded=True):
                graphiques_detailles()
    
    elif hselected == "OPTIONS":
        if type_ecole in ["Tous", "Secondaire"] and not df_selection.empty:
            if 'OPTION' in df_selection.columns and df_selection['OPTION'].notna().any():
                graphiques_detailles()
            else:
                st.warning("Aucune donnée d'option disponible.")
        else:
            st.warning("Aucune donnée à afficher. Sélectionnez 'Secondaire' dans les filtres.")
    
    elif hselected == "PRIMAIRE":
        if type_ecole in ["Tous", "Primaire"] and not df_selection.empty:
            graphiques_primaire()
        else:
            st.warning("Aucune donnée primaire à afficher. Sélectionnez 'Primaire' dans les filtres.")
    
    else:
        graphiqueGLobal()

elif selectedRendu == "TABLEAU":
    if hselected == "GLOBALE":
        tableauGLobal()
    elif hselected == "LISTES PAR CLASSE":
        # Redirection vers le contrôle élève pour les listes par classe
        controle_eleve()
    else:
        tableauGLobal()

# === PANEL D'INFORMATIONS RAPIDES ===
st.sidebar.markdown("---")
st.sidebar.markdown("## Informations rapides")

if not df.empty:
    total_eleves = len(df)
    total_inscription = df['INSCRIPTION'].sum()
    total_minerval = df['MINERVAL'].sum()
    total_tranches = df['TRANCHE1'].sum() + df['TRANCHE2'].sum() + df.get('TRANCHE3', pd.Series([0])).sum()
    
    st.sidebar.metric("Total élèves", total_eleves)
    st.sidebar.metric("Total FC", f"{total_inscription + total_minerval:,.0f} FC")
    st.sidebar.metric("Total $", f"{total_tranches:,.0f} $")
    
    if 'DATE_DERNIER_PAIEMENT' in df.columns and not df['DATE_DERNIER_PAIEMENT'].isna().all():
        df_dates = df[df['DATE_DERNIER_PAIEMENT'].notna() & (df['DATE_DERNIER_PAIEMENT'] != '')]
        
        if not df_dates.empty:
            try:
                dernier_paiement = df_dates.iloc[-1]
                date_paiement = dernier_paiement.get('DATE_DERNIER_PAIEMENT', '')
                heure_paiement = dernier_paiement.get('HEURE_DERNIER_PAIEMENT', '')
                
                if date_paiement and heure_paiement:
                    st.sidebar.markdown(
                        f"*Dernier paiement:*\n"
                        f"{dernier_paiement['NOMS']}\n"
                        f"{date_paiement} à {heure_paiement}"
                    )
                elif date_paiement:
                    st.sidebar.markdown(
                        f"*Dernier paiement:*\n"
                        f"{dernier_paiement['NOMS']}\n"
                        f"{date_paiement}"
                    )
            except Exception as e:
                st.sidebar.info("Informations de paiement disponibles")

# Bouton d'actualisation
if st.sidebar.button("Actualiser les données"):
    st.cache_data.clear()
    st.rerun()

# === FOOTER ===
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 12px;'>"
    "Complexe Scolaire du Jourdain 1 © 2024 - Système de Gestion des Frais Scolaires"
    "</div>",
    unsafe_allow_html=True
)