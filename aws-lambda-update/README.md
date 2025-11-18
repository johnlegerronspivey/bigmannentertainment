# AWS Lambda Runtime Update Guide

## 📋 Overview

Automated scripts to safely update AWS Lambda functions from Node.js 20.x to the newest version (Node.js 22.x) with backup and rollback capabilities.

**Target Functions:** 4 Amplify Auth Lambda functions  
**Region:** us-east-2 (Ohio)  
**Current Runtime:** nodejs20.x  
**Target Runtime:** nodejs22.x (latest stable)

---

## 🎯 Lambda Functions to Update

1. **amplify-login-create-auth-challenge-ec5da3fb**
   - ARN: `arn:aws:lambda:us-east-2:314108682794:function:amplify-login-create-auth-challenge-ec5da3fb`
   - Purpose: Creates custom auth challenges for Amplify login

2. **amplify-login-custom-message-ec5da3fb**
   - ARN: `arn:aws:lambda:us-east-2:314108682794:function:amplify-login-custom-message-ec5da3fb`
   - Purpose: Customizes authentication messages

3. **amplify-login-define-auth-challenge-ec5da3fb**
   - ARN: `arn:aws:lambda:us-east-2:314108682794:function:amplify-login-define-auth-challenge-ec5da3fb`
   - Purpose: Defines the authentication challenge flow

4. **amplify-login-verify-auth-challenge-ec5da3fb**
   - ARN: `arn:aws:lambda:us-east-2:314108682794:function:amplify-login-verify-auth-challenge-ec5da3fb`
   - Purpose: Verifies auth challenge responses

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install AWS CLI (if not already installed)
brew install awscli  # macOS
# or
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install jq (for Bash script)
brew install jq  # macOS
# or
sudo apt-get install jq  # Ubuntu/Debian

# Install boto3 (for Python script)
pip install boto3
```

### Configure AWS Credentials

```bash
aws configure
# Enter:
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region: us-east-2
# Default output format: json
```

### Verify Access

```bash
# Check credentials
aws sts get-caller-identity

# Verify Lambda access
aws lambda list-functions --region us-east-2 | head -20
```

---

## 📦 Available Scripts

### 1. Python Script (Recommended)

**File:** `update-lambda-runtime.py`

**Features:**
- ✅ Color-coded terminal output
- ✅ Automatic backup
- ✅ Runtime compatibility check
- ✅ Function testing after update
- ✅ Automatic rollback on failure
- ✅ CloudWatch metrics integration

**Usage:**
```bash
cd /app/aws-lambda-update
python3 update-lambda-runtime.py
```

### 2. Bash Script (Alternative)

**File:** `update-lambda-runtime.sh`

**Features:**
- ✅ No Python dependencies
- ✅ Works on any Linux/macOS
- ✅ Backup and rollback
- ✅ Function verification

**Usage:**
```bash
cd /app/aws-lambda-update
./update-lambda-runtime.sh
```

---

## 🔧 Execution Steps

### Step-by-Step Process

**1. Pre-Flight Checks**
- Verify AWS credentials
- Check Lambda function access
- Validate current runtime versions
- Check available Node.js runtimes

**2. Backup**
- Export current configuration
- Save to `lambda-backup-TIMESTAMP.json`
- Include runtime, handler, timeout, memory settings

**3. Runtime Update**
- Update each function to nodejs22.x
- Wait for AWS to complete update
- Verify runtime change

**4. Function Testing**
- Check function state (Active/Inactive)
- Verify last update status
- Optional: Invoke function with test event

**5. Summary & Rollback**
- Display update statistics
- Show success/failure for each function
- Offer rollback if any failures

---

## 📊 What Gets Updated

### Configuration Changes

| Setting | Action |
|---------|--------|
| Runtime | nodejs20.x → nodejs22.x |
| Handler | Unchanged |
| Timeout | Unchanged |
| Memory | Unchanged |
| Environment Variables | Unchanged |
| VPC Config | Unchanged |
| Layers | Unchanged |
| IAM Role | Unchanged |

**Only the runtime version changes!**

---

## 🔄 Backup & Rollback

### Automatic Backup

**Backup File Format:**
```json
{
  "timestamp": "2025-11-18T14:00:00Z",
  "region": "us-east-2",
  "functions": {
    "amplify-login-create-auth-challenge-ec5da3fb": {
      "runtime": "nodejs20.x",
      "handler": "index.handler",
      "timeout": 3,
      "memory_size": 128,
      "revision_id": "abc123..."
    },
    ...
  }
}
```

### Manual Rollback

If you need to rollback manually:

```bash
# Using AWS CLI
aws lambda update-function-configuration \
  --function-name amplify-login-create-auth-challenge-ec5da3fb \
  --runtime nodejs20.x \
  --region us-east-2

# Repeat for each function
```

### Automated Rollback

The scripts offer automatic rollback if updates fail:
```
⚠ Some functions failed to update or test
Rollback all functions? (yes/no):
```

---

## 🧪 Testing

### Pre-Update Testing

```bash
# Check current runtime
aws lambda get-function-configuration \
  --function-name amplify-login-create-auth-challenge-ec5da3fb \
  --region us-east-2 \
  --query 'Runtime'
```

### Post-Update Verification

```bash
# Verify new runtime
aws lambda get-function-configuration \
  --function-name amplify-login-create-auth-challenge-ec5da3fb \
  --region us-east-2 \
  --query 'Runtime'

# Check function state
aws lambda get-function-configuration \
  --function-name amplify-login-create-auth-challenge-ec5da3fb \
  --region us-east-2 \
  --query 'State'
