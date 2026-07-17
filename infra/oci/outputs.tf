output "instance_id" {
  description = "OCID of the Wilson Lab compute instance."
  value       = oci_core_instance.wilson_lab.id
}

output "public_ip" {
  description = "Public IPv4 address for the DNS A record."
  value       = oci_core_instance.wilson_lab.public_ip
}

output "api_url" {
  description = "Expected Wilson Lab API URL after DNS propagation and Caddy certificate issuance."
  value       = "https://${var.api_domain}"
}

output "ssh_command" {
  description = "SSH command for the Ubuntu instance."
  value       = "ssh ubuntu@${oci_core_instance.wilson_lab.public_ip}"
}

output "dns_instruction" {
  description = "DNS record that must be created outside this Terraform module."
  value       = "Create an A record for ${var.api_domain} pointing to ${oci_core_instance.wilson_lab.public_ip}."
}

output "selected_ubuntu_image" {
  description = "Dynamically selected OCI Ubuntu platform image."
  value       = data.oci_core_images.ubuntu.images[0].display_name
}
