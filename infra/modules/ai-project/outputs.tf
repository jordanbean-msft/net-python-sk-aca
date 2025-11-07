output "ai_foundry_project_id" {
  value = azapi_resource.ai_foundry_project.id
}

output "ai_foundry_project_name" {
  value = azapi_resource.ai_foundry_project.name
}

output "ai_foundry_project_principal_id" {
  value = azapi_resource.ai_foundry_project.output.identity.principalId
}

output "ai_foundry_project_internal_id" {
  value = azapi_resource.ai_foundry_project.output.properties.internalId
}

output "ai_foundry_project_endpoint" {
  value = "https://${regex("/accounts/([^/]+)$", azapi_resource.ai_foundry_project.parent_id)[0]}.services.ai.azure.com/api/projects/${azapi_resource.ai_foundry_project.name}"
}
