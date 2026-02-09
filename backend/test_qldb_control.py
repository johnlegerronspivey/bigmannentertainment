import boto3
import sys

try:
    client = boto3.client('qldb', region_name='us-east-1')
    response = client.list_ledgers()
    print(f"QLDB List Ledgers Successful: {response['Ledgers']}")
except Exception as e:
    print(f"QLDB Connection Failed: {e}")
    sys.exit(1)
