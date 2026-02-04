import boto3
import os
import sys

def check_qldb():
    try:
        client = boto3.client(
            'qldb',
            region_name='us-east-1',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        print("Attempting to list ledgers...")
        response = client.list_ledgers()
        print("Success!")
        print(response)
    except Exception as e:
        print(f"Error: {e}")
        # Print detailed DNS info if possible
        import socket
        try:
            print(f"DNS Resolution for qldb.us-east-1.amazonaws.com: {socket.gethostbyname('qldb.us-east-1.amazonaws.com')}")
        except Exception as dns_e:
            print(f"DNS Resolution failed: {dns_e}")

if __name__ == "__main__":
    check_qldb()
