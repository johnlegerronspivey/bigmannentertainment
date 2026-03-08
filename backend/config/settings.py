"""
Application settings and environment configuration.
All env vars and constants are centralized here.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')


class Settings:
    # Authentication
    SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    MAX_LOGIN_ATTEMPTS = 10
    LOCKOUT_DURATION_MINUTES = 15
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 24

    # Email
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME", "no-reply@bigmannentertainment.com")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
    EMAIL_FROM_NAME = os.environ.get("EMAIL_FROM_NAME", "Big Mann Entertainment")
    EMAIL_FROM_ADDRESS = os.environ.get("EMAIL_FROM_ADDRESS", "no-reply@bigmannentertainment.com")

    # Stripe
    STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

    # Blockchain
    ETHEREUM_CONTRACT_ADDRESS = os.environ.get('ETHEREUM_CONTRACT_ADDRESS', '0xdfe98870c599734335900ce15e26d1d2ccc062c1')
    ETHEREUM_WALLET_ADDRESS = os.environ.get('ETHEREUM_WALLET_ADDRESS', '0xdfe98870c599734335900ce15e26d1d2ccc062c1')
    INFURA_PROJECT_ID = os.environ.get('INFURA_PROJECT_ID', 'your_infura_project_id')
    BLOCKCHAIN_NETWORK = os.environ.get('BLOCKCHAIN_NETWORK', 'ethereum_mainnet')

    # Social Media
    INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")
    TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
    TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
    TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "")
    FACEBOOK_ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN", "")
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
    TIKTOK_CLIENT_ID = os.environ.get("TIKTOK_CLIENT_ID", "")
    TIKTOK_CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "")

    # Business Configuration
    BUSINESS_EIN = os.environ.get('BUSINESS_EIN', '270658077')
    BUSINESS_ADDRESS = os.environ.get('BUSINESS_ADDRESS', '1314 Lincoln Heights Street, Alexander City, Alabama 35010')
    BUSINESS_PHONE = os.environ.get('BUSINESS_PHONE', '(256) 234-5678')
    BUSINESS_NAICS_CODE = os.environ.get('BUSINESS_NAICS_CODE', '512200')
    BUSINESS_TIN = os.environ.get('BUSINESS_TIN', '270658077')

    # Product and Global Identification Numbers
    UPC_COMPANY_PREFIX = os.environ.get('UPC_COMPANY_PREFIX', '8600043402')
    GLOBAL_LOCATION_NUMBER = os.environ.get('GLOBAL_LOCATION_NUMBER', '0860004340201')
    ISRC_PREFIX = os.environ.get('ISRC_PREFIX', 'QZ9H8')
    PUBLISHER_NUMBER = os.environ.get('PUBLISHER_NUMBER', 'PA04UV')
    IPI_BUSINESS = os.environ.get('IPI_NUMBER_COMPANY', '813048171')
    IPI_PRINCIPAL = os.environ.get('IPI_NUMBER_INDIVIDUAL', '578413032')
    IPN_NUMBER = os.environ.get('IPN_NUMBER', '10959387')
    DPID = os.environ.get('DPID', 'PADPIDA2018072700C')
    BUSINESS_LEGAL_NAME = os.environ.get('BUSINESS_LEGAL_NAME', 'Big Mann Entertainment')
    PRINCIPAL_NAME = os.environ.get('PRINCIPAL_NAME', 'John LeGerron Spivey')

    # AWS
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'bigmann-entertainment-media')
    SES_VERIFIED_SENDER = os.environ.get('SES_VERIFIED_SENDER', 'no-reply@bigmannentertainment.com')
    SES_SENDER_NAME = os.environ.get('SES_SENDER_NAME', 'Big Mann Entertainment')

    # Frontend
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

    # CORS Origins - respect env var, fallback to known domains
    _cors_env = os.environ.get('CORS_ORIGINS', '')
    if _cors_env.strip('"').strip("'") == '*':
        CORS_ORIGINS = ["*"]
    else:
        CORS_ORIGINS = [
            origin.strip() for origin in _cors_env.split(',') if origin.strip()
        ] if _cors_env and _cors_env.strip('"').strip("'") != '*' else []
        CORS_ORIGINS.extend([
            "http://localhost:3000",
            "https://bigmannentertainment.com",
            "https://www.bigmannentertainment.com",
            "https://dev.bigmannentertainment.com",
            "https://staging.bigmannentertainment.com",
            "https://api.bigmannentertainment.com",
            "https://cdn.bigmannentertainment.com",
            "https://d36jfidccx04u0.cloudfront.net",
        ])
        _preview = os.environ.get("REACT_APP_BACKEND_URL", "")
        if _preview:
            CORS_ORIGINS.append(_preview)


settings = Settings()
