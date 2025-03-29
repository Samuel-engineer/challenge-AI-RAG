import os
import uuid
import shutil
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from langchain_utils import get_rag_chain
from db_utils import (
    insert_application_log, get_chat_history, get_all_documents, 
    insert_document, delete_document, delete_all_documents, get_chat_history_a
)
from chroma_utils import index_document_to_chroma, delete_doc_from_chroma, delete_all_docs_from_chroma

# Configuration du logger
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    """Gère les requêtes de chat via le modèle RAG."""
    session_id = query_input.session_id or str(uuid.uuid4())

    logging.info(f"🔹 [Session: {session_id}] Question: {query_input.question} | Model: {query_input.model.value}")
    
    chat_history = get_chat_history(session_id)
    rag_chain = get_rag_chain(query_input.model.value)
    
    try:
        answer = rag_chain.invoke({
            "input": query_input.question,
            "chat_history": chat_history
        })['answer']
        
        insert_application_log(session_id, query_input.question, answer, query_input.model.value)
        logging.info(f"✅ [Session: {session_id}] Réponse générée.")
        return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)
    except Exception as e:
        logging.error(f"❌ Erreur dans /chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors du traitement de la requête.")

@app.post("/upload-doc")
def upload_and_index_document(file: UploadFile = File(...)):
    """Upload un fichier et l'indexe dans ChromaDB."""
    allowed_extensions = {".pdf", ".docx", ".html"}
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"❌ Format non supporté. Types autorisés: {', '.join(allowed_extensions)}")
    
    temp_file_path = f"temp_{uuid.uuid4().hex}{file_extension}"

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_id = insert_document(file.filename)
        if not index_document_to_chroma(temp_file_path, file_id):
            delete_document(file_id)
            raise HTTPException(status_code=500, detail=f"Échec de l'indexation du fichier {file.filename}.")
        
        return {"message": f"✅ Fichier {file.filename} indexé avec succès.", "file_id": file_id}
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'upload de {file.filename} : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/upload-web-doc")
def upload_documents():
    """Indexe un document HTML récupéré depuis un site web."""
    output_file = os.path.join(os.path.dirname(__file__), "result.txt")

    try:
        file_id = insert_document("html epo web sites")
        if not index_document_to_chroma(output_file, file_id):
            delete_document(file_id)
            raise HTTPException(status_code=500, detail="Échec de l'indexation des fichiers HTML.")
        
        return {"message": "✅ Documents HTML indexés avec succès."}
    except Exception as e:
        logging.error(f"❌ Erreur dans /upload-web-doc : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/list-docs", response_model=list[DocumentInfo])
def list_documents():
    """Retourne la liste des documents stockés."""
    return get_all_documents()

@app.post("/delete-doc")
def delete_document(request: DeleteFileRequest):
    """Supprime un document spécifique de ChromaDB et de la base de données."""
    try:
        if not delete_doc_from_chroma(request.file_id):
            raise HTTPException(status_code=500, detail=f"❌ Échec de la suppression dans Chroma pour file_id {request.file_id}.")

        if not delete_document(request.file_id):
            raise HTTPException(status_code=500, detail=f"⚠️ Supprimé de Chroma, mais échec dans la base de données.")

        return {"message": f"✅ Document file_id {request.file_id} supprimé avec succès."}
    except Exception as e:
        logging.error(f"❌ Erreur lors de la suppression de file_id {request.file_id} : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.post("/deleteAll-doc")
def deleteAll_document():
    """Supprime tous les documents stockés dans ChromaDB et la base de données."""
    try:
        if not delete_all_docs_from_chroma():
            raise HTTPException(status_code=500, detail="❌ Échec de la suppression de Chroma.")

        if not delete_all_documents():
            raise HTTPException(status_code=500, detail="⚠️ Supprimé de Chroma, mais échec dans la base de données.")

        return {"message": "✅ Tous les documents ont été supprimés avec succès."}
    except Exception as e:
        logging.error(f"❌ Erreur lors de la suppression de tous les documents : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/get-chat-history")
def get_chat_history_api(session_id: str):
    """Récupère l'historique de chat pour une session donnée."""
    try:
        history = get_chat_history_a(session_id)

        if not history:
            raise HTTPException(status_code=404, detail=f"⚠️ Aucun historique trouvé pour la session {session_id}.")

        return {"session_id": session_id, "history": history}
    
    except Exception as e:
        logging.error(f"❌ Erreur dans /get-chat-history : {e}")
        

