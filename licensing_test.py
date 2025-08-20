#!/usr/bin/env python3
"""
Comprehensive Licensing System Testing for Big Mann Entertainment
Tests all licensing functionality as requested in the review.
"""

import requests
import json
import os
from backend_test import BackendTester

def main():
    """Run comprehensive licensing system tests"""
    print("🏢 COMPREHENSIVE PLATFORM LICENSING SYSTEM TESTING")
    print("=" * 80)
    print("Testing the comprehensive platform licensing system for Big Mann Entertainment")
    print("Focus: Backend Integration, Core Endpoints, Authentication, Platform Integration")
    print("=" * 80)
    
    # Initialize tester
    tester = BackendTester()
    
    # Authenticate first
    print("\n🔐 AUTHENTICATION SETUP")
    print("-" * 40)
    if not tester.test_user_registration():
        print("⚠️  Registration failed, trying login...")
    if not tester.test_user_login():
        print("❌ Cannot proceed without authentication")
        return
    
    # Run comprehensive licensing tests
    tester.run_licensing_tests()
    
    # Print detailed summary
    print("\n" + "=" * 80)
    print("🏢 COMPREHENSIVE LICENSING SYSTEM TEST RESULTS")
    print("=" * 80)
    
    licensing_categories = [
        'licensing_backend_integration',
        'licensing_dashboard', 
        'licensing_platform_initialization',
        'licensing_platform_management',
        'licensing_compliance',
        'licensing_usage_tracking',
        'licensing_authentication',
        'licensing_platform_integration'
    ]
    
    total_passed = 0
    total_failed = 0
    
    for category in licensing_categories:
        if category in tester.results:
            passed = tester.results[category]['passed']
            failed = tester.results[category]['failed']
            total_passed += passed
            total_failed += failed
            
            print(f"\n{category.replace('_', ' ').title()}:")
            for detail in tester.results[category]['details']:
                print(f"  {detail}")
    
    print(f"\n📊 OVERALL LICENSING SYSTEM TEST SUMMARY:")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📈 Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%" if (total_passed+total_failed) > 0 else "No tests run")
    
    if total_failed == 0:
        print("\n🎉 ALL LICENSING SYSTEM TESTS PASSED!")
        print("The comprehensive platform licensing system is fully functional and integrated.")
    else:
        print(f"\n⚠️  {total_failed} licensing tests failed. Review the details above.")

if __name__ == "__main__":
    main()