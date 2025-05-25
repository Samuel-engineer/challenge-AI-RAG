import sqlite3
import logging
from datetime import datetime

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DB_NAME = "data_battle.db"

def get_db_connection():
    """Établit une connexion à la base de données SQLite."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # Permet d'accéder aux résultats sous forme de dictionnaire
        return conn
    except sqlite3.Error as e:
        logging.error(f"❌ Erreur de connexion à la base de données : {e}")
        return None

def create_tables():
    """Crée les tables si elles n'existent pas déjà."""
    queries = [
        '''CREATE TABLE IF NOT EXISTS application_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_query TEXT,
            gpt_response TEXT,
            model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS document_store (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''
    ]
    
    with get_db_connection() as conn:
        if conn:
            cursor = conn.cursor()
            for query in queries:
                cursor.execute(query)
            conn.commit()
            logging.info("✅ Tables créées avec succès.")

def insert_application_log(session_id, user_query, gpt_response, model):
    """Ajoute une entrée dans la table application_logs."""
    query = '''INSERT INTO application_logs (session_id, user_query, gpt_response, model) 
               VALUES (?, ?, ?, ?)'''
    try:
        with get_db_connection() as conn:
            if conn:
                conn.execute(query, (session_id, user_query, gpt_response, model))
                conn.commit()
                logging.info("✅ Log ajouté avec succès.")
    except sqlite3.Error as e:
        logging.error(f"❌ Erreur lors de l'insertion du log : {e}")

def get_chat_history(session_id):
    """Récupère l'historique de chat pour une session donnée."""
    query = '''SELECT user_query, gpt_response FROM application_logs 
               WHERE session_id = ? ORDER BY created_at'''
    try:
        with get_db_connection() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute(query, (session_id,))
                messages = [{"role": "human", "content": row["user_query"]} for row in cursor.fetchall()]
                return messages
    except sqlite3.Error as e:
        logging.error(f"❌ Erreur lors de la récupération du chat history : {e}")
    return []

def insert_document(filename):
    """Ajoute un document à la base de données."""
    query = "INSERT INTO document_store (filename) VALUES (?)"
    try:
        with get_db_connection() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute(query, (filename,))
                file_id = cursor.lastrowid
                conn.commit()
                logging.info(f"✅ Document ajouté : {filename} (ID: {file_id})")
                return file_id
    except sqlite3.Error as e:
        logging.error(f"❌ Erreur lors de l'ajout du document : {e}")
    return None

def delete_document(file_id):
    """Supprime un document spécifique."""
    query = "DELETE FROM document_store WHERE id = ?"
    try:
        with get_db_connection() as conn:
            if conn:
                conn.execute(query, (file_id,))
                conn.commit()
                logging.info(f"✅ Document ID {file_id} supprimé avec succès.")
                return True
    except sqlite3.Error as e:
        logging.error(f"❌ Erreur lors de la suppression du document : {e}")
    return False

def delete_all_documents():
    """Supprime tous les documents de la base."""
    query = "DELETE FROM document_store"
    try:
        with get_db_connection() as conn:
            if conn:
                conn.execute(query)
                conn.commit()
                logging.info("✅ Tous les documents ont été supprimés.")
                return True
    except sqlite3.Error as e:
        logging.error(f"❌ Erreur lors de la suppression des documents : {e}")
    return False

def get_all_documents():
    """Récupère tous les documents de la base."""
    query = '''SELECT id, filename, upload_timestamp FROM document_store ORDER BY upload_timestamp DESC'''
    try:
        with get_db_connection() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logging.error(f"❌ Erreur lors de la récupération des documents : {e}")
    return []

def get_chat_history_a(session_id):
    query = "SELECT user_query, gpt_response, created_at FROM application_logs WHERE session_id = ? ORDER BY created_at ASC"
    try:
        with get_db_connection() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute(query,(session_id,))
                return [dict(row) for row in cursor.fetchall()]
            
    except sqlite3.Error as e:
        logging.error(f"❌ Erreur lors de la récupération des documents : {e}")
    return False
    
    

# Initialisation des tables au démarrage
create_tables()
