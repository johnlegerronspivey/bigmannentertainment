import boto3
import requests
import sys

def fix_rds_access():
    print("--- Attempting to Fix RDS Access ---")
    
    # 1. Get Public IP
    try:
        my_ip = requests.get('https://checkip.amazonaws.com').text.strip()
        print(f"Container IP: {my_ip}")
    except Exception as e:
        print(f"Failed to get IP: {e}")
        return

    # 2. Connect to AWS
    try:
        rds = boto3.client('rds', region_name='us-east-1')
        ec2 = boto3.client('ec2', region_name='us-east-1')
    except Exception as e:
        print(f"Failed to connect to AWS: {e}")
        return

    # 3. Find RDS Instance
    try:
        instances = rds.describe_db_instances()
        target_db = None
        for db in instances['DBInstances']:
            if 'bigmann-profiles-db' in db['DBInstanceIdentifier']:
                target_db = db
                break
        
        if not target_db:
            print("❌ Could not find RDS instance 'bigmann-profiles-db'")
            return

        print(f"Found RDS: {target_db['DBInstanceIdentifier']}")
        
        # 4. Get Security Groups
        sg_ids = [sg['VpcSecurityGroupId'] for sg in target_db['VpcSecurityGroups']]
        print(f"Security Groups: {sg_ids}")

        if not sg_ids:
            print("No Security Groups attached to RDS.")
            return

        # 5. Add Inbound Rule to the first SG
        sg_id = sg_ids[0]
        print(f"Attempting to add rule to SG: {sg_id}")
        
        try:
            ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 5432,
                        'ToPort': 5432,
                        'IpRanges': [{'CidrIp': f'{my_ip}/32', 'Description': 'Emergent Container Access'}]
                    }
                ]
            )
            print(f"✅ Successfully authorized {my_ip} on port 5432 for {sg_id}")
        except ec2.exceptions.ClientError as e:
            if 'InvalidPermission.Duplicate' in str(e):
                print(f"✅ IP {my_ip} is already authorized.")
            else:
                print(f"❌ Failed to authorize ingress: {e}")

    except Exception as e:
        print(f"❌ Error during AWS operations: {e}")

if __name__ == "__main__":
    fix_rds_access()
