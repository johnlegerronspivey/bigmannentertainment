# Quick Start Guide - Lambda Runtime Update

## 🚀 1-Minute Setup

### Step 1: Configure AWS (One-time)

```bash
aws configure
```

Enter your credentials:
- **AWS Access Key ID:** [Your key]
- **AWS Secret Access Key:** [Your secret]
- **Default region:** us-east-2
- **Default output format:** json

### Step 2: Navigate to Scripts

```bash
cd /app/aws-lambda-update
```

### Step 3: Run Update (Choose One)

**Option A: Python Script (Recommended)**
```bash
python3 update-lambda-runtime.py
```

**Option B: Bash Script**
```bash
./update-lambda-runtime.sh
```

### Step 4: Confirm Update

When prompted:
```
Proceed with update? (yes/no):
```

Type `yes` and press Enter.

### Step 5: Wait for Completion

The script will:
1. ✅ Backup all functions (~10 seconds)
2. ✅ Update runtimes (~30 seconds)
3. ✅ Test functions (~20 seconds)
4. ✅ Show results

**Total Time:** ~60 seconds

---

## 📊 What Happens

### Functions Being Updated

1. **amplify-login-create-auth-challenge-ec5da3fb**
2. **amplify-login-custom-message-ec5da3fb**
3. **amplify-login-define-auth-challenge-ec5da3fb**
4. **amplify-login-verify-auth-challenge-ec5da3fb**

### Runtime Change

```
nodejs20.x  →  nodejs22.x
```

**Everything else stays the same:**
- ✅ Code unchanged
- ✅ Configuration unchanged
- ✅ Permissions unchanged
- ✅ Triggers unchanged

---

## ✅ Expected Output

```
=====================================
  BACKING UP FUNCTION CONFIGURATIONS
=====================================

ℹ Backing up: amplify-login-create-auth-challenge-ec5da3fb
✓ Backed up: amplify-login-create-auth-challenge-ec5da3fb (Runtime: nodejs20.x)
ℹ Backing up: amplify-login-custom-message-ec5da3fb
✓ Backed up: amplify-login-custom-message-ec5da3fb (Runtime: nodejs20.x)
...

✓ Backup saved to: lambda-backup-20251118-140000.json

=====================================
      UPDATING LAMBDA RUNTIMES
=====================================

ℹ Updating: amplify-login-create-auth-challenge-ec5da3fb
ℹ Current runtime: nodejs20.x
ℹ Target runtime: nodejs22.x
✓ Successfully updated to nodejs22.x
...

=====================================
      UPDATE SUMMARY
=====================================

Statistics:
  Total functions: 4
  Successful updates: 4
  Successful tests: 4

Detailed Results:
✓ amplify-login-create-auth-challenge-ec5da3fb
    Update: ✓  Test: ✓
✓ amplify-login-custom-message-ec5da3fb
    Update: ✓  Test: ✓
✓ amplify-login-define-auth-challenge-ec5da3fb
    Update: ✓  Test: ✓
✓ amplify-login-verify-auth-challenge-ec5da3fb
    Update: ✓  Test: ✓

✅ UPDATE COMPLETE
```

---

## 🔄 If Something Goes Wrong

### Option 1: Automatic Rollback

If any function fails, the script will ask:
```
⚠ Some functions failed to update or test
Rollback all functions? (yes/no):
```

Type `yes` to automatically restore all functions.

### Option 2: Manual Rollback

```bash
# Find your backup file
ls -la lambda-backup-*.json

# Use AWS CLI to restore
aws lambda update-function-configuration \
  --function-name amplify-login-create-auth-challenge-ec5da3fb \
  --runtime nodejs20.x \
  --region us-east-2

# Repeat for each function
```

---

## 🧪 Verify Update

### Check Runtime Version

```bash
aws lambda get-function-configuration \
  --function-name amplify-login-create-auth-challenge-ec5da3fb \
  --region us-east-2 \
  --query 'Runtime'
```

**Expected:** `"nodejs22.x"`

### Test Authentication

1. Go to your Amplify app
2. Try to login
3. Verify authentication works
4. Check custom messages appear correctly

### Check CloudWatch Logs

```bash
aws logs tail /aws/lambda/amplify-login-create-auth-challenge-ec5da3fb --follow --region us-east-2
```

Look for any errors or warnings.

---

## 📞 Need Help?

### Prerequisites Missing?

**AWS CLI not installed:**
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Python boto3 not installed:**
```bash
pip install boto3
```

**jq not installed (for Bash script):**
```bash
# macOS
brew install jq

# Linux
sudo apt-get install jq
```

### Permission Errors?

Check your IAM user has these permissions:
- `lambda:GetFunctionConfiguration`
- `lambda:UpdateFunctionConfiguration`
- `lambda:ListFunctions`

### Still Stuck?

1. Check full documentation: `README.md`
2. View logs: `aws logs tail /aws/lambda/FUNCTION_NAME --follow`
3. AWS Console: https://console.aws.amazon.com/lambda
4. Contact support: devops@bigmannentertainment.com

---

## 🎯 Success Criteria

After running the script, verify:

- [ ] All 4 functions show ✓ for Update
- [ ] All 4 functions show ✓ for Test
- [ ] Backup file created (lambda-backup-*.json)
- [ ] No error messages in output
- [ ] Authentication still works in your app
- [ ] CloudWatch shows no new errors

**If all checked: You're done! 🎉**

---

## ⏱️ Timeline

| Step | Duration |
|------|----------|
| Configure AWS | 2 min (one-time) |
| Run script | 1 min |
| Verification | 2 min |
| **Total** | **5 minutes** |

---

## 💡 Pro Tips

1. **Run during low traffic** - Update when fewer users are active
2. **Keep backup file** - Save `lambda-backup-*.json` for 30 days
3. **Monitor after update** - Watch CloudWatch for 1 hour
4. **Test thoroughly** - Verify all auth flows work
5. **Document** - Note the update time and any issues

---

**Ready? Let's update!**

```bash
cd /app/aws-lambda-update
python3 update-lambda-runtime.py
```

Good luck! 🚀
