# Agentic AI Financier Multimodal (GCP)

Une architecture d'agent IA de niveau entreprise, capable d'analyser des téraoctets de données financières et des rapports complexes en temps réel, entièrement déployée sur Google Cloud Platform.

## 🚀 Fonctionnalités Clés
- **Routage Intelligent (Multi-Agent) :** Un superviseur IA délègue dynamiquement les requêtes entre un agent SQL, un agent documentaire (RAG) et un agent de conversation.
- **Big Data Engineering :** Interrogation en temps réel de bases massives (ex: transactions Bitcoin) via **BigQuery** et **Google Standard SQL**.
- **RAG Financier Avancé :** Lecture et analyse de rapports financiers (10-K) avec gestion de quotas (Batching) et citations par page.
- **Mémoire Persistante :** Utilisation de **LangGraph Checkpointer** pour maintenir le contexte des conversations.
- **Expérience Utilisateur (UI/UX) :** Interface **Streamlit** avec streaming en temps réel pour afficher les étapes de raisonnement du graphe.

## 🏗️ Architecture Technique
- **LLM :** Gemini 3.5 Flash (via Vertex AI)
- **Framework :** LangChain & LangGraph
- **Data Warehouse :** BigQuery (Google Cloud)
- **Vector Search :** ChromaDB (RAG)
- **Frontend :** Streamlit (asynchrone)
- **Infrastructure :** Conteneurisation Docker, déployé sur Google Cloud Run.

## 📁 Structure du Projet
- **`/agent/`** : "Cerveau" de l'application (LangGraph). Contient la logique de routage (`main.py`) et la configuration des outils d'IA (`rag_tool.py`, `tools.py`).
- **`/app/`** : Interface utilisateur web asynchrone (`app.py` via Streamlit).
- **`/data/`** : Stockage local des données sources (rapports PDF, fichiers TXT/CSV) et de la base vectorielle ChromaDB.
- **`/infra/`** : Infrastructure as Code (Terraform) pour le déploiement automatisé des ressources sur Google Cloud (`main.tf`).
- **`Dockerfile`** : Recette de conteneurisation de l'application pour Cloud Run.
- **`requirements.txt`** : Liste exhaustive des dépendances Python.
- **`setup_bq.py` & `setup_db.py`** : Scripts d'ingénierie des données pour initialiser les bases de données SQL et BigQuery.

## 💡 Pourquoi ce projet ?
Ce PoC démontre la capacité à transformer des données brutes (non structurées et massives) en insights financiers actionnables grâce à une architecture d'agents autonomes, tout en respectant les contraintes de performance et de sécurité Cloud.