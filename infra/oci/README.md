# Oracle Cloud Infrastructure Activation

This Terraform module provisions the Oracle Cloud resources required to activate Wilson Lab on an isolated cloud VM.

It creates:

- a dedicated VCN
- a public subnet
- an internet gateway and default route
- a security list allowing:
  - SSH from one administrator IPv4 address only
  - public TCP 80 and 443
  - public UDP 443 for HTTP/3
- one `VM.Standard.A1.Flex` Ubuntu instance
- a public IPv4 address
- cloud-init that installs Docker and starts the Wilson Lab deployment automatically

The default shape is **1 OCPU, 6 GB RAM, and a 50 GB boot volume**. Keep all OCI resources in the account's home region and confirm that the selected shape is marked Always Free Eligible before applying.

## What Terraform does not own

You must still provide:

- an activated OCI account
- the home region
- a compartment OCID
- an SSH public key
- the current administrator public IPv4 address
- a DNS name you control

Terraform outputs the VM public IP. Create the DNS `A` record after the instance is provisioned.

## Recommended path: OCI Resource Manager

Resource Manager is the easiest path because Terraform runs inside OCI and its state remains associated with the stack.

### 1. Prepare an SSH key in Windows PowerShell

```powershell
$KeyPath = "$HOME\.ssh\wilson_lab_oci"
ssh-keygen -t ed25519 -f $KeyPath -C "wilson-lab-oci"
Get-Content "$KeyPath.pub"
```

Keep the private file at `$KeyPath`. Paste only the `.pub` contents into Resource Manager.

### 2. Find your current public IPv4 address

```powershell
(Invoke-RestMethod -Uri "https://api.ipify.org").Trim()
```

Append `/32` when entering `ssh_allowed_cidr`. Example:

```text
203.0.113.10/32
```

Update this value and re-apply Terraform when your public IP changes.

### 3. Create or identify a compartment

In the OCI Console:

1. Open **Identity & Security**.
2. Open **Compartments**.
3. Create a compartment named `wilson-lab`, or select an existing compartment intended for this project.
4. Copy its OCID.

Do not place Wilson Lab in a compartment containing unrelated production resources.

### 4. Create the Resource Manager stack

Two supported approaches are available.

#### Upload the folder

1. Download and extract the Wilson Lab repository.
2. In OCI, open **Developer Services → Resource Manager → Stacks**.
3. Select **Create stack**.
4. Choose **My configuration** and **Folder**.
5. Upload the `infra/oci` folder.
6. Select a Terraform version compatible with `>= 1.8.0`.

#### Use the Git repository

1. Configure a GitHub configuration source provider in Resource Manager.
2. Create a stack from the `cbw29512/wilson-lab` repository.
3. Select branch `main`.
4. Set the working directory to `infra/oci`.

The folder-upload route requires fewer GitHub-to-Oracle integration steps.

### 5. Configure stack variables

Set these values in Resource Manager:

| Variable | Value |
|---|---|
| `oci_auth` | `ResourcePrincipal` |
| `region` | Your OCI home-region identifier |
| `compartment_ocid` | OCID copied from the selected compartment |
| `ssh_public_key` | Complete contents of `wilson_lab_oci.pub` |
| `ssh_public_key_path` | Leave blank |
| `ssh_allowed_cidr` | Your current public IPv4 address plus `/32` |
| `api_domain` | DNS name such as `api.yourdomain.com` |
| `availability_domain_index` | Start with `0` |
| `instance_ocpus` | `1` |
| `instance_memory_gbs` | `6` |
| `boot_volume_size_gbs` | `50` |

Do not place private keys, passwords, JWT secrets, or other confidential values in Resource Manager variables.

### 6. Plan before applying

Run a **Plan** job and review the proposed resources. The plan should include one VCN, one subnet, one internet gateway, one route table, one security list, and one compute instance.

Confirm:

- the region is the account's home region
- the shape is `VM.Standard.A1.Flex`
- SSH is restricted to the supplied `/32`
- ports 80 and 443 are the only globally reachable service ports
- no unrelated existing resources are modified

Then run **Apply**.

### 7. Handle capacity errors

Always Free A1 capacity may be temporarily unavailable in an availability domain.

When the apply reports insufficient capacity:

1. Change `availability_domain_index` from `0` to `1` when another domain exists.
2. Run Plan again.
3. Apply again.

Do not increase the instance shape or create paid resources merely to bypass a capacity error.

