import operator
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from agent.rag_tool import setup_rag_retriever
from langchain_community.utilities import SQLDatabase
from langgraph.checkpoint.memory import MemorySaver

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

def sql_agent_node(state: AgentState):
    """Spécialiste Big Data avec AUTO-CORRECTION (Self-Reflection)."""
    last_message = state["messages"][-1].content
    
    db = SQLDatabase.from_uri("bigquery://agentic-finance-poc/crypto_massive_data")
    schema = db.get_table_info()
    
    # --- DÉBUT DE LA LOGIQUE D'AUTO-CORRECTION ---
    max_retries = 3
    historique_erreurs = "" # Mémoire des erreurs pour que le LLM apprenne de ses échecs
    
    for tentative in range(max_retries):
        print(f"\n🔄 [Agent SQL] Tentative {tentative + 1} / {max_retries}...")
        try:
            prompt_sql = f"""
            Tu es un Lead Data Engineer certifié Google Cloud.
            Voici le schéma de notre Data Warehouse BigQuery :
            {schema}
            
            Génère une requête en 'Google Standard SQL' pour répondre à : "{last_message}"
            
            {historique_erreurs}
            
            RÈGLES IMPORTANTES :
            - UTILISE EXACTEMENT les noms de tables du schéma (ex: `bigquery-public-data.crypto_bitcoin.transactions`).
            - Renvoie UNIQUEMENT le code SQL pur (pas de balises markdown).
            - Utilise 'UTC' pour les dates.
            """
            
            reponse_brute = llm.invoke(prompt_sql).content
            texte_sql = reponse_brute[0].get('text', str(reponse_brute)) if isinstance(reponse_brute, list) else str(reponse_brute)
            requete_sql = texte_sql.replace("```sql", "").replace("```", "").strip()
            
            print(f"[DEBUG] Requête BQ testée :\n{requete_sql}")
            
            # 4. Exécution (C'est ici que ça peut planter !)
            resultat_brut = db.run(requete_sql)
            
            # SI ON ARRIVE ICI : C'EST UN SUCCÈS ! ON SORT DE LA BOUCLE.
            print("✅ [Agent SQL] Requête exécutée avec succès !")
            
            prompt_final = f"""
            Question : {last_message}
            SQL exécuté : {requete_sql}
            Résultat : {resultat_brut}
            Formule une réponse claire pour un analyste financier.
            """
            
            reponse_finale_brute = llm.invoke(prompt_final).content
            texte_final = reponse_finale_brute[0].get('text', str(reponse_finale_brute)) if isinstance(reponse_finale_brute, list) else str(reponse_finale_brute)
            
            return {"messages": [AIMessage(content=texte_final)]}
            
        except Exception as e:
            # SI ÇA PLANTE : ON ATTRAPE L'ERREUR ET ON LA DONNE AU LLM
            erreur_actuelle = str(e)
            print(f"⚠️ [Agent SQL] Échec de la tentative {tentative + 1} : {erreur_actuelle}")
            
            # On met à jour l'historique pour la prochaine boucle
            historique_erreurs += f"\nATTENTION ! Ta requête précédente ({requete_sql}) a échoué avec l'erreur : {erreur_actuelle}. Analyse cette erreur et corrige ta syntaxe SQL pour la prochaine tentative.\n"

    # SI ON SORT DE LA BOUCLE SANS SUCCÈS (après 3 tentatives)
    return {"messages": [AIMessage(content="[Agent SQL] J'ai tenté de générer la requête 3 fois, mais la base de données renvoie toujours une erreur. La question est peut-être trop complexe ou les données n'existent pas.")]}

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

def agent_conversationnel_node(state: AgentState):
    """Gère la discussion générale et utilise la mémoire de LangGraph."""
    
    # La magie est ici : on donne TOUT l'historique de la conversation au LLM
    # pour qu'il puisse lire les anciens messages et se souvenir de toi.
    messages_historique = state["messages"]
    
    # Le LLM lit l'historique et génère une réponse
    reponse = llm.invoke(messages_historique)
    
    return {"messages": [AIMessage(content=reponse.content)]}

# ==========================================
# 4. CRÉATION DU SUPERVISEUR (ROUTING)
# ==========================================
# On force le LLM à répondre avec une structure stricte grâce à Pydantic
class RouteResponse(BaseModel):
    next_agent: Literal["SQL_AGENT", "RAG_AGENT", "Agent_Conversationnel", "FINISH"] = Field(
        description="Choisissez l'agent en fonction de la question. 'SQL_AGENT' pour les chiffres/données, 'RAG_AGENT' pour les textes/causes/rapports, 'Agent_Conversationnel' pour les salutations ou se souvenir du prénom/métier, 'FINISH' si la réponse a été donnée."
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
workflow.add_node("Agent_Conversationnel", agent_conversationnel_node)



# Définition des chemins (Edges)
workflow.add_edge(START, "Supervisor")

# Logique conditionnelle de routage
workflow.add_conditional_edges(
    "Supervisor",
    lambda state: state["next_agent"], # La fonction lit la décision du superviseur
    {
        "SQL_AGENT": "SQL_AGENT",
        "RAG_AGENT": "RAG_AGENT",
        "Agent_Conversationnel": "Agent_Conversationnel",
        "FINISH": END
    }
)

# Après qu'un spécialiste ait répondu, on retourne au Superviseur (ou FINISH directement)
workflow.add_edge("SQL_AGENT", END) 
workflow.add_edge("RAG_AGENT", END)
workflow.add_edge("Agent_Conversationnel", END)

# --- INITIALISATION DE LA MÉMOIRE ---
memory = MemorySaver()

# Compilation du graphe AVEC le système de sauvegarde (checkpointer)
agentic_app = workflow.compile(checkpointer=memory)

# ==========================================
# 6. FONCTION PRINCIPALE POUR STREAMLIT
# ==========================================
def run_agent_stream(user_message: str):
    """Point d'entrée pour Streamlit. Lance le graphe avec la question de l'utilisateur."""
    
    # 1. On configure l'identifiant de la conversation
    config = {"configurable": {"thread_id": "session_utilisateur_1"}}
    
    # 2. On prépare le message
    inputs = {"messages": [HumanMessage(content=user_message)]}
    
    # Au lieu d'attendre la fin avec .invoke(), on lit le flux en direct avec .stream()
    for output in agentic_app.stream(inputs, config=config):
        # output est un dictionnaire qui ressemble à {"Nom_Du_Noeud": {"messages": [...]}}
        for node_name, state_data in output.items():
            yield node_name, state_data