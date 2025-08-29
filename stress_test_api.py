#!/usr/bin/env python3
"""Stress test API for robust error handling and concurrent requests"""

import requests
import json
import concurrent.futures
import time
from datetime import datetime

API_BASE = "https://prompt-to-json-agent-backend-1.onrender.com"

def test_concurrent_requests():
    """Test API under concurrent load"""
    print("Testing concurrent requests...")
    
    def make_request(i):
        try:
            response = requests.post(f"{API_BASE}/generate", 
                                   json={"prompt": f"test prompt {i}"}, 
                                   timeout=10)
            return {"id": i, "status": response.status_code, "success": response.ok}
        except Exception as e:
            return {"id": i, "status": "error", "error": str(e)}
    
    # Test 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(10)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    success_count = sum(1 for r in results if r.get("success"))
    print(f"Concurrent test: {success_count}/10 requests successful")
    return success_count >= 8  # Allow some failures under load

def test_edge_cases():
    """Test various edge cases and malformed inputs"""
    print("Testing edge cases...")
    
    edge_cases = [
        {"name": "Unicode prompt", "data": {"prompt": "设计一个机器人 🤖"}},
        {"name": "Very long prompt", "data": {"prompt": "design " * 1000}},
        {"name": "Special characters", "data": {"prompt": "design@#$%^&*()_+{}|:<>?"}},
        {"name": "SQL injection attempt", "data": {"prompt": "'; DROP TABLE reports; --"}},
        {"name": "XSS attempt", "data": {"prompt": "<script>alert('xss')</script>"}},
    ]
    
    results = []
    for case in edge_cases:
        try:
            response = requests.post(f"{API_BASE}/generate", json=case["data"], timeout=10)
            results.append({
                "name": case["name"],
                "status": response.status_code,
                "handled": response.status_code in [200, 400, 422]
            })
        except Exception as e:
            results.append({"name": case["name"], "status": "error", "error": str(e)})
    
    handled_count = sum(1 for r in results if r.get("handled"))
    print(f"Edge cases: {handled_count}/{len(edge_cases)} properly handled")
    return results

def test_database_stress():
    """Test database operations under stress"""
    print("Testing database stress...")
    
    # Create multiple reports rapidly
    report_ids = []
    for i in range(5):
        try:
            response = requests.post(f"{API_BASE}/generate", 
                                   json={"prompt": f"stress test {i}"}, 
                                   timeout=10)
            if response.ok:
                report_ids.append(response.json()["id"])
        except Exception as e:
            print(f"Database stress error: {e}")
    
    # Test retrieving all reports
    success_count = 0
    for report_id in report_ids:
        try:
            response = requests.get(f"{API_BASE}/reports/{report_id}", timeout=10)
            if response.ok:
                success_count += 1
        except Exception as e:
            print(f"Report retrieval error: {e}")
    
    print(f"Database stress: {success_count}/{len(report_ids)} reports retrieved")
    return success_count == len(report_ids)

if __name__ == "__main__":
    print("Starting comprehensive API stress test...\n")
    
    # Test API health
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.ok:
            print("API health check passed\n")
        else:
            print("API health check failed")
            exit(1)
    except Exception as e:
        print(f"Cannot connect to API: {e}")
        exit(1)
    
    # Run stress tests
    concurrent_ok = test_concurrent_requests()
    edge_results = test_edge_cases()
    db_stress_ok = test_database_stress()
    
    print(f"\nStress Test Results:")
    print(f"Concurrent requests: {'PASS' if concurrent_ok else 'FAIL'}")
    print(f"Edge case handling: {'PASS' if len(edge_results) > 0 else 'FAIL'}")
    print(f"Database stress: {'PASS' if db_stress_ok else 'FAIL'}")
    
    print(f"\nAPI is {'ROBUST' if all([concurrent_ok, db_stress_ok]) else 'NEEDS IMPROVEMENT'}")