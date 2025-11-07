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

variable "tags" {
  type    = map(string)
  default = {}
}