```

### Integration Testing

Test your Amplify authentication flow:

1. **Login Flow Test**
   - Attempt user login
   - Verify auth challenge creation
   - Check custom messages
   - Validate challenge verification

2. **CloudWatch Logs**
   ```bash
   # View function logs
   aws logs tail /aws/lambda/amplify-login-create-auth-challenge-ec5da3fb --follow
   ```

3. **CloudWatch Metrics**
   ```bash
   # Check for errors
   aws cloudwatch get-metric-statistics \
     --namespace AWS/Lambda \
     --metric-name Errors \
     --dimensions Name=FunctionName,Value=amplify-login-create-auth-challenge-ec5da3fb \
     --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 3600 \
     --statistics Sum \
     --region us-east-2
   ```

---

## ⚠️ Important Notes

### Node.js 22.x Changes

**What's New:**
- Improved performance
- Better ES modules support
- Enhanced security features
- Updated V8 engine
- Better async/await handling

**Breaking Changes:**
- Most code should be compatible
- Check for deprecated features
- Review AWS SDK compatibility
- Test thoroughly in dev first

### AWS Lambda Support

**Supported Runtimes (as of 2025):**
- nodejs22.x ✅ Latest
- nodejs20.x ✅ Current
- nodejs18.x ✅ Maintenance
- nodejs16.x ⚠️ Deprecated
- nodejs14.x ❌ End of life

### Amplify Considerations

**Custom Auth Lambda Triggers:**
- No code changes required for runtime update
- Handler signature remains the same
- Environment variables preserved
- Cognito integration unaffected

**Testing Required:**
- Create auth challenge
- Define auth challenge
- Verify auth challenge
- Custom message triggers

---

## 🔍 Troubleshooting

### Common Issues

**1. Access Denied**
```bash
Error: User is not authorized to perform: lambda:UpdateFunctionConfiguration
```

**Solution:**
```bash
# Verify IAM permissions
aws iam get-user

# Required permissions:
# - lambda:GetFunctionConfiguration
# - lambda:UpdateFunctionConfiguration
# - lambda:ListFunctions
```

**2. Function Update Failed**
```bash
Error: The runtime parameter of nodejs22.x is not supported
```

**Solution:**
- Check if runtime is available in your region
- Use nodejs20.x if nodejs22.x not yet available
- Update TARGET_RUNTIME in script

**3. Concurrent Modification**
```bash
Error: The operation cannot be performed at this time. The function is currently being updated.
```

**Solution:**
- Wait 30 seconds and retry
- Increase sleep time in script
- Check AWS Console for function status

**4. Import Error (Python)**
```bash
ModuleNotFoundError: No module named 'boto3'
```

**Solution:**
```bash
pip install boto3
# or
pip3 install boto3
```

---

## 📈 Expected Results

### Successful Update

```
✓ Backed up: amplify-login-create-auth-challenge-ec5da3fb (Runtime: nodejs20.x)
✓ Successfully updated to nodejs22.x
✓ Function is active and ready
✓ Backed up: amplify-login-custom-message-ec5da3fb (Runtime: nodejs20.x)
✓ Successfully updated to nodejs22.x
✓ Function is active and ready
...

Statistics:
  Total functions: 4
  Successful updates: 4
  Successful tests: 4
```

### Failed Update

```
✗ Failed to update amplify-login-create-auth-challenge-ec5da3fb: Runtime not supported
⚠ Some functions failed to update or test
Rollback all functions? (yes/no):
```

---

## 🔒 Security Best Practices

**Before Update:**
1. ✅ Review IAM permissions
2. ✅ Backup Lambda code
3. ✅ Test in dev environment first
4. ✅ Notify team members
5. ✅ Schedule maintenance window

**After Update:**
1. ✅ Monitor CloudWatch logs
2. ✅ Check error rates
3. ✅ Test authentication flow
4. ✅ Keep backup file secure
5. ✅ Document changes

---

## 📞 Support

### AWS Lambda Documentation
- Runtime Support: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
- Node.js Runtime: https://docs.aws.amazon.com/lambda/latest/dg/lambda-nodejs.html
- Custom Auth: https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-challenge.html

### Amplify Documentation
- Auth Triggers: https://docs.amplify.aws/lib/auth/advanced/q/platform/js/

### Emergency Contacts
- AWS Support: https://console.aws.amazon.com/support
- BME DevOps: devops@bigmannentertainment.com

---

## 📝 Checklist

**Pre-Update:**
- [ ] AWS credentials configured
- [ ] Script permissions set (chmod +x)
- [ ] Backup location verified
- [ ] Team notified
- [ ] Maintenance window scheduled

**During Update:**
- [ ] Backup completed successfully
- [ ] All 4 functions updated
- [ ] Function tests passed
- [ ] No errors in CloudWatch

**Post-Update:**
- [ ] Authentication flow tested
- [ ] Users can login
- [ ] Custom messages working
- [ ] No increased error rates
- [ ] Backup file saved securely

---

## 🎯 Quick Reference

### Update Command
```bash
# Python (recommended)
python3 update-lambda-runtime.py

# Bash
./update-lambda-runtime.sh
```

### Check Runtime
```bash
aws lambda get-function-configuration \
  --function-name FUNCTION_NAME \
  --region us-east-2 \
  --query 'Runtime'
```

### Manual Update
```bash
aws lambda update-function-configuration \
  --function-name FUNCTION_NAME \
  --runtime nodejs22.x \
  --region us-east-2
```

### View Logs
```bash
aws logs tail /aws/lambda/FUNCTION_NAME --follow
```

---

**Last Updated:** November 18, 2025  
**Script Version:** 1.0  
**Target Runtime:** nodejs22.x  
**Status:** ✅ Ready for Execution
