#!/usr/bin/env python3

import sys
import os
import json
import requests
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_module_integration():
    """Test new modules and capture integration proof."""
    
    base_url = "http://localhost:8001"
    test_results = {
        "test_timestamp": datetime.now().isoformat(),
        "test_description": "Module integration proof for example_math and example_validation",
        "modules_tested": ["example_math", "example_validation"],
        "test_cases": []
    }
    
    # Test cases
    test_cases = [
        {
            "module": "example_math",
            "description": "Math addition operation",
            "request": {
                "module": "example_math",
                "intent": "process", 
                "user_id": "test_user_math",
                "data": {
                    "operation": "add",
                    "numbers": [10, 20, 30]
                }
            }
        },
        {
            "module": "example_validation", 
            "description": "Email validation",
            "request": {
                "module": "example_validation",
                "intent": "process",
                "user_id": "test_user_validation",
                "data": {
                    "validation_type": "email",
                    "value": "test@example.com"
                }
            }
        }
    ]
    
    print("Starting module integration tests...")
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['description']}")
        
        try:
            # Send request
            response = requests.post(
                f"{base_url}/core",
                json=test_case["request"],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            # Capture results
            result = {
                "test_id": i + 1,
                "module": test_case["module"],
                "description": test_case["description"],
                "input": test_case["request"],
                "output": response.json() if response.status_code == 200 else {"error": response.text},
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "timestamp": datetime.now().isoformat()
            }
            
            test_results["test_cases"].append(result)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(result['output'], indent=2)}")
            
        except Exception as e:
            error_result = {
                "test_id": i + 1,
                "module": test_case["module"],
                "description": test_case["description"],
                "input": test_case["request"],
                "output": {"error": str(e)},
                "status_code": 0,
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            test_results["test_cases"].append(error_result)
            print(f"Error: {str(e)}")
    
    # Get telemetry logs
    try:
        logs_response = requests.get(f"{base_url}/system/logs/latest?limit=10")
        if logs_response.status_code == 200:
            test_results["telemetry_logs"] = logs_response.json()
        else:
            test_results["telemetry_logs"] = {"error": "Could not retrieve logs"}
    except Exception as e:
        test_results["telemetry_logs"] = {"error": str(e)}
    
    # Save results
    with open("module_integration_proof.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nIntegration proof saved to module_integration_proof.json")
    print(f"Total tests: {len(test_cases)}")
    print(f"Successful: {sum(1 for tc in test_results['test_cases'] if tc['success'])}")
    
    return test_results

if __name__ == "__main__":
    test_module_integration()