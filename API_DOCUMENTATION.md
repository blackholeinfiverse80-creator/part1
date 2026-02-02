# Core Integrator Sprint API Documentation

**Base URL**: `https://core-integrator-sprint.onrender.com`

## 📋 Complete Endpoint List

### **1. Root Endpoint**
```
GET /
```
**Sample Response:**
```json
{
  "message": "Unified Backend Bridge API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### **2. Main Processing Endpoint**
```
POST /core
```
**Sample Request:**
```json
{
  "module": "sample_text",
  "intent": "generate",
  "user_id": "test_user",
  "data": {
    "text": "Hello World",
    "context": "greeting"
  }
}
```

**Finance Module:**
```json
{
  "module": "finance",
  "intent": "analyze",
  "user_id": "user123",
  "data": {
    "amount": 1000,
    "category": "investment"
  }
}
```

**Education Module:**
```json
{
  "module": "education",
  "intent": "learn",
  "user_id": "student1",
  "data": {
    "topic": "mathematics",
    "level": "beginner"
  }
}
```

**Creator Module:**
```json
{
  "module": "creator",
  "intent": "generate",
  "user_id": "creator1",
  "data": {
    "type": "content",
    "prompt": "Write a blog post about AI"
  }
}
```

### **3. User History**
```
GET /get-history?user_id=test_user
```

### **4. User Context**
```
GET /get-context?user_id=test_user
```

### **5. Feedback Submission**
```
POST /feedback
```
**Sample Request:**
```json
{
  "user_id": "test_user",
  "generation_id": "gen_123",
  "rating": 5,
  "feedback_text": "Great response!",
  "feedback_type": "positive"
}
```

### **6. Creator History**
```
GET /creator/history?user_id=creator1
```

### **7. System Health**
```
GET /system/health
```
**Sample Response:**
```json
{
  "status": "ok",
  "dependencies": {
    "database": "up",
    "gateway": "up",
    "noopur": "disabled",
    "video_service": "disabled"
  },
  "timestamp": "2026-02-02T12:00:00Z"
}
```

### **8. System Diagnostics**
```
GET /system/diagnostics
```

### **9. System Logs**
```
GET /system/logs/latest?limit=50
```

### **10. API Documentation**
```
GET /docs
```

## 🧪 Quick Test Commands

**1. Basic Health Check:**
```bash
curl https://core-integrator-sprint.onrender.com/system/health
```

**2. Sample Text Processing:**
```bash
curl -X POST https://core-integrator-sprint.onrender.com/core \
  -H "Content-Type: application/json" \
  -d '{
    "module": "sample_text",
    "intent": "generate",
    "user_id": "test_user",
    "data": {"text": "Hello World"}
  }'
```

**3. Finance Analysis:**
```bash
curl -X POST https://core-integrator-sprint.onrender.com/core \
  -H "Content-Type: application/json" \
  -d '{
    "module": "finance",
    "intent": "analyze",
    "user_id": "user123",
    "data": {"amount": 1000, "category": "investment"}
  }'
```

**4. Get User History:**
```bash
curl "https://core-integrator-sprint.onrender.com/get-history?user_id=test_user"
```

**5. Submit Feedback:**
```bash
curl -X POST https://core-integrator-sprint.onrender.com/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "generation_id": "gen_123",
    "rating": 5,
    "feedback_text": "Excellent!"
  }'
```

## 📊 Available Modules
- `sample_text` - Text processing
- `finance` - Financial analysis
- `education` - Educational content
- `creator` - Content creation
- `video` - Video generation (disabled in deployment)

## 🔧 Response Format
All endpoints return JSON responses with proper error handling and security validation.

**Success Response:**
```json
{
  "status": "success",
  "message": "Request processed",
  "result": { ... }
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

## 🚀 Live Testing
Visit the interactive API documentation at:
`https://core-integrator-sprint.onrender.com/docs`