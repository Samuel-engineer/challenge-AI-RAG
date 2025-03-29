import streamlit as st
import sqlite3
import bcrypt
import importlib.util
import os

# 🌟 Ajout du CSS avec des couleurs pastel et un beau bleu
st.markdown(
    """
    <style>
        /* Styles généraux */
        body {
            background-color: #E3F2FD; /* Bleu pastel clair */
            font-family: 'Arial', sans-serif;
        }

        /* Titres principaux */
        .main-title {
            text-align: center;
            font-size: 2.5em;
            font-weight: bold;
            color: #6C9BCF; /* Bleu doux */
            margin-bottom: 20px;
        }

        /* Conteneur principal */
        .stApp {
            background-color: #FDFBFF; /* Blanc cassé */
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0px 4px 10px rgba(108, 155, 207, 0.2);
        }

        /* Boutons */
        div.stButton > button {
            background-color: #003366; /* Bleu foncé */
            color: white;
            font-size: 1.2em;  /* Augmenter la taille du texte */
            padding: 15px 25px;  /* Augmenter la hauteur et la largeur */
            border-radius: 8px;
            border: none;
            width: 190px;  /* Étendre le bouton sur toute la largeur */
            transition: background-color 0.3s ease-in-out;
        }

        div.stButton > button:hover {
            background-color: #002244; /* Bleu foncé légèrement plus sombre */
            transform: scale(1.05);
        }

        /* Champs de formulaire */
        .stTextInput > div > input {
            border: 2px solid #6C9BCF; /* Bleu doux */
            border-radius: 8px;
            padding: 10px;
        }

        /* Messages de succès et d'erreur */
        .stAlert {
            padding: 15px;
            border-radius: 8px;
            font-size: 1.1em;
        }

        .stAlert-success {
            background-color: #D6E4FF; /* Bleu pastel */
            color: #3B5998;
        }

        .stAlert-error {
            background-color: #FFDDDD;
            color: #D32F2F;
        }

        /* Barre latérale */
        .stSidebar {
            background-color: #D6E4FF; /* Bleu pastel */
            padding: 15px;
            border-radius: 10px;
        }

        /* Pied de page */
        .footer {
            text-align: center;
            font-size: 1.1em;
            color: #888;
            margin-top: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Connexion à la base de données SQLite
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# Création de la table des utilisateurs si elle n'existe pas
c.execute(''' 
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT,
        password TEXT
    )
''')
conn.commit()

# Initialisation des variables de session
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "id" not in st.session_state:
    st.session_state.id = ""
if "session_id" not in st.session_state:
    st.session_state.session_id = ""
if "page" not in st.session_state:
    st.session_state.page = "Accueil"  # Démarrer sur la page d'accueil par défaut

# Fonction pour changer de page
def change_page(page_name):
    st.session_state.page = page_name

# Fonction pour afficher la barre de navigation
def show_sidebar():
    st.sidebar.image("logo.jpeg",  width=100)
    
    if st.session_state.authenticated:
        st.sidebar.write(f"👤 **{st.session_state.username}**")
        if st.sidebar.button("🏠 Accueil"):
            change_page("Accueil")
        if st.sidebar.button("💼 Espace de Travail"):
            change_page("Travail")
        if st.sidebar.button("🔐 Déconnexion"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.id = ""
            st.session_state.session_id = ""
            st.session_state.messages = []
            change_page("Connexion")
    else:
        if st.sidebar.button("🔑 Connexion"):
            change_page("Connexion")
        if st.sidebar.button("📝 Inscription"):
            change_page("Inscription")

# Page d'inscription
def show_signup():
    st.markdown("<h1 class='main-title'>📝 Inscription</h1>", unsafe_allow_html=True)
    st.image("logo.jpeg", width=100)

    with st.form("signup_form"):
        new_user = st.text_input("Nom d'utilisateur")
        new_email = st.text_input("Email")
        new_password = st.text_input("Mot de passe", type="password")
        submit_button = st.form_submit_button("S'inscrire")

    if submit_button:
        if new_user and new_email and new_password:
            try:
                hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                          (new_user, new_email, hashed_pw))
                conn.commit()
                st.success("✅ Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
                change_page("Connexion")
            except sqlite3.IntegrityError:
                st.error("❌ Ce nom d'utilisateur est déjà pris.")
        else:
            st.warning("⚠️ Veuillez remplir tous les champs.")

# Page de connexion
def show_login():
    st.markdown("<h1 class='main-title'>🔑 Connexion</h1>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit_button = st.form_submit_button("Se connecter")

    if submit_button:
        c.execute("SELECT username, email, password, id FROM users WHERE username=?", (username,))
        user_data = c.fetchone()

        if user_data and bcrypt.checkpw(password.encode(), user_data[2].encode()):
            st.session_state.authenticated = True
            st.session_state.username = user_data[0]
            st.session_state.id = user_data[3]
            st.success(f"✅ Bienvenue {username} ! Redirection vers votre espace de travail...")
            change_page("Accueil")  # Rediriger directement vers la page Accueil
        else:
            st.error("❌ Nom d'utilisateur ou mot de passe incorrect.")

# Chargement dynamique du fichier workspace.py
def workspace_page():
    if not st.session_state.authenticated:
        st.warning("🔒 Vous devez être connecté pour accéder à l'espace de travail.")
        change_page("Connexion")
    else:
        workspace_path = "workspace.py"
        if os.path.exists(workspace_path):
            spec = importlib.util.spec_from_file_location("workspace", workspace_path)
            workspace = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(workspace)
            workspace.main()  # Assurez-vous que workspace.py contient une fonction `main()` pour exécuter son contenu
        else:
            st.error("❌ Le fichier workspace.py est introuvable.")

# Chargement dynamique du fichier home.py
def home_page():
    home_path = "home.py"
    if os.path.exists(home_path):
        spec = importlib.util.spec_from_file_location("home", home_path)
        home = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(home)
        home.main()  # Assurez-vous que home.py contient une fonction `main()`
    else:
        st.error("❌ Le fichier home.py est introuvable.")

# Affichage du menu de navigation
show_sidebar()

# Affichage de la page sélectionnée
if st.session_state.page == "Accueil":
    home_page()
elif st.session_state.page == "Inscription":
    show_signup()
elif st.session_state.page == "Travail":
    workspace_page()
elif st.session_state.page == "Connexion":
    show_login()
