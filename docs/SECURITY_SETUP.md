# Security Setup Guide for BME Platform

## Environment Configuration

### 1. Backend Environment Setup

Copy the example environment file and configure your secrets:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your actual credentials:

- **Database**: Update `MONGO_URL` with your MongoDB connection string
- **JWT**: Generate a secure `SECRET_KEY` 
- **Stripe**: Add your actual Stripe API keys (use test keys for development)
- **PayPal**: Configure your PayPal client credentials
- **AWS**: Add your AWS access keys and configure S3 bucket
- **Email**: Configure SES or SMTP settings
- **Blockchain**: Add your Ethereum/Infura configuration
- **Business**: Add your actual business identification numbers

### 2. Frontend Environment Setup

Copy the example environment file:

```bash
cp frontend/.env.example frontend/.env
```

Configure:
- `REACT_APP_BACKEND_URL`: Your backend API URL
- `REACT_APP_STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
- `REACT_APP_PAYPAL_CLIENT_ID`: Your PayPal client ID

### 3. Security Checklist

#### Before Deployment:
- [ ] All `.env` files contain actual credentials (not placeholders)
- [ ] Test files with hardcoded secrets are not committed
- [ ] API keys have proper permissions and are not expired
- [ ] Database credentials are secure and use strong passwords
- [ ] JWT secret key is cryptographically strong
- [ ] CORS origins are properly configured for production

#### API Key Security:
- [ ] Stripe keys: Use live keys only in production
- [ ] AWS keys: Follow principle of least privilege
- [ ] PayPal: Use production environment for live deployments
- [ ] Email: Verify SES sender identity for production

#### Development vs. Production:
- **Development**: Use test/sandbox credentials
- **Production**: Use live credentials with proper security measures

### 4. Sensitive Files Already Protected

The following files contain sensitive information and are properly ignored by Git:

- `backend/.env` - Backend environment variables
- `frontend/.env` - Frontend environment variables
- `*_test.py` - Test files that may contain hardcoded credentials
- `setup_aws_*.py` - AWS setup scripts with hardcoded keys

### 5. Getting Required Credentials

#### Stripe:
1. Create account at https://stripe.com
2. Get API keys from Dashboard > Developers > API keys
3. Use test keys for development, live keys for production

#### PayPal:
1. Create developer account at https://developer.paypal.com
2. Create an application to get client ID and secret
3. Use sandbox for development, live for production

#### AWS:
1. Create AWS account and IAM user
2. Generate access keys with appropriate permissions
3. Create S3 bucket for media storage
4. Set up SES for email sending

#### MongoDB:
1. Set up MongoDB instance (local or cloud)
2. Create database and configure connection string
3. Ensure proper authentication and network security

### 6. Emergency Response

If secrets are accidentally exposed:
1. **Immediately revoke** all exposed API keys
2. **Generate new credentials** from respective service dashboards
3. **Update environment files** with new credentials
4. **Restart services** to use new credentials
5. **Review commit history** and force-push if necessary

### 7. Production Deployment Notes

- Use environment-specific configuration management
- Store secrets in secure key management systems
- Use HTTPS for all external communications
- Regularly rotate API keys and credentials
- Monitor for any unauthorized access

## Support

For questions about security setup, contact the development team or refer to the main README.md file.