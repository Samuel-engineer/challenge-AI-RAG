import streamlit as st
from PIL import Image

# Définition des styles CSS pour une meilleure présentation
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 2.5em;
            font-weight: bold;
            color: #1E88E5;
        }
        .subtitle {
            text-align: center;
            font-size: 1.5em;
            color: #555;
        }
        .highlight {
            background-color: #F0F0F0;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            font-size: 1.1em;
            color: #888;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    # Vérification si 'page' existe dans session_state
    if "page" not in st.session_state:
        st.session_state.page = "Accueil"

    # Affichage des logos en haut
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.image("logo1.jpeg", width=100)
    with col2:
        st.image("logo.jpeg", width=100)
    with col3:
        st.image("LOGO_EFREI.jpeg", width=150)

    # Titre principal
    st.markdown("<p class='title'>🏠 Bienvenue sur l'application</p>", unsafe_allow_html=True)

    # Message utilisateur
    if st.session_state.get("authenticated", False):
        st.success(f"👋 Bonjour {st.session_state.username}, explorez votre espace de travail !")
    else:
        st.info("🔑 Veuillez vous connecter pour accéder à vos données.")

    # Présentation de la plateforme
    st.markdown("<p class='subtitle'>💡 Découvrez la propriété intellectuelle de manière interactive</p>", unsafe_allow_html=True)
    st.write(
        "Cette plateforme vous aide à mieux comprendre les concepts de propriété intellectuelle "
        "à travers des exercices interactifs, des études de cas et des outils avancés basés sur l'intelligence artificielle."
    )

    # Affichage de la première image
    st.image("propriete-intellectuelle.jpeg", width=700)
    
    # Avantages de la plateforme
    st.markdown("<p class='highlight'>🚀 Pourquoi utiliser notre solution ?</p>", unsafe_allow_html=True)

    avantages = {
        "📚 Apprentissage interactif" : "Des exercices variés et adaptés pour comprendre la propriété intellectuelle.",
        "🤖 Intelligence artificielle" : "Un assistant intelligent pour répondre à toutes vos questions.",
        "🌍 Accessibilité" : "Disponible à tout moment, partout, et sur tous vos appareils."
    }

    for titre, description in avantages.items():
        st.markdown(f"### {titre}")
        st.write(description)

    # Appel à l'action avec redirection correcte, uniquement si l'utilisateur n'est pas connecté
    if not st.session_state.get("authenticated", False):  # Vérifier si l'utilisateur n'est pas connecté
        st.markdown("<p class='highlight'>🔑 Rejoignez-nous !</p>", unsafe_allow_html=True)
        st.write("Créez un compte ou connectez-vous pour profiter pleinement de la plateforme.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Se connecter"):
                st.session_state.page = "Connexion"  # Redirection vers la page de connexion
        with col2:
            if st.button("📝 Créer un compte"):
                st.session_state.page = "Inscription"  # Redirection vers la page d'inscription
    else:
        st.success(f"👋 Vous êtes déjà connecté, explorez votre espace de travail !")

    # Pied de page
    st.markdown("<p class='footer'>© 2025 - Tous droits réservés | Plateforme de propriété intellectuelle</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
