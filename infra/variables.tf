variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name for all resources"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "unique_suffix" {
  description = "Unique suffix for resource naming (leave empty to auto-generate)"
  type        = string
  default     = ""
}

variable "azure_ai_model_deployment" {
  description = "Azure AI model deployment name"
  type        = string
  default     = "gpt-4o"
}

variable "azure_openai_api_key" {
  description = "Azure OpenAI API key (optional, uses managed identity if not provided)"
  type        = string
  default     = null
  sensitive   = true
}

variable "backend_image" {
  description = "Backend container image"
  type        = string
  default     = null
}

variable "ai_service_image" {
  description = "AI service container image"
  type        = string
  default     = null
}

variable "enable_diagnostics" {
  description = "Enable diagnostic settings"
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
