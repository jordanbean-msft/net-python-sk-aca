########## Log Analytics Module ##########

resource "azurerm_log_analytics_workspace" "main" {
  count               = var.create ? 1 : 0
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_in_days
  tags                = var.tags
}
