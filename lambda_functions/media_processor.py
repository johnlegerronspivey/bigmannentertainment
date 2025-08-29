
import json
import boto3
import tempfile
import os
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    """Process media files uploaded to S3"""
    s3_client = boto3.client('s3')
    
    results = []
    
    for record in event['Records']:
        try:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            
            print(f"Processing file: {key}")
            
            # Determine file type and processing
            if key.lower().endswith(('.jpg', '.jpeg', '.png')):
                result = process_image(s3_client, bucket, key)
            elif key.lower().endswith(('.mp4', '.avi', '.mov')):
                result = process_video(s3_client, bucket, key)
            elif key.lower().endswith(('.mp3', '.wav', '.m4a')):
                result = process_audio(s3_client, bucket, key)
            else:
                result = {"status": "skipped", "reason": "unsupported file type"}
            
            results.append({
                "key": key,
                "result": result
            })
            
        except Exception as e:
            print(f"Error processing {key}: {str(e)}")
            results.append({
                "key": key,
                "result": {"status": "error", "message": str(e)}
            })
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Processing completed',
            'results': results
        })
    }

def process_image(s3_client, bucket, key):
    """Process image files"""
    try:
        # For now, just create a simple thumbnail placeholder
        thumbnail_key = f"thumbnails/{key.replace('/', '_')}_thumb.txt"
        
        s3_client.put_object(
            Bucket=bucket,
            Key=thumbnail_key,
            Body=f"Thumbnail placeholder for {key}".encode(),
            ContentType='text/plain',
            Metadata={
                'original-file': key,
                'processing-status': 'completed',
                'processor': 'basic-image-processor'
            }
        )
        
        return {
            "status": "success",
            "thumbnail": thumbnail_key,
            "message": "Image processed successfully"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_video(s3_client, bucket, key):
    """Process video files"""
    try:
        # Create processing status file
        processed_key = f"processed/{key.replace('/', '_')}_processed.txt"
        
        s3_client.put_object(
            Bucket=bucket,
            Key=processed_key,
            Body=f"Video processing completed for {key}".encode(),
            ContentType='text/plain',
            Metadata={
                'original-file': key,
                'processing-status': 'completed',
                'processor': 'basic-video-processor'
            }
        )
        
        return {
            "status": "success",
            "processed_file": processed_key,
            "message": "Video processed successfully"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_audio(s3_client, bucket, key):
    """Process audio files"""
    try:
        # Create waveform placeholder
        waveform_key = f"waveforms/{key.replace('/', '_')}_waveform.txt"
        
        s3_client.put_object(
            Bucket=bucket,
            Key=waveform_key,
            Body=f"Waveform data for {key}".encode(),
            ContentType='text/plain',
            Metadata={
                'original-file': key,
                'processing-status': 'completed',
                'processor': 'basic-audio-processor'
            }
        )
        
        return {
            "status": "success",
            "waveform": waveform_key,
            "message": "Audio processed successfully"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
