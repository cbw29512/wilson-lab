terraform {
  required_version = ">= 1.8.0"

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 8.19.0, < 9.0.0"
    }
  }
}

provider "oci" {
  auth = var.oci_auth
  config_file_profile = contains(["APIKey", "SecurityToken"], var.oci_auth) ? var.oci_profile : null
  region = var.region
}
