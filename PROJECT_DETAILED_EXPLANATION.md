# Core Integrator - Detailed Project Explanation

## 🎯 Project Overview

**Core Integrator** is a production-ready, enterprise-grade backend orchestration system that acts as a central hub for multiple AI agents and external services. It's built with FastAPI and designed to handle complex workflows involving content generation, feedback processing, and contextual memory management.

**Current Status**: Production Ready (v1.0.0)  
**Architecture**: Microservices with BridgeClient integration pattern  
**Primary Language**: Python (FastAPI + SQLite/MongoDB)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER REQUESTS                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   FastAPI      │
                    │   (Port 8001)  │
                    └────────┬───────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌────────┐          ┌────────┐          ┌────────┐
    │ /core  │          │/feedback│         │/health │
    │endpoint│          │endpoint │         │endpoint│
    └────┬───┘          └────┬───┘          └────┬───┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │    GATEWAY      │
                    │  (Routing Hub)  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌─────────┐         ┌──────────┐        ┌──────────┐
    │ Finance │         │Education │        │ Creator  │
    │ Agent   │         │ Agent    │        │ Agent    │
    └────┬────┘         └────┬─────┘        └────┬─────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │  BridgeClient   │
                    │ (Integration    │
                    │  Surface)       │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │ MongoDB  │        │ SQLite   │        │CreatorCore
    │ (Primary)│        │(Fallback)│        │Backend   │
    └──────────┘        └──────────┘        │(Port5001)│
                                            └──────────┘
```

---

## 📦 Core Components

### 1. **FastAPI Application** (`main.py`)
- **Purpose**: HTTP server and request routing
- **Port**: 8001
- **Key Features**:
  - RESTful API endpoints
  - Security middleware integration
  - SSPL (Server Side Public License) support
  - Request validation and sanitization

**Main Endpoints**:
```
POST   /core              - Main processing endpoint
POST   /feedback          - Feedback submission
GET    /get-context      - Retrieve user context
GET    /get-history      - Get interaction history
GET    /system/health    - Health check
GET    /system/diagnostics - Integration readiness
```

### 2. **Gateway** (`src/core/gateway.py`)
- **Purpose**: Central routing and orchestration
- **Responsibilities**:
  - Route requests to appropriate agents
  - Manage agent lifecycle
  - Handle external service communication via BridgeClient
  - Validate feedback against canonical schema
  - Monitor external service health

**Key Methods**:
```python
process_request()           # Route to appropriate agent
check_external_service_health()  # Monitor CreatorCore backend
validate_feedback()         # Validate feedback schema
```

### 3. **Agent System** (`src/agents/`)
Three specialized agents handle domain-specific logic:

#### **Finance Agent** (`finance.py`)
- Handles financial calculations and analysis
- Processes financial queries and recommendations
- Manages financial context and history

#### **Education Agent** (`education.py`)
- Manages educational content and learning paths
- Processes educational queries
- Tracks learning progress

#### **Creator Agent** (`creator.py`)
- Handles creative content generation
- Manages creative workflows
- Integrates with CreatorCore backend via BridgeClient

**Agent Base Class**:
```python
class BaseAgent(ABC):
    def handle_request(self, intent: str, data: Dict, context: List) -> Dict:
        """Process request and return response"""
```

### 4. **BridgeClient** (`src/utils/bridge_client.py`)
- **Purpose**: Canonical integration surface for external services
- **Version**: 1.0.0
- **Target Service**: CreatorCore Backend (Port 5001)

**Public Methods**:
```python
generate(payload)       # POST /generate
feedback(payload)       # POST /feedback
history(topic)          # GET /history
get_context(limit)      # GET /core/context
log(data)              # POST /core/log
health_check()         # GET /system/health
is_healthy()           # Boolean wrapper
```

**Error Handling**:
- Network errors → fallback response
- Schema validation errors → detailed error response
- Retry logic with exponential backoff
- Deterministic error classification (network, logic, schema, unexpected)

### 5. **Database Layer** (`src/db/`)

#### **Memory Adapter** (`memory.py`)
- SQLite-based context memory
- Stores user interactions and generations
- Thread-safe with WAL mode enabled
- Supports concurrent access

**Tables**:
```sql
interactions (id, user_id, module, timestamp, request_data, response_data)
generations (generation_id, user_id, interaction_id, created_at, payload)
```

#### **Multi-Database Support**:
1. **MongoDB Adapter** (Primary) - Cloud-based, scalable
2. **Noopur Adapter** (Secondary) - Remote backend integration
3. **SQLite Adapter** (Fallback) - Local, always available

**Priority Order**: MongoDB > Noopur > SQLite

### 6. **Security Layer** (`src/utils/security_hardening.py`)
- **SSPL Phase III**: Ed25519 digital signatures
- **Nonce Replay Protection**: Prevents replay attacks
- **Request Validation**: User ID and request sanitization
- **Response Sanitization**: Removes sensitive data

**Key Features**:
```python
validate_user_request()     # Validate user identity
sanitize_response()         # Remove sensitive data
require_sspl()             # SSPL dependency injection
security_middleware()      # HTTP middleware
```

### 7. **Telemetry** (`src/utils/insightflow.py`)
- **Purpose**: Structured event logging for monitoring
- **Integration**: InsightFlow telemetry system
- **Event Types**:
  - `heartbeat` - Regular health signals
  - `integration_ready` - System ready status
  - `degraded_alert` - Service degradation warnings

**Event Structure**:
```json
{
  "insightflow_version": "1.0.0",
  "event_type": "heartbeat|integration_ready|degraded_alert",
  "component": "gateway|bridge_client|database",
  "status": "healthy|degraded|unhealthy",
  "details": {},
  "timestamp": "ISO 8601",
  "integration_score": 0.95
}
```

---

## 🔄 Request Flow

### Example: Content Generation Request

```
1. User sends POST /core
   {
     "module": "creator",
     "intent": "generate_story",
     "user_id": "user_123",
     "data": {"topic": "AI", "goal": "educate"}
   }

