#!/usr/bin/env python3
"""
Test the complete execution discipline flow through the gateway
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.gateway import Gateway
import json

def test_gateway_execution_discipline():
    """Test gateway with execution discipline enforcement"""
    print("Testing Gateway Execution Discipline")
    print("=" * 40)
    
    # Initialize gateway
    gateway = Gateway()
    
    # Test valid request
    print("1. Testing valid module request...")
    response = gateway.process_request(
        module="sample_text",
        intent="generate",
        user_id="discipline_test_user",
        data={"text": "Execution discipline test payload"}
    )
    
    print(f"   Status: {response.get('status')}")
    print(f"   Message: {response.get('message')}")
    
    # Check for execution envelope
    if 'execution_envelope' in response:
        envelope = response['execution_envelope']
        print(f"   Execution ID: {envelope.get('execution_id')}")
        print(f"   Input Hash: {envelope.get('input_hash', '')[:16]}...")
        print(f"   Output Hash: {envelope.get('output_hash', '')[:16]}...")
        print(f"   Classification: {envelope.get('truth_classification_level')}")
        print(f"   Duration: {envelope.get('execution_duration_ms')}ms")
        
        # Save example response
        with open("gateway_execution_example.json", "w") as f:
            json.dump(response, f, indent=2)
        print(f"   Saved response to: gateway_execution_example.json")
    else:
        print("   No execution envelope found")
    
    print()
    
    # Test invalid request
    print("2. Testing invalid module request...")
    invalid_response = gateway.process_request(
        module="nonexistent_module",
        intent="generate", 
        user_id="discipline_test_user",
        data={"test": "data"}
    )
    
    print(f"   Status: {invalid_response.get('status')}")
    print(f"   Message: {invalid_response.get('message')}")
    print(f"   Validation Error: {invalid_response.get('validation_error', False)}")
    
    print()
    print("=" * 40)
    print("Gateway execution discipline test completed")

if __name__ == "__main__":
    test_gateway_execution_discipline()