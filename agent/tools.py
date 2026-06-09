from google.cloud import bigquery
from google.cloud import storage
from langchain.tools import tool

# On initialise les clients GCP (ils utiliseront tes credentials automatiquement)
bq_client = bigquery.Client(project="722746477682")
storage_client = storage.Client(project="722746477682")

# Le décorateur @tool transforme cette fonction Python en un "Outil" compréhensible par l'IA.
# La docstring (les commentaires entre """) est vitale : c'est ce que l'IA lit pour savoir QUAND utiliser cet outil.
@tool
def get_financial_metrics(query: str) -> str:
    """
    Utilise cet outil UNIQUEMENT pour obtenir des chiffres structurés sur les entreprises 
    (chiffre d'affaires, bénéfice, marge, années).
    La table s'appelle `722746477682.financial_data.metrics`.
    L'entrée (query) DOIT être une requête SQL Google Standard SQL valide.
    """
    try:
        query_job = bq_client.query(query)
        results = query_job.result()
        # On formate le résultat SQL en texte pour que le LLM puisse le lire
        return "\n".join([str(dict(row)) for row in results])
    except Exception as e:
        return f"Erreur lors de la requête SQL: {e}"

@tool
def read_annual_report(company_name: str) -> str:
    """
    Utilise cet outil pour lire le rapport annuel d'une entreprise et comprendre le contexte,
    la stratégie ou les explications de la direction.
    L'entrée doit être le nom de l'entreprise (ex: 'techcorp').
    """
    try:
        bucket = storage_client.bucket("722746477682-finance-pdfs")
        # On simplifie pour le PoC : on cherche le fichier txt
        blob = bucket.blob(f"rapport_{company_name.lower()}_2023.txt")
        return blob.download_as_text()
    except Exception as e:
        return f"Rapport introuvable pour {company_name}. Erreur: {e}"

# Liste des outils que l'on donnera à notre Agent
agent_tools = [get_financial_metrics, read_annual_report]