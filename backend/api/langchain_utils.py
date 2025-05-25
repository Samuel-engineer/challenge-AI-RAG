from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from chroma_utils import vectorstore
from dotenv import load_dotenv
import logging

# Charger les variables d'environnement
load_dotenv()

# Optimisation du Retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # On réduit k pour accélérer la recherche

# Définition des prompts
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", 
"""
You are an expert in patent engineering. You understand the technical and legal intricacies of patents.\
Your goal is to help retrieving the most accurate, relevant, and up-to-date information given the user query.\
Only provide precise references and topics.
"""
     ),
    ("human", "{input}"),
])

role ="""
You are a helpful professor in patent engineering, knowledgeable about both the technical and legal aspects of patents.\
Your goal is to help students understand the procedures of patent law with precise, well-referenced, and educational answers.\
from the most accurate, relevant, and up-to-date information given the user query and the context.\
Response Format:\
Use Markdown for better readability.\
Include links to legal texts, rules, and case law in the format [source name](URL).\
Provide tables to summarize complex information.\
Add emojis to make explanations more engaging 😊.\
Methodology:\
Question Analysis: Clarify technical terms and context.\
Educational Explanation: Break down complex concepts into simple, step-by-step explanations.
"""

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", role),
    ("system", "Context: {context}"),
    #MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

def get_rag_chain(model="mistral-large-latest"):
    """
    Crée un pipeline RAG optimisé avec LangChain et MistralAI.
    """
    try:
        llm = ChatMistralAI(model=model, temperature=0)  

        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        logging.info(f"✅ RAG Chain créé avec le modèle {model}")
        return rag_chain

    except Exception as e:
        logging.error(f"❌ Erreur lors de la création du RAG Chain : {e}")
        return None
