# 1. TELL TERRAFORM WHICH PLUGINS TO DOWNLOAD
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

# 2. CONFIGURE THE AZURE PROVIDER (This block is mandatory)
provider "azurerm" {
  features {} # Required block for AzureRM 3.0+
}

# 3. CREATE A RESOURCE GROUP (The logical container)
resource "azurerm_resource_group" "lab" {
  name     = "ai-lab-rg"
  location = "East US"
}

# 4. THE VULNERABLE RESOURCE (Syntactically correct, but insecure)
resource "azurerm_storage_account" "insecure" {
  name                     = "aisecuritylab99" # Must be unique!
  resource_group_name      = azurerm_resource_group.lab.name
  location                 = azurerm_resource_group.lab.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  # SECURITY FLAW: Allowing public access
  public_network_access_enabled = true 
}

# VULNERABILITY 2: Public Key Vault
# This exposes sensitive secrets to the public internet
resource "azurerm_key_vault" "insecure_kv" {
  name                        = "aisecuritylab99kv"
  location                    = azurerm_resource_group.lab.location
  resource_group_name         = azurerm_resource_group.lab.name
  enabled_for_disk_encryption = true
  tenant_id                   = "3c54bdde-9890-4f71-820c-b31ae8240cd6" # Matches your subscription
  sku_name                    = "standard"

  # SECURITY FLAW: Allows access from all networks
  network_acls {
    bypass         = "AzureServices"
    default_action = "Allow"
  }
}