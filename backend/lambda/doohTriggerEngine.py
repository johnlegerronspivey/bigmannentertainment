import json
import boto3
import uuid
import requests
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import logging
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
eventbridge_client = boto3.client('events')

# DynamoDB Tables
TRIGGERS_TABLE = dynamodb.Table('BME-DOOH-Triggers')
CAMPAIGNS_TABLE = dynamodb.Table('BME-DOOH-Campaigns')

# Environment variables for external APIs
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'demo_key')
ESPN_API_KEY = os.getenv('ESPN_API_KEY', 'demo_key')
EVENTBRITE_API_KEY = os.getenv('EVENTBRITE_API_KEY', 'demo_key')

def lambda_handler(event, context):
    """
    Main handler for DOOH Trigger Engine Lambda function
    """
    try:
        # Determine if this is an API Gateway request or EventBridge trigger
        if 'source' in event and event['source'] == 'aws.events':
            # This is a scheduled EventBridge trigger
            return handle_scheduled_trigger_evaluation(event, context)
        else:
            # This is an API Gateway request
            return handle_api_request(event, context)
            
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def handle_api_request(event, context):
    """Handle API Gateway requests for trigger management"""
    try:
        http_method = event.get('httpMethod')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        
        # Get user information
        user_id = get_user_id_from_context(event)
        if not user_id:
            return create_response(401, {'error': 'Unauthorized'})
        
        # Route the request
        if path.startswith('/triggers'):
            return handle_triggers_request(http_method, path, path_parameters, query_parameters, body, user_id)
        elif path.startswith('/weather'):
            return handle_weather_request(query_parameters, user_id)
        elif path.startswith('/sports'):
            return handle_sports_request(query_parameters, user_id)
        elif path.startswith('/events'):
            return handle_events_request(query_parameters, user_id)
        else:
            return create_response(404, {'error': 'Not found'})
            
    except Exception as e:
        logger.error(f"Error in handle_api_request: {str(e)}")
        return create_response(500, {'error': 'API request failed'})

