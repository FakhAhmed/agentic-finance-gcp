# Agentic AI Financier Multimodal sur GCP

Ce projet est une preuve de concept (PoC) d'un Agent IA financier capable d'analyser à la fois des données structurées (SQL) et non structurées (PDF). Il est déployé de manière automatisée sur Google Cloud Platform.

## 🎯 Objectifs
- Interroger des bases de données financières via des requêtes SQL générées par le LLM.
- Analyser sémantiquement des rapports annuels (Architecture RAG).
- Fournir une interface conversationnelle via Cloud Run.

## 🛠️ Stack Technique
- **Cloud Provider :** Google Cloud Platform (GCP)
- **IaC & CI/CD :** Terraform, Cloud Build
- **Data & Base de données :** BigQuery, AlloyDB (pgvector), Cloud Storage
- **Intelligence Artificielle :** Vertex AI (Gemini), LangChain
- **Application :** Python, Streamlit, Cloud Run

## 🏗️ Architecture
*(Schéma à venir)*
