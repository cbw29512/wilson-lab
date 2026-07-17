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
  auth                = var.oci_auth
  config_file_profile = var.oci_profile
  region              = var.region
}
