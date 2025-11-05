variable "unique_suffix" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "ai_foundry_id" {
  type = string
}

variable "ai_foundry_ready" {
  description = "Dependency marker to ensure AI Foundry is ready"
  type        = string
}

variable "storage_account_id" {
  type = string
}

variable "storage_account_name" {
  type = string
}

variable "storage_account_primary_blob_endpoint" {
  type = string
}

variable "cosmosdb_id" {
  type = string
}

variable "cosmosdb_name" {
  type = string
}

variable "cosmosdb_endpoint" {
  type = string
}

variable "ai_search_id" {
  type = string
}

variable "ai_search_name" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
