variable "name" { type = string }
variable "environment_id" { type = string }
variable "resource_group_name" { type = string }
variable "revision_mode" {
  type    = string
  default = "Single"
}
variable "image" {
  type        = string
  description = "Container image (defaults to placeholder if not provided)"
  default     = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
}
variable "cpu" {
  type    = number
  default = 0.5
}
variable "memory" {
  type    = string
  default = "1Gi"
}
variable "min_replicas" {
  type    = number
  default = 1
}
variable "max_replicas" {
  type    = number
  default = 10
}
variable "external_enabled" {
  type    = bool
  default = false
}
variable "target_port" { type = number }
variable "tags" {
  type    = map(string)
  default = {}
}
variable "registry_server" { type = string }
variable "registry_identity_id" { type = string }
variable "identity_ids" { type = list(string) }
variable "env_vars" {
  type    = map(string)
  default = {}
}
variable "secret_env_vars" {
  type    = map(string)
  default = {}
}

variable "health_probe_path" {
  type        = string
  description = "Path for health probes"
  default     = "/health"
}

variable "startup_probe_initial_delay" {
  type        = number
  description = "Initial delay in seconds for startup probe"
  default     = 10
}

variable "startup_probe_timeout" {
  type        = number
  description = "Timeout in seconds for startup probe"
  default     = 5
}

variable "startup_probe_period" {
  type        = number
  description = "Period in seconds for startup probe"
  default     = 10
}

variable "startup_probe_failure_threshold" {
  type        = number
  description = "Failure threshold for startup probe"
  default     = 6
}

variable "dapr_app_id" {
  type        = string
  description = "Dapr application ID (mandatory)"
}

variable "dapr_app_port" {
  type        = number
  description = "Port that the application is listening on (mandatory)"
}

variable "dapr_log_level" {
  type        = string
  description = "Dapr log level (debug, info, warn, error)"
  default     = "info"
}

variable "dapr_enable_api_logging" {
  type        = bool
  description = "Enable API logging for Dapr"
  default     = false
}
