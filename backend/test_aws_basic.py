import boto3
import sys

try:
    sts = boto3.client('sts', region_name='us-east-1')
    id = sts.get_caller_identity()
    print(f"STS Connection Successful: {id['Arn']}")
except Exception as e:
    print(f"STS Connection Failed: {e}")
    sys.exit(1)
