import streamlit as st
import datetime
import os
import sys
import importlib.util
import uuid
import re

# Ajouter les chemins vers les modules
sys.path.append("../data battle/app")
from api_utils import get_api_response

# 🔍 Parse le texte brut en objets questions
def parse_questions_from_text(text):
    questions = []
    blocks = re.split(r'Question\s+\d+', text)[1:]

    for block in blocks:
        lines = block.strip().split("\n")
        if not lines:
            continue

        question_text = lines[0].strip()
        all_text = ' '.join(lines[1:])
        choices = re.findall(r"[A-D]\)\s*([^A-D]+)", all_text)

        if choices:
            questions.append({
                "text": question_text,
                "type": "QCM",
                "choices": [c.strip() for c in choices]
            })
        else:
            questions.append({
                "text": question_text,
                "type": "Questions ouvertes"
            })
    return questions

# ➕ Génère un ID de session unique
def get_session_id():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

# 🔁 Interroge l’API pour générer les questions
def send_questionnaire_request(user_data):
    session_id = get_session_id()

    prompt = (
        f"Génère un questionnaire sur les thèmes suivants :\n"
        f"- Catégories : {', '.join(user_data['categories'])}\n"
        f"- Sous-catégories : {', '.join(user_data['subcategories'])}\n"
        f"- Types de questions : {', '.join(user_data['question_types'])}\n"
        f"Nombre de questions : {user_data['num_questions']}\n"
        """-Start with all the QUESTIONS only.
- Then, in a separate section, write the corresponding ANSWERS.
- Finally, provide EXPLANATIONS for each answer if relevant.
- Do not mix answers with the questions.
"""
    )

    rag_response = get_api_response(prompt, session_id=session_id, model="mistral-large-latest")

    if rag_response and isinstance(rag_response, dict):
        chatbot_message = rag_response.get("answer", "⚠ Aucune réponse reçue.")
        parsed_questions = parse_questions_from_text(chatbot_message)
    else:
        chatbot_message = "❌ Erreur : l'API n'a pas répondu correctement."
        parsed_questions = []

    return {
        "chatbot_response": chatbot_message,
        "questions": parsed_questions
    }

