data "oci_identity_availability_domains" "available" {
  compartment_id = var.compartment_ocid
}

data "oci_core_images" "ubuntu" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Canonical Ubuntu"
  operating_system_version = var.ubuntu_version
  shape                    = var.instance_shape
  state                    = "AVAILABLE"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

locals {
  availability_domain = try(
    data.oci_identity_availability_domains.available.availability_domains[var.availability_domain_index].name,
    "",
  )
  ubuntu_image_id = try(data.oci_core_images.ubuntu.images[0].id, "")
  ssh_authorized_keys = trimspace(
    var.ssh_public_key != "" ? var.ssh_public_key : try(file(pathexpand(var.ssh_public_key_path)), "")
  )
}

check "ssh_public_key_provided" {
  assert {
    condition     = local.ssh_authorized_keys != ""
    error_message = "Set ssh_public_key for Resource Manager or ssh_public_key_path for local Terraform."
  }
}

check "availability_domain_exists" {
  assert {
    condition     = local.availability_domain != ""
    error_message = "availability_domain_index is outside the availability domains returned for this region."
  }
}

check "ubuntu_image_exists" {
  assert {
    condition     = local.ubuntu_image_id != ""
    error_message = "No matching Canonical Ubuntu image was found for the selected version and shape."
  }
}

resource "oci_core_vcn" "wilson_lab" {
  compartment_id = var.compartment_ocid
  cidr_blocks     = [var.vcn_cidr]
  display_name    = "${var.display_name}-vcn"
  dns_label       = "wilsonlab"

  freeform_tags = {
    project   = "wilson-lab"
    managedBy = "terraform"
  }
}

resource "oci_core_internet_gateway" "wilson_lab" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.wilson_lab.id
  display_name   = "${var.display_name}-internet-gateway"
  enabled        = true
}

resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.wilson_lab.id
  display_name   = "${var.display_name}-public-routes"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.wilson_lab.id
  }
}

resource "oci_core_security_list" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.wilson_lab.id
  display_name   = "${var.display_name}-public-security"

  egress_security_rules {
    destination      = "0.0.0.0/0"
    destination_type = "CIDR_BLOCK"
    protocol         = "all"
    stateless        = false
  }

  ingress_security_rules {
    protocol  = "6"
    source    = var.ssh_allowed_cidr
    stateless = false

    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol  = "6"
    source    = "0.0.0.0/0"
    stateless = false

    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol  = "6"
    source    = "0.0.0.0/0"
    stateless = false

    tcp_options {
      min = 443
      max = 443
    }
  }

  ingress_security_rules {
    protocol  = "17"
    source    = "0.0.0.0/0"
    stateless = false

    udp_options {
      min = 443
      max = 443
    }
  }
}

resource "oci_core_subnet" "public" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.wilson_lab.id
  cidr_block                 = var.subnet_cidr
  display_name               = "${var.display_name}-public-subnet"
  dns_label                  = "public"
  prohibit_public_ip_on_vnic = false
  route_table_id             = oci_core_route_table.public.id
  security_list_ids          = [oci_core_security_list.public.id]
}

resource "oci_core_instance" "wilson_lab" {
  availability_domain = local.availability_domain
  compartment_id      = var.compartment_ocid
  display_name        = "${var.display_name}-vm"
  shape               = var.instance_shape

  shape_config {
    ocpus         = var.instance_ocpus
    memory_in_gbs = var.instance_memory_gbs
  }

  create_vnic_details {
    assign_public_ip = true
    display_name     = "${var.display_name}-primary-vnic"
    hostname_label   = "wilson-lab"
    subnet_id        = oci_core_subnet.public.id
  }

  source_details {
    source_type             = "image"
    source_id               = local.ubuntu_image_id
    boot_volume_size_in_gbs = var.boot_volume_size_gbs
    boot_volume_vpus_per_gb = 10
  }

  metadata = {
    ssh_authorized_keys = local.ssh_authorized_keys
    user_data = base64encode(templatefile("${path.module}/cloud-init.yaml.tftpl", {
      api_domain        = var.api_domain
      repository_url    = var.repository_url
      repository_branch = var.repository_branch
    }))
  }

  instance_options {
    are_legacy_imds_endpoints_disabled = true
  }

  freeform_tags = {
    project   = "wilson-lab"
    managedBy = "terraform"
    workload  = "showcase"
  }
}
