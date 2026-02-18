# CORE INTEGRATOR — FINAL AUTHORITY DECLARATION

## 1. Authority Statement

Core Integrator is the sole orchestration authority for all agent and module interactions within this system. All requests to Finance, Education, Creator, and Video agents must route through the Gateway component. Direct invocation of agents, direct database access, or any mechanism that bypasses the Gateway violates the system contract and is explicitly unsupported.

The Gateway component in `src/core/gateway.py` is the single point of control for:
- Agent selection and invocation
- Module discovery and execution
- Memory adapter selection and initialization
- Request validation and routing
- Response standardization

Any integration that does not use the documented HTTP endpoints exposed by `main.py` is operating outside the system contract.

## 2. System Guarantees

The following guarantees reflect actual implemented behavior:

### Storage Mode Selection
- Storage backend is selected deterministically at Gateway initialization based on environment variables
- Selection order: USE_MONGODB=true → MongoDB, INTEGRATOR_USE_NOOPUR=true → Noopur, default → SQLite
- No runtime switching between storage backends after initialization
- Storage mode remains fixed for the lifetime of the process

### Request/Response Contract
- All requests to POST /core must conform to CoreRequest schema: `{module, intent, user_id, data}`
- All successful responses conform to CoreResponse schema: `{status, message, result}`
- Error responses return HTTP error codes with `{detail}` payload
- Schema validation is enforced via Pydantic models

### Error Propagation
- Storage backend failures (SQLite, MongoDB, Noopur) propagate as HTTP 500 errors
- Request validation failures return HTTP 400 errors
- Security validation failures return HTTP 403 errors
- All storage operations are synchronous and deterministic

### External Service Fallback
- BridgeClient (CreatorCore) returns mock responses on external service failure
- VideoBridgeClient (Video Service) returns mock responses on external service failure
- Mock responses include `fallback_used: true` flag
- Fallback behavior is silent and does not propagate errors to caller

### Security Validation
- SSPL signature validation is optional and controlled by SSPL_ENABLED environment variable
- Default configuration: SSPL_ENABLED=false (validation disabled)
- When enabled, Ed25519 signature verification is enforced on all requests
- Nonce replay protection is active when SSPL is enabled
- Security middleware applies globally to all endpoints

### Memory Persistence
- All interactions are stored in the configured storage backend
- SQLite: Stored in local database files (db/context.db, db/nonce_store.db)
- MongoDB: Stored in configured MongoDB database
- Noopur: Proxied to external Noopur service
- Retention policy: Last 5 interactions per user per module (SQLite)

## 3. Explicit Non-Responsibilities

Core Integrator does NOT provide the following capabilities:

### AI Model Inference
- No AI model execution or inference
- No content generation logic
- No machine learning operations
- Agent implementations may delegate to external services

### Automatic Storage Fallback
- No automatic fallback from MongoDB to SQLite on failure
- No automatic fallback from Noopur to SQLite on failure
- If configured storage backend is unavailable, system fails
- SQLite is the default mode, not a fallback mode

### External Service Availability
- No guarantee of external service availability (CreatorCore, Video Service, Noopur)
- No health monitoring of external services beyond health check endpoint
- No automatic retry logic for failed external requests
- No circuit breaker pattern implementation

### Runtime Reconfiguration
- No runtime modification of storage backend
- No runtime modification of security settings
- No runtime modification of agent configuration
- All configuration is read at startup from environment variables

### API Versioning
- No API version negotiation
- No backward compatibility guarantees across versions
- No version headers or version-specific endpoints
- Schema changes are breaking changes

### Telemetry Ownership
- No metrics collection or storage
- No distributed tracing implementation
- No performance monitoring beyond basic logging
- Logging is local file-based only

### Business Decision Logic
- No business rules beyond request routing
- No content filtering or moderation
- No user authorization or access control
- No rate limiting or quota enforcement

## 4. Integration Surface Freeze

### Supported Endpoints

The following endpoints constitute the complete integration surface:

**System Endpoints:**
- `GET /` - Root information (API name, version, documentation link)
- `GET /system/health` - Binary health status with dependency checks
- `GET /system/diagnostics` - Internal diagnostics and configuration summary
- `GET /system/logs/latest?limit=N` - Recent log entries retrieval

**Core Processing:**
- `POST /core` - Main processing endpoint for all agent and module requests

**Memory & Context:**
- `GET /get-history?user_id=X` - Full user interaction history (limited to 10 most recent)
- `GET /get-context?user_id=X` - Recent context (last 3 interactions)

**Feedback & Creator:**
- `POST /feedback` - Feedback submission for generated content
- `GET /creator/history?user_id=X` - Creator-specific generation history

### Supported Storage Modes

Three storage modes are supported, selected at startup via environment variables:

1. **SQLite (Default)**
   - Activated when: USE_MONGODB=false AND INTEGRATOR_USE_NOOPUR=false
   - Database files: db/context.db, db/nonce_store.db
   - Local file-based persistence
   - No external dependencies

2. **MongoDB**
   - Activated when: USE_MONGODB=true
   - Requires: MONGODB_CONNECTION_STRING, MONGODB_DATABASE_NAME
   - Remote database persistence
   - No fallback to SQLite on failure

3. **Noopur**
   - Activated when: INTEGRATOR_USE_NOOPUR=true
   - Requires: NOOPUR_BASE_URL, NOOPUR_API_KEY
   - External service proxy for memory operations
   - No fallback to SQLite on failure

**Explicit Statement:** No additional endpoints or storage modes are supported without version increment. Any undocumented endpoint usage or storage mode is unsupported and may break without notice.