# 🔁 Affiche les questions dans un formulaire interactif
def display_questions(questions):
    st.subheader("📝 Répondez aux questions générées")
    user_answers = {}

    for i, question in enumerate(questions, start=1):
        st.markdown(f"Question {i}: {question['text']}")
        if question["type"] == "Vrai_ou_faux":
            user_answers[f"question_{i}"] = st.radio(
                f"Votre réponse pour la question {i} :", ["Vrai", "Faux"], key=f"q{i}_radio"
            )
        elif question["type"] == "QCM":
            user_answers[f"question_{i}"] = st.multiselect(
                f"Votre réponse pour la question {i} :", question["choices"], key=f"q{i}_multiselect"
            )
        elif question["type"] in ["Réponses ouvertes", "Questions ouvertes"]:
            user_answers[f"question_{i}"] = st.text_input(
                f"Votre réponse pour la question {i} :", key=f"q{i}_textinput"
            )

    if st.button("📤 Soumettre"):
        st.success("✅ Vos réponses ont été soumises avec succès !")
        st.write("Voici vos réponses :", user_answers)

    if st.button("🔄 Repasser le test"):
        for key in ["generated_questions", "chatbot_message"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()

# 🔁 Gère la génération et l’affichage
def handle_questionnaire_generation(user_data):
    result = send_questionnaire_request(user_data)
    if "chatbot_response" in result:
        st.session_state["generated_questions"] = result["questions"]
        st.session_state["chatbot_message"] = result["chatbot_response"]
    else:
        st.error("❌ Erreur lors de la génération du questionnaire.")

# 🎯 Application principale Streamlit
def main():
    st.markdown("""
        <style>
        .main-title { font-size: 32px; color: #3F3D56; font-weight: bold; }
        .info-text { font-size: 16px; color: #6B7280; }
        .stButton>button {
            background-color: #1E3A8A; color: white;
            font-size: 16px; font-weight: 600;
            padding: 10px; border-radius: 5px;
        }
        .stButton>button:hover { background-color: #4C51BF; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1: st.image("logo1.jpeg", width=100)
    with col3: st.image("LOGO_EFREI.jpeg", width=150)

    st.markdown('<p class="main-title">📄 Générateur de Questionnaire - Propriété Intellectuelle</p>', unsafe_allow_html=True)

    nav = st.radio("Navigation", ("Créer un questionnaire", "Historique des questionnaires", "Chatbot"), horizontal=True)

    if nav == "Créer un questionnaire":
        st.markdown('<p class="info-text">Sélectionnez les catégories, sous-catégories et types de questions.</p>', unsafe_allow_html=True)

        categories = {
            "1. Filing requirements and formalities": [
                "1.1 Minimum requirements for a filing date", "1.2 Filing methods and locations", "1.3 Formality examination"
            ],
            "2. Priority claims and right of priority": [
                "2.1 Substantive requirements for priority", "2.2 Time limits and restoration", "2.3 Multiple priorities and partial priority"
            ],
            "3. Divisional applications": [
                "3.1 Filing requirements", "3.2 Subject-matter and scope", "3.3 Fees for divisionals"
            ],
            "4. Fees, payment methods, and time limits": [
                "4.1 Types and calculation of fees", "4.2 Payment mechanisms", "4.3 Fee deadlines and late payment consequences"
            ],
            "5. Languages and translations": [
                "5.1 Language of filing and procedural language", "5.2 Translation requirements", "5.3 Effects on rights"
            ],
            "6. Procedural remedies and legal effect": [
                "6.1 Further processing", "6.2 Re-establishment of rights", "6.3 Loss of rights and remedies"
            ],
            "7. PCT procedure and entry into the European phase": [
                "7.1 International filing", "7.2 Preliminary examination", "7.3 European phase entry"
            ],
            "8. Examination, amendments, and grant": [
                "8.1 Examination procedure", "8.2 Claim amendments", "8.3 Grant stage and publication"
            ],
            "9. Opposition and appeals": [
                "9.1 Grounds for opposition", "9.2 Procedure and admissibility", "9.3 Appeal proceedings"
            ],
            "10. Substantive patent law": [
                "10.1 Novelty analysis", "10.2 Inventive step", "10.3 Special claim types"
            ],
            "11. Entitlement and transfers": [
                "11.1 Entitlement disputes", "11.2 Transfers", "11.3 Consequences"
            ],
            "12. Biotech and sequence listings": [
                "12.1 Sequence listing", "12.2 Subject-matter", "12.3 Exceptions"
            ],
            "13. Unity of invention": [
                "13.1 Unity in EP applications", "13.2 Unity in PCT", "13.3 Strategies"
            ]
        }

        selected_categories = st.multiselect("📌 Choisissez les catégories :", list(categories.keys()))
        selected_subcategories = []
        for cat in selected_categories:
            selected_subcategories += st.multiselect(f"📂 Sous-catégories pour {cat} :", categories[cat])

        question_types = st.multiselect("❓ Types de questions :", ["QCM", "Vrai_ou_faux", "Questions ouvertes"])
        num_questions = st.number_input("🔢 Nombre de questions :", min_value=5, step=1, value=5)
        num_choices = st.slider("📊 Nombre de choix :", 2, 4, 2) if "QCM" in question_types else None
        
        def genere(): 
            user_data = {
                "categories": selected_categories,
                "subcategories": selected_subcategories,
                "question_types": question_types,
                "num_questions": num_questions,
                "num_choices": num_choices
            }
            handle_questionnaire_generation(user_data)

        if st.button("📌 Enregistrer et Générer"):
            genere()

        if "generated_questions" in st.session_state:
            st.success("✅ Questionnaire généré avec succès !")
            st.subheader("💬 Réponse du chatbot")
            st.write(st.session_state["chatbot_message"])
            display_questions(st.session_state["generated_questions"])

    #elif nav == "Historique des questionnaires":
      #  chat_path = os.path.normpath("../data battle/app/streamlit_app.py")
       # if os.path.exists(chat_path):
        #    spec = importlib.util.spec_from_file_location("questionnaire", chat_path)
         #   mon_questionnaire = importlib.util.module_from_spec(spec)
          #  spec.loader.exec_module(mon_questionnaire)
        #else:
        #    st.error("❌ Fichier d'historique introuvable !")

    elif nav == "Chatbot":
        chat_path = os.path.normpath("../data battle/app/streamlit_app.py")
        if os.path.exists(chat_path):
            spec = importlib.util.spec_from_file_location("chatbot", chat_path)
            chatbot_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(chatbot_module)
        else:
            st.error("❌ Fichier du chatbot introuvable !")

if __name__ == "_main_":
    main()
