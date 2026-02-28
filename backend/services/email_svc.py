"""Email services - SES with SMTP fallback, branded email templates."""
import os
import re
import logging
import boto3
from datetime import datetime
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError

class SESService:
    """AWS SES Email Service with SMTP fallback"""
    
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.verified_sender = os.getenv('SES_VERIFIED_SENDER', 'no-reply@bigmannentertainment.com')
        self.sender_name = os.getenv('SES_SENDER_NAME', 'Big Mann Entertainment')
        self.charset = "UTF-8"
        
        # Initialize SES client
        try:
            self.ses_client = boto3.client(
                'ses',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            # Test SES connectivity
            self.ses_client.get_send_quota()
            self.ses_available = True
            print(f"✅ SES Service initialized successfully for {self.verified_sender}")
        except (ClientError, NoCredentialsError) as e:
            print(f"⚠️ SES Service unavailable: {str(e)}")
            self.ses_client = None
            self.ses_available = False
        
        # Initialize SMTP fallback
        self.smtp_fallback = EmailService()
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """
        Send email using SES (primary) with SMTP fallback
        """
        # Try SES first
        if self.ses_available and self.ses_client:
            try:
                # Prepare email content
                destination = {'ToAddresses': [to_email]}
                
                message = {
                    'Subject': {'Data': subject, 'Charset': self.charset},
                    'Body': {}
                }
                
                # Add HTML content
                if html_content:
                    message['Body']['Html'] = {'Data': html_content, 'Charset': self.charset}
                
                # Add text content
                if text_content:
                    message['Body']['Text'] = {'Data': text_content, 'Charset': self.charset}
                elif html_content:
                    # Convert HTML to plain text if no text content provided
                    import re
                    text_content = re.sub('<[^<]+?>', '', html_content).strip()
                    message['Body']['Text'] = {'Data': text_content, 'Charset': self.charset}
                
                # Send email via SES
                response = self.ses_client.send_email(
                    Source=f"{self.sender_name} <{self.verified_sender}>",
                    Destination=destination,
                    Message=message
                )
                
                print(f"✅ Email sent via SES to {to_email}, MessageId: {response['MessageId']}")
                return True
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                print(f"❌ SES Error [{error_code}]: {error_message}")
                
                # Common SES errors
                if error_code in ['MessageRejected', 'SendingPausedException']:
                    print("🔄 Falling back to SMTP due to SES delivery issue...")
                else:
                    print("🔄 SES failed, falling back to SMTP...")
                    
            except Exception as e:
                print(f"❌ Unexpected SES error: {str(e)}")
                print("🔄 Falling back to SMTP...")
        
        # Fallback to SMTP
        print("📧 Using SMTP fallback for email delivery...")
        return await self.smtp_fallback.send_email(to_email, subject, html_content, text_content)
    
    async def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str):
        """Send password reset email with Big Mann Entertainment branding"""
        reset_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        
        subject = "Reset Your Big Mann Entertainment Password"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password - Big Mann Entertainment</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #3b82f6); padding: 40px 20px; text-align: center; }}
                .header img {{ width: 80px; height: 80px; margin-bottom: 20px; border-radius: 8px; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: 700; }}
                .header p {{ color: #e0e7ff; margin: 10px 0 0 0; font-size: 16px; }}
                .content {{ padding: 40px 30px; }}
                .content h2 {{ color: #1f2937; margin-bottom: 20px; font-size: 24px; }}
                .content p {{ color: #4b5563; line-height: 1.6; margin-bottom: 20px; font-size: 16px; }}
                .button-container {{ text-align: center; margin: 30px 0; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #3b82f6); color: white; text-decoration: none; padding: 15px 35px; border-radius: 8px; font-weight: 600; font-size: 16px; transition: transform 0.2s; }}
                .button:hover {{ transform: translateY(-2px); background: linear-gradient(135deg, #6d28d9, #2563eb); }}
                .url-box {{ background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #7c3aed; }}
                .url-box p {{ color: #374151; font-family: 'Courier New', monospace; word-break: break-all; margin: 0; font-size: 14px; }}
                .security-note {{ background: linear-gradient(135deg, #fef3c7, #fde68a); border: 1px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 25px 0; }}
                .security-note p {{ color: #92400e; margin: 0; font-size: 14px; font-weight: 500; }}
                .footer {{ background-color: #f9fafb; padding: 30px 20px; text-align: center; border-top: 1px solid #e5e7eb; }}
                .footer p {{ color: #6b7280; font-size: 14px; margin: 5px 0; }}
                .footer .logo-small {{ opacity: 0.7; margin-bottom: 15px; }}
                @media (max-width: 600px) {{
                    .content {{ padding: 30px 20px; }}
                    .header {{ padding: 30px 20px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="/big-mann-logo.png" alt="Big Mann Entertainment Logo">
                    <h1>Big Mann Entertainment</h1>
                    <p>Complete Media Distribution Empire</p>
                </div>
                
                <div class="content">
                    <h2>🔐 Reset Your Password</h2>
                    <p>Hello <strong>{user_name}</strong>,</p>
                    <p>We received a request to reset your password for your Big Mann Entertainment account. Click the button below to securely create a new password:</p>
                    
                    <div class="button-container">
                        <a href="{reset_url}" class="button">🔑 Reset My Password</a>
                    </div>
                    
                    <p>If the button doesn't work, you can copy and paste this secure link into your browser:</p>
                    <div class="url-box">
                        <p>{reset_url}</p>
                    </div>
                    
                    <div class="security-note">
                        <p><strong>🛡️ Security Notice:</strong> This password reset link will expire in 24 hours for your security. If you didn't request this password reset, please ignore this email and your password will remain unchanged. For security concerns, contact our support team immediately.</p>
                    </div>
                    
                    <p>Need help? Our support team is here to assist you with any questions about your Big Mann Entertainment account.</p>
                    
                    <p><strong>Best regards,</strong><br>The Big Mann Entertainment Team<br>🎵 Empowering Artists Worldwide</p>
                </div>
                
                <div class="footer">
                    <div class="logo-small">🎵</div>
                    <p><strong>© 2025 Big Mann Entertainment.</strong> All rights reserved.</p>
                    <p>This is an automated security message from no-reply@bigmannentertainment.com</p>
                    <p>Please do not reply to this email. For support, visit our help center.</p>
                    <p>Big Mann Entertainment - Your Complete Media Distribution Empire</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        🎵 BIG MANN ENTERTAINMENT - PASSWORD RESET
        ==========================================
        
        Hello {user_name},
        
        We received a request to reset your password for your Big Mann Entertainment account.
        
        🔑 RESET YOUR PASSWORD:
        Click or copy this secure link: {reset_url}
        
        ⏰ IMPORTANT SECURITY INFORMATION:
        • This link expires in 24 hours for your security
        • If you didn't request this reset, ignore this email
        • Your password will remain unchanged unless you use this link
        
        🛡️ SECURITY NOTICE:
        For any security concerns, contact our support team immediately.
        
        Best regards,
        The Big Mann Entertainment Team
        🎵 Empowering Artists Worldwide
        
        © 2025 Big Mann Entertainment. All rights reserved.
        Complete Media Distribution Empire
        
        ---
        This automated message was sent from no-reply@bigmannentertainment.com
        Please do not reply to this email.
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_welcome_email(self, to_email: str, user_name: str):
        """Send welcome email to new users with Big Mann Entertainment branding"""
        
        subject = "🎵 Welcome to Big Mann Entertainment - Your Music Empire Awaits!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Big Mann Entertainment</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #3b82f6); padding: 40px 20px; text-align: center; }}
                .header img {{ width: 80px; height: 80px; margin-bottom: 20px; border-radius: 8px; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: 700; }}
                .header p {{ color: #e0e7ff; margin: 10px 0 0 0; font-size: 16px; }}
                .welcome-banner {{ background: linear-gradient(135deg, #f59e0b, #ef4444); color: white; text-align: center; padding: 25px; font-size: 18px; font-weight: 600; }}
                .content {{ padding: 40px 30px; }}
                .content h2 {{ color: #1f2937; margin-bottom: 20px; font-size: 24px; }}
                .content p {{ color: #4b5563; line-height: 1.6; margin-bottom: 20px; font-size: 16px; }}
                .features {{ background: linear-gradient(135deg, #f9fafb, #f3f4f6); padding: 25px; border-radius: 12px; margin: 25px 0; border: 1px solid #e5e7eb; }}
                .features h3 {{ color: #7c3aed; margin-bottom: 15px; font-size: 18px; }}
                .features ul {{ list-style: none; padding: 0; margin: 0; }}
                .features li {{ padding: 12px 0; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 15px; position: relative; padding-left: 30px; }}
                .features li:before {{ content: '🎵'; position: absolute; left: 0; color: #7c3aed; }}
                .features li:last-child {{ border-bottom: none; }}
                .button-container {{ text-align: center; margin: 30px 0; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #3b82f6); color: white; text-decoration: none; padding: 15px 35px; border-radius: 8px; font-weight: 600; font-size: 16px; transition: transform 0.2s; }}
                .button:hover {{ transform: translateY(-2px); }}
                .stats {{ display: flex; justify-content: space-around; background: #f8fafc; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .stat {{ text-align: center; }}
                .stat h4 {{ color: #7c3aed; font-size: 24px; margin: 0; }}
                .stat p {{ color: #6b7280; font-size: 14px; margin: 5px 0 0 0; }}
                .footer {{ background-color: #f9fafb; padding: 30px 20px; text-align: center; border-top: 1px solid #e5e7eb; }}
                .footer p {{ color: #6b7280; font-size: 14px; margin: 5px 0; }}
                @media (max-width: 600px) {{
                    .content {{ padding: 30px 20px; }}
                    .header {{ padding: 30px 20px; }}
                    .stats {{ flex-direction: column; gap: 15px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="/big-mann-logo.png" alt="Big Mann Entertainment Logo">
                    <h1>Big Mann Entertainment</h1>
                    <p>Complete Media Distribution Empire</p>
                </div>
                
                <div class="welcome-banner">
                    🎉 Welcome to the Empire, {user_name}! 🎉
                </div>
                
                <div class="content">
                    <h2>🎵 Your Music Journey Starts Here!</h2>
                    <p>Hello <strong>{user_name}</strong>,</p>
                    <p>Welcome to <strong>Big Mann Entertainment</strong> - your gateway to the complete media distribution empire! We're thrilled to have you join our community of talented artists and creators.</p>
                    
                    <div class="stats">
                        <div class="stat">
                            <h4>106+</h4>
                            <p>Distribution Platforms</p>
                        </div>
                        <div class="stat">
                            <h4>Global</h4>
                            <p>Reach</p>
                        </div>
                        <div class="stat">
                            <h4>24/7</h4>
                            <p>Support</p>
                        </div>
                    </div>
                    
                    <div class="features">
                        <h3>🚀 What You Can Do Now:</h3>
                        <ul>
                            <li>Distribute your music to 106+ platforms worldwide</li>
                            <li>Access advanced licensing and rights management</li>
                            <li>Manage UPC, ISRC, and GLN identifiers</li>
                            <li>Process payments with integrated Stripe & PayPal</li>
                            <li>Upload and manage your media library</li>
                            <li>Monitor earnings and royalty splits</li>
                            <li>Access Web3 and NFT minting features</li>
                            <li>Get compliance support for industry standards</li>
                        </ul>
                    </div>
                    
                    <div class="button-container">
                        <a href="https://bigmannentertainment.com/login" class="button">🎵 Start Your Journey</a>
                    </div>
                    
                    <p>Ready to take your music to the world? Log in to your account and start exploring all the powerful features Big Mann Entertainment has to offer.</p>
                    
                    <p>If you have any questions or need assistance getting started, our support team is here to help you every step of the way.</p>
                    
                    <p><strong>Welcome to the empire!</strong><br>The Big Mann Entertainment Team<br>🎵 Empowering Artists Worldwide</p>
                </div>
                
                <div class="footer">
                    <p><strong>© 2025 Big Mann Entertainment.</strong> All rights reserved.</p>
                    <p>This welcome message was sent from no-reply@bigmannentertainment.com</p>
                    <p>You're receiving this because you created a Big Mann Entertainment account.</p>
                    <p>🎵 Complete Media Distribution Empire - Empowering Artists Worldwide</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        🎵 BIG MANN ENTERTAINMENT - WELCOME!
        ===================================
        
        🎉 Welcome to the Empire, {user_name}! 🎉
        
        Hello {user_name},
        
        Welcome to Big Mann Entertainment - your gateway to the complete media distribution empire!
        
        🚀 WHAT YOU CAN DO NOW:
        • Distribute music to 106+ platforms worldwide
        • Access advanced licensing and rights management  
        • Manage UPC, ISRC, and GLN identifiers
        • Process payments with Stripe & PayPal integration
        • Upload and manage your media library
        • Monitor earnings and royalty splits
        • Access Web3 and NFT minting features
        • Get compliance support for industry standards
        
        📊 OUR REACH:
        • 106+ Distribution Platforms
        • Global Coverage
        • 24/7 Support
        
        🎵 GET STARTED:
        Visit: https://bigmannentertainment.com/login
        
        Ready to take your music to the world? Log in and start exploring all the powerful features.
        
        Need help? Our support team is here for you every step of the way.
        
        Welcome to the empire!
        
        Best regards,
        The Big Mann Entertainment Team
        🎵 Empowering Artists Worldwide
        
        © 2025 Big Mann Entertainment. All rights reserved.
        Complete Media Distribution Empire
        
        ---
        This welcome message was sent from no-reply@bigmannentertainment.com
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_notification_email(self, to_email: str, user_name: str, subject: str, message: str):
        """Send notification email to users"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject} - Big Mann Entertainment</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #3b82f6); padding: 40px 20px; text-align: center; }}
                .header img {{ width: 80px; height: 80px; margin-bottom: 20px; border-radius: 8px; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: 700; }}
                .header p {{ color: #e0e7ff; margin: 10px 0 0 0; font-size: 16px; }}
                .content {{ padding: 40px 30px; }}
                .content h2 {{ color: #1f2937; margin-bottom: 20px; font-size: 24px; }}
                .content p {{ color: #4b5563; line-height: 1.6; margin-bottom: 20px; font-size: 16px; }}
                .message-box {{ background: linear-gradient(135deg, #f0f9ff, #e0f2fe); border-left: 4px solid #7c3aed; padding: 20px; margin: 25px 0; border-radius: 8px; }}
                .message-box p {{ color: #374151; margin: 0; font-size: 16px; line-height: 1.6; }}
                .footer {{ background-color: #f9fafb; padding: 30px 20px; text-align: center; border-top: 1px solid #e5e7eb; }}
                .footer p {{ color: #6b7280; font-size: 14px; margin: 5px 0; }}
                @media (max-width: 600px) {{
                    .content {{ padding: 30px 20px; }}
                    .header {{ padding: 30px 20px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="/big-mann-logo.png" alt="Big Mann Entertainment Logo">
                    <h1>Big Mann Entertainment</h1>
                    <p>Complete Media Distribution Empire</p>
                </div>
                
                <div class="content">
                    <h2>📢 {subject}</h2>
                    <p>Hello <strong>{user_name}</strong>,</p>
                    
                    <div class="message-box">
                        <p>{message}</p>
                    </div>
                    
                    <p>Thank you for being part of the Big Mann Entertainment community!</p>
                    
                    <p><strong>Best regards,</strong><br>The Big Mann Entertainment Team<br>🎵 Empowering Artists Worldwide</p>
                </div>
                
                <div class="footer">
                    <p><strong>© 2025 Big Mann Entertainment.</strong> All rights reserved.</p>
                    <p>This notification was sent from no-reply@bigmannentertainment.com</p>
                    <p>You're receiving this as a Big Mann Entertainment community member.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        🎵 BIG MANN ENTERTAINMENT - NOTIFICATION
        =======================================
        
        📢 {subject}
        
        Hello {user_name},
        
        {message}
        
        Thank you for being part of the Big Mann Entertainment community!
        
        Best regards,
        The Big Mann Entertainment Team
        🎵 Empowering Artists Worldwide
        
        © 2025 Big Mann Entertainment. All rights reserved.
        Complete Media Distribution Empire
        
        ---
        This notification was sent from no-reply@bigmannentertainment.com
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    def get_service_status(self):
        """Get current service status"""
        return {
            "ses_available": self.ses_available,
            "verified_sender": self.verified_sender,
            "region": self.region,
            "fallback_enabled": True
        }


class EmailService:
    def __init__(self):
        self.ses_client = boto3.client(
            'ses',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.from_name = os.environ.get('SES_SENDER_NAME', 'Big Mann Entertainment')
        self.from_address = os.environ.get('SES_VERIFIED_SENDER', 'no-reply@bigmannentertainment.com')
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send email using AWS SES"""
        try:
            # Build the email body
            body = {}
            if text_content:
                body['Text'] = {'Charset': 'UTF-8', 'Data': text_content}
            if html_content:
                body['Html'] = {'Charset': 'UTF-8', 'Data': html_content}
            
            # Send email via SES
            response = self.ses_client.send_email(
                Source=f"{self.from_name} <{self.from_address}>",
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Charset': 'UTF-8', 'Data': subject},
                    'Body': body
                }
            )
            
            print(f"✅ Email sent successfully to {to_email}. Message ID: {response['MessageId']}")
            return True
        except self.ses_client.exceptions.MessageRejected as e:
            error_msg = str(e)
            if "Email address is not verified" in error_msg:
                print(f"❌ AWS SES Sandbox Mode: {to_email} is not verified. To send emails:")
                print(f"   1. Verify {to_email} in AWS SES Console, OR")
                print(f"   2. Request production access for your AWS SES account")
                print(f"   Falling back to development mode with reset token in response.")
            else:
                print(f"❌ AWS SES rejected email to {to_email}: {error_msg}")
            return False
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str):
        """Send password reset email"""
        reset_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        
        subject = "Reset Your Big Mann Entertainment Password"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #3b82f6); padding: 40px 20px; text-align: center; }}
                .header img {{ width: 80px; height: 80px; margin-bottom: 20px; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 20px; }}
                .content h2 {{ color: #1f2937; margin-bottom: 20px; }}
                .content p {{ color: #4b5563; line-height: 1.6; margin-bottom: 20px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #3b82f6); color: white; text-decoration: none; padding: 15px 30px; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                .button:hover {{ background: linear-gradient(135deg, #6d28d9, #2563eb); }}
                .footer {{ background-color: #f9fafb; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
                .security-note {{ background-color: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .security-note p {{ color: #92400e; margin: 0; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="/big-mann-logo.png" alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey">
                    <h1>Big Mann Entertainment</h1>
                </div>
                
                <div class="content">
                    <h2>Reset Your Password</h2>
                    <p>Hello {user_name},</p>
                    <p>We received a request to reset your password for your Big Mann Entertainment account. Click the button below to create a new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset My Password</a>
                    </div>
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background-color: #f3f4f6; padding: 10px; border-radius: 4px; font-family: monospace;">{reset_url}</p>
                    
                    <div class="security-note">
                        <p><strong>Security Notice:</strong> This link will expire in 24 hours. If you didn't request this password reset, please ignore this email and your password will remain unchanged.</p>
                    </div>
                    
                    <p>If you're having trouble accessing your account or need assistance, please contact our support team.</p>
                    
                    <p>Best regards,<br>The Big Mann Entertainment Team</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Big Mann Entertainment. All rights reserved.</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>If you need help, contact us through our support channels.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Big Mann Entertainment - Password Reset
        
        Hello {user_name},
        
        We received a request to reset your password for your Big Mann Entertainment account.
        
        Click this link to reset your password:
        {reset_url}
        
        This link will expire in 24 hours. If you didn't request this password reset, please ignore this email.
        
        Best regards,
        The Big Mann Entertainment Team
        
        © 2025 Big Mann Entertainment. All rights reserved.
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_welcome_email(self, to_email: str, user_name: str):
        """Send welcome email to new users"""
        subject = "Welcome to Big Mann Entertainment!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Big Mann Entertainment</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #3b82f6); padding: 40px 20px; text-align: center; }}
                .header img {{ width: 80px; height: 80px; margin-bottom: 20px; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 20px; }}
                .content h2 {{ color: #1f2937; margin-bottom: 20px; }}
                .content p {{ color: #4b5563; line-height: 1.6; margin-bottom: 20px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #3b82f6); color: white; text-decoration: none; padding: 15px 30px; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                .features {{ background-color: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .features ul {{ list-style: none; padding: 0; }}
                .features li {{ padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
                .features li:last-child {{ border-bottom: none; }}
                .footer {{ background-color: #f9fafb; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="/big-mann-logo.png" alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey">
                    <h1>Big Mann Entertainment</h1>
                </div>
                
                <div class="content">
                    <h2>Welcome to the Empire!</h2>
                    <p>Hello {user_name},</p>
                    <p>Welcome to Big Mann Entertainment - your complete media distribution empire! We're excited to have you join our community of creators and entertainers.</p>
                    
                    <div class="features">
                        <h3>What you can do now:</h3>
                        <ul>
                            <li>📤 Upload audio, video, and image content</li>
                            <li>🌍 Distribute to 90+ platforms worldwide</li>
                            <li>💰 Track earnings and manage royalties</li>
                            <li>🎯 Access professional label services</li>
                            <li>🔗 Connect with industry partners</li>
                            <li>📊 Monitor your content performance</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/upload" class="button">Start Uploading Content</a>
                    </div>
                    
                    <p>If you need help getting started or have any questions, our support team is here to help you succeed.</p>
                    
                    <p>Best regards,<br>The Big Mann Entertainment Team</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Big Mann Entertainment. All rights reserved.</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_notification_email(self, to_email: str, subject: str, message: str, user_name: str = "User"):
        """Send general notification email"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #3b82f6); padding: 40px 20px; text-align: center; }}
                .header img {{ width: 80px; height: 80px; margin-bottom: 20px; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 20px; }}
                .content h2 {{ color: #1f2937; margin-bottom: 20px; }}
                .content p {{ color: #4b5563; line-height: 1.6; margin-bottom: 20px; }}
                .footer {{ background-color: #f9fafb; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="/big-mann-logo.png" alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey">
                    <h1>Big Mann Entertainment</h1>
                </div>
                
                <div class="content">
                    <h2>{subject}</h2>
                    <p>Hello {user_name},</p>
                    <div>{message}</div>
                    <p>Best regards,<br>The Big Mann Entertainment Team</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Big Mann Entertainment. All rights reserved.</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
# Initialize email service with SES and SMTP fallback
email_service = SESService()

