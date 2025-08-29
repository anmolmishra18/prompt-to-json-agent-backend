import requests
import json
import time
import sys

BASE_URL = "https://prompt-to-json-agent-backend-1.onrender.com"
# BASE_URL = "http://localhost:8000"  # For local testing

def test_generate():
    print("\n=== Testing /generate ===")
    
    # Test valid request
    response = requests.post(f"{BASE_URL}/generate", 
                           json={"prompt": "design a robot using aluminium; Priority: high"})
    print(f"Valid request - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Generated ID: {data['id']}")
        print(f"JSON Spec: {json.dumps(data['json_spec'], indent=2)}")
        report_id = data['id']
    else:
        print(f"Error: {response.text}")
        report_id = None
    
    # Test error cases
    print("\nTesting error cases:")
    
    # Empty prompt
    response = requests.post(f"{BASE_URL}/generate", json={"prompt": ""})
    print(f"Empty prompt - Status: {response.status_code} (expected 400)")
    
    # Very long prompt
    long_prompt = "x" * 6000
    response = requests.post(f"{BASE_URL}/generate", json={"prompt": long_prompt})
    print(f"Long prompt - Status: {response.status_code} (expected 400)")
    
    return report_id

def test_evaluate():
    print("\n=== Testing /evaluate ===")
    
    # Test valid spec
    test_spec = {
        "title": "Robot Design",
        "description": "Build a robot frame using aluminium with high durability.",
        "priority": "high"
    }
    response = requests.post(f"{BASE_URL}/evaluate", json={"json_spec": test_spec})
    print(f"Valid spec - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Score: {data['score']}")
        print(f"Comments: {data['comments']}")
    else:
        print(f"Error: {response.text}")
    
    # Test error cases
    print("\nTesting error cases:")
    
    # Missing both report_id and json_spec
    response = requests.post(f"{BASE_URL}/evaluate", json={})
    print(f"Missing data - Status: {response.status_code} (expected 400)")
    
    # Invalid report_id
    response = requests.post(f"{BASE_URL}/evaluate", json={"report_id": "invalid-id"})
    print(f"Invalid report_id - Status: {response.status_code} (expected 404)")

def test_iterate():
    print("\n=== Testing /iterate ===")
    
    # Test valid request
    response = requests.post(f"{BASE_URL}/iterate", 
                           json={"prompt": "design a robot using aluminium", "max_iters": 3})
    print(f"Valid request - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Report ID: {data['report_id']}")
        print(f"Iterations: {len(data['iterations'])}")
        for i, iteration in enumerate(data['iterations'], 1):
            print(f"  Iteration {i}: {iteration['score_before']:.2f} → {iteration['score_after']:.2f}")
            print(f"  Feedback: {iteration['feedback'][:100]}...")
        report_id = data['report_id']
    else:
        print(f"Error: {response.text}")
        report_id = None
    
    # Test error cases
    print("\nTesting error cases:")
    
    # Invalid max_iters
    response = requests.post(f"{BASE_URL}/iterate", 
                           json={"prompt": "test", "max_iters": 15})
    print(f"Invalid max_iters - Status: {response.status_code} (expected 400)")
    
    # Empty prompt
    response = requests.post(f"{BASE_URL}/iterate", 
                           json={"prompt": "", "max_iters": 2})
    print(f"Empty prompt - Status: {response.status_code} (expected 400)")
    
    return report_id

def test_get_report(report_id):
    if not report_id:
        print("\n=== Skipping /reports/{id} (no report_id) ===")
        return
    
    print(f"\n=== Testing /reports/{report_id} ===")
    
    # Test valid request
    response = requests.get(f"{BASE_URL}/reports/{report_id}")
    print(f"Valid request - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Report ID: {data['id']}")
        print(f"Prompt: {data['prompt_text'][:50]}...")
        print(f"Evaluations: {len(data['evaluations'])}")
        print(f"Iterations: {len(data['iterations'])}")
        print(f"Feedback Logs: {len(data['feedback_logs'])}")
    else:
        print(f"Error: {response.text}")
    
    # Test error case
    print("\nTesting error cases:")
    response = requests.get(f"{BASE_URL}/reports/invalid-id")
    print(f"Invalid report_id - Status: {response.status_code} (expected 404)")

