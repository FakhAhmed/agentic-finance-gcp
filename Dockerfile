# 1. Utiliser une image Python officielle et légère
FROM python:3.11-slim

# 2. Définir le dossier de travail à l'intérieur du conteneur
WORKDIR /app

# 3. Copier la liste des dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copier tout le reste de ton projet (code, data, app)
COPY . .

# 5. Indiquer que l'application va utiliser le port 8501 (Streamlit)
EXPOSE 8501

# 6. La commande qui sera exécutée au démarrage du conteneur
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]