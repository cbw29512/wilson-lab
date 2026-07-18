# Wilson Lab Release Process

This procedure creates a documented showcase release without publishing credentials, cloud identifiers, Terraform state, or private verification data.

## Release contract

These values must agree:

- root `VERSION`
- `backend/pyproject.toml` project version
- the release heading in `CHANGELOG.md`
- the Git tag, formatted as `v<version>`

The `Release Check` workflow validates this contract and creates a downloadable `release-manifest.json` artifact.

## 1. Prepare the release branch

From Windows PowerShell:

```powershell
Set-Location C:\Path\To\wilson-lab
git switch main
git pull --ff-only
git switch -c release/v0.8.0
```

Update the version, changelog, case study, and any release documentation. Do not include secrets or live cloud identifiers.

## 2. Run local validation

```powershell
Set-Location frontend
npm ci
npm run check
npm audit --omit=dev --audit-level=high

Set-Location ..\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[test]"
pytest
Deactivate

Set-Location ..
python -m compileall -q tools
python -m unittest discover -s tools/tests -v
```

Terraform validation requires Terraform installed locally:

```powershell
terraform -chdir=infra/oci fmt -check
terraform -chdir=infra/oci init -backend=false
terraform -chdir=infra/oci validate
```

## 3. Push and review

```powershell
git status
git add VERSION CHANGELOG.md README.md docs backend .github
git commit -m "Prepare Wilson Lab v0.8.0 release"
git push -u origin release/v0.8.0
```

Open a pull request and confirm these checks are green:

- Frontend CI
- Backend CI
- Deployment CI
- Infrastructure CI when Terraform changed
- Verification CI when verifier code changed
- Dependency Audit
- Release Check

## 4. Merge and tag

After the release-preparation pull request is merged:

```powershell
git switch main
git pull --ff-only
git tag -a v0.8.0 -m "Wilson Lab v0.8.0"
git push origin v0.8.0
```

The tag triggers `Release Check`. Confirm the generated manifest reports:

- project `wilson-lab`
- version `0.8.0`
- backend version `0.8.0`
- the tagged commit SHA
- live API status `external activation required`

## 5. Create the GitHub release

In GitHub:

1. Open **Releases**.
2. Choose **Draft a new release**.
3. Select tag `v0.8.0`.
4. Use title `Wilson Lab v0.8.0 — Secure Control Plane Showcase`.
5. Copy the `0.8.0` section from `CHANGELOG.md`.
6. Link the live dashboard and `docs/CASE_STUDY.md`.
7. State clearly that the public dashboard is in demo mode until OCI and DNS activation are complete.
8. Publish the release.

## 6. Post-release verification

```powershell
Invoke-WebRequest https://cbw29512.github.io/wilson-lab/ -Method Head
```

Then confirm:

- README badges are green
- the dashboard loads
- the changelog and case study links work
- no credentials or private identifiers appear in the release notes
- issue #5 remains the source of truth for live OCI activation

## Live activation release

Do not mark Wilson Lab as verified-live merely because the code release exists. After OCI activation, create a later release only after:

- DNS and HTTPS succeed
- health verification passes
- read-only RBAC verification passes
- the full managed operation produces a matching audit event
- the proof bundle passes sensitive-data validation
- the portfolio screenshots and wording are updated accurately
