variable "unique_suffix" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "subscription_id" {
  type = string
}

variable "log_analytics_workspace_id" {
  type = string
}

variable "application_insights_id" {
  type    = string
  default = null
}

variable "application_insights_connection_string" {
  type      = string
  default   = null
  sensitive = true
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "enable_diagnostics" {
  type    = bool
  default = true
}
