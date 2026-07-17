variable "oci_auth" {
  description = "OCI provider authentication: APIKey locally or ResourcePrincipal in OCI Resource Manager."
  type        = string
  default     = "APIKey"

  validation {
    condition     = contains(["APIKey", "ResourcePrincipal", "SecurityToken"], var.oci_auth)
    error_message = "oci_auth must be APIKey, ResourcePrincipal, or SecurityToken."
  }
}

variable "oci_profile" {
  description = "Profile name from ~/.oci/config for APIKey or SecurityToken authentication."
  type        = string
  default     = "DEFAULT"
}

variable "region" {
  description = "OCI home region, for example us-ashburn-1. Always Free compute must be created in the home region."
  type        = string
}

variable "compartment_ocid" {
  description = "OCID of the compartment that will own the Wilson Lab resources."
  type        = string
}

variable "ssh_public_key" {
  description = "Public SSH key text. Recommended for OCI Resource Manager."
  type        = string
  default     = ""
}

variable "ssh_public_key_path" {
  description = "Local path to a public SSH key. Recommended for local Terraform."
  type        = string
  default     = ""
}

variable "ssh_allowed_cidr" {
  description = "Single administrative public IPv4 address in /32 CIDR form."
  type        = string

  validation {
    condition     = can(cidrhost(var.ssh_allowed_cidr, 0)) && can(regex("/32$", var.ssh_allowed_cidr))
    error_message = "ssh_allowed_cidr must be a single IPv4 address ending in /32."
  }
}

variable "api_domain" {
  description = "Public DNS name that will resolve to the instance, such as api.example.com."
  type        = string

  validation {
    condition     = can(regex("^[A-Za-z0-9][A-Za-z0-9.-]+[A-Za-z0-9]$", var.api_domain))
    error_message = "api_domain must be a DNS hostname."
  }
}

variable "availability_domain_index" {
  description = "Zero-based availability-domain index. Change this when Always Free capacity is unavailable."
  type        = number
  default     = 0

  validation {
    condition     = var.availability_domain_index >= 0 && floor(var.availability_domain_index) == var.availability_domain_index
    error_message = "availability_domain_index must be a non-negative whole number."
  }
}

variable "instance_shape" {
  description = "Always Free-compatible ARM shape."
  type        = string
  default     = "VM.Standard.A1.Flex"
}

variable "instance_ocpus" {
  description = "OCPUs assigned to the ARM instance."
  type        = number
  default     = 1

  validation {
    condition     = var.instance_ocpus >= 1 && var.instance_ocpus <= 2
    error_message = "Use between 1 and 2 OCPUs to remain inside the documented Always Free allowance."
  }
}

variable "instance_memory_gbs" {
  description = "Memory assigned to the ARM instance."
  type        = number
  default     = 6

  validation {
    condition     = var.instance_memory_gbs >= 4 && var.instance_memory_gbs <= 12
    error_message = "Use between 4 and 12 GB of memory for this deployment."
  }
}

variable "ubuntu_version" {
  description = "Canonical Ubuntu platform image version."
  type        = string
  default     = "24.04"
}

variable "boot_volume_size_gbs" {
  description = "Boot-volume size. OCI platform images currently require at least 50 GB."
  type        = number
  default     = 50

  validation {
    condition     = var.boot_volume_size_gbs >= 50 && var.boot_volume_size_gbs <= 100
    error_message = "Use a boot volume between 50 and 100 GB for the showcase."
  }
}

variable "display_name" {
  description = "Prefix used for OCI resource display names."
  type        = string
  default     = "wilson-lab"
}

variable "vcn_cidr" {
  description = "CIDR for the dedicated VCN."
  type        = string
  default     = "10.42.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR for the public Wilson Lab subnet."
  type        = string
  default     = "10.42.10.0/24"
}

variable "repository_url" {
  description = "Public Git repository cloned by cloud-init."
  type        = string
  default     = "https://github.com/cbw29512/wilson-lab.git"
}

variable "repository_branch" {
  description = "Repository branch deployed by cloud-init."
  type        = string
  default     = "main"
}
