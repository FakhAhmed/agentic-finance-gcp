from google.cloud import bigquery

project_id = "agentic-finance-poc"
client = bigquery.Client(project=project_id)

# 1. Création du Dataset
dataset_name = "crypto_massive_data"
dataset_id = f"{project_id}.{dataset_name}"
dataset = bigquery.Dataset(dataset_id)
dataset.location = "US"

client.create_dataset(dataset, exists_ok=True)
print(f"📦 Dataset '{dataset_name}' préparé en région US !")

# 2. Définition des Vues avec les bonnes colonnes de dates pour chaque table
views_config = {
    "btc_blocks": {
        "table": "`bigquery-public-data.crypto_bitcoin.blocks`",
        "date_column": "timestamp" # <--- Ici c'est 'timestamp'
    },
    "btc_transactions": {
        "table": "`bigquery-public-data.crypto_bitcoin.transactions`",
        "date_column": "block_timestamp" # <--- Ici c'est 'block_timestamp'
    }
}

for view_name, config in views_config.items():
    view_id = f"{dataset_id}.{view_name}"
    view = bigquery.Table(view_id)
    
    # On crée la requête dynamiquement avec la bonne colonne
    col = config["date_column"]
    view.view_query = f"SELECT * FROM {config['table']} WHERE DATE({col}) >= '2023-01-01' AND DATE({col}) <= '2023-12-31'"
    
    # Création ou mise à jour de la vue
    client.create_table(view, exists_ok=True)
    print(f"🔗 Vue '{view_name}' branchée avec succès !")