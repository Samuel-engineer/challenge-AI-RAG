import streamlit as st
from api_utils import get_api_response, get_chat_history
import uuid

def display_chat_interface():
    # Initialisation sécurisée des variables de session
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Supprimer la clé s'il y a eu une erreur de duplication
    if "chat_input_key" not in st.session_state or st.session_state.chat_input_key is None:
        st.session_state.chat_input_key = f"chat_input_{uuid.uuid4()}"

    # Affichage de l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Affichage du champ de saisie
    try:
        prompt = st.chat_input("Query:", key=st.session_state.chat_input_key)
    except st.errors.StreamlitDuplicateElementKey:
        # Régénérer une clé si erreur de duplication
        st.session_state.chat_input_key = f"chat_input_{uuid.uuid4()}"
        prompt = st.chat_input("Query:", key=st.session_state.chat_input_key)

    # Traitement de la requête
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Generating response..."):
            response = get_api_response(
                prompt,
                st.session_state.session_id,
                st.session_state.model
            )

        if response:
            st.session_state.session_id = response.get("session_id", st.session_state.session_id)
            answer = response["answer"]
            st.session_state.messages.append({"role": "assistant", "content": answer})

            with st.chat_message("assistant"):
                st.markdown(answer)

                with st.expander("Details"):
                    st.subheader("Generated Answer")
                    st.code(answer)
                    st.subheader("Model Used")
                    st.code(response["model"])
                    st.subheader("Session ID")
                    st.code(response["session_id"])
        else:
            st.error("Failed to get a response from the API.")


# Fonction pour récupérer l'historique des conversations




def display_chat_history():
    """Affiche l'historique des messages"""
    session_id = st.session_state.get("session_id")
    if not session_id:
        return  # Pas de session active

    history = get_chat_history(session_id)
    
    # Ajouter l'historique à st.session_state.messages si ce n'est pas déjà fait
    if history :
        for msg in history["history"]:
            st.session_state.messages.append(
                {"role": "user", "content": msg["user_query"]}
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": msg["gpt_response"]}
            )

    # Affichage des messages (y compris l'historique)
    #for message in st.session_state.messages:
    #    with st.chat_message(message["role"]):
     #       st.markdown(message["content"])


# Ajouter l'affichage de l'historique au lancement


