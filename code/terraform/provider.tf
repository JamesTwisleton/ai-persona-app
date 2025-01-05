terraform {
    backend "s3" {
    bucket         = "ai-persona-app-terraform-state-bucket"
    key            = "terraform/state/ai-persona-app.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
  required_providers {
    mongodbatlas = {
      source = "mongodb/mongodbatlas"
    }
  }
  required_version = ">= 0.13"
}

provider "mongodbatlas" {
  public_key  = var.mongodbatlas_public_key
  private_key = var.mongodbatlas_private_key
}

provider "aws" {
  region = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_access_key
}
