import os
import shutil
import logging
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader, TextLoader
)

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Charger les variables d'environnement
load_dotenv()

# Configuration de Chroma et de l'embedding
PERSIST_DIR = "./chroma_db"
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
embedding_function = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding_function)

def load_and_split_document(file_path: str) -> List[Document]:
    """Charge un document et le divise en segments de texte."""
    try:
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        elif file_path.endswith('.html'):
            loader = UnstructuredHTMLLoader(file_path)
        elif file_path.endswith('.txt'):
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError(f"❌ Format non pris en charge : {file_path}")

        documents = loader.load()
        return text_splitter.split_documents(documents)
    except Exception as e:
        logging.error(f"❌ Erreur lors du chargement du document {file_path} : {e}")
        return []

def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    """Indexe un document dans la base Chroma."""
    try:
        splits = load_and_split_document(file_path)
        
        if not splits:
            logging.warning(f"⚠️ Aucun segment extrait pour {file_path}. L'indexation est annulée.")
            return False
        
        for split in splits:
            split.metadata['file_id'] = file_id
        
        vectorstore.add_documents(splits)
        logging.info(f"✅ Document {file_path} indexé avec succès dans Chroma.")
        return True
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'indexation du document {file_path} : {e}")
        return False

def delete_doc_from_chroma(file_id: int) -> bool:
    """Supprime un document de la base Chroma en utilisant son file_id."""
    try:
        results = vectorstore.get()
        
        doc_ids = [doc_id for doc_id, metadata in zip(results["ids"], results["metadatas"]) if metadata.get("file_id") == file_id]

        if not doc_ids:
            logging.warning(f"⚠️ Aucun document trouvé avec file_id {file_id}.")
            return False

        vectorstore.delete(doc_ids)
        logging.info(f"✅ Document avec file_id {file_id} supprimé de Chroma.")
        return True
    except Exception as e:
        logging.error(f"❌ Erreur lors de la suppression du document {file_id} de Chroma : {e}")
        return False

def delete_all_docs_from_chroma() -> bool:
    """Supprime complètement tous les documents de Chroma en supprimant le répertoire de persistance."""
    try:
        if os.path.exists(PERSIST_DIR):
            shutil.rmtree(PERSIST_DIR)
            logging.info(f"✅ Répertoire de persistance '{PERSIST_DIR}' supprimé.")
            return True
        else:
            logging.warning(f"⚠️ Aucun répertoire de persistance trouvé à '{PERSIST_DIR}'.")
            return False
    except Exception as e:
        logging.error(f"❌ Erreur lors de la suppression de Chroma : {e}")
        return False
