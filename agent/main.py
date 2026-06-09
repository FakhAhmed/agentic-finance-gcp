import operator
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from agent.rag_tool import setup_rag_retriever
from langchain_community.utilities import SQLDatabase

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
    """Spécialiste Big Data : connecté aux Téraoctets de BigQuery."""
    last_message = state["messages"][-1].content
    
    # 1. Connexion au Dataset Cloud
    db = SQLDatabase.from_uri("bigquery://agentic-finance-poc/crypto_massive_data")
    
    # 2. Récupération du schéma (Les colonnes des blocs et transactions Bitcoin)
    schema = db.get_table_info()
    
    try:
        # 3. Le Prompt adapté pour le Big Data
        prompt_sql = f"""
        Tu es un Lead Data Engineer certifié Google Cloud.
        Voici le schéma de notre Data Warehouse BigQuery contenant les transactions Bitcoin de 2023 :
        {schema}
        
        Génère une requête en 'Google Standard SQL' pour répondre à cette question : "{last_message}"
        RÈGLES :
        - Renvoie UNIQUEMENT le code SQL pur (pas de balises markdown ```sql).
        - Utilise des LIMIT si la requête risque de renvoyer trop de lignes.
        """
        
        reponse_brute = llm.invoke(prompt_sql).content
        if isinstance(reponse_brute, list) and len(reponse_brute) > 0:
            texte_sql = reponse_brute[0].get('text', str(reponse_brute))
        else:
            texte_sql = str(reponse_brute)
            
        requete_sql = texte_sql.replace("```sql", "").replace("```", "").strip()
        print(f"\n[DEBUG] Requête BQ générée : \n{requete_sql}\n")
        
        # 4. Exécution sur l'infrastructure Google
        resultat_brut = db.run(requete_sql)
        
        # 5. Interprétation
        prompt_final = f"""
        Question : {last_message}
        SQL exécuté : {requete_sql}
        Résultat BigQuery : {resultat_brut}
        
        Formule une réponse claire et professionnelle pour un analyste financier.
        """
        reponse_finale_brute = llm.invoke(prompt_final).content
        
        if isinstance(reponse_finale_brute, list) and len(reponse_finale_brute) > 0:
            texte_final = reponse_finale_brute[0].get('text', str(reponse_finale_brute))
        else:
            texte_final = str(reponse_finale_brute)
        
        return {"messages": [AIMessage(content=texte_final)]}
        
    except Exception as e:
        erreur_msg = f"[Agent SQL BigQuery] Erreur lors de l'analyse : {str(e)}"
        return {"messages": [AIMessage(content=erreur_msg)]}

def rag_agent_node(state: AgentState):
    """Spécialiste de l'analyse documentaire avancée avec citations."""
    last_message = state["messages"][-1].content
    
    try:
        retriever = setup_rag_retriever()
        docs_trouves = retriever.invoke(last_message)
        
        # On formate le contexte en incluant EXPLICITEMENT le numéro de la page source
        contexte_formate = "\n\n".join(
            [f"[Page {doc.metadata.get('page', 'Inconnue')}] : {doc.page_content}" for doc in docs_trouves]
        )
        
        prompt_rag = f"""
        Tu es un Auditeur Financier Senior. Réponds à la question de l'utilisateur de manière détaillée et analytique.
        
        RÈGLE ABSOLUE : Tu dois t'appuyer UNIQUEMENT sur les extraits ci-dessous.
        RÈGLE DE CITATION : À chaque fois que tu affirmes un chiffre ou un fait, tu DOIS indiquer la source sous ce format exact : [Source : Page X].
        
        Extraits du rapport financier :
        {contexte_formate}
        
        Question : {last_message}
        """
        
        reponse = llm.invoke(prompt_rag)
        return {"messages": [AIMessage(content=reponse.content)]}
        
    except Exception as e:
        return {"messages": [AIMessage(content=f"[Agent RAG] Erreur de lecture documentaire : {str(e)}")]}

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