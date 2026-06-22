import sys
import os
import streamlit as st

# On dit à Python de remonter au dossier parent (la racine du projet) pour trouver le module 'agent'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from agent.main import run_agent_stream

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
if prompt := st.chat_input("Posez votre question financière..."):
    # 1. Afficher la question de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Préparer la réponse de l'Assistant
    with st.chat_message("assistant"):
        # Création d'une boîte de statut visuelle "en direct"
        status_container = st.status("🧠 L'IA analyse votre demande...", expanded=True)
        
        reponse_finale = ""
        
        # 3. On lit le flux en temps réel provenant de LangGraph
        for node_name, node_state in run_agent_stream(prompt):
            
            # Affichage dynamique selon l'agent qui travaille
            if node_name == "Guardrail":
                status_container.write("🛡️ Le Pare-feu IA analyse la sécurité de votre requête...")
            elif node_name == "Supervisor":
                status_container.write("🕵️‍♂️ Le Superviseur réfléchit et cherche le bon expert...")
            elif node_name == "SQL_AGENT":
                status_container.write("📊 L'Agent SQL interroge les Téraoctets de BigQuery...")
            elif node_name == "RAG_AGENT":
                status_container.write("📄 L'Agent RAG fouille dans le rapport financier PDF...")
            elif node_name == "MARKET_AGENT":
                status_container.write("📈 L'Agent Marchés analyse les cours en temps réel sur Yahoo Finance...")
            elif node_name == "Agent_Conversationnel":
                status_container.write("💬 L'Agent Conversationnel formule sa réponse...")
            
            # Sauvegarde du dernier message généré pour l'afficher à la fin
            if "messages" in node_state and len(node_state["messages"]) > 0:
                contenu_brut = node_state["messages"][-1].content
                
                # NETTOYAGE : Si Vertex AI renvoie une liste complexe (avec thought_signature)
                if isinstance(contenu_brut, list):
                    # On fouille dans la liste et on ne garde que le texte
                    reponse_finale = "".join([part.get("text", "") for part in contenu_brut if isinstance(part, dict) and "text" in part])
                else:
                    # Si c'est déjà du texte propre
                    reponse_finale = str(contenu_brut)
        
        # 4. Quand c'est fini, on ferme joliment la boîte de statut
        status_container.update(label="✅ Réponse générée avec succès !", state="complete", expanded=True)   
             
        # 5. On affiche la vraie réponse de l'IA
        st.markdown(reponse_finale)
        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})