## Local Terraform alternative

Use this route only after configuring OCI API-key authentication in `~/.oci/config`.

```powershell
cd path\to\wilson-lab\infra\oci
Copy-Item terraform.tfvars.example terraform.tfvars
notepad terraform.tfvars
terraform init
terraform fmt -check
terraform validate
terraform plan -out wilson-lab.tfplan
terraform apply wilson-lab.tfplan
```

For local execution:

```hcl
oci_auth            = "APIKey"
oci_profile         = "DEFAULT"
ssh_public_key_path = "~/.ssh/wilson_lab_oci.pub"
ssh_public_key      = ""
```

Terraform state and `terraform.tfvars` are ignored by Git. Protect the state file because it contains infrastructure metadata.

## After Terraform apply

### 1. Read the outputs

Resource Manager exposes the outputs after a successful Apply. Record:

- `public_ip`
- `api_url`
- `ssh_command`
- `dns_instruction`
- `selected_ubuntu_image`

### 2. Create the DNS record

At the DNS provider for your domain, create:

```text
Type: A
Name: the subdomain portion of api_domain
Value: public_ip from Terraform
TTL: 300
```

Caddy retries certificate issuance automatically after DNS begins resolving to the VM.

### 3. Check cloud-init

From PowerShell:

```powershell
ssh -i "$HOME\.ssh\wilson_lab_oci" ubuntu@PUBLIC_IP
```

On the VM:

```bash
sudo cloud-init status --wait
sudo tail -n 200 /var/log/cloud-init-output.log
cd /opt/wilson-lab/deploy
docker compose ps
docker compose logs --tail=200 caddy api
```

Cloud-init performs the following:

1. updates Ubuntu packages
2. installs Docker Engine and Compose from Docker's official repository
3. clones Wilson Lab into `/opt/wilson-lab`
4. creates `deploy/.env`
5. generates file-backed application secrets
6. builds the API image
7. starts Caddy, the API, and the labeled demo services

### 4. Validate HTTPS

```powershell
Invoke-RestMethod -Uri "https://YOUR_API_DOMAIN/health"
```

Expected fields:

```text
status      ok
environment production
runtime     docker
```

### 5. Retrieve the demo credentials

On the VM:

```bash
cd /opt/wilson-lab
bash deploy/scripts/show-credentials.sh
```

Store these credentials in a password manager. Do not place them in GitHub, screenshots, portfolio text, or public documentation.

### 6. Connect GitHub Pages

In the `cbw29512/wilson-lab` GitHub repository:

1. Open **Settings → Secrets and variables → Actions → Variables**.
2. Create `VITE_API_ORIGIN`.
3. Set its value to `https://YOUR_API_DOMAIN` with no trailing slash.
4. Open **Actions → Deploy Frontend to GitHub Pages**.
5. Run the workflow.

The public dashboard should then show **API: available** while preserving Demo Data fallback during an outage.

## Maintenance

### Update the application

```bash
sudo systemctl start wilson-lab-update.service
sudo journalctl -u wilson-lab-update.service --no-pager -n 200
```

### Backup the audit database

```bash
cd /opt/wilson-lab
bash deploy/scripts/backup.sh
```

Copy resulting backups from `/opt/wilson-lab/deploy/backups/` to encrypted off-host storage.

### Destroy the OCI infrastructure

Create a final database backup first. Then run a Resource Manager **Destroy** job, or locally:

```powershell
terraform destroy
```

Destroying the stack deletes the VM and boot volume. Off-host backups and DNS records are not removed automatically.

## Troubleshooting

### SSH times out

- Confirm `ssh_allowed_cidr` matches your current public IPv4 address plus `/32`.
- Confirm the instance has the expected public IP.
- Confirm the Resource Manager Apply completed successfully.

### Terraform reports no matching Ubuntu image

Confirm `ubuntu_version = "24.04"` and `instance_shape = "VM.Standard.A1.Flex"`. The module selects the newest available matching Canonical Ubuntu platform image dynamically.

### API remains unavailable after DNS resolves

```bash
sudo cloud-init status --long
sudo tail -n 300 /var/log/cloud-init-output.log
cd /opt/wilson-lab/deploy
docker compose ps
docker compose logs --tail=300 caddy api
```

### A public IP changed after recreation

Update the DNS `A` record to the new Terraform `public_ip` output, wait for propagation, and recheck `/health`.
