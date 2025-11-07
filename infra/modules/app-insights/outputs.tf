output "connection_string" {
  description = "App Insights connection string (null if not created)"
  value       = var.create ? azurerm_application_insights.main[0].connection_string : null
}
