#!/bin/bash
# AWS Lambda Runtime Update Script (Bash version)
# Updates Lambda functions to newest Node.js runtime

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
AWS_REGION="us-east-2"
TARGET_RUNTIME="nodejs22.x"
BACKUP_FILE="lambda-backup-$(date +%Y%m%d-%H%M%S).json"

# Lambda Functions
LAMBDA_FUNCTIONS=(
    "amplify-login-create-auth-challenge-ec5da3fb"
    "amplify-login-custom-message-ec5da3fb"
    "amplify-login-define-auth-challenge-ec5da3fb"
    "amplify-login-verify-auth-challenge-ec5da3fb"
)

# Helper functions
print_header() {
    echo -e "\n${BOLD}${BLUE}$(printf '=%.0s' {1..70})${NC}"
    echo -e "${BOLD}${BLUE}${1}${NC}"
    echo -e "${BOLD}${BLUE}$(printf '=%.0s' {1..70})${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Check AWS CLI installation
check_prerequisites() {
    print_header "CHECKING PREREQUISITES"
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install it first."
        exit 1
    fi
    print_success "AWS CLI installed"
    
    if ! command -v jq &> /dev/null; then
        print_error "jq not found. Please install it first."
        exit 1
    fi
    print_success "jq installed"
    
    # Verify AWS credentials
    if ! aws sts get-caller-identity --region $AWS_REGION &> /dev/null; then
        print_error "AWS credentials not configured or invalid"
        exit 1
    fi
    print_success "AWS credentials valid"
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_info "AWS Account: $ACCOUNT_ID"
    print_info "Region: $AWS_REGION"
}

# Get Lambda function configuration
get_function_config() {
    local function_name=$1
    aws lambda get-function-configuration \
        --function-name "$function_name" \
        --region "$AWS_REGION" 2>/dev/null
}

# Backup function configurations
backup_functions() {
    print_header "BACKING UP FUNCTION CONFIGURATIONS"
    
    echo "{" > "$BACKUP_FILE"
    echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"," >> "$BACKUP_FILE"
    echo "  \"region\": \"$AWS_REGION\"," >> "$BACKUP_FILE"
    echo "  \"functions\": {" >> "$BACKUP_FILE"
    
    local first=true
    for function_name in "${LAMBDA_FUNCTIONS[@]}"; do
        print_info "Backing up: $function_name"
        
        config=$(get_function_config "$function_name")
        
        if [ -n "$config" ]; then
            runtime=$(echo "$config" | jq -r '.Runtime')
            
            if [ "$first" = true ]; then
                first=false
            else
                echo "," >> "$BACKUP_FILE"
            fi
            
            echo "    \"$function_name\": {" >> "$BACKUP_FILE"
            echo "      \"runtime\": \"$runtime\"," >> "$BACKUP_FILE"
            echo "      \"handler\": $(echo "$config" | jq '.Handler')," >> "$BACKUP_FILE"
            echo "      \"timeout\": $(echo "$config" | jq '.Timeout')," >> "$BACKUP_FILE"
            echo "      \"memory_size\": $(echo "$config" | jq '.MemorySize')," >> "$BACKUP_FILE"
            echo "      \"revision_id\": $(echo "$config" | jq '.RevisionId')" >> "$BACKUP_FILE"
            echo -n "    }" >> "$BACKUP_FILE"
            
            print_success "Backed up: $function_name (Runtime: $runtime)"
        else
            print_error "Failed to backup: $function_name"
        fi
    done
    
    echo "" >> "$BACKUP_FILE"
    echo "  }" >> "$BACKUP_FILE"
    echo "}" >> "$BACKUP_FILE"
    
    print_success "Backup saved to: $BACKUP_FILE"
}

# Check available Node.js runtimes
check_available_runtimes() {
    print_info "Checking available Node.js runtimes..."
    
    # List of common Node.js runtimes
    runtimes=("nodejs22.x" "nodejs20.x" "nodejs18.x")
    
    print_info "Available Node.js runtimes:"
    for runtime in "${runtimes[@]}"; do
        echo "  - $runtime"
    done
    
    # Check if target runtime is supported
    if aws lambda list-functions --region "$AWS_REGION" \
        --query "Functions[?Runtime=='$TARGET_RUNTIME']" --output json | jq -e '. | length > 0' &> /dev/null; then
        print_success "Target runtime $TARGET_RUNTIME is supported"
    else
        print_warning "No functions currently using $TARGET_RUNTIME"
        print_info "This might indicate it's a new runtime. Proceeding anyway..."
    fi
}

# Update Lambda runtime
update_function_runtime() {
    local function_name=$1
    
    print_info "Updating: $function_name"
    
    # Get current runtime
    current_runtime=$(get_function_config "$function_name" | jq -r '.Runtime')
    print_info "Current runtime: $current_runtime"
    print_info "Target runtime: $TARGET_RUNTIME"
    
    # Check if already up to date
    if [ "$current_runtime" = "$TARGET_RUNTIME" ]; then
        print_success "Already using $TARGET_RUNTIME"
        return 0
    fi
    
    # Update runtime
    if aws lambda update-function-configuration \
        --function-name "$function_name" \
        --runtime "$TARGET_RUNTIME" \
        --region "$AWS_REGION" &> /dev/null; then
        
        # Wait for update to complete
        print_info "Waiting for update to complete..."
        sleep 5
        
        # Verify update
        new_runtime=$(get_function_config "$function_name" | jq -r '.Runtime')
        
        if [ "$new_runtime" = "$TARGET_RUNTIME" ]; then
            print_success "Successfully updated to $TARGET_RUNTIME"
            return 0
        else
            print_error "Runtime update verification failed"
            return 1
        fi
    else
        print_error "Failed to update runtime"
        return 1
    fi
}

# Test function after update
test_function() {
    local function_name=$1
    
    print_info "Testing: $function_name"
    
    # Get function state
    state=$(get_function_config "$function_name" | jq -r '.State')
    last_update_status=$(get_function_config "$function_name" | jq -r '.LastUpdateStatus')
    
    if [ "$state" = "Active" ] && [ "$last_update_status" = "Successful" ]; then
        print_success "Function is active and healthy"
        return 0
    else
        print_warning "Function state: $state, Last update: $last_update_status"
        return 1
    fi
}

# Rollback function
rollback_function() {
    local function_name=$1
    
    print_warning "Rolling back: $function_name"
    
    # Get original runtime from backup
    original_runtime=$(jq -r ".functions[\"$function_name\"].runtime" "$BACKUP_FILE")
    
    if [ "$original_runtime" != "null" ] && [ -n "$original_runtime" ]; then
        aws lambda update-function-configuration \
            --function-name "$function_name" \
            --runtime "$original_runtime" \
            --region "$AWS_REGION" &> /dev/null
        
        sleep 5
        
        new_runtime=$(get_function_config "$function_name" | jq -r '.Runtime')
        
        if [ "$new_runtime" = "$original_runtime" ]; then
            print_success "Rolled back to $original_runtime"
            return 0
        else
            print_error "Rollback verification failed"
            return 1
        fi
    else
        print_error "No backup found for $function_name"
        return 1
    fi
}

# Main execution
main() {
    print_header "AWS LAMBDA RUNTIME UPDATE SCRIPT"
    
    echo -e "${BOLD}Configuration:${NC}"
    echo "  Region: $AWS_REGION"
    echo "  Target Runtime: $TARGET_RUNTIME"
    echo "  Functions: ${#LAMBDA_FUNCTIONS[@]}"
    echo ""
    
    echo -e "${BOLD}Functions to update:${NC}"
    for i in "${!LAMBDA_FUNCTIONS[@]}"; do
        echo "  $((i+1)). ${LAMBDA_FUNCTIONS[$i]}"
    done
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Check available runtimes
    check_available_runtimes
    
    # Confirmation
    echo ""
    read -p "$(echo -e ${YELLOW})Proceed with update? (yes/no): $(echo -e ${NC})" confirm
    
    if [ "$confirm" != "yes" ]; then
        print_warning "Update cancelled by user"
        exit 0
    fi
    
    # Backup
    backup_functions
    
    # Update functions
    print_header "UPDATING LAMBDA RUNTIMES"
    
    declare -A update_results
    declare -A test_results
    
    for function_name in "${LAMBDA_FUNCTIONS[@]}"; do
        if update_function_runtime "$function_name"; then
            update_results["$function_name"]=1
        else
            update_results["$function_name"]=0
        fi
        echo ""
    done
    
    # Test functions
    print_header "TESTING UPDATED FUNCTIONS"
    
    for function_name in "${LAMBDA_FUNCTIONS[@]}"; do
        if [ "${update_results[$function_name]}" -eq 1 ]; then
            if test_function "$function_name"; then
                test_results["$function_name"]=1
            else
                test_results["$function_name"]=0
            fi
        else
            test_results["$function_name"]=0
            print_warning "Skipping test (update failed)"
        fi
        echo ""
    done
    
    # Summary
    print_header "UPDATE SUMMARY"
    
    successful_updates=0
    successful_tests=0
    
    for function_name in "${LAMBDA_FUNCTIONS[@]}"; do
        [ "${update_results[$function_name]}" -eq 1 ] && ((successful_updates++)) || true
        [ "${test_results[$function_name]}" -eq 1 ] && ((successful_tests++)) || true
    done
    
    echo -e "${BOLD}Statistics:${NC}"
    echo "  Total functions: ${#LAMBDA_FUNCTIONS[@]}"
    echo "  Successful updates: $successful_updates"
    echo "  Successful tests: $successful_tests"
    echo ""
    
    echo -e "${BOLD}Detailed Results:${NC}"
    for function_name in "${LAMBDA_FUNCTIONS[@]}"; do
        update_status="✗"
        test_status="✗"
        color=$RED
        
        [ "${update_results[$function_name]}" -eq 1 ] && update_status="✓"
        [ "${test_results[$function_name]}" -eq 1 ] && test_status="✓"
        
        if [ "${update_results[$function_name]}" -eq 1 ] && [ "${test_results[$function_name]}" -eq 1 ]; then
            color=$GREEN
        fi
        
        echo -e "${color}  $function_name${NC}"
        echo "    Update: $update_status  Test: $test_status"
    done
    
    echo ""
    
    # Rollback option
    if [ $successful_updates -lt ${#LAMBDA_FUNCTIONS[@]} ] || [ $successful_tests -lt ${#LAMBDA_FUNCTIONS[@]} ]; then
        print_warning "Some functions failed to update or test"
        read -p "$(echo -e ${YELLOW})Rollback all functions? (yes/no): $(echo -e ${NC})" rollback_confirm
        
        if [ "$rollback_confirm" = "yes" ]; then
            print_header "ROLLING BACK FUNCTIONS"
            for function_name in "${LAMBDA_FUNCTIONS[@]}"; do
                rollback_function "$function_name"
                echo ""
            done
        fi
    fi
    
    print_header "UPDATE COMPLETE"
    print_info "Backup file: $BACKUP_FILE"
    print_info "Keep this backup for manual rollback if needed"
    echo ""
}

# Run main function
main
