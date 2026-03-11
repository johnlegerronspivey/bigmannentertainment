# AWS SES Email Service Configuration

## Current Status
✅ **AWS SES is configured and working**
- Service: AWS Simple Email Service (SES)
- Region: us-east-1
- Verified Sender: no-reply@bigmannentertainment.com
- Verified Recipient: owner@bigmannentertainment.com

## Sandbox Mode Limitations

AWS SES starts in **Sandbox Mode** with the following restrictions:
- ✅ Can send FROM verified email addresses only
- ❌ Can send TO verified email addresses only
- 📊 Limit: 200 emails per 24 hours
- 📊 Rate: 1 email per second

**Current Behavior:**
- Password reset emails will only work for verified email addresses
- Unverified recipients will trigger a fallback to "development mode"
- Development mode returns the reset token in the API response instead of emailing it

## How to Verify Additional Email Addresses

### Option 1: AWS Console (Manual)
1. Go to AWS SES Console: https://console.aws.amazon.com/ses/
2. Navigate to "Verified identities"
3. Click "Create identity"
4. Select "Email address"
5. Enter the email address you want to verify
6. Click "Create identity"
7. Check the inbox of that email address
8. Click the verification link sent by AWS

### Option 2: Using BME API (Programmatic)
Use the admin endpoint to request verification:
```bash
curl -X POST http://localhost:8001/api/admin/ses/verify-email \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Option 3: Python Script
```python
import boto3

ses_client = boto3.client('ses', region_name='us-east-1')
email = 'user@example.com'

response = ses_client.verify_email_identity(EmailAddress=email)
print(f"Verification email sent to {email}")
```

## Moving to Production Access

To send emails to ANY email address (not just verified ones), request production access:

### Steps to Request Production Access:
1. Go to AWS SES Console: https://console.aws.amazon.com/ses/
2. Click on "Account dashboard" in the left sidebar
3. Look for "Sending statistics" section
4. Click "Request production access" button
5. Fill out the request form:
   - **Mail type**: Transactional
   - **Website URL**: https://bigmannentertainment.com
   - **Use case description**: 
     ```
     Big Mann Entertainment is a complete media distribution platform that needs 
     to send transactional emails including:
     - Password reset emails
     - Account verification emails
     - Licensing notifications
     - Royalty payment notifications
     - DAO governance notifications
     ```
   - **Compliance**: Confirm you have opt-out mechanism and comply with AWS policies
6. Submit the request
7. AWS typically responds within 24 hours

### Benefits of Production Access:
- ✅ Send to ANY email address (no verification required)
- 📊 Higher sending limits (50,000 emails per day by default)
- 📊 Higher rate limits (14 emails per second)
- 🚀 Scale your application without email restrictions

## Testing Password Reset

### For Verified Emails (works now):
```bash
# Send password reset email
curl -X POST http://localhost:8001/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "owner@bigmannentertainment.com"}'

# Response: Email sent successfully
```

### For Unverified Emails (sandbox mode):
```bash
# Send password reset email
curl -X POST http://localhost:8001/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "uln.admin@bigmann.com"}'

# Response: Includes reset_token and reset_url in response (development fallback)
```

## Environment Variables

Required environment variables in `/app/backend/.env`:
```bash
AWS_ACCESS_KEY_ID="AKIAUSISWEIVEHCZUOF3"
AWS_SECRET_ACCESS_KEY="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"
AWS_REGION="us-east-1"
SES_VERIFIED_SENDER="no-reply@bigmannentertainment.com"
SES_SENDER_NAME="Big Mann Entertainment"
FRONTEND_URL="https://bigmannentertainment.com"
```

## Troubleshooting

### Error: "Email address is not verified"
**Cause**: Trying to send to an unverified email in sandbox mode
**Solution**: 
- Verify the recipient email address in AWS SES Console
- OR request production access

### Error: "AccessDenied"
**Cause**: AWS credentials don't have SES permissions
**Solution**: Ensure IAM user has `ses:SendEmail` permission

### Error: "Daily message quota exceeded"
**Cause**: Exceeded 200 emails/day limit in sandbox mode
**Solution**: Request production access or wait 24 hours

## Production Deployment Checklist

✅ AWS SES configured with credentials
✅ Sender email verified (no-reply@bigmannentertainment.com)
✅ Email service switched from SMTP to AWS SES
✅ FRONTEND_URL set to production domain
⏳ Request production access (recommended before launch)
⏳ Verify recipient emails OR wait for production access
✅ Test password reset flow end-to-end

## Support

For issues with AWS SES:
- AWS SES Documentation: https://docs.aws.amazon.com/ses/
- AWS Support: https://console.aws.amazon.com/support/
- Check AWS Service Health Dashboard: https://status.aws.amazon.com/
