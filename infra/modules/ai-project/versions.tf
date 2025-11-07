terraform {
  required_providers {
    azapi = {
      source  = "azure/azapi"
      version = "~> 2.5"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.37"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.13"
    }
  }
}
