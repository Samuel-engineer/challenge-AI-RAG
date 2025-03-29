import streamlit as st
from sidebar import display_sidebar
from chat_interface import display_chat_interface, display_chat_history

# Initialisation des variables de session pour les messages et session_id
if "messages" not in st.session_state:
    st.session_state.messages = []
    
st.session_state.session_id = f"session_2_{st.session_state.id}"
print(st.session_state.session_id)

# Afficher la barre latérale pour l'upload et gestion des documents
display_sidebar()

display_chat_history()
# Afficher l'interface de chat
display_chat_interface()

