import requests
import streamlit as st

# Définir l'URL de l'API
API_URL = "http://localhost:8000"

def api_request(endpoint, method="GET", headers=None, data=None, files=None):
    """Effectue une requête API générique et gère les erreurs."""
    url = f"{API_URL}{endpoint}"
    headers = headers or {"accept": "application/json", "Content-Type": "application/json"}

    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=data, files=files)
        else:
            response = requests.get(url, headers=headers)

        response.raise_for_status()  # Déclenche une exception en cas d'erreur HTTP
        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"🚨 Erreur API [{method} {endpoint}] : {e}")
        return None

def get_api_response(question, session_id=None, model="gpt-3.5"):
    """Envoie une question à l'API et retourne la réponse du modèle."""
    data = {"question": question, "model": model}
    if session_id:
        data["session_id"] = session_id

    return api_request("/chat", method="POST", data=data)

def upload_document(file):
    """Upload un fichier vers l'API et l'indexe dans ChromaDB."""
    if file is None:
        st.error("❌ Aucun fichier sélectionné.")
        return None

    st.info("📤 Envoi du fichier...")

    files = {"file": (file.name, file, file.type)}
    return api_request("/upload-doc", method="POST", files=files)

def upload_web_document():
    """Upload des documents web pré-récupérés et les indexe."""
    st.info("🌐 Indexation des documents web...")
    return api_request("/upload-web-doc", method="POST")

def list_documents():
    """Récupère la liste des documents indexés."""
    return api_request("/list-docs")

def delete_document(file_id):
    """Supprime un document spécifique."""
    if not file_id:
        st.error("❌ ID du fichier manquant.")
        return None

    st.warning(f"🗑 Suppression du fichier {file_id}...")
    return api_request("/delete-doc", method="POST", data={"file_id": file_id})

def delete_all_documents():
    """Supprime tous les documents stockés dans ChromaDB et la base de données."""
    st.warning("⚠ Suppression de tous les documents en cours...")
    return api_request("/deleteAll-doc", method="POST")

def get_chat_history(session_id):
    """Récupère l'historique des messages pour une session donnée."""
    if not session_id:
        st.error("❌ ID de session manquant.")
        return None

    return api_request(f"/get-chat-history?session_id={session_id}", method="GET")
