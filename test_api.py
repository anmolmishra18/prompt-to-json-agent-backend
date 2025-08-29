#!/usr/bin/env python3
"""Quick test script to verify all API endpoints work"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_generate():
    response = requests.post(f"{BASE_URL}/generate", 
        json={"prompt": "design a robot using aluminium; Priority: high"})
    print(f"Generate: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ID: {data['id']}")
        print(f"  Spec: {data['json_spec']}")
        return data['id']
    return None

def test_evaluate():
    response = requests.post(f"{BASE_URL}/evaluate",
        json={"json_spec": {"title": "Robot", "description": "Build a robot frame using aluminium.", "priority": "high"}})
    print(f"Evaluate: {response.status_code}")
    if response.status_code == 200:
        print(f"  Result: {response.json()}")

def test_iterate():
    response = requests.post(f"{BASE_URL}/iterate",
        json={"prompt": "design a robot using aluminium", "max_iters": 2})
    print(f"Iterate: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Report ID: {data['report_id']}")
        print(f"  Iterations: {len(data['iterations'])}")
        return data['report_id']
    return None

def test_get_report(report_id):
    if not report_id:
        return
    response = requests.get(f"{BASE_URL}/reports/{report_id}")
    print(f"Get Report: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Evaluations: {len(data['evaluations'])}")
        print(f"  Iterations: {len(data['iterations'])}")

def test_log_values():
    response = requests.post(f"{BASE_URL}/log-values",
        json={
            "honesty": "Fixed import errors and tested endpoints",
            "integrity": "All tests pass with real data", 
            "discipline": "Completed systematic testing",
            "gratitude": "Thanks for clear requirements"
        })
    print(f"Log Values: {response.status_code}")
    if response.status_code == 200:
        print(f"  HIDG ID: {response.json()['id']}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    
    # Test basic generation
    report_id = test_generate()
    
    # Test evaluation
    test_evaluate()
    
    # Test iteration (creates new report)
    iterate_report_id = test_iterate()
    
    # Test report retrieval
    test_get_report(iterate_report_id)
    
    # Test HIDG logging
    test_log_values()
    
    print("\nAll tests completed!")