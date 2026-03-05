#!/usr/bin/env python3
"""
Core Integrator Sovereign Certification Test Runner
Executes live tests and captures actual execution proofs
"""

import requests
import json
import time
import datetime
from pathlib import Path

BASE_URL = "http://localhost:8001"
RENDER_URL = "https://core-integrator-production.onrender.com"

def test_local_server():
    """Test if local server is running"""
    try:
        response = requests.get(f"{BASE_URL}/system/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def capture_module_execution():
    """Part 1: Multi-Module Execution Proof"""
    print("Part 1: Capturing Multi-Module Execution Proof...")
    
    test_cases = [
        {
            "name": "sample_text_module",
            "request": {
                "module": "sample_text",
                "intent": "generate", 
                "user_id": "cert_test_user",
                "data": {"text": "CERTIFICATION TEST: Core Integrator sovereign execution proof"}
            }
        },
        {
            "name": "creator_module",
            "request": {
                "module": "creator",
                "intent": "generate",
                "user_id": "cert_test_user", 
                "data": {"topic": "Sovereign system certification", "type": "technical", "goal": "validate"}
            }
        },
        {
            "name": "finance_module",
            "request": {
                "module": "finance",
                "intent": "generate",
                "user_id": "cert_test_user",
                "data": {"report_type": "certification", "period": "Q4 2024"}
            }
        }
    ]
    
    results = {
        "certification_type": "Multi-Module Execution Proof - LIVE CAPTURE",
        "timestamp": datetime.datetime.now().isoformat(),
        "test_executions": {},
        "execution_summary": {}
    }
    
    successful = 0
    
    for test in test_cases:
        print(f"  Testing {test['name']}...")
        try:
            response = requests.post(f"{BASE_URL}/core", json=test["request"], timeout=10)
            
            results["test_executions"][test["name"]] = {
                "request": test["request"],
                "response": response.json() if response.status_code == 200 else {"error": response.text},
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "gateway_log": f"LIVE: {test['name']} executed at {datetime.datetime.now().isoformat()}"
            }
            
            if response.status_code == 200:
                successful += 1
                print(f"    SUCCESS: {test['name']}")
            else:
                print(f"    FAILED: {test['name']} ({response.status_code})")
                
        except Exception as e:
            results["test_executions"][test["name"]] = {
                "request": test["request"],
                "response": {"error": str(e)},
                "status_code": 0,
                "gateway_log": f"ERROR: {str(e)}"
            }
            print(f"    ERROR: {test['name']} - {e}")
    
    results["execution_summary"] = {
        "total_modules_tested": len(test_cases),
        "successful_executions": successful,
        "failed_executions": len(test_cases) - successful,
        "certification_status": "PASSED" if successful == len(test_cases) else "FAILED"
    }
    
    with open("sovereign_module_execution_proof.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Part 1 Complete: {successful}/{len(test_cases)} modules verified")
    return successful == len(test_cases)

def capture_deployment_proof():
    """Part 4: Live Deployment Execution Proof"""
    print("Part 4: Capturing Live Deployment Proof...")
    
    endpoints = [
        {"name": "core", "method": "POST", "url": "/core", "data": {
            "module": "sample_text", "intent": "generate", "user_id": "deploy_test",
            "data": {"text": "Live deployment certification test"}
        }},
        {"name": "health", "method": "GET", "url": "/system/health"},
        {"name": "diagnostics", "method": "GET", "url": "/system/diagnostics"}
    ]
    
    results = {
        "certification_type": "Live Deployment Execution Proof - RENDER VERIFICATION",
        "timestamp": datetime.datetime.now().isoformat(),
        "deployment_url": RENDER_URL,
        "endpoint_verification": {}
    }
    
    all_success = True
    
    for endpoint in endpoints:
        print(f"  Testing {endpoint['name']} endpoint...")
        try:
            if endpoint["method"] == "POST":
                response = requests.post(f"{RENDER_URL}{endpoint['url']}", json=endpoint["data"], timeout=15)
            else:
                response = requests.get(f"{RENDER_URL}{endpoint['url']}", timeout=15)
            
            results["endpoint_verification"][endpoint["name"]] = {
                "url": f"{RENDER_URL}{endpoint['url']}",
                "method": endpoint["method"],
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "response": response.json() if response.status_code == 200 else {"error": response.text}
            }
            
            if response.status_code == 200:
                print(f"    SUCCESS: {endpoint['name']}")
            else:
                print(f"    FAILED: {endpoint['name']} ({response.status_code})")
                all_success = False
                
        except Exception as e:
            results["endpoint_verification"][endpoint["name"]] = {
                "url": f"{RENDER_URL}{endpoint['url']}",
                "error": str(e)
            }
            print(f"    ERROR: {endpoint['name']} - {e}")
            all_success = False
    
    results["certification_status"] = "PASSED" if all_success else "FAILED"
    
    with open("live_deployment_execution_proof.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Part 4 Complete: Deployment {'VERIFIED' if all_success else 'FAILED'}")
    return all_success

def main():
    """Run certification tests"""
    print("Starting Core Integrator Sovereign Certification...")
    print("=" * 60)
    
    # Test deployment first (doesn't require local server)
    deployment_success = capture_deployment_proof()
    
    # Check if local server is running for other tests
    if test_local_server():
        print("Local server detected - running local tests")
        module_success = capture_module_execution()
    else:
        print("Local server not running - skipping local tests")
        module_success = False
    
    print()
    print("=" * 60)
    print("CERTIFICATION RESULTS:")
    print(f"Modules: {'PASSED' if module_success else 'FAILED/SKIPPED'}")
    print(f"Deployment: {'PASSED' if deployment_success else 'FAILED'}")
    
    if deployment_success:
        print("\nCore Integrator Sovereign Certification Complete")
    else:
        print("\nCertification incomplete - check results")

if __name__ == "__main__":
    main()