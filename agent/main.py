import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from agent.tools import agent_tools
from langchain_google_vertexai import ChatVertexAI


# 1. Configuration du modèle (On utilise la version Flash dispo sur ton interface)
llm = ChatVertexAI(
    model="gemini-3.5-flash",
    project="agentic-finance-poc",
    location="global", 
    temperature=0
)

# 2. Création de l'Agent Autonome
agent_executor = create_react_agent(llm, agent_tools)

# 3. Le "Prompt Système" (Les règles du jeu)
system_prompt = """
Tu es un Analyste Financier Expert travaillant pour un Big 4.
Ton but est de répondre aux questions des utilisateurs en utilisant les outils à ta disposition.

Règles strictes :
1. Si on te pose une question sur des chiffres ou des bilans, utilise l'outil `get_financial_metrics` pour générer et exécuter une requête SQL.
2. Si on te pose une question sur la stratégie, le contexte ou ce que dit la direction, utilise l'outil `read_annual_report`.
3. Si la question nécessite de croiser des chiffres et du contexte, utilise les deux outils successivement avant de répondre.
4. Réponds toujours en français de manière professionnelle, claire et concise.
"""

# 4. Fonction principale
def run_agent(user_query: str) -> str:
    """Envoie la question à l'Agent et récupère la réponse finale."""
    print(f"\n[Agent] Réflexion en cours pour : '{user_query}'...")
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]
    
    response = agent_executor.invoke({"messages": messages})
    
    return response["messages"][-1].content

if __name__ == "__main__":
    print("--- Test de l'Agentic AI Financier ---")
    
    question_1 = "Quel est le chiffre d'affaires de TechCorp en 2023 et compare le avec 2022 ?"
    print(f"\nQuestion 1: {question_1}")
    print(f"Réponse :\n{run_agent(question_1)}")
    
    print("-" * 50)
    
    question_2 = "Selon le rapport annuel, pourquoi TechCorp a eu des difficultés au 3ème trimestre ?"
    print(f"\nQuestion 2: {question_2}")
    print(f"Réponse :\n{run_agent(question_2)}")