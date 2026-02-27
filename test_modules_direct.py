#!/usr/bin/env python3

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.modules.example_math.module import ExampleMathModule
from src.modules.example_validation.module import ExampleValidationModule

def test_modules_direct():
    """Test modules directly to verify implementation."""
    
    print("Testing modules directly...")
    
    # Test math module
    print("\n=== Testing ExampleMathModule ===")
    math_module = ExampleMathModule()
    
    # Test addition
    result1 = math_module.process({
        "operation": "add",
        "numbers": [10, 20, 30]
    })
    print(f"Math Add: {json.dumps(result1, indent=2)}")
    
    # Test validation module  
    print("\n=== Testing ExampleValidationModule ===")
    validation_module = ExampleValidationModule()
    
    # Test email validation
    result2 = validation_module.process({
        "validation_type": "email",
        "value": "test@example.com"
    })
    print(f"Email Validation: {json.dumps(result2, indent=2)}")
    
    # Test invalid email
    result3 = validation_module.process({
        "validation_type": "email", 
        "value": "invalid-email"
    })
    print(f"Invalid Email: {json.dumps(result3, indent=2)}")
    
    # Test metadata
    print(f"\nMath Metadata: {math_module.metadata()}")
    print(f"Validation Metadata: {validation_module.metadata()}")
    
    # Create integration proof
    proof = {
        "test_timestamp": datetime.now().isoformat(),
        "direct_module_tests": {
            "example_math": {
                "add_operation": result1,
                "metadata": math_module.metadata()
            },
            "example_validation": {
                "valid_email": result2,
                "invalid_email": result3,
                "metadata": validation_module.metadata()
            }
        }
    }
    
    with open("module_integration_proof.json", "w") as f:
        json.dump(proof, f, indent=2)
    
    print(f"\nDirect test proof saved to module_integration_proof.json")

if __name__ == "__main__":
    test_modules_direct()