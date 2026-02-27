"""
Script to extract inline code from server.py into modular files.
This performs the bulk extraction safely.
"""
import re

def read_file(path):
    with open(path) as f:
        return f.readlines()

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

lines = read_file('/app/backend/server.py')

def extract_range(start_line, end_line):
    """Extract lines (1-indexed) and return as string"""
    return ''.join(lines[start_line-1:end_line])

# Find exact line numbers for each section
def find_line(pattern, start_from=1):
    for i, line in enumerate(lines, 1):
        if i >= start_from and pattern in line:
            return i
    return None

# Map all sections
sections = {}

# Licensing endpoints (457-658)
sections['licensing_start'] = find_line('@api_router.get("/licensing/health")')
sections['licensing_end'] = find_line('# Auth functions imported from auth/service.py') - 1

# Agency router + endpoints (668-1290)
sections['agency_start'] = find_line('# Create agency router')
sections['agency_end'] = find_line('@agency_router.get("/status")') 
# Find end of agency_status function
for i in range(sections['agency_end'], len(lines)+1):
    if i > sections['agency_end'] + 5 and lines[i-1].strip() == '' and (i >= len(lines) or not lines[i].startswith(' ')):
        sections['agency_end'] = i
        break

# Admin notification endpoints (1295-1360)
sections['admin_notif_start'] = find_line('@api_router.post("/admin/send-notification")')
sections['admin_notif_end'] = find_line('# Distribution Service Classes') - 1

# Service classes
sections['dist_svc_start'] = find_line('class DistributionService:')
sections['dist_svc_end'] = find_line('distribution_service = DistributionService()') 

sections['email_ses_start'] = find_line('# Email Service Functions')
sections['email_ses_end'] = find_line('email_service = SESService()', sections['email_ses_start'])

sections['email_basic_start'] = find_line('class EmailService:', sections['email_ses_end'])
sections['email_basic_end'] = find_line('# Initialize email service', sections['email_basic_start']) - 1

# S3 + second SES + EmailNotification
sections['s3_start'] = find_line('# AWS S3 Service Class')
sections['s3_end'] = find_line('# AWS SES Service Class', sections['s3_start']) - 1

sections['ses2_start'] = find_line('# AWS SES Service Class', sections['s3_start'])
sections['ses2_end'] = find_line('# Enhanced Email Notification Service') - 1

sections['email_notif_start'] = find_line('# Enhanced Email Notification Service')
sections['email_notif_end'] = find_line('enhanced_email_service = EmailNotificationService()')

# UPC helper
sections['upc_start'] = find_line('def calculate_upc_check_digit')
sections['upc_end'] = find_line('# API Endpoints', sections['upc_start']) - 1

# Auth endpoints
sections['auth_start'] = find_line('# API Endpoints', sections['upc_start'])
sections['auth_end'] = find_line('# DAO and Smart Contract endpoints') - 1

# DAO endpoints
sections['dao_start'] = find_line('# DAO and Smart Contract endpoints')
sections['dao_end'] = find_line('# Payment & Financial Services Endpoints') - 1

# Health check endpoints (payment, paypal, stripe, metadata, reporting, batch)
sections['health_check_start'] = find_line('# Payment & Financial Services Endpoints')
sections['health_check_end'] = find_line('# Business Identifiers Endpoints') - 1

# Business endpoints
sections['business_start'] = find_line('# Business Identifiers Endpoints')
sections['business_end'] = find_line('# Media Management Endpoints') - 1

# Media endpoints
sections['media_start'] = find_line('# Media Management Endpoints') or find_line('@api_router.post("/media/upload")')
sections['media_end'] = find_line('# AWS S3 Enhanced Media Endpoints') - 1

# AWS S3/SES endpoints
sections['aws_ep_start'] = find_line('# AWS S3 Enhanced Media Endpoints')
sections['aws_ep_end'] = find_line('@api_router.get("/distribution/platforms")') - 1

# Distribution endpoints
sections['dist_ep_start'] = find_line('@api_router.get("/distribution/platforms")')
sections['dist_ep_end'] = find_line('@api_router.get("/admin/users")') - 1

# Admin CRUD endpoints
sections['admin_crud_start'] = find_line('@api_router.get("/admin/users")')
sections['admin_crud_end'] = find_line('@api_router.get("/mlc/health")') - 1

# More health checks (mlc, mde, pdooh)
sections['health2_start'] = find_line('@api_router.get("/mlc/health")')
sections['health2_end'] = find_line('@api_router.post("/aws/media/process/{file_type}")') - 1

# AWS media processing endpoints
sections['aws_proc_start'] = find_line('@api_router.post("/aws/media/process/{file_type}")')
sections['aws_proc_end'] = find_line('@api_router.get("/phase2/status")')

# Phase2 status
sections['phase2_start'] = find_line('@api_router.get("/phase2/status")')
# Find the end of phase2 - it's followed by router includes
for i in range(sections['phase2_start'], len(lines)+1):
    if 'from router_setup' in lines[i-1]:
        sections['phase2_end'] = i - 1
        break

# System/health endpoints at the end 
sections['sys_start'] = find_line('# API root endpoint')
sections['sys_end'] = find_line('@app.post("/api/webhook/stripe")') - 1

# Stripe webhook 
sections['webhook_start'] = find_line('@app.post("/api/webhook/stripe")')
sections['webhook_end'] = find_line('# Basic endpoints for immediate 200 responses') - 1

# Misc basic endpoints
sections['misc_start'] = find_line('# Basic endpoints for immediate 200 responses')
sections['misc_end'] = find_line('# Phase 2: CloudFront') - 1

# AWS service classes (CloudFront, Lambda, Rekognition)
sections['aws_svc_start'] = find_line('# Phase 2: CloudFront')
sections['aws_svc_end'] = find_line('rekognition_service = RekognitionService()')

print("=== Section Map ===")
for k, v in sorted(sections.items()):
    print(f"  {k}: line {v}")

print(f"\n=== Total lines: {len(lines)} ===")
