# CVE Remediation Infrastructure — Deployment & Operations Guide

## Architecture Overview

```
AWS Inspector  →  EventBridge Rule  →  Lambda  →  GitHub Issues
                  (CRITICAL/HIGH)       ↓
                                   CloudWatch Metrics
                                   (CVE_Detected_Count, Remediation_Issues_Created)
```

## Directory Structure

```
infra/
  main.tf                  # Lambda + EventBridge + IAM
  variables.tf             # Input variable definitions
  outputs.tf               # Exported resource identifiers
  environments/
    dev.tfvars             # Dev environment config
    staging.tfvars         # Staging environment config
    prod.tfvars            # Production environment config

lambda/
  remediation_lambda.py    # Lambda handler (EventBridge → GitHub)
  requirements.txt         # Python dependencies for Lambda
  package.sh               # Packaging script → remediation.zip

.github/workflows/
  build-lambda.yml         # CI — package and upload to S3
```

## Prerequisites

1. **S3 Bucket**: `model-agency-assets` must exist
2. **Secrets Manager**: GitHub PAT stored at the ARN in tfvars
3. **DynamoDB Table**: `terraform-lock` for state locking
4. **GitHub PAT**: Must have `repo` scope for issue creation

## Lambda Packaging

```bash
chmod +x lambda/package.sh
./lambda/package.sh
# Produces lambda/remediation.zip
```

### Verify zip contents
```bash
unzip -l lambda/remediation.zip
# Expect: remediation_lambda.py, requests/ package files
```

## Deployment Commands

### Deploy to dev
```bash
cd infra
terraform init
terraform workspace select dev || terraform workspace new dev
terraform apply -var-file=./environments/dev.tfvars -auto-approve
```

### Promote to staging
```bash
terraform workspace select staging || terraform workspace new staging
terraform apply -var-file=./environments/staging.tfvars -auto-approve
```

### Promote to prod
```bash
terraform workspace select prod || terraform workspace new prod
terraform apply -var-file=./environments/prod.tfvars -auto-approve
```

## Validation Checklist

After each environment deployment:

- [ ] Trigger a test EventBridge event simulating an Inspector finding → confirm GitHub issue appears
- [ ] Open a PR with a known vulnerable dependency → confirm `security.yml` runs SBOM and Snyk and blocks on critical findings
- [ ] Confirm SBOM artifact is attached to the PR artifacts
- [ ] Confirm Lambda logs in CloudWatch show the event and issue creation
- [ ] Confirm Terraform outputs `remediation_lambda_arn` and `inspector_event_rule_name`

### Test EventBridge Event

```bash
aws events put-events --entries '[{
  "Source": "aws.inspector2",
  "DetailType": "Inspector2 Finding",
  "Detail": "{\"severity\":\"CRITICAL\",\"title\":\"Test CVE-2025-0001\",\"description\":\"Test finding for validation\",\"type\":\"PACKAGE_VULNERABILITY\",\"inspectorScore\":9.8}"
}]'
```

## S3 Artifact Keys

| Environment | S3 Key |
|-------------|--------|
| dev | `s3://model-agency-assets/remediation-dev.zip` |
| staging | `s3://model-agency-assets/remediation-staging.zip` |
| prod | `s3://model-agency-assets/remediation-prod.zip` |

## CloudWatch Metrics

| Metric | Description |
|--------|-------------|
| `CVE_Detected_Count` | Incremented on each Lambda invocation containing a finding |
| `Remediation_Issues_Created` | Incremented after successful GitHub issue creation |
| `Auto_PRs_Created` | Incremented when an auto-PR is opened |

Namespace: `CVERemediation`, Dimension: `Environment`

## Quick Runbooks

### Critical Finding Detected
1. SNS → Slack alert fires
2. Identify owner from resource tags
3. Check if auto-PR was created
4. If auto-PR green: promote canary → monitor 30 min → promote to prod
5. Update remediation item status

### Auto-PR Failed
1. Issue assigned to owner with CI logs
2. Owner triages and patches manually
3. Update remediation status to `in_review`

### Postmortem Template
- Detection time
- Remediation time
- Root cause
- Preventive action
- Was auto-remediation effective?
