import operator
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

# ==========================================
# 1. DÉFINITION DE L'ÉTAT DU GRAPHE (STATE)
# ==========================================
# C'est la "mémoire" partagée entre tous nos agents.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_agent: str # Indique qui doit prendre la main

# ==========================================
# 2. CONFIGURATION DU MODÈLE (VERTEX AI)
# ==========================================
llm = ChatVertexAI(
    model="gemini-3.5-flash",
    project="agentic-finance-poc",
    location="global", 
    temperature=0
)

# ==========================================
# 3. CRÉATION DES AGENTS SPÉCIALISTES (WORKERS)
# ==========================================
# Pour l'instant, on simule (mock) leur comportement. 
# Dans les prochaines étapes, ils auront de vrais outils SQL et RAG.

def sql_agent_node(state: AgentState):
    """Spécialiste des données quantitatives et bases de données."""
    last_message = state["messages"][-1].content
    # Ici, l'agent utiliserait ses outils SQL (Étape 3)
    response = f"[Agent SQL] J'ai analysé les chiffres pour : '{last_message}'. Le CA 2023 est de 165 milliards."
    return {"messages": [AIMessage(content=response)]}

def rag_agent_node(state: AgentState):
    """Spécialiste de la recherche dans les rapports textuels."""
    last_message = state["messages"][-1].content
    # Ici, l'agent utiliserait son outil Vector/PDF (Étape 2)
    response = f"[Agent RAG] J'ai lu les rapports annuels concernant : '{last_message}'. Les difficultés viennent du marché européen."
    return {"messages": [AIMessage(content=response)]}

# ==========================================
# 4. CRÉATION DU SUPERVISEUR (ROUTING)
# ==========================================
# On force le LLM à répondre avec une structure stricte grâce à Pydantic
class RouteResponse(BaseModel):
    next_agent: Literal["SQL_AGENT", "RAG_AGENT", "FINISH"] = Field(
        description="Choisissez l'agent en fonction de la question. 'SQL_AGENT' pour les chiffres/données, 'RAG_AGENT' pour les textes/causes/rapports, 'FINISH' si la réponse a été donnée ou si c'est une salutation."
    )

supervisor_llm = llm.with_structured_output(RouteResponse)

def supervisor_node(state: AgentState):
    """Analyse la conversation et délègue au bon spécialiste."""
    # Le superviseur lit la question et décide grâce au structured output
    decision = supervisor_llm.invoke(state["messages"])
    return {"next_agent": decision.next_agent}

# ==========================================
# 5. ASSEMBLAGE DU DAG (Directed Acyclic Graph)
# ==========================================
workflow = StateGraph(AgentState)

# Ajout des nœuds
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("SQL_AGENT", sql_agent_node)
workflow.add_node("RAG_AGENT", rag_agent_node)

# Définition des chemins (Edges)
workflow.add_edge(START, "Supervisor")

# Logique conditionnelle de routage
workflow.add_conditional_edges(
    "Supervisor",
    lambda state: state["next_agent"], # La fonction lit la décision du superviseur
    {
        "SQL_AGENT": "SQL_AGENT",
        "RAG_AGENT": "RAG_AGENT",
        "FINISH": END
    }
)

# Après qu'un spécialiste ait répondu, on retourne au Superviseur (ou FINISH directement)
workflow.add_edge("SQL_AGENT", END) 
workflow.add_edge("RAG_AGENT", END)

# Compilation du graphe
agentic_app = workflow.compile()

# ==========================================
# 6. FONCTION PRINCIPALE POUR STREAMLIT
# ==========================================
def run_agent(question: str):
    """Exécute le graphe avec la question de l'utilisateur."""
    inputs = {"messages": [HumanMessage(content=question)]}
    
    # On récupère l'état final
    final_state = agentic_app.invoke(inputs)
    
    # On retourne le contenu du tout dernier message
    return final_state["messages"][-1].content