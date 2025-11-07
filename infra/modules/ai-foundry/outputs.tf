output "ai_foundry_id" {
  value = azapi_resource.ai_foundry.id
}

output "ai_foundry_name" {
  value = azapi_resource.ai_foundry.name
}

output "ai_foundry_endpoint" {
  value = "https://${azapi_resource.ai_foundry.name}.cognitiveservices.azure.com/"
}

output "ai_foundry_ready" {
  description = "Marker output to ensure AI Foundry is ready for project creation"
  value       = time_sleep.wait_ai_foundry.id
}

output "ai_model_deployment_name" {
  value = azurerm_cognitive_deployment.gpt_4o.name
}
