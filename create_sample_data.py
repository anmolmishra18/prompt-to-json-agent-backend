#!/usr/bin/env python3
"""Create sample HIDG logs and test data to demonstrate meaningful storage"""

import requests
import json
from datetime import datetime, timedelta
import time

API_BASE = "https://prompt-to-json-agent-backend-1.onrender.com"

# Sample HIDG values showing meaningful daily reflections
sample_hidg_logs = [
    {
        "honesty": "Successfully deployed backend but CORS issues blocked frontend integration initially. Fixed by updating origins configuration.",
        "integrity": "All test results documented accurately including 3 failed attempts before successful deployment to Render.",
        "discipline": "Completed all 4 sprint endpoints on schedule. Maintained systematic approach to debugging CORS and validation issues.",
        "gratitude": "Grateful for comprehensive feedback that identified specific improvement areas. Team collaboration made debugging faster."
    },
    {
        "honesty": "RL agent was initially using mock improvements. Enhanced to show genuine learning progression with score validation.",
        "integrity": "Admitted that first iteration logic was too simplistic. Rewrote to include actual learning patterns and memory.",
        "discipline": "Refactored 3 service classes to ensure consistent run() interface for BHIV Core compatibility as planned.",
        "gratitude": "Thankful for clear requirements that helped prioritize genuine learning over quick hacks."
    },
    {
        "honesty": "Database connection failed twice during deployment due to environment variable issues. Took 2 hours to debug properly.",
        "integrity": "Recorded exact error messages and solutions in deployment notes. No shortcuts taken on error handling.",
        "discipline": "Implemented comprehensive input validation for all endpoints including length limits and format checks.",
        "gratitude": "Appreciated having SQLAlchemy ORM that made database debugging more manageable than raw SQL."
    },
    {
        "honesty": "Analytics endpoint was returning basic stats only. Enhanced with meaningful insights about reflection depth and consistency.",
        "integrity": "Previous analytics were placeholder quality. Rebuilt with actual value-add metrics for daily reflection tracking.",
        "discipline": "Added proper error handling to all 8 endpoints with specific HTTP status codes and detailed error messages.",
        "gratitude": "Grateful for production deployment experience that revealed real-world edge cases not caught in local testing."
    },
    {
        "honesty": "Demo UI took longer than expected due to CORS debugging. Should have tested cross-origin requests earlier in development.",
        "integrity": "Documented all integration challenges for Rishabh's frontend work. Provided working examples and error scenarios.",
        "discipline": "Created comprehensive test suite covering happy path, error cases, and stress testing scenarios.",
        "gratitude": "Thankful for opportunity to build full-stack integration experience and learn production deployment challenges."
    }
]

def create_sample_logs():
    """Create sample HIDG logs to demonstrate meaningful storage"""
    print("Creating sample HIDG logs...")
    
    for i, log_data in enumerate(sample_hidg_logs):
        try:
            response = requests.post(f"{API_BASE}/log-values", json=log_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"Created log {i+1}: {result['id']}")
            else:
                print(f"Failed to create log {i+1}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error creating log {i+1}: {str(e)}")
        
        time.sleep(1)  # Avoid overwhelming the API

def test_rl_learning_depth():
    """Test RL agent with multiple iterations to show genuine learning"""
    print("\nTesting RL learning depth...")
    
    test_prompts = [
        "design a mobile app for task management",
        "create a REST API for user authentication", 
        "build a machine learning model for image classification"
    ]
    
    for prompt in test_prompts:
        try:
            response = requests.post(f"{API_BASE}/iterate", 
                                   json={"prompt": prompt, "max_iters": 5}, 
                                   timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"RL Test - {prompt[:30]}...")
                if 'learning_summary' in result:
                    summary = result['learning_summary']
                    print(f"   Improvement: {summary['initial_score']:.2f} → {summary['final_score']:.2f} (+{summary['improvement']:.2f})")
                print(f"   Report ID: {result['report_id']}")
            else:
                print(f"RL Test failed: {response.status_code}")
        except Exception as e:
            print(f"RL Test error: {str(e)}")
        
        time.sleep(2)

def test_error_handling():
    """Test comprehensive error handling scenarios"""
    print("\nTesting error handling scenarios...")
    
    error_tests = [
        # Empty prompt
        {"endpoint": "/generate", "data": {"prompt": ""}, "expected": "empty"},
        # Too long prompt  
        {"endpoint": "/generate", "data": {"prompt": "x" * 6000}, "expected": "too long"},
        # Invalid JSON in evaluate
        {"endpoint": "/evaluate", "data": {"json_spec": "invalid json"}, "expected": "invalid"},
        # Non-existent report ID
        {"endpoint": "/reports/nonexistent-id", "method": "GET", "expected": "not found"},
        # Empty HIDG values
        {"endpoint": "/log-values", "data": {"honesty": "", "integrity": "test", "discipline": "test", "gratitude": "test"}, "expected": "empty"},
        # Too short HIDG values
        {"endpoint": "/log-values", "data": {"honesty": "short", "integrity": "test value here", "discipline": "test value here", "gratitude": "test value here"}, "expected": "too short"}
    ]
    
    for test in error_tests:
        try:
            method = test.get("method", "POST")
            if method == "GET":
                response = requests.get(f"{API_BASE}{test['endpoint']}", timeout=10)
            else:
                response = requests.post(f"{API_BASE}{test['endpoint']}", json=test['data'], timeout=10)
            
            print(f"Error test ({test['expected']}): {response.status_code} - {response.json().get('detail', 'No detail')[:50]}...")
        except Exception as e:
            print(f"Error test failed: {str(e)}")

def check_analytics():
    """Check HIDG analytics for meaningful insights"""
    print("\nChecking HIDG analytics...")
    
    try:
        response = requests.get(f"{API_BASE}/hidg-analytics", timeout=10)
        if response.status_code == 200:
            analytics = response.json()
            print(f"Analytics retrieved:")
            print(f"   Total entries: {analytics.get('total_entries', 0)}")
            print(f"   Consistency score: {analytics.get('consistency_score', 0):.2f}")
            if 'insights' in analytics:
                insights = analytics['insights']
                print(f"   Most detailed area: {insights.get('most_detailed_area', 'N/A')}")
                print(f"   Reflection depth: {insights.get('reflection_depth', 'N/A')}")
        else:
            print(f"Analytics failed: {response.status_code}")
    except Exception as e:
        print(f"Analytics error: {str(e)}")

if __name__ == "__main__":
    print("Creating sample data and testing API robustness...\n")
    
    # Test API health first
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            print("API is healthy, proceeding with tests...\n")
        else:
            print("API health check failed")
            exit(1)
    except Exception as e:
        print(f"Cannot connect to API: {str(e)}")
        exit(1)
    
    create_sample_logs()
    test_rl_learning_depth() 
    test_error_handling()
    check_analytics()
    
    print("\nSample data creation and testing complete!")
    print(f"View analytics at: {API_BASE}/hidg-analytics")
    print(f"View logs at: {API_BASE}/hidg-logs")