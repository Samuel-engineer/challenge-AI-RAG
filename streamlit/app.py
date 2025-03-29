import streamlit as st
import home
import streamlit.workspace as workspace

# Gestion des pages
if st.session_state.page == "Accueil":
    home.show_home()
elif st.session_state.page == "Travail":
    workspace.main()
