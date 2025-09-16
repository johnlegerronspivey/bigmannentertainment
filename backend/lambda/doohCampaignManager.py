import json
import boto3
import uuid
from datetime import datetime, timezone
from decimal import Decimal
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
kinesis_client = boto3.client('kinesis')

# DynamoDB Tables
CAMPAIGNS_TABLE = dynamodb.Table('BME-DOOH-Campaigns')
USERS_TABLE = dynamodb.Table('BME-DOOH-Users')
ASSETS_TABLE = dynamodb.Table('BME-DOOH-Assets')

# Kinesis Stream for analytics
ANALYTICS_STREAM = 'BME-DOOH-Analytics-Stream'

def lambda_handler(event, context):
    """
    Main handler for DOOH Campaign Management Lambda function
    """
    try:
        # Parse the event
        http_method = event.get('httpMethod')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        
        # Get user information from Cognito
        user_id = get_user_id_from_context(event)
        if not user_id:
            return create_response(401, {'error': 'Unauthorized'})
        
        # Route the request
        if path.startswith('/campaigns'):
            return handle_campaigns_request(http_method, path, path_parameters, query_parameters, body, user_id)
        elif path.startswith('/assets'):
            return handle_assets_request(http_method, path, path_parameters, query_parameters, body, user_id)
        elif path.startswith('/analytics'):
            return handle_analytics_request(http_method, path, path_parameters, query_parameters, body, user_id)
        else:
            return create_response(404, {'error': 'Not found'})
            
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def get_user_id_from_context(event):
    """Extract user ID from Cognito authentication context"""
    try:
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        claims = authorizer.get('claims', {})
        return claims.get('sub')
    except Exception as e:
        logger.error(f"Error extracting user ID: {str(e)}")
        return None

def handle_campaigns_request(method, path, path_params, query_params, body, user_id):
    """Handle campaign-related requests"""
    try:
        if method == 'GET':
            if path == '/campaigns':
                return get_campaigns(query_params, user_id)
            elif 'campaignId' in path_params:
                return get_campaign(path_params['campaignId'], user_id)
        
        elif method == 'POST':
            if path == '/campaigns':
                return create_campaign(body, user_id)
            elif path.endswith('/launch'):
                return launch_campaign(path_params['campaignId'], user_id)
        
        elif method == 'PUT':
            if 'campaignId' in path_params:
                return update_campaign(path_params['campaignId'], body, user_id)
        
        elif method == 'DELETE':
            if 'campaignId' in path_params:
                return delete_campaign(path_params['campaignId'], user_id)
        
        return create_response(404, {'error': 'Campaign endpoint not found'})
        
    except Exception as e:
        logger.error(f"Error in handle_campaigns_request: {str(e)}")
        return create_response(500, {'error': 'Campaign request failed'})

