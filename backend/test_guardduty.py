import boto3
import sys

try:
    client = boto3.client('guardduty', region_name='us-east-1')
    response = client.list_detectors()
    print(f"GuardDuty Connection Successful: {response['DetectorIds']}")
except Exception as e:
    print(f"GuardDuty Connection Failed: {e}")
    sys.exit(1)
