variable "create" {
  type    = bool
  default = true
}

variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "workspace_id" {
  type = string
}

variable "application_type" {
  type    = string
  default = "web"
}

variable "tags" {
  type    = map(string)
  default = {}
}
