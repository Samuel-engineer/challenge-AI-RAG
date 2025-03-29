import streamlit as st
import subprocess
from api_utils import (
    upload_document, list_documents, delete_document,
    upload_web_document, delete_all_documents
)

def refresh_documents():
    """Rafraîchir la liste des documents et les stocker dans session_state."""
    with st.spinner("📂 Chargement des documents..."):
        st.session_state.documents = list_documents()

def display_sidebar():
    # Sélection du modèle
    model_options = ["mistral-large-latest"]
    st.sidebar.selectbox("🤖 Modèle d'IA", options=model_options, key="model")

    # **📂 Gestion des Documents**
    st.sidebar.header("📂 Gestion des Documents")
    
    # Upload de fichier
    uploaded_file = st.sidebar.file_uploader("📤 Ajouter un fichier", type=["pdf", "docx", "html"])
    if uploaded_file and st.sidebar.button("📎 Télécharger"):
        with st.spinner("📤 Téléchargement en cours..."):
            upload_response = upload_document(uploaded_file)
            if upload_response:
                st.sidebar.success(f"✅ {uploaded_file.name} ajouté avec succès (ID: {upload_response['file_id']})")
                refresh_documents()

    # Upload des sites web
    if st.sidebar.button("🌐 Télécharger les sites"):
        with st.spinner("📥 Récupération et indexation en cours..."):
            upload_response = upload_web_document()
            if upload_response:
                st.sidebar.success("✅ Données web ajoutées avec succès !")
                refresh_documents()

    # **📋 Liste des Documents**
    st.sidebar.header("📋 Documents Indexés")
    
    # Vérification et rafraîchissement des documents
    if "documents" not in st.session_state:
        refresh_documents()

    documents = st.session_state.get("documents", [])
    
    if documents:
        # Sélection d'un document à supprimer
        selected_file_id = st.sidebar.selectbox(
            "🗑 Sélectionner un document à supprimer",
            options=[doc["id"] for doc in documents],
            format_func=lambda x: next(doc["filename"] for doc in documents if doc["id"] == x)
        )

        if st.sidebar.button("🗑 Supprimer le document"):
            with st.spinner("🔄 Suppression en cours..."):
                delete_response = delete_document(selected_file_id)
                if delete_response:
                    st.sidebar.success(f"✅ Document (ID: {selected_file_id}) supprimé avec succès")
                    refresh_documents()
                else:
                    st.sidebar.error(f"❌ Échec de la suppression du document ID: {selected_file_id}")

        # Suppression de tous les documents
        if st.sidebar.button("🗑 Supprimer tous les documents"):
            with st.spinner("🔄 Suppression en cours..."):
                delete_response = delete_all_documents()
                if delete_response:
                    st.sidebar.success("✅ Tous les documents ont été supprimés avec succès")
                    refresh_documents()
                else:
                    st.sidebar.error("❌ Échec de la suppression des documents.")

    else:
        st.sidebar.info("📭 Aucun document indexé.")

    # **🚀 Exécution du script de scraping**
    if st.sidebar.button("🏃‍♂️ Lancer le scraping"):
        with st.spinner("🔄 Exécution en cours..."):
            subprocess.run(["python", "script/scrape_utils.py"], shell=True)
        st.sidebar.success("✅ Script exécuté avec succès !")
