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
- `/agent` : Logique métier des agents (SQL, RAG, Superviseur).
- `/app` : Interface utilisateur Streamlit.
- `setup_bq.py` : Scripts de Data Engineering pour BigQuery.

## 💡 Pourquoi ce projet ?
Ce PoC démontre la capacité à transformer des données brutes (non structurées et massives) en insights financiers actionnables grâce à une architecture d'agents autonomes, tout en respectant les contraintes de performance et de sécurité Cloud.