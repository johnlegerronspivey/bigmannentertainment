
import json
import boto3
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    """Moderate content using Rekognition"""
    rekognition_client = boto3.client('rekognition')
    s3_client = boto3.client('s3')
    
    results = []
    
    for record in event['Records']:
        try:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            
            print(f"Moderating content: {key}")
            
            # Only process image files for moderation
            if key.lower().endswith(('.jpg', '.jpeg', '.png')):
                result = moderate_image(rekognition_client, s3_client, bucket, key)
            else:
                result = {"status": "skipped", "reason": "content moderation only for images"}
            
            results.append({
                "key": key,
                "result": result
            })
            
        except Exception as e:
            print(f"Error moderating {key}: {str(e)}")
            results.append({
                "key": key,
                "result": {"status": "error", "message": str(e)}
            })
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Content moderation completed',
            'results': results
        })
    }

def moderate_image(rekognition_client, s3_client, bucket, key):
    """Moderate image content using Rekognition"""
    try:
        # Perform content moderation
        response = rekognition_client.detect_moderation_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MinConfidence=60.0
        )
        
        moderation_labels = response.get('ModerationLabels', [])
        
        # Determine if content is flagged
        flagged = len(moderation_labels) > 0
        max_confidence = max([label['Confidence'] for label in moderation_labels]) if moderation_labels else 0
        
        # Move content based on moderation result
        if flagged:
            new_key = f"quarantine/{key}"
            status = 'QUARANTINED'
        else:
            new_key = f"approved/{key}"
            status = 'APPROVED'
        
        # Copy to new location
        s3_client.copy_object(
            CopySource={'Bucket': bucket, 'Key': key},
            Bucket=bucket,
            Key=new_key,
            MetadataDirective='REPLACE',
            Metadata={
                'moderation-status': status,
                'max-confidence': str(max_confidence),
                'flagged-labels': str(len(moderation_labels))
            }
        )
        
        return {
            "status": "success",
            "moderation_status": status,
            "flagged": flagged,
            "labels": moderation_labels,
            "max_confidence": max_confidence,
            "new_location": new_key
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