2. FastAPI validates request and applies security middleware

3. Gateway routes to CreatorAgent

4. CreatorAgent calls BridgeClient.generate()

5. BridgeClient makes HTTP POST to CreatorCore backend (port 5001)
   POST http://localhost:5001/generate
   {
     "prompt": "Write a story about AI",
     "topic": "AI",
     "goal": "educate",
     "type": "story"
   }

6. CreatorCore backend returns:
   {
     "generation_id": "gen_abc123",
     "generated_text": "Once upon a time...",
     "related_context": [...],
     "metadata": {...}
   }

7. Gateway stores generation mapping:
   generations table: generation_id -> interaction_id

8. Response returned to user:
   {
     "status": "success",
     "result": {
       "generation_id": "gen_abc123",
       "content": "Once upon a time...",
       "context": [...]
     }
   }
```

### Example: Feedback Flow

```
1. User sends POST /feedback
   {
     "generation_id": "gen_abc123",
     "command": "+1",
     "user_id": "user_123"
   }

2. Gateway validates against CanonicalFeedbackSchema

3. BridgeClient.feedback() called:
   POST http://localhost:5001/feedback
   {
     "generation_id": "gen_abc123",
     "command": "+1",
     "user_id": "user_123",
     "timestamp": "2026-01-19T..."
   }

4. CreatorCore backend records feedback

5. Feedback stored in local database for future context

6. Response: {"status": "success", "message": "Feedback recorded"}
```

---

## 🗄️ Data Models

### CoreRequest
```python
{
  "module": str,           # "finance", "education", "creator"
  "intent": str,           # Specific action within module
  "user_id": str,          # User identifier
  "data": Dict[str, Any]   # Module-specific data
}
```

### CoreResponse
```python
{
  "status": str,           # "success" or "error"
  "result": Dict,          # Response data
  "message": str,          # Human-readable message
  "generation_id": str     # Optional, for tracking
}
```

### CanonicalFeedbackSchema
```python
{
  "generation_id": str,    # Required - links to generation
  "command": str,          # "+2", "+1", "-1", "-2"
  "user_id": str,          # Optional
  "timestamp": str         # Optional, ISO 8601
}
```

---

## 🔐 Security Features

### 1. **SSPL Phase III**
- Ed25519 digital signatures for request authentication
- Configurable via `SSPL_ENABLED` environment variable
- Signature validation on protected endpoints

### 2. **Nonce Replay Protection**
- Prevents duplicate request processing
- Stored in `nonce_store.db`
- Automatic cleanup of expired nonces

### 3. **Request Validation**
- User ID validation
- Request data schema validation
- Pydantic models for type safety

### 4. **Response Sanitization**
- Removes sensitive fields
- Prevents information leakage
- Consistent error responses

---

## 🚀 External Integration: CreatorCore Backend

### Purpose
The CreatorCore Backend (running on port 5001) is the external service that handles actual content generation using AI models.

### Key Endpoints
```
POST /generate      - Generate creative content
POST /feedback      - Record user feedback
GET  /history       - Retrieve generation history
GET  /system/health - Health check
```

### Integration Pattern
- **BridgeClient** is the only supported integration point
- Automatic retry logic with exponential backoff
- Graceful fallback when service is unavailable
- Health monitoring and status reporting

### Configuration
```bash
INTEGRATOR_USE_NOOPUR=true
NOOPUR_BASE_URL=http://localhost:5001
```

---

## 📊 Database Schema

### interactions table
```sql
CREATE TABLE interactions (
  id INTEGER PRIMARY KEY,
  user_id TEXT NOT NULL,
  module TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  request_data TEXT NOT NULL,
  response_data TEXT NOT NULL
);
```

### generations table
```sql
CREATE TABLE generations (
  generation_id TEXT PRIMARY KEY,
  user_id TEXT,
  interaction_id INTEGER,
  created_at TEXT,
  payload TEXT
);
```

### nonce_store table
```sql
CREATE TABLE nonces (
  nonce TEXT PRIMARY KEY,
  created_at TEXT,
  expires_at TEXT
);
```

---

## 🔧 Configuration

### Environment Variables
```bash
# Security
SSPL_ENABLED=true

