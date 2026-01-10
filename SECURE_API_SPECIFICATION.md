# Secure Core Integrator API Specification

## Authentication Flow

### 1. Login (Public)
```
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "session_token_here",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 2. Authenticated Requests
```
Authorization: Bearer <session_token>
```

## Secure Endpoints

### Core Processing (Authenticated)
```
POST /core
Authorization: Bearer <token>
Content-Type: application/json

{
  "module": "finance",
  "intent": "analyze", 
  "data": {"query": "market analysis"}
  // NO user_id - derived from session
}
```

### Context Retrieval (Authenticated, Own Data Only)
```
GET /get-context
Authorization: Bearer <token>

// Returns only authenticated user's context
// No user_id parameter - prevents IDOR
```

### Public Health Check (Limited Info)
```
GET /system/health

Response:
{
  "status": "healthy",
  "timestamp": "2026-01-10T12:00:00Z"
  // No internal paths, module details, or architecture info
}
```

### Authenticated Diagnostics (Limited)
```
GET /system/diagnostics  
Authorization: Bearer <token>

Response:
{
  "integration_ready": true,
  "integration_score": 1.0,
  "timestamp": "2026-01-10T12:00:00Z"
  // No module names, db paths, or internal details
}
```

## Security Controls

### Session Management
- Internal user ID mapping (SHA256 hash)
- Session expiration (24 hours)
- Secure token generation (32-byte random)
- Session invalidation on logout

### Input Validation
- Pydantic models for all requests
- No client-supplied user identifiers
- Sanitized error messages
- Rate limiting (recommended)

### Output Sanitization
- Remove internal database paths
- Hide module implementation details
- Mask system architecture information
- Filter sensitive configuration data

## Implementation Priority

### Phase 1: Critical Security (Required)
1. Add authentication middleware
2. Implement session management
3. Remove client-supplied user_id
4. Add IDOR protection

### Phase 2: Hardening (Recommended)
1. Add rate limiting
2. Implement audit logging
3. Add input sanitization
4. Enhance error handling

### Phase 3: Advanced Security (Optional)
1. Add OAuth2/OIDC integration
2. Implement role-based access control
3. Add API key management
4. Enhanced monitoring/alerting