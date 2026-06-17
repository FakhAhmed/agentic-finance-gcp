# Agentic AI Financier Multimodal (GCP)

Une architecture d'agent IA de niveau entreprise, capable d'analyser des téraoctets de données financières, de lire des rapports complexes et d'interroger les marchés en temps réel, le tout entièrement sécurisé, tracé et déployé sur Google Cloud Platform.

## 🚀 Fonctionnalités Clés
- **Routage Intelligent (Multi-Agent) :** Un superviseur IA délègue dynamiquement les requêtes entre 4 experts spécialisés : 
  - 📊 **Agent SQL :** Analyse Big Data avec auto-correction des requêtes.
  - 📄 **Agent RAG :** Recherche vectorielle dans des documents financiers complexes.
  - 📈 **Agent Marchés :** Connexion API en temps réel aux cours de la bourse.
  - 💬 **Agent Conversationnel :** Interactions générales et synthèses.
- **Sécurité "Enterprise-Grade" (Guardrails) :** Un pare-feu IA (Videur) analyse chaque requête entrante pour bloquer les attaques de *Prompt Injection* et les requêtes hors-sujet avant même l'exécution du graphe.
- **Connexion au Monde Réel :** Intégration de l'API Yahoo Finance (`yfinance`) pour récupérer les cours des actions à la seconde près.
- **Observabilité & MLOps :** Intégration complète de **LangSmith** pour le tracing en direct, le calcul précis des coûts par token, et la surveillance des performances (latence des agents).
- **Big Data Engineering :** Interrogation en temps réel de bases massives (ex: blockchain Bitcoin) via **BigQuery** et **Google Standard SQL**.
- **Mémoire Persistante :** Utilisation de **LangGraph Checkpointer** pour maintenir le contexte des conversations d'un bout à l'autre.
- **Expérience Utilisateur (UI/UX) :** Interface **Streamlit** fluide avec streaming asynchrone pour afficher le raisonnement de l'IA étape par étape.

## 🏗️ Architecture Technique
- **LLM :** Gemini Flash (via Google Vertex AI)
- **Orchestration :** LangChain & LangGraph (StateGraph)
- **Data Warehouse :** BigQuery (Google Cloud)
- **Vector Search & RAG :** ChromaDB
- **MLOps / Tracing :** LangSmith
- **API Externe :** Yahoo Finance API
- **Frontend :** Streamlit
- **Infrastructure :** Conteneurisation Docker, déployé en Serverless sur Google Cloud Run.

## 📁 Structure du Projet
- **`/agent/`** : "Cerveau" de l'application (LangGraph). Contient la logique de routage (`main.py`) et la configuration des outils d'IA (`rag_tool.py`, `tools.py`).
- **`/app/`** : Interface utilisateur web asynchrone (`app.py` via Streamlit).
- **`/data/`** : Stockage local des données sources (rapports PDF, fichiers TXT/CSV) et de la base vectorielle ChromaDB.
- **`/infra/`** : Infrastructure as Code (Terraform) pour le déploiement automatisé des ressources sur Google Cloud (`main.tf`).
- **`Dockerfile`** : Recette de conteneurisation de l'application pour Cloud Run.
- **`requirements.txt`** : Liste exhaustive des dépendances Python.
- **`setup_bq.py` & `setup_db.py`** : Scripts d'ingénierie des données pour initialiser les bases de données SQL et BigQuery.

## 💡 Pourquoi ce projet ?
Ce PoC démontre la capacité à transformer des données brutes (non structurées, massives et en temps réel) en insights financiers actionnables grâce à une architecture d'agents autonomes. Il intègre les meilleures pratiques de l'industrie : sécurité dès la conception (Guardrails), observabilité totale (MLOps), et scalabilité Cloud.