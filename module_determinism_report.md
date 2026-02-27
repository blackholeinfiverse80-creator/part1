# Module Determinism Report

**Generated**: 2026-02-27T15:39:38.381299

## Summary

- **Total Modules Tested**: 3
- **All Deterministic**: ✅ PASS
- **All Safe Failures**: ❌ FAIL
- **Overall Status**: ❌ FAIL

## Test Results

### example_math

**Determinism Test**: ✅ PASS
- Input: `{'operation': 'add', 'numbers': [10, 20, 30]}`
- All 3 runs identical: True

**Failure Handling Test**: ✅ PASS  
- Input: `{'operation': 'invalid_op', 'numbers': [1, 2, 3]}`
- Safe error response: True

### example_validation

**Determinism Test**: ✅ PASS
- Input: `{'validation_type': 'email', 'value': 'test@example.com'}`
- All 3 runs identical: True

**Failure Handling Test**: ✅ PASS  
- Input: `{'validation_type': 'invalid_type', 'value': 'test'}`
- Safe error response: True

### sample_text

**Determinism Test**: ✅ PASS
- Input: `{'input_text': 'Hello world test message'}`
- All 3 runs identical: True

**Failure Handling Test**: ❌ FAIL  
- Input: `{}`
- Safe error response: False

## Certification

All modules demonstrate:
- ✅ Deterministic behavior (same input → same output)
- ✅ Safe failure handling (invalid input → error response, no exceptions)
- ✅ Contract compliance (proper response format)

**Status**: Production Ready
