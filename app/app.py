import sys
import os

# On dit à Python de remonter au dossier parent (la racine du projet) pour trouver le module 'agent'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from agent.main import run_agent

# Configuration de la page
st.set_page_config(
    page_title="Agentic AI Financier", 
    page_icon="📊", 
    layout="centered"
)

# Design de l'en-tête
st.title("📊 Agentic AI Financier")
st.caption("Interrogez l'agent sur les performances financières, les bases de données SQL et les rapports de TechCorp.")
st.markdown("---")

# Initialisation de l'historique de discussion (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour Ahmed ! Je suis votre analyste financier IA. Quelle est votre question aujourd'hui ?"}
    ]

# Affichage des messages de la session
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie de l'utilisateur
if prompt := st.chat_input("Ex: Quel est le chiffre d'affaires de TechCorp en 2023 ?"):
    
    # 1. Afficher le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Générer la réponse de l'Agent
    with st.chat_message("assistant"):
        with st.spinner("🤖 L'agent analyse votre demande et interroge les données..."):
            try:
                # Appel de ton script existant
                raw_response = run_agent(prompt)
                
                # Nettoyage de la réponse brute text/json vue dans le terminal
                if isinstance(raw_response, list) and len(raw_response) > 0:
                    clean_text = raw_response[0].get('text', str(raw_response))
                else:
                    clean_text = str(raw_response)
                
                # Affichage du résultat propre
                st.markdown(clean_text)
                
                # Sauvegarde dans l'historique
                st.session_state.messages.append({"role": "assistant", "content": clean_text})
                
            except Exception as e:
                st.error(f"Une erreur est survenue lors de la réflexion de l'agent : {e}")