#!/usr/bin/env python3
"""
AWS Lambda Runtime Update Script
Updates Lambda functions from Node.js 20.x to the newest version
Includes backup and rollback capabilities
"""

import boto3
import json
from datetime import datetime
from typing import List, Dict, Any
import time

# Configuration
AWS_REGION = "us-east-2"
TARGET_RUNTIME = "nodejs22.x"  # Latest stable Node.js runtime
BACKUP_FILE = f"lambda-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"

# Lambda function ARNs to update
LAMBDA_FUNCTIONS = [
    "arn:aws:lambda:us-east-2:314108682794:function:amplify-login-create-auth-challenge-ec5da3fb",
    "arn:aws:lambda:us-east-2:314108682794:function:amplify-login-custom-message-ec5da3fb",
    "arn:aws:lambda:us-east-2:314108682794:function:amplify-login-define-auth-challenge-ec5da3fb",
    "arn:aws:lambda:us-east-2:314108682794:function:amplify-login-verify-auth-challenge-ec5da3fb"
]

# Initialize AWS clients
lambda_client = boto3.client('lambda', region_name=AWS_REGION)
cloudwatch_client = boto3.client('cloudwatch', region_name=AWS_REGION)


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(message: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.RESET}")


def extract_function_name(arn: str) -> str:
    """Extract function name from ARN"""
    return arn.split(':')[-1]


def get_function_config(function_name: str) -> Dict[str, Any]:
    """Get current Lambda function configuration"""
    try:
        response = lambda_client.get_function_configuration(
            FunctionName=function_name
        )
        return response
    except Exception as e:
        print_error(f"Failed to get config for {function_name}: {str(e)}")
        return None


def backup_function_configs(function_names: List[str]) -> Dict[str, Any]:
    """Backup all function configurations"""
    print_header("BACKING UP FUNCTION CONFIGURATIONS")
    
    backup_data = {
        "timestamp": datetime.now().isoformat(),
        "region": AWS_REGION,
        "functions": {}
    }
    
    for function_name in function_names:
        print_info(f"Backing up: {function_name}")
        config = get_function_config(function_name)
        
        if config:
            backup_data["functions"][function_name] = {
                "runtime": config.get("Runtime"),
                "handler": config.get("Handler"),
                "timeout": config.get("Timeout"),
                "memory_size": config.get("MemorySize"),
                "environment": config.get("Environment", {}),
                "description": config.get("Description"),
                "role": config.get("Role"),
                "layers": config.get("Layers", []),
                "vpc_config": config.get("VpcConfig", {}),
                "revision_id": config.get("RevisionId")
            }
            print_success(f"Backed up: {function_name} (Runtime: {config.get('Runtime')})")
        else:
            print_error(f"Failed to backup: {function_name}")
    
    # Save backup to file
    with open(BACKUP_FILE, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print_success(f"Backup saved to: {BACKUP_FILE}")
    return backup_data


def check_runtime_compatibility(current_runtime: str, target_runtime: str) -> bool:
    """Check if runtime update is compatible"""
    if not current_runtime.startswith('nodejs'):
        print_warning(f"Function is not using Node.js runtime: {current_runtime}")
        return False
    
    # Extract version numbers
    current_version = current_runtime.replace('nodejs', '').replace('.x', '')
    target_version = target_runtime.replace('nodejs', '').replace('.x', '')
    
    try:
        current_ver = int(current_version)
        target_ver = int(target_version)
        
        if target_ver < current_ver:
            print_warning(f"Target runtime ({target_runtime}) is older than current ({current_runtime})")
            return False
        
        return True
    except ValueError:
        print_warning(f"Unable to parse runtime versions: {current_runtime} -> {target_runtime}")
        return False


def update_function_runtime(function_name: str, target_runtime: str) -> bool:
    """Update Lambda function runtime"""
    try:
        print_info(f"Updating runtime for: {function_name}")
        
        # Get current config
        current_config = get_function_config(function_name)
        if not current_config:
            return False
        
        current_runtime = current_config.get('Runtime')
        print_info(f"Current runtime: {current_runtime}")
        print_info(f"Target runtime: {target_runtime}")
        
        # Check compatibility
        if not check_runtime_compatibility(current_runtime, target_runtime):
            print_error("Runtime update not compatible")
            return False
        
        # Update runtime
        response = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Runtime=target_runtime
        )
        
        # Wait for update to complete
        print_info("Waiting for update to complete...")
        time.sleep(5)
        
        # Verify update
        updated_config = get_function_config(function_name)
        if updated_config and updated_config.get('Runtime') == target_runtime:
            print_success(f"Successfully updated to {target_runtime}")
            return True
        else:
            print_error("Runtime update verification failed")
            return False
            
    except Exception as e:
        print_error(f"Failed to update {function_name}: {str(e)}")
        return False