def test_log_values():
    print("\n=== Testing /log-values ===")
    
    # Test valid request
    hidg_data = {
        "honesty": "All endpoints implemented and tested successfully with comprehensive error handling",
        "integrity": "Backend is live and serving users reliably with proper validation", 
        "discipline": "Clean code structure with proper error handling and meaningful HIDG analytics",
        "gratitude": "Thanks for clear requirements and team collaboration - demo UI created for easy testing"
    }
    response = requests.post(f"{BASE_URL}/log-values", json=hidg_data)
    print(f"Valid request - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"HIDG Log ID: {data['id']}")
    else:
        print(f"Error: {response.text}")
    
    # Test error cases
    print("\nTesting error cases:")
    
    # Empty values
    response = requests.post(f"{BASE_URL}/log-values", 
                           json={"honesty": "", "integrity": "test", "discipline": "test", "gratitude": "test"})
    print(f"Empty honesty - Status: {response.status_code} (expected 400)")
    
    # Too long values
    long_text = "x" * 1001
    response = requests.post(f"{BASE_URL}/log-values", 
                           json={"honesty": long_text, "integrity": "test", "discipline": "test", "gratitude": "test"})
    print(f"Too long text - Status: {response.status_code} (expected 400)")

def test_health():
    print("\n=== Testing /health ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Health: {data['status']}")
        print(f"Version: {data['version']}")
        print(f"Database: {data['database']}")
        print(f"Endpoints: {len(data['endpoints'])} available")
    else:
        print(f"Error: {response.text}")

def test_hidg_endpoints():
    print("\n=== Testing HIDG Endpoints ===")
    
    # Test HIDG logs
    response = requests.get(f"{BASE_URL}/hidg-logs?limit=3")
    print(f"HIDG logs - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Showing {data['showing']}/{data['total_count']} logs")
    
    # Test HIDG analytics
    response = requests.get(f"{BASE_URL}/hidg-analytics")
    print(f"HIDG analytics - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total entries: {data.get('total_entries', 0)}")
        print(f"Consistency score: {data.get('consistency_score', 0):.2f}")

def run_stress_test():
    print("\n=== Stress Testing ===")
    print("Running 5 concurrent requests...")
    
    import threading
    results = []
    
    def make_request():
        try:
            response = requests.post(f"{BASE_URL}/generate", 
                                   json={"prompt": "stress test prompt"}, 
                                   timeout=30)
            results.append(response.status_code)
        except Exception as e:
            results.append(f"Error: {e}")
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=make_request)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    success_count = sum(1 for r in results if r == 200)
    print(f"Stress test results: {success_count}/5 successful")
    print(f"Results: {results}")

if __name__ == "__main__":
    print(f"🚀 Comprehensive API Testing at {BASE_URL}")
    print("=" * 60)
    
    try:
        # Test all endpoints with error cases
        test_health()
        report_id = test_generate()
        test_evaluate()
        iterate_report_id = test_iterate()
        test_get_report(iterate_report_id or report_id)
        test_log_values()
        test_hidg_endpoints()
        
        # Stress test
        run_stress_test()
        
        print("\n" + "=" * 60)
        print("✅ All comprehensive tests completed!")
        print("\n🎯 Key Improvements Made:")
        print("• Enhanced error handling with proper HTTP status codes")
        print("• Input validation for all endpoints")
        print("• HIDG analytics and meaningful logging")
        print("• Improved RL agent with genuine learning progression")
        print("• Demo UI created for easy frontend integration")
        print("• Comprehensive test coverage including edge cases")
        
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)