def handle_scheduled_trigger_evaluation(event, context):
    """Handle scheduled trigger evaluation from EventBridge"""
    try:
        logger.info("Starting scheduled trigger evaluation")
        
        # Get all active triggers
        response = TRIGGERS_TABLE.scan(
            FilterExpression='is_active = :active',
            ExpressionAttributeValues={':active': True}
        )
        
        active_triggers = response.get('Items', [])
        logger.info(f"Found {len(active_triggers)} active triggers")
        
        evaluation_results = []
        
        for trigger in active_triggers:
            try:
                result = await evaluate_trigger(trigger)
                evaluation_results.append(result)
                
                if result['triggered']:
                    # Execute trigger actions
                    await execute_trigger_actions(trigger, result)
                    
            except Exception as e:
                logger.error(f"Error evaluating trigger {trigger['id']}: {str(e)}")
        
        logger.info(f"Completed trigger evaluation. Results: {len(evaluation_results)} triggers processed")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'triggers_evaluated': len(evaluation_results),
                'triggers_activated': len([r for r in evaluation_results if r['triggered']])
            })
        }
        
    except Exception as e:
        logger.error(f"Error in scheduled trigger evaluation: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

def handle_triggers_request(method, path, path_params, query_params, body, user_id):
    """Handle trigger-related API requests"""
    try:
        if method == 'GET':
            if path == '/triggers':
                return get_triggers(query_params, user_id)
            elif 'triggerId' in path_params:
                return get_trigger(path_params['triggerId'], user_id)
        
        elif method == 'POST':
            if path == '/triggers':
                return create_trigger(body, user_id)
            elif path.endswith('/test'):
                return test_trigger(path_params['triggerId'], user_id)
        
        elif method == 'PUT':
            if 'triggerId' in path_params:
                return update_trigger(path_params['triggerId'], body, user_id)
        
        elif method == 'DELETE':
            if 'triggerId' in path_params:
                return delete_trigger(path_params['triggerId'], user_id)
        
        return create_response(404, {'error': 'Trigger endpoint not found'})
        
    except Exception as e:
        logger.error(f"Error in handle_triggers_request: {str(e)}")
        return create_response(500, {'error': 'Trigger request failed'})

def get_triggers(query_params, user_id):
    """Get triggers for a user"""
    try:
        # In a real application, you might want to filter by user or allow admins to see all
        response = TRIGGERS_TABLE.scan()
        triggers = response.get('Items', [])
        triggers = convert_decimals(triggers)
        
        return create_response(200, {
            'success': True,
            'triggers': triggers,
            'total_count': len(triggers)
        })
        
    except Exception as e:
        logger.error(f"Error getting triggers: {str(e)}")
        return create_response(500, {'error': 'Failed to get triggers'})

def create_trigger(trigger_data, user_id):
    """Create a new trigger"""
    try:
        trigger_id = str(uuid.uuid4())
        
        trigger_item = {
            'id': trigger_id,
            'name': trigger_data['name'],
            'description': trigger_data.get('description', ''),
            'type': trigger_data['type'],
            'conditions': trigger_data['conditions'],
            'actions': trigger_data['actions'],
            'priority': trigger_data.get('priority', 1),
            'is_active': trigger_data.get('isActive', True),
            'campaigns': trigger_data.get('campaigns', []),
            'created_by': user_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'trigger_count': 0,
            'last_triggered': None,
            'schedule': trigger_data.get('schedule', {})
        }
        
        TRIGGERS_TABLE.put_item(Item=trigger_item)
        
        return create_response(201, {
            'success': True,
            'trigger': convert_decimals(trigger_item),
            'message': 'Trigger created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating trigger: {str(e)}")
        return create_response(500, {'error': 'Failed to create trigger'})

def test_trigger(trigger_id, user_id):
    """Test a trigger manually"""
    try:
        # Get trigger
        response = TRIGGERS_TABLE.get_item(Key={'id': trigger_id})
        trigger = response.get('Item')
        
        if not trigger:
            return create_response(404, {'error': 'Trigger not found'})
        
        # Evaluate trigger
        result = evaluate_trigger_sync(trigger)
        
        return create_response(200, {
            'success': True,
            'result': result,
            'message': 'Trigger test completed'
        })
        
    except Exception as e:
        logger.error(f"Error testing trigger: {str(e)}")
        return create_response(500, {'error': 'Failed to test trigger'})

def handle_weather_request(query_params, user_id):
    """Handle weather data requests"""
    try:
        latitude = float(query_params.get('latitude', 0))
        longitude = float(query_params.get('longitude', 0))
        location_name = query_params.get('location_name', '')
        
        weather_data = get_weather_data(latitude, longitude, location_name)
        
        return create_response(200, {
            'success': True,
            'weather_data': weather_data
        })
        
    except Exception as e:
        logger.error(f"Error getting weather data: {str(e)}")
        return create_response(500, {'error': 'Failed to get weather data'})

def handle_sports_request(query_params, user_id):
    """Handle sports events requests"""
    try:
        location = query_params.get('location', '')
        date = query_params.get('date')
        
        if date:
            date = datetime.fromisoformat(date)
        else:
            date = datetime.now(timezone.utc)
        
        sports_events = get_sports_events(location, date)
        
        return create_response(200, {
            'success': True,
            'sports_events': sports_events,
            'events_count': len(sports_events)
        })
        
    except Exception as e:
        logger.error(f"Error getting sports events: {str(e)}")
        return create_response(500, {'error': 'Failed to get sports events'})

def handle_events_request(query_params, user_id):
    """Handle local events requests"""
    try:
        location = query_params.get('location', '')
        radius_km = int(query_params.get('radius_km', 25))
        date = query_params.get('date')
        
        if date:
            date = datetime.fromisoformat(date)
        else:
            date = datetime.now(timezone.utc)
        
        local_events = get_local_events(location, radius_km, date)
        
        return create_response(200, {
            'success': True,
            'local_events': local_events,
            'events_count': len(local_events)
        })
        
    except Exception as e:
        logger.error(f"Error getting local events: {str(e)}")
        return create_response(500, {'error': 'Failed to get local events'})

def get_weather_data(latitude, longitude, location_name):
    """Get weather data from OpenWeatherMap API"""
    try:
        if OPENWEATHER_API_KEY == 'demo_key':
            # Return mock data for demo
            import random
            conditions = ['sunny', 'cloudy', 'rainy', 'snowy', 'stormy']
            return {
                'location': location_name or f"Location {latitude:.2f},{longitude:.2f}",
                'latitude': latitude,
                'longitude': longitude,
                'temperature': round(random.uniform(10, 30), 1),
                'condition': random.choice(conditions),
                'humidity': round(random.uniform(30, 90), 1),
                'wind_speed': round(random.uniform(0, 25), 1),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        # Real API call would go here
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        return {
            'location': data.get('name', location_name),
            'latitude': latitude,
            'longitude': longitude,
            'temperature': data['main']['temp'],
            'condition': data['weather'][0]['main'].lower(),
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'] * 3.6,  # Convert m/s to km/h
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting weather data: {str(e)}")
        # Return default data
        return {
            'location': location_name or 'Unknown Location',
            'latitude': latitude,
            'longitude': longitude,
            'temperature': 20.0,
            'condition': 'sunny',
            'humidity': 50.0,
            'wind_speed': 5.0,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

def get_sports_events(location, date):
    """Get sports events from ESPN API or similar"""
    try:
        # Mock data for demo
        import random
        
        sports = ['football', 'basketball', 'baseball', 'hockey', 'soccer']
        events = []
        
        num_events = random.randint(0, 3)
        for i in range(num_events):
            sport = random.choice(sports)
            teams = [f"Team {random.randint(1, 20)}", f"Team {random.randint(1, 20)}"]
            
            event = {
                'event_id': f"event_{uuid.uuid4().hex[:8]}",
                'sport': sport,
                'teams': teams,
                'venue': f"{location} {sport.title()} Arena",
                'start_time': (date + timedelta(hours=random.randint(12, 22))).isoformat(),
                'status': random.choice(['scheduled', 'live', 'completed']),
                'score': {teams[0]: random.randint(0, 5), teams[1]: random.randint(0, 5)} if random.choice([True, False]) else None,
                'location': location,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            events.append(event)
        
        return events
        
    except Exception as e:
        logger.error(f"Error getting sports events: {str(e)}")
        return []

def get_local_events(location, radius_km, date):
    """Get local events from Eventbrite API or similar"""
    try:
        # Mock data for demo
        import random
        
        event_types = ['concert', 'festival', 'conference', 'exhibition', 'sports_game']
        events = []
        
        num_events = random.randint(1, 5)
        for i in range(num_events):
            event_type = random.choice(event_types)
            start_time = date + timedelta(hours=random.randint(6, 48))
            duration_hours = random.randint(2, 12)
            
            event = {
                'event_id': f"event_{uuid.uuid4().hex[:8]}",
                'name': f"{event_type.title()} Event {i+1}",
                'event_type': event_type,
                'location': f"{location} Event Center",
                'start_time': start_time.isoformat(),
                'end_time': (start_time + timedelta(hours=duration_hours)).isoformat(),
                'attendance_estimate': random.randint(100, 10000),
                'related_artists': [f"Artist {random.randint(1, 100)}" for _ in range(random.randint(0, 3))],
                'metadata': {
                    'price_range': f"${random.randint(10, 200)}-${random.randint(200, 500)}",
                    'age_restriction': random.choice(['All Ages', '18+', '21+']),
                    'genre': random.choice(['Pop', 'Rock', 'Hip-Hop', 'Electronic', 'Classical'])
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            events.append(event)
        
        return events
        
    except Exception as e:
        logger.error(f"Error getting local events: {str(e)}")
        return []

def evaluate_trigger_sync(trigger):
    """Synchronously evaluate a trigger (for testing)"""
    try:
        trigger_type = trigger['type']
        conditions = trigger['conditions']
        
        if trigger_type == 'weather':
            return evaluate_weather_trigger(conditions)
        elif trigger_type == 'sports':
            return evaluate_sports_trigger(conditions)
        elif trigger_type == 'time':
            return evaluate_time_trigger(conditions)
        elif trigger_type == 'location':
            return evaluate_location_trigger(conditions)
        else:
            return {
                'triggered': False,
                'message': f'Unknown trigger type: {trigger_type}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error evaluating trigger: {str(e)}")
        return {
            'triggered': False,
            'message': f'Error evaluating trigger: {str(e)}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

def evaluate_weather_trigger(conditions):
    """Evaluate weather-based trigger conditions"""
    try:
        # Get current weather for default location (NYC)
        weather = get_weather_data(40.7580, -73.9855, "New York City")
        
        triggered = True
        reasons = []
        
        for condition, criteria in conditions.items():
            if condition == 'temperature':
                operator = criteria.get('operator', '>')
                value = criteria.get('value', 25)
                
                if operator == '>' and weather['temperature'] <= value:
                    triggered = False
                elif operator == '<' and weather['temperature'] >= value:
                    triggered = False
                elif operator == '=' and weather['temperature'] != value:
                    triggered = False
                    
                reasons.append(f"Temperature {weather['temperature']}°C {operator} {value}°C")
            
            elif condition == 'condition':
                expected = criteria.get('value', 'sunny')
                if weather['condition'] != expected:
                    triggered = False
                reasons.append(f"Weather condition is {weather['condition']}, expected {expected}")
        
        return {
            'triggered': triggered,
            'message': f"Weather trigger evaluation: {', '.join(reasons)}",
            'weather_data': weather,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            'triggered': False,
            'message': f'Weather trigger evaluation failed: {str(e)}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

def evaluate_sports_trigger(conditions):
    """Evaluate sports-based trigger conditions"""
    try:
        # Get sports events for default location
        events = get_sports_events("New York", datetime.now(timezone.utc))
        
        triggered = False
        matching_events = []
        
        for event in events:
            match = True
            for condition, criteria in conditions.items():
                if condition == 'eventType' and event['sport'] != criteria.get('value'):
                    match = False
                elif condition == 'eventStatus' and event['status'] != criteria.get('value'):
                    match = False
            
            if match:
                triggered = True
                matching_events.append(event)
        
        return {
            'triggered': triggered,
            'message': f"Found {len(matching_events)} matching sports events",
            'matching_events': matching_events,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            'triggered': False,
            'message': f'Sports trigger evaluation failed: {str(e)}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

def evaluate_time_trigger(conditions):
    """Evaluate time-based trigger conditions"""
    try:
        now = datetime.now(timezone.utc)
        triggered = True
        reasons = []
        
        for condition, criteria in conditions.items():
            if condition == 'timeRange':
                start_hour = criteria.get('start', 0)
                end_hour = criteria.get('end', 23)
                current_hour = now.hour
                
                if not (start_hour <= current_hour <= end_hour):
                    triggered = False
                reasons.append(f"Current hour {current_hour} in range {start_hour}-{end_hour}")
        
        return {
            'triggered': triggered,
            'message': f"Time trigger evaluation: {', '.join(reasons)}",
            'current_time': now.isoformat(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            'triggered': False,
            'message': f'Time trigger evaluation failed: {str(e)}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

def evaluate_location_trigger(conditions):
    """Evaluate location-based trigger conditions"""
    try:
        # Mock location data
        triggered = True
        reasons = ["Location trigger conditions met"]
        
        return {
            'triggered': triggered,
            'message': f"Location trigger evaluation: {', '.join(reasons)}",
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            'triggered': False,
            'message': f'Location trigger evaluation failed: {str(e)}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

async def execute_trigger_actions(trigger, evaluation_result):
    """Execute actions when a trigger is activated"""
    try:
        actions = trigger.get('actions', {})
        
        # Update trigger statistics
        TRIGGERS_TABLE.update_item(
            Key={'id': trigger['id']},
            UpdateExpression='SET trigger_count = trigger_count + :inc, last_triggered = :timestamp',
            ExpressionAttributeValues={
                ':inc': 1,
                ':timestamp': datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Execute each action
        for action_type, action_value in actions.items():
            if action_type == 'switchVariant':
                await switch_creative_variant(trigger, action_value)
            elif action_type == 'overlayText':
                await add_text_overlay(trigger, action_value)
            elif action_type == 'changeColor':
                await change_color_scheme(trigger, action_value)
        
        logger.info(f"Executed actions for trigger {trigger['id']}")
        
    except Exception as e:
        logger.error(f"Error executing trigger actions: {str(e)}")

async def switch_creative_variant(trigger, variant_name):
    """Switch creative variant for campaigns"""
    try:
        campaigns = trigger.get('campaigns', [])
        for campaign_id in campaigns:
            # Update campaign creative variant
            CAMPAIGNS_TABLE.update_item(
                Key={'id': campaign_id},
                UpdateExpression='SET current_variant = :variant, updated_at = :timestamp',
                ExpressionAttributeValues={
                    ':variant': variant_name,
                    ':timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
        
        logger.info(f"Switched to variant {variant_name} for {len(campaigns)} campaigns")
        
    except Exception as e:
        logger.error(f"Error switching creative variant: {str(e)}")

async def add_text_overlay(trigger, overlay_text):
    """Add text overlay to campaigns"""
    try:
        campaigns = trigger.get('campaigns', [])
        for campaign_id in campaigns:
            # Update campaign with overlay text
            CAMPAIGNS_TABLE.update_item(
                Key={'id': campaign_id},
                UpdateExpression='SET overlay_text = :text, updated_at = :timestamp',
                ExpressionAttributeValues={
                    ':text': overlay_text,
                    ':timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
        
        logger.info(f"Added overlay text '{overlay_text}' to {len(campaigns)} campaigns")
        
    except Exception as e:
        logger.error(f"Error adding text overlay: {str(e)}")

async def change_color_scheme(trigger, color_scheme):
    """Change color scheme for campaigns"""
    try:
        campaigns = trigger.get('campaigns', [])
        for campaign_id in campaigns:
            # Update campaign color scheme
            CAMPAIGNS_TABLE.update_item(
                Key={'id': campaign_id},
                UpdateExpression='SET color_scheme = :scheme, updated_at = :timestamp',
                ExpressionAttributeValues={
                    ':scheme': color_scheme,
                    ':timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
        
        logger.info(f"Changed color scheme to {color_scheme} for {len(campaigns)} campaigns")
        
    except Exception as e:
        logger.error(f"Error changing color scheme: {str(e)}")

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