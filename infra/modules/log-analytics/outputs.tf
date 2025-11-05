output "id" {
  description = "Log Analytics Workspace ID (null if not created)"
  value       = var.create ? azurerm_log_analytics_workspace.main[0].id : null
}
