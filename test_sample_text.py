#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.modules.sample_text.module import SampleTextModule

def test_sample_text():
    """Test the sample_text module directly"""
    module = SampleTextModule()
    
    # Test case 1: Normal text
    result1 = module.process({"input_text": "Hello world this is a test"})
    print("Test 1 - Normal text:")
    print(f"Input: 'Hello world this is a test'")
    print(f"Result: {result1}")
    print()
    
    # Test case 2: Empty text
    result2 = module.process({"input_text": ""})
    print("Test 2 - Empty text:")
    print(f"Input: ''")
    print(f"Result: {result2}")
    print()
    
    # Test case 3: No input_text key
    result3 = module.process({})
    print("Test 3 - No input_text key:")
    print(f"Input: {{}}")
    print(f"Result: {result3}")
    print()
    
    # Test metadata
    metadata = module.metadata()
    print("Module metadata:")
    print(f"Metadata: {metadata}")

if __name__ == "__main__":
    test_sample_text()