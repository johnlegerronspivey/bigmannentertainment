"""AWS SES transactional email service + enhanced notification service."""
import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError
from services.email_svc import EmailService

class SESService:
    def __init__(self):
        try:
            self.ses_client = boto3.client(
                'ses',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.verified_sender = os.getenv('SES_VERIFIED_SENDER', 'no-reply@bigmannentertainment.com')
            self.platform_name = os.getenv('PLATFORM_NAME', 'Big Mann Entertainment')
            self.logger = logging.getLogger(__name__)
            self.ses_available = self._check_ses_availability()
        except Exception as e:
            self.logger.warning(f"SES initialization failed: {e}")
            self.ses_available = False
    
    def _check_ses_availability(self):
        """Check if SES is available and properly configured"""
        try:
            # Test basic SES connectivity
            self.ses_client.get_send_quota()
            return True
        except ClientError as e:
            self.logger.warning(f"SES not available: {e.response['Error']['Code']}")
            return False
        except Exception as e:
            self.logger.warning(f"SES check failed: {str(e)}")
            return False
    
    def send_transactional_email(
        self,
        to_addresses: List[str],
        subject: str,
        html_content: str,
        text_content: str = None,
        from_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send transactional email using SES"""
        if not self.ses_available:
            return {
                'success': False,
                'error_message': 'SES not available - permissions may be pending',
                'timestamp': datetime.now().isoformat()
            }
            
        try:
            sender = from_address or self.verified_sender
            
            # Prepare email message
            message = {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Html': {'Data': html_content, 'Charset': 'UTF-8'}
                }
            }
            
            # Add text content if provided
            if text_content:
                message['Body']['Text'] = {'Data': text_content, 'Charset': 'UTF-8'}
            
            # Send email
            response = self.ses_client.send_email(
                Source=sender,
                Destination={'ToAddresses': to_addresses},
                Message=message
            )
            
            # Log successful send
            self.logger.info(f"Email sent successfully. MessageId: {response['MessageId']}")
            
            return {
                'success': True,
                'message_id': response['MessageId'],
                'timestamp': datetime.now().isoformat(),
                'to_addresses': to_addresses,
                'subject': subject
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            self.logger.error(f"SES ClientError: {error_code} - {error_message}")
            
            return {
                'success': False,
                'error_code': error_code,
                'error_message': error_message,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error sending email: {str(e)}")
            return {
                'success': False,
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def send_welcome_email(self, user_email: str, user_name: str) -> Dict[str, Any]:
        """Send welcome email to new users"""
        if not self.ses_available:
            return {
                'success': False,
                'error_message': 'SES not available - using SMTP fallback',
                'timestamp': datetime.now().isoformat()
            }
            
        subject = f'Welcome to {self.platform_name}!'
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to {self.platform_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #3b82f6); padding: 40px 20px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 20px; }}
                .content h2 {{ color: #1f2937; margin-bottom: 20px; }}
                .content p {{ color: #4b5563; line-height: 1.6; margin-bottom: 20px; }}
                .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="/big-mann-logo.png" alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" style="width: 80px; height: 80px; margin-bottom: 20px;">
                    <h1>{self.platform_name}</h1>
                </div>
                <div class="content">
                    <h2>Welcome to our platform!</h2>
                    <p>Hello {user_name},</p>
                    <p>Thank you for joining {self.platform_name}! You can now upload and distribute your creative content across 90+ platforms.</p>
                    <p>Get started by uploading your first media file and distributing it to your audience.</p>
                    <p>Best regards,<br>{self.platform_name} Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 {self.platform_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to {self.platform_name}!
        
        Hello {user_name},
        
        Thank you for joining {self.platform_name}! You can now upload and distribute your creative content across 90+ platforms.
        
        Get started by uploading your first media file and distributing it to your audience.
        
        Best regards,
        {self.platform_name} Team
        """
        
        return self.send_transactional_email(
            to_addresses=[user_email],
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_file_upload_notification(
        self,
        user_email: str,
        user_name: str,
        filename: str,
        file_type: str,
        file_size: str,
        file_url: str
    ) -> Dict[str, Any]:
        """Notify user of successful file upload"""
        if not self.ses_available:
            return {
                'success': False,
                'error_message': 'SES not available - using SMTP fallback',
                'timestamp': datetime.now().isoformat()
            }
            
        subject = f'File Upload Successful - {filename}'
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>File Upload Successful</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #3b82f6); padding: 40px 20px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 20px; }}
                .content h2 {{ color: #1f2937; margin-bottom: 20px; }}
                .content p {{ color: #4b5563; line-height: 1.6; margin-bottom: 20px; }}
                .file-details {{ background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .file-details ul {{ list-style: none; padding: 0; }}
                .file-details li {{ margin-bottom: 10px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #3b82f6); color: white; text-decoration: none; padding: 15px 30px; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="/big-mann-logo.png" alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" style="width: 80px; height: 80px; margin-bottom: 20px;">
                    <h1>{self.platform_name}</h1>
                </div>
                <div class="content">
                    <h2>File Upload Successful</h2>
                    <p>Hello {user_name},</p>
                    <p>Your file "{filename}" has been successfully uploaded to {self.platform_name}.</p>
                    <div class="file-details">
                        <strong>File Details:</strong>
                        <ul>
                            <li><strong>File Type:</strong> {file_type}</li>
                            <li><strong>Size:</strong> {file_size}</li>
                            <li><strong>Upload Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                        </ul>
                    </div>
                    <p>Your file is now ready for distribution across our network of 90+ platforms.</p>
                    <p>Best regards,<br>{self.platform_name} Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 {self.platform_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_transactional_email(
            to_addresses=[user_email],
            subject=subject,
            html_content=html_content
        )

# Enhanced Email Notification Service (combining SES and SMTP fallback)
class EmailNotificationService:
    def __init__(self):
        self.ses_service = SESService()
        self.smtp_service = EmailService()
        self.platform_name = os.getenv('PLATFORM_NAME', 'Big Mann Entertainment')
    
    async def send_email_with_fallback(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None
    ) -> bool:
        """Send email using SES with SMTP fallback"""
        # Try SES first
        result = self.ses_service.send_transactional_email(
            to_addresses=[to_email],
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
        if result['success']:
            return True
        
        # Fallback to SMTP
        try:
            return await self.smtp_service.send_email(to_email, subject, html_content, text_content)
        except Exception as e:
            logging.error(f"Both SES and SMTP failed: {e}")
            return False
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email with fallback"""
        try:
            result = await self.ses_service.send_welcome_email(user_email, user_name)
            return result['success']
        except Exception as e:
            logging.error(f"SES welcome email failed, using SMTP fallback: {e}")
            # Use existing SMTP email service as fallback
            return await self.smtp_service.send_welcome_email(user_email, user_name)
    
    async def send_file_upload_notification(
        self,
        user_email: str,
        user_name: str,
        filename: str,
        file_type: str,
        file_size: str,
        file_url: str
    ) -> bool:
        """Send file upload notification with fallback"""
        try:
            result = await self.ses_service.send_file_upload_notification(
                user_email, user_name, filename, file_type, file_size, file_url
            )
            return result['success']
        except Exception as e:
            logging.error(f"SES file upload notification failed: {e}")
            return False

