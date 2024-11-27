variable "mongodbatlas_public_key" {
  description = "MongoDB Atlas Public Key"
  type        = string
}

variable "mongodbatlas_private_key" {
  description = "MongoDB Atlas Private Key"
  type        = string
}

variable "aws_region" {
  description = "AWS Region"
  type        = string
}

variable "aws_access_key" {
  description = "AWS Access Key"
  type        = string
}

variable "aws_secret_access_key" {
  description = "AWS Secret Key"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
}

variable "replicate_api_token" {
  description = "Replicate API Token"
  type        = string
}

variable "mongodb_uri" {
  description = "MongoDB URI"
  type        = string
}

variable "mongodb_db" {
  description = "MongoDB DB"
  type        = string
}

variable "bluesky_username" {
  description = "BlueSky username"
  type        = string
}

variable "bluesky_password" {
  description = "BlueSky password"
  type        = string
}

variable "bluesky_profile_base_url" {
  description = "BlueSky profile base url"
  type        = string
}