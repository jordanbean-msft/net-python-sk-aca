########## Function Plan Module (azurerm_service_plan) ##########

resource "azurerm_service_plan" "main" {
  name                = var.name
  resource_group_name = var.resource_group_name
  location            = var.location
  os_type             = "Linux"
  sku_name            = var.sku_size
  tags                = var.tags
}