### Unsupported / Contract Violations

The following integration patterns are explicitly unsupported and violate the system contract:

**Direct Database Access:**
- Direct SQLite database file access
- Direct MongoDB collection access
- Bypassing memory adapter abstraction

**Direct Agent Invocation:**
- Importing and instantiating agent classes directly
- Calling agent methods without Gateway routing
- Bypassing request validation and security middleware

**Runtime Backend Switching:**
- Attempting to change storage backend after initialization
- Hot-swapping memory adapters
- Dynamic reconfiguration of database connections

**Undocumented Endpoints:**
- Any HTTP endpoint not listed in this document
- Any HTTP method not explicitly documented
- Any query parameter or request body field not in schema

**Bypassing Gateway:**
- Direct module imports and execution
- Direct bridge client usage
- Any code path that does not flow through Gateway.process_request()

## 5. Dependency Behavior Declaration

The following table documents exact failure behavior for all dependencies:

### Storage Dependencies

**SQLite (Default Mode)**
- Condition: USE_MONGODB=false AND INTEGRATOR_USE_NOOPUR=false
- Failure Mode: Database file inaccessible or corrupted
- System Behavior: HTTP 500 error returned to caller
- Error Propagation: Yes - sqlite3.OperationalError propagated to endpoint
- Fallback: None - SQLite is the final fallback
- Recovery: Manual intervention required

**MongoDB (When Enabled)**
- Condition: USE_MONGODB=true
- Failure Mode: Connection refused, authentication failure, network timeout
- System Behavior: HTTP 500 error returned to caller
- Error Propagation: Yes - pymongo exceptions propagated to endpoint
- Fallback: None - no automatic fallback to SQLite
- Recovery: Manual intervention required

**Noopur (When Enabled)**
- Condition: INTEGRATOR_USE_NOOPUR=true
- Failure Mode: HTTP connection failure, service unavailable, timeout
- System Behavior: HTTP 500 error returned to caller
- Error Propagation: Yes - HTTP exceptions propagated to endpoint
- Fallback: None - no automatic fallback to SQLite
- Recovery: Manual intervention required

### External Service Dependencies

**CreatorCore Service**
- Condition: CREATORCORE_BASE_URL configured
- Failure Mode: HTTP connection failure, service unavailable, timeout
- System Behavior: Mock response returned with fallback_used=true
- Error Propagation: No - exception caught and handled silently
- Fallback: Yes - automatic mock response generation
- Recovery: Automatic on next request if service recovers

**Video Service**
- Condition: VIDEO_SERVICE_URL configured AND DISABLE_VIDEO_SERVICE=false
- Failure Mode: HTTP connection failure, service unavailable, timeout
- System Behavior: Mock response returned with fallback_used=true
- Error Propagation: No - exception caught and handled silently
- Fallback: Yes - automatic mock response generation
- Recovery: Automatic on next request if service recovers

### Security Dependencies

**SSPL Validation (When Enabled)**
- Condition: SSPL_ENABLED=true
- Failure Mode: Invalid signature, missing signature, nonce replay detected
- System Behavior: HTTP 403 Forbidden returned to caller
- Error Propagation: Yes - security validation failure is explicit
- Fallback: None - security violations are not bypassed
- Recovery: Client must provide valid signature

**SSPL Validation (When Disabled)**
- Condition: SSPL_ENABLED=false (default)
- Failure Mode: N/A - validation bypassed entirely
- System Behavior: All requests pass security validation
- Error Propagation: N/A
- Fallback: N/A
- Recovery: N/A

### Truth Table Summary

| Dependency | Failure Condition | Error Propagated | Fallback Triggered | System Continues | Deterministic |
|------------|-------------------|------------------|-------------------|------------------|---------------|
| SQLite | File inaccessible | Yes (500) | No | No | Yes |
| MongoDB | Connection failed | Yes (500) | No | No | Yes |
| Noopur | Service down | Yes (500) | No | No | Yes |
| CreatorCore | Service down | No | Yes (mock) | Yes | Yes |
| Video Service | Service down | No | Yes (mock) | Yes | Yes |
| SSPL (enabled) | Invalid signature | Yes (403) | No | Yes | Yes |
| SSPL (disabled) | N/A | No | N/A | Yes | Yes |

## 6. Demo Safety Statement

Core Integrator is demo-safe under the following configuration:

**Required Configuration:**
- USE_MONGODB=false
- INTEGRATOR_USE_NOOPUR=false
- SSPL_ENABLED=false (or true with valid test keys)
- DB_PATH=db/context.db (writable directory)

**Demo-Safe Behavior:**
- SQLite storage operates entirely locally without external dependencies
- External service failures (CreatorCore, Video) trigger mock responses automatically
- System continues to function in offline mode with mock data
- All endpoints remain accessible and return valid responses
- Sample text module (word count) functions without external dependencies

**Deterministic Behavior:**
- Same input produces same output under same configuration
- Storage operations are synchronous and ordered
- No race conditions in single-threaded request handling
- Mock responses are consistent and predictable

**Demo Limitations:**
- MongoDB and Noopur modes require external services (not demo-safe without infrastructure)
- SSPL validation requires key management (can be disabled for demos)
- External service integration requires network connectivity (falls back to mocks)

**Statement:** Under default configuration (SQLite, SSPL disabled, external services optional), Core Integrator behavior is deterministic, predictable, and safe for demonstration purposes. All documented endpoints function correctly with or without external service availability.

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-02  
**Authority Status:** FROZEN  
**Modification Policy:** Critical fixes only, no feature expansion, no behavioral drift
