# Module Integration Contract

**Version**: 1.0.0  
**Status**: Sovereign-Safe Certified  
**Compatibility**: Core Integrator v1.0.0

## Contract Overview

This contract defines the mandatory interface for all modules in the Core Integrator system. Modules must implement this contract exactly to ensure sovereign-safe operation, telemetry compliance, and integration stability.

## Required Interface

### BaseModule Abstract Class

All modules MUST inherit from `src.modules.base.BaseModule`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseModule(ABC):
    @abstractmethod
    def process(self, data: Dict[str, Any], context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process incoming data and return result dict"""
        raise NotImplementedError()
    
    def metadata(self) -> Dict[str, Any]:
        """Optional module metadata"""
        return {}
```

### Required Methods

#### 1. `process(data, context) -> Dict[str, Any]`

**MANDATORY**: Core processing method

**Parameters**:
- `data`: Input data dictionary from request
- `context`: Optional user context history (List of previous interactions)

**Return Format**:
```python
{
    "status": "success|error",
    "message": "Human readable message",
    "result": {
        # Module-specific result data
    }
}
```

#### 2. `metadata() -> Dict[str, Any]` 

**OPTIONAL**: Module information

**Return Format**:
```python
{
    "name": "module_name",
    "version": "x.y.z",
    "description": "Module description"
}
```

## Module Structure

### Directory Layout
```
src/modules/<module_name>/
├── __init__.py          # Empty file
├── config.json          # Module configuration
└── module.py           # Implementation
```

### config.json Format
```json
{
    "name": "module_name",
    "version": "1.0.0",
    "description": "Module description"
}
```

### module.py Implementation
```python
from typing import Dict, Any, List
from src.modules.base import BaseModule

class ModuleNameModule(BaseModule):
    def process(self, data: Dict[str, Any], context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Implementation here
        return {
            "status": "success",
            "message": "Processing completed",
            "result": {"key": "value"}
        }
    
    def metadata(self) -> Dict[str, Any]:
        return {"name": "module_name", "version": "1.0.0"}
```

## Response Format Contract

### Success Response
```python
{
    "status": "success",
    "message": "Operation completed successfully",
    "result": {
        # Module-specific data
    }
}
```

### Error Response
```python
{
    "status": "error", 
    "message": "Error description",
    "result": {}
}
```

## Failure Handling Rules

### 1. Input Validation
- Modules MUST validate input data
- Invalid input MUST return error status, not raise exceptions
- Missing required fields MUST be handled gracefully

### 2. Exception Handling
- Modules MUST NOT let exceptions propagate to gateway
- All exceptions MUST be caught and converted to error responses
- Error messages MUST be user-safe (no stack traces)

### 3. Timeout Handling
- Modules MUST complete processing within 30 seconds
- Long-running operations MUST be designed for async execution
- No blocking I/O without timeout

## Telemetry Emission Requirements

### 1. Automatic Telemetry
- Gateway automatically logs module invocation
- Gateway logs response status and timing
- No manual telemetry required in modules

### 2. Custom Events (Optional)
Modules MAY emit custom telemetry via logger:
```python
import logging
logger = logging.getLogger(__name__)

def process(self, data, context):
    logger.info("Custom event", extra={
        "event_type": "module_custom",
        "module_name": self.metadata().get("name"),
        "custom_data": {"key": "value"}
    })
```

## Security Requirements

### 1. Input Sanitization
- Modules MUST sanitize all input data
- No direct execution of user-provided code
- No file system access outside module directory

### 2. Output Sanitization  
- Response data MUST be JSON serializable
- No sensitive information in responses
- No system paths or internal details

## Integration Guarantees

### 1. Gateway Integration
- Modules are loaded dynamically via `module_loader.py`
- Gateway routes requests to modules via contract only
- No hardcoded module references in gateway

### 2. Storage Integration
- All module interactions are stored in context database
- Storage is handled by gateway, not modules
- Modules receive context via `context` parameter

### 3. External Service Integration
- Modules MAY call external services
- External calls MUST have timeout handling
- External failures MUST NOT crash module

## Validation Checklist

Before deployment, modules MUST pass:

- [ ] Inherits from BaseModule
- [ ] Implements process() method correctly
- [ ] Returns proper response format
- [ ] Handles invalid input gracefully
- [ ] Completes within timeout limits
- [ ] Has valid config.json
- [ ] Passes determinism tests (same input → same output)
- [ ] Passes failure tests (invalid input → safe error)

## Breaking Changes

The following changes would break the contract:
- Changing BaseModule interface
- Modifying response format structure
- Changing module loading mechanism
- Altering gateway routing logic

## Compliance Certification

Modules following this contract are certified as:
- **Sovereign-Safe**: Cannot break core system
- **Integration-Ready**: Compatible with all system components  
- **Demo-Safe**: Suitable for production demonstrations
- **Telemetry-Compliant**: Proper logging and monitoring

**Contract Authority**: Core Integrator Team  
**Last Updated**: 2024-01-27  
**Next Review**: 2024-04-27