# Database
USE_MONGODB=true
MONGODB_CONNECTION_STRING=mongodb+srv://...
MONGODB_DATABASE_NAME=core_integrator

# External Services
INTEGRATOR_USE_NOOPUR=true
NOOPUR_BASE_URL=http://localhost:5001

# Logging
LOG_LEVEL=INFO
```

### File Structure
```
Core-Integrator/
├── main.py                          # FastAPI app entry point
├── config/
│   └── config.py                    # Configuration management
├── src/
│   ├── agents/                      # Agent implementations
│   │   ├── base.py
│   │   ├── finance.py
│   │   ├── education.py
│   │   └── creator.py
│   ├── core/                        # Core logic
│   │   ├── gateway.py               # Request routing
│   │   ├── models.py                # Data models
│   │   ├── feedback_models.py       # Feedback schema
│   │   └── module_loader.py         # Dynamic module loading
│   ├── db/                          # Database layer
│   │   ├── memory.py                # SQLite adapter
│   │   ├── memory_adapter.py        # Adapter interface
│   │   ├── mongodb_adapter.py       # MongoDB adapter
│   │   └── nonce_store.py           # Nonce management
│   ├── modules/                     # Extensible modules
│   │   └── sample_text/
│   └── utils/                       # Utilities
│       ├── bridge_client.py         # External service client
│       ├── insightflow.py           # Telemetry
│       ├── logger.py                # Logging
│       ├── security_hardening.py    # Security
│       └── sspl.py                  # SSPL implementation
├── external/
│   └── CreatorCore-Task/            # External backend
│       └── backend/
│           ├── app.py               # Flask app
│           ├── db_utils.py          # Database utilities
│           ├── embeddings_utils.py  # Vector embeddings
│           └── prompts.py           # AI prompts
└── requirements.txt
```

---

## 🧪 Testing

### Test Suite
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_ci_safe.py -v

# Run with coverage
pytest tests/ --cov=src
```

### Key Test Files
- `test_ci_safe.py` - Core integration tests (11/11 passing)
- `test_bridge_client.py` - BridgeClient functionality
- `test_feedback_flow_v2.py` - Feedback processing
- `test_noopur_integration.py` - External service integration

---

## 📈 Performance & Scalability

### Concurrency
- SQLite WAL mode for concurrent reads
- Thread-safe memory adapter
- Async FastAPI endpoints

### Fallback Strategy
- MongoDB → Noopur → SQLite
- Automatic failover on connection errors
- Health monitoring for all backends

### Rate Limiting
- Per-endpoint rate limits
- User-based throttling
- Graceful degradation under load

---

## 🎯 Key Design Decisions

### 1. **BridgeClient as First-Class Integration Surface**
- Provides stable, versioned interface
- Enables schema enforcement
- Supports ecosystem compatibility
- Allows graceful degradation

### 2. **Multi-Database Strategy**
- MongoDB for production scalability
- SQLite for local development
- Noopur for remote integration
- Automatic fallback chain

### 3. **Agent-Based Architecture**
- Modular, extensible design
- Domain-specific agents
- Shared memory and context
- Easy to add new agents

### 4. **Canonical Feedback Schema**
- Standardized feedback format
- Deterministic generation_id mapping
- Enables cross-system feedback tracking
- Supports reinforcement learning

---

## 🚀 Deployment

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run application
python main.py

# Server available at http://localhost:8001
```

### Production Deployment
- Use production WSGI server (Gunicorn, uWSGI)
- Enable SSPL security
- Configure MongoDB Atlas
- Set up monitoring and logging
- Enable rate limiting

---

## 📞 Integration Contacts

- **Ashmit** (Ecosystem Integration) → `documentation/DEPLOYMENT_GUIDE.md`
- **Noopur** (Backend API) → `documentation/NOOPUR_API_CONTRACT.md`
- **Sankalp** (Telemetry) → `documentation/INSIGHTFLOW_INTEGRATION.md`

---

## ✅ Production Status

- ✅ CI-safe test suite (11/11 passing)
- ✅ BridgeClient canonical integration
- ✅ InsightFlow telemetry active
- ✅ Multi-database fallback
- ✅ SSPL Phase III security
- ✅ Deterministic feedback mapping
- ✅ Machine-consumable signals
- ✅ No ambiguity, no dead code

---

## 🔮 Future Enhancements

1. **GraphQL API** - Alternative query interface
2. **WebSocket Support** - Real-time updates
3. **Advanced Analytics** - Usage patterns and insights
4. **ML-Based Routing** - Intelligent agent selection
5. **Distributed Tracing** - End-to-end request tracking
6. **API Versioning** - Backward compatibility management

---

This architecture provides a robust, scalable, and maintainable foundation for multi-agent AI systems with enterprise-grade security and observability.
