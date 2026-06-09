import pandas as pd
import sqlite3
import os

# S'assurer que le dossier data existe
os.makedirs('data', exist_ok=True)

# 1. Lire le CSV existant
df = pd.read_csv('data/metrics.csv')

# 2. Créer une connexion à une base de données SQLite locale
conn = sqlite3.connect('data/finance.db')

# 3. Injecter les données dans une table nommée 'financial_metrics'
df.to_sql('financial_metrics', conn, if_exists='replace', index=False)
conn.close()

print("✅ Base de données SQL 'finance.db' créée avec succès dans le dossier data/ !")