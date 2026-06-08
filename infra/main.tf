terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Configuration du fournisseur GCP
provider "google" {
  project = var.project_id
  region  = var.region
}

# Définition des variables
variable "project_id" {
  description = "L'ID de ton projet GCP (pas le nom, l'ID exact)"
  type        = string
}

variable "region" {
  description = "La région GCP (europe-west1 pour la Belgique / France)"
  type        = string
  default     = "europe-west1" 
}

# 1. Activation des APIs Google Cloud nécessaires
resource "google_project_service" "apis" {
  for_each = toset([
    "aiplatform.googleapis.com",   # Vertex AI (Le cerveau)
    "run.googleapis.com",          # Cloud Run (L'interface)
    "bigquery.googleapis.com",     # BigQuery (Data structurée)
    "storage.googleapis.com",      # Cloud Storage (Data non structurée)
    "cloudbuild.googleapis.com",   # Cloud Build (CI/CD)
    "iam.googleapis.com"           # Gestion des droits
  ])
  service            = each.key
  disable_on_destroy = false
}

# 2. Création du Bucket GCS pour les PDF
resource "google_storage_bucket" "pdf_bucket" {
  name          = "${var.project_id}-finance-pdfs" # Doit être unique mondialement
  location      = var.region
  force_destroy = true # Pratique pour tout supprimer proprement à la fin du projet
  
  uniform_bucket_level_access = true
  depends_on = [google_project_service.apis]
}

# 3. Création du Dataset BigQuery
resource "google_bigquery_dataset" "finance_dataset" {
  dataset_id                  = "financial_data"
  friendly_name               = "Données Financières"
  description                 = "Dataset pour l'Agent AI contenant les bilans structurés"
  location                    = var.region
  delete_contents_on_destroy  = true # Permet la suppression facile du PoC

  depends_on = [google_project_service.apis]
}