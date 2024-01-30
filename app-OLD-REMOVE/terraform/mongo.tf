resource "mongodbatlas_project" "ai_persona_app_mongodb_project" {
  name = "ai-persona-app"
  org_id = "606851337d8ecd0f699fc681"
}

resource "mongodbatlas_cluster" "ai_persona_app_mongodb_cluster" {
  name = "Cluster0"
  project_id = mongodbatlas_project.ai_persona_app_mongodb_project.id
  provider_name = "TENANT"
  provider_instance_size_name = "M0"
  provider_region_name     = "EU_WEST_1"
}