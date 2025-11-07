variable "name" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "storage_account_name" { type = string }
variable "storage_account_access_key" { type = string }
variable "app_service_plan_id" { type = string }
variable "identity_id" { type = string }
variable "tags" {
  type    = map(string)
  default = {}
}
