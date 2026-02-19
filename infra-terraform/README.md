# infra-terraform

## Overview
Terraform repo for Big Mann Entertainment Programmatic DOOH platform.

## Architecture

### Modules
| Module | Description | Key Resources |
|--------|-------------|---------------|
| `cognito` | User authentication | User Pool, App Client |
| `s3-cloudfront` | Frontend hosting | S3 Bucket, CloudFront CDN |
| `dynamodb` | NoSQL data store | Campaigns, Creatives, Attribution, Royalties tables |
| `kinesis` | Real-time streaming | Impressions stream |
| `lambda` | Serverless compute | Campaign + Creative functions, IAM roles |
| `eventbridge` | Event routing | Custom event bus, weather trigger rule |
| `sns` | Notifications | Alert topic with email subscription |
| `secrets-manager` | Credential storage | Blockchain keys secret |
| `qldb` | Immutable ledger (optional) | QLDB Ledger |
| `media-convert` | Video transcoding (optional) | MediaConvert queue + IAM role |
| `stepfunctions` | Workflow orchestration | State machine |

### Environments
- **prod** - Production environment (higher Kinesis shard count, longer retention)
- **staging** - Staging environment (lower resource allocation)

## Quickstart (staging)

1. Install Terraform >= 1.4
2. Configure AWS credentials (profile or env vars)
3. Initialize:
```bash
cd infra-terraform/envs/staging
terraform init
```

4. Plan:
```bash
terraform plan -var-file=terraform.tfvars
```

5. Apply:
```bash
terraform apply -var-file=terraform.tfvars
```

## Notes
- Replace `campaign_zip` and `creative_zip` with built Lambda artifact zips.
- Replace `tfstate_bucket` with your S3 backend bucket and configure locking (DynamoDB table).
- Secrets: rotate and store production keys in Secrets Manager; do not commit secrets to repo.
- CI/CD: use GitHub Actions or CodePipeline to run `terraform plan` and `terraform apply` with least-privilege deploy role.

## Deployment Checklist

1. **Backend state**: Create S3 bucket for Terraform state and a DynamoDB table for state locking before running `terraform init`.
2. **Artifacts**: Build your Lambda zips and place them under `infra-terraform/artifacts/`.
3. **Secrets**: Populate `initial_secret_json` only with placeholders in repo; use CI secrets or manual `aws secretsmanager put-secret-value` for production.
4. **Least privilege**: After initial deploy, tighten IAM policies for Lambda roles.
5. **Observability**: Add CloudWatch dashboards and alarms.
6. **Testing**: Deploy to staging first, run integration tests.
7. **CI/CD**: Recommended pipeline: build artifacts -> upload to artifact store -> terraform plan -> terraform apply with deploy role.