def test_function(function_name: str) -> bool:
    """Test Lambda function after update"""
    try:
        print_info(f"Testing function: {function_name}")
        
        # For auth challenge functions, we'll just check if they're in active state
        config = get_function_config(function_name)
        
        if config and config.get('State') == 'Active':
            print_success(f"Function is active and ready")
            return True
        else:
            print_warning(f"Function state: {config.get('State') if config else 'Unknown'}")
            return False
            
    except Exception as e:
        print_error(f"Test failed for {function_name}: {str(e)}")
        return False


def get_function_metrics(function_name: str) -> Dict[str, Any]:
    """Get CloudWatch metrics for function"""
    try:
        end_time = datetime.now()
        start_time = datetime.fromtimestamp(end_time.timestamp() - 3600)  # Last hour
        
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Errors',
            Dimensions=[
                {'Name': 'FunctionName', 'Value': function_name}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Sum']
        )
        
        return response
    except Exception as e:
        print_warning(f"Could not fetch metrics: {str(e)}")
        return {}


def rollback_function(function_name: str, backup_data: Dict[str, Any]) -> bool:
    """Rollback function to previous runtime"""
    try:
        print_warning(f"Rolling back: {function_name}")
        
        function_backup = backup_data["functions"].get(function_name)
        if not function_backup:
            print_error(f"No backup found for {function_name}")
            return False
        
        response = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Runtime=function_backup["runtime"]
        )
        
        time.sleep(5)
        
        # Verify rollback
        config = get_function_config(function_name)
        if config and config.get('Runtime') == function_backup["runtime"]:
            print_success(f"Rolled back to {function_backup['runtime']}")
            return True
        else:
            print_error("Rollback verification failed")
            return False
            
    except Exception as e:
        print_error(f"Rollback failed for {function_name}: {str(e)}")
        return False


def main():
    """Main execution function"""
    print_header("AWS LAMBDA RUNTIME UPDATE SCRIPT")
    
    print(f"{Colors.BOLD}Configuration:{Colors.RESET}")
    print(f"  Region: {AWS_REGION}")
    print(f"  Target Runtime: {TARGET_RUNTIME}")
    print(f"  Functions to update: {len(LAMBDA_FUNCTIONS)}")
    print()
    
    # Extract function names
    function_names = [extract_function_name(arn) for arn in LAMBDA_FUNCTIONS]
    
    # Display functions
    print(f"{Colors.BOLD}Functions:{Colors.RESET}")
    for i, name in enumerate(function_names, 1):
        print(f"  {i}. {name}")
    print()
    
    # Confirmation
    confirm = input(f"{Colors.YELLOW}Proceed with update? (yes/no): {Colors.RESET}")
    if confirm.lower() != 'yes':
        print_warning("Update cancelled by user")
        return
    
    # Step 1: Backup configurations
    backup_data = backup_function_configs(function_names)
    
    # Step 2: Update runtimes
    print_header("UPDATING LAMBDA RUNTIMES")
    
    update_results = {}
    for function_name in function_names:
        success = update_function_runtime(function_name, TARGET_RUNTIME)
        update_results[function_name] = success
        print()
    
    # Step 3: Test functions
    print_header("TESTING UPDATED FUNCTIONS")
    
    test_results = {}
    for function_name in function_names:
        if update_results.get(function_name):
            success = test_function(function_name)
            test_results[function_name] = success
        else:
            test_results[function_name] = False
            print_warning(f"Skipping test for {function_name} (update failed)")
        print()
    
    # Step 4: Results summary
    print_header("UPDATE SUMMARY")
    
    successful_updates = sum(1 for v in update_results.values() if v)
    successful_tests = sum(1 for v in test_results.values() if v)
    
    print(f"{Colors.BOLD}Statistics:{Colors.RESET}")
    print(f"  Total functions: {len(function_names)}")
    print(f"  Successful updates: {successful_updates}")
    print(f"  Successful tests: {successful_tests}")
    print()
    
    print(f"{Colors.BOLD}Detailed Results:{Colors.RESET}")
    for function_name in function_names:
        update_status = "✓" if update_results.get(function_name) else "✗"
        test_status = "✓" if test_results.get(function_name) else "✗"
        
        status_color = Colors.GREEN if (update_results.get(function_name) and test_results.get(function_name)) else Colors.RED
        
        print(f"{status_color}  {function_name}{Colors.RESET}")
        print(f"    Update: {update_status}  Test: {test_status}")
    
    print()
    
    # Rollback option if there are failures
    if successful_updates < len(function_names) or successful_tests < len(function_names):
        print_warning("Some functions failed to update or test")
        rollback = input(f"{Colors.YELLOW}Rollback all functions? (yes/no): {Colors.RESET}")
        
        if rollback.lower() == 'yes':
            print_header("ROLLING BACK FUNCTIONS")
            for function_name in function_names:
                rollback_function(function_name, backup_data)
                print()
    
    print_header("UPDATE COMPLETE")
    print_info(f"Backup file: {BACKUP_FILE}")
    print_info("Keep this backup file for manual rollback if needed")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nUpdate cancelled by user")
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