def get_campaigns(query_params, user_id):
    """Get campaigns for a user"""
    try:
        # Query campaigns by user
        response = CAMPAIGNS_TABLE.scan(
            FilterExpression='created_by = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        campaigns = response.get('Items', [])
        
        # Convert Decimal to float for JSON serialization
        campaigns = convert_decimals(campaigns)
        
        return create_response(200, {
            'success': True,
            'campaigns': campaigns,
            'total_count': len(campaigns)
        })
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {str(e)}")
        return create_response(500, {'error': 'Failed to get campaigns'})

def create_campaign(campaign_data, user_id):
    """Create a new campaign"""
    try:
        # Generate campaign ID
        campaign_id = str(uuid.uuid4())
        
        # Prepare campaign item
        campaign_item = {
            'id': campaign_id,
            'name': campaign_data['name'],
            'description': campaign_data.get('description', ''),
            'campaign_type': campaign_data['campaign_type'],
            'status': 'draft',
            'created_by': user_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'start_date': campaign_data['start_date'],
            'end_date': campaign_data['end_date'],
            'budget_total': Decimal(str(campaign_data['budget_total'])),
            'budget_spent': Decimal('0'),
            'platforms': campaign_data.get('platforms', []),
            'target_audience': campaign_data.get('target_audience', {}),
            'creative_assets': campaign_data.get('creative_assets', []),
            'triggers': campaign_data.get('triggers', []),
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'ctr': Decimal('0'),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Save to DynamoDB
        CAMPAIGNS_TABLE.put_item(Item=campaign_item)
        
        # Send analytics event
        send_analytics_event('campaign_created', {
            'campaign_id': campaign_id,
            'user_id': user_id,
            'campaign_type': campaign_data['campaign_type'],
            'budget': float(campaign_data['budget_total'])
        })
        
        # Convert Decimal for response
        campaign_item = convert_decimals(campaign_item)
        
        return create_response(201, {
            'success': True,
            'campaign': campaign_item,
            'message': 'Campaign created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        return create_response(500, {'error': 'Failed to create campaign'})

def launch_campaign(campaign_id, user_id):
    """Launch a campaign"""
    try:
        # Get campaign
        response = CAMPAIGNS_TABLE.get_item(Key={'id': campaign_id})
        campaign = response.get('Item')
        
        if not campaign:
            return create_response(404, {'error': 'Campaign not found'})
        
        if campaign['created_by'] != user_id:
            return create_response(403, {'error': 'Unauthorized'})
        
        # Update campaign status
        CAMPAIGNS_TABLE.update_item(
            Key={'id': campaign_id},
            UpdateExpression='SET #status = :status, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'active',
                ':updated_at': datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Send analytics event
        send_analytics_event('campaign_launched', {
            'campaign_id': campaign_id,
            'user_id': user_id,
            'platforms': campaign.get('platforms', [])
        })
        
        return create_response(200, {
            'success': True,
            'message': 'Campaign launched successfully'
        })
        
    except Exception as e:
        logger.error(f"Error launching campaign: {str(e)}")
        return create_response(500, {'error': 'Failed to launch campaign'})

def handle_assets_request(method, path, path_params, query_params, body, user_id):
    """Handle asset-related requests"""
    try:
        if method == 'GET':
            if path == '/assets':
                return get_assets(query_params, user_id)
            elif 'assetId' in path_params:
                return get_asset(path_params['assetId'], user_id)
        
        elif method == 'POST':
            if path == '/assets':
                return create_asset(body, user_id)
        
        elif method == 'PUT':
            if 'assetId' in path_params:
                return update_asset(path_params['assetId'], body, user_id)
        
        elif method == 'DELETE':
            if 'assetId' in path_params:
                return delete_asset(path_params['assetId'], user_id)
        
        return create_response(404, {'error': 'Asset endpoint not found'})
        
    except Exception as e:
        logger.error(f"Error in handle_assets_request: {str(e)}")
        return create_response(500, {'error': 'Asset request failed'})

def get_assets(query_params, user_id):
    """Get assets for a user"""
    try:
        # Query assets by user
        response = ASSETS_TABLE.scan(
            FilterExpression='created_by = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        assets = response.get('Items', [])
        assets = convert_decimals(assets)
        
        return create_response(200, {
            'success': True,
            'assets': assets,
            'total_count': len(assets)
        })
        
    except Exception as e:
        logger.error(f"Error getting assets: {str(e)}")
        return create_response(500, {'error': 'Failed to get assets'})

def create_asset(asset_data, user_id):
    """Create a new asset"""
    try:
        asset_id = str(uuid.uuid4())
        
        asset_item = {
            'id': asset_id,
            'title': asset_data['title'],
            'description': asset_data.get('description', ''),
            'type': asset_data['type'],
            'format': asset_data['format'],
            'file_size': asset_data['file_size'],
            'url': asset_data['url'],
            's3_key': asset_data.get('s3_key', ''),
            'tags': asset_data.get('tags', []),
            'category': asset_data['category'],
            'created_by': user_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'status': 'active',
            'usage_count': 0,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        ASSETS_TABLE.put_item(Item=asset_item)
        
        # Send analytics event
        send_analytics_event('asset_created', {
            'asset_id': asset_id,
            'user_id': user_id,
            'asset_type': asset_data['type'],
            'category': asset_data['category']
        })
        
        return create_response(201, {
            'success': True,
            'asset': asset_item,
            'message': 'Asset created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating asset: {str(e)}")
        return create_response(500, {'error': 'Failed to create asset'})

def handle_analytics_request(method, path, path_params, query_params, body, user_id):
    """Handle analytics-related requests"""
    try:
        if method == 'GET':
            if path == '/analytics/dashboard':
                return get_dashboard_analytics(query_params, user_id)
            elif path == '/analytics/campaigns':
                return get_campaign_analytics(query_params, user_id)
            elif path == '/analytics/realtime':
                return get_realtime_analytics(user_id)
        
        return create_response(404, {'error': 'Analytics endpoint not found'})
        
    except Exception as e:
        logger.error(f"Error in handle_analytics_request: {str(e)}")
        return create_response(500, {'error': 'Analytics request failed'})

def get_dashboard_analytics(query_params, user_id):
    """Get dashboard analytics data"""
    try:
        # Mock analytics data - In production, this would aggregate from Kinesis/DynamoDB
        analytics_data = {
            'overview': {
                'total_impressions': 12450000,
                'total_clicks': 42560,
                'total_reach': 8950000,
                'total_spend': 156780,
                'average_ctr': 0.34,
                'active_campaigns': 8
            },
            'trends': generate_trend_data(),
            'platforms': generate_platform_data(),
            'locations': generate_location_data()
        }
        
        return create_response(200, {
            'success': True,
            'data': analytics_data
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {str(e)}")
        return create_response(500, {'error': 'Failed to get analytics'})

def send_analytics_event(event_type, data):
    """Send event to Kinesis analytics stream"""
    try:
        event_data = {
            'event_type': event_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': data
        }
        
        kinesis_client.put_record(
            StreamName=ANALYTICS_STREAM,
            Data=json.dumps(event_data),
            PartitionKey=data.get('user_id', 'default')
        )
        
    except Exception as e:
        logger.error(f"Error sending analytics event: {str(e)}")

def generate_trend_data():
    """Generate mock trend data"""
    import random
    
    trends = {
        'impressions': [],
        'clicks': []
    }
    
    for i in range(7):
        date = (datetime.now(timezone.utc) - timedelta(days=6-i)).strftime('%Y-%m-%d')
        trends['impressions'].append({
            'date': date,
            'value': random.randint(1500000, 2500000)
        })
        trends['clicks'].append({
            'date': date,
            'value': random.randint(5000, 8000)
        })
    
    return trends

def generate_platform_data():
    """Generate mock platform performance data"""
    return [
        {'name': 'Vistar Media', 'impressions': 3250000, 'spend': 45230, 'share': 26.1},
        {'name': 'Hivestack', 'impressions': 2890000, 'spend': 38940, 'share': 23.2},
        {'name': 'The Trade Desk', 'impressions': 2650000, 'spend': 41250, 'share': 21.3},
        {'name': 'Broadsign', 'impressions': 2100000, 'spend': 22180, 'share': 16.9},
        {'name': 'VIOOH', 'impressions': 1560000, 'spend': 9180, 'share': 12.5}
    ]

def generate_location_data():
    """Generate mock location performance data"""
    return [
        {'city': 'New York', 'state': 'NY', 'impressions': 2450000, 'footfall': 45600, 'spend': 32100},
        {'city': 'Los Angeles', 'state': 'CA', 'impressions': 2120000, 'footfall': 38900, 'spend': 28740},
        {'city': 'Chicago', 'state': 'IL', 'impressions': 1890000, 'footfall': 32100, 'spend': 25200},
        {'city': 'Miami', 'state': 'FL', 'impressions': 1650000, 'footfall': 28700, 'spend': 22150},
        {'city': 'Atlanta', 'state': 'GA', 'impressions': 1480000, 'footfall': 24200, 'spend': 19800}
    ]

def convert_decimals(obj):
    """Convert DynamoDB Decimal objects to float for JSON serialization"""
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def create_response(status_code, body):
    """Create HTTP response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }

# For local testing
if __name__ == '__main__':
    # Mock event for testing
    test_event = {
        'httpMethod': 'GET',
        'path': '/campaigns',
        'queryStringParameters': {},
        'body': None,
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'test-user-id'
                }
            }
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))