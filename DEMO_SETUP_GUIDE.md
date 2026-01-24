# 🎬 Complete Demo Setup Guide

This guide walks you through setting up and running a complete working demo of the Core Integrator with Text-to-Video integration.

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- Git
- Your friend's text-to-video project

## 🚀 Quick Start (5 minutes)

### Step 1: Start Core Integrator (Already Running)

The Core Integrator is already running on port 8001. Verify it:

```bash
curl http://localhost:8001/system/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-19T...",
  "components": {...}
}
```

### Step 2: Setup Text-to-Video Service

Your friend's text-to-video project should expose these endpoints:

```bash
# Clone or copy your friend's project
cd text-to-video-project

# Install dependencies
pip install -r requirements.txt

# Run on port 5002
python app.py
```

The service should respond to:
```bash
curl http://localhost:5002/health
```

### Step 3: Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will open at http://localhost:3000

## 📊 System Architecture for Demo

```
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (React)                           │
│                   http://localhost:3000                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Requests
                         │
                         ▼
            ┌────────────────────────────┐
            │   Core Integrator API      │
            │   http://localhost:8001    │
            │   (FastAPI)                │
            └────────────┬───────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    ┌────────┐      ┌──────────┐    ┌──────────┐
    │Finance │      │Education │    │ Video    │
    │Agent   │      │Agent     │    │Agent     │
    └────────┘      └──────────┘    └────┬─────┘
                                         │
                                    ┌────▼─────┐
                                    │Bridge    │
                                    │Client    │
                                    └────┬─────┘
                                         │
                                    ┌────▼──────────────┐
                                    │Text-to-Video      │
                                    │Service            │
                                    │Port 5002          │
                                    │(Your Friend's)    │
                                    └───────────────────┘
```

## 🔧 Detailed Setup Instructions

### Part 1: Prepare Your Friend's Text-to-Video Service

Your friend's service needs to implement these endpoints:

#### 1. POST /generate-video
```bash
curl -X POST http://localhost:5002/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "A robot walking through a futuristic city",
    "topic": "sci-fi",
    "style": "cinematic",
    "duration": 30
  }'
```

Expected response:
```json
{
  "generation_id": "vid_12345",
  "video_url": "/videos/vid_12345.mp4",
  "status": "processing",
  "metadata": {
    "model": "text-to-video-v1",
    "timestamp": "2026-01-19T10:30:00Z"
  }
}
```

#### 2. GET /status/{generation_id}
```bash
curl http://localhost:5002/status/vid_12345
```

Expected response:
```json
{
  "generation_id": "vid_12345",
  "status": "completed",
  "video_url": "/videos/vid_12345.mp4",
  "progress": 100
}
```

#### 3. POST /feedback
```bash
curl -X POST http://localhost:5002/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": "vid_12345",
    "rating": 5,
    "comment": "Great video!"
  }'
```

#### 4. GET /health
```bash
curl http://localhost:5002/health
```

Expected response:
```json
{
  "status": "healthy",
  "components": {
    "video_encoder": "healthy",
    "storage": "healthy"
  }
}
```

### Part 2: Integrate Video Agent into Core Integrator

The video agent is already created at `src/agents/video.py`. Update the gateway:

Edit `src/core/gateway.py` and add:

```python
from ..agents.video import VideoAgent
from ..utils.video_bridge_client import VideoBridgeClient

class Gateway:
    def __init__(self):
        # ... existing code ...
        
        # Add video agent
        self.agents["video"] = VideoAgent()
        self.video_bridge_client = VideoBridgeClient()
        
        # ... rest of init ...
```

### Part 3: Setup Frontend

```bash
# Create React app (if not exists)
npx create-react-app frontend

# Copy the provided App.jsx and App.css
cp App.jsx frontend/src/
cp App.css frontend/src/

# Install axios
cd frontend
npm install axios

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8001" > .env

# Start frontend
npm start
```

## ✅ Testing Each Component

### Test 1: Video Service Health
```bash
curl http://localhost:5002/health
# Should return: {"status": "healthy", ...}
```

### Test 2: Core Integrator Health
```bash
curl http://localhost:8001/system/health
# Should return: {"status": "healthy", ...}
```

### Test 3: Generate Video via API
```bash
curl -X POST http://localhost:8001/core \
  -H "Content-Type: application/json" \
  -d '{
    "module": "video",
    "intent": "generate",
    "user_id": "test_user",
    "data": {
      "text": "A beautiful sunset over the ocean"
    }
  }'
```

Expected response:
```json
{
  "status": "success",
  "result": {
    "generation_id": "vid_...",
    "status": "processing"
  }
}
```

### Test 4: Check Video Status
```bash
curl -X POST http://localhost:8001/core \
  -H "Content-Type: application/json" \
  -d '{
    "module": "video",
    "intent": "get_status",
    "user_id": "test_user",
    "data": {
      "generation_id": "vid_..."
    }
  }'
```

### Test 5: Submit Feedback
```bash
curl -X POST http://localhost:8001/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": "vid_...",
    "command": "+1",
    "user_id": "test_user"
  }'
```

## 🎯 Running the Complete Demo

### Terminal 1: Start Core Integrator
```bash
# Already running on port 8001
# If not, run:
python main.py
```

### Terminal 2: Start Text-to-Video Service
```bash
cd text-to-video-project
python app.py  # Should run on port 5002
```

### Terminal 3: Start Frontend
```bash
cd frontend
npm start  # Opens http://localhost:3000
```

### Terminal 4: Monitor Logs (Optional)
```bash
# Watch Core Integrator logs
tail -f logs/core_integrator.log

# Or watch video service logs
tail -f text-to-video-project/logs/app.log
```

## 🎬 Demo Workflow

1. **Open Frontend**: http://localhost:3000
2. **Enter Text**: "A robot dancing in a disco"
3. **Click Generate**: Watch the status update
4. **Wait for Video**: Frontend polls for completion
5. **View Video**: Video displays when ready
6. **Rate Video**: Click stars to rate (1-5)
7. **Submit Feedback**: Click "Submit Feedback"
8. **Check History**: View previous videos in sidebar

## 📊 Expected Demo Flow

```
User Input
    ↓
Frontend sends POST /core
    ↓
Core Integrator routes to VideoAgent
    ↓
VideoAgent calls VideoBridgeClient
    ↓
VideoBridgeClient calls text-to-video service
    ↓
Service generates video (returns generation_id)
    ↓
Frontend polls for status
    ↓
Service completes video
    ↓
Frontend displays video
    ↓
User rates and submits feedback
    ↓
Feedback stored in database
```

## 🐛 Troubleshooting

### Issue: CORS Error
**Solution**: Add CORS middleware to FastAPI
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Video Service Not Responding
**Solution**: Check if service is running
```bash
curl http://localhost:5002/health
# If fails, restart the service
```

### Issue: Frontend Can't Connect to API
**Solution**: Check environment variable
```bash
# In frontend/.env
REACT_APP_API_URL=http://localhost:8001
```

### Issue: Video Generation Timeout
**Solution**: Increase timeout in VideoBridgeClient
```python
self.timeout = 600  # 10 minutes
```

### Issue: Database Errors
**Solution**: Ensure database is initialized
```bash
# SQLite will auto-create
# For MongoDB, ensure connection string is correct
```

## 📈 Performance Tips

1. **Use SQLite for Development**: Faster than MongoDB
2. **Enable Caching**: Cache video URLs
3. **Optimize Video Size**: Compress videos before serving
4. **Use CDN**: Serve videos from CDN in production
5. **Implement Pagination**: Limit history to 10 items

## 🔐 Security for Demo

For demo purposes, security is minimal. For production:

1. **Enable SSPL**: Set `SSPL_ENABLED=true`
2. **Add Authentication**: Implement JWT tokens
3. **Rate Limiting**: Limit requests per user
4. **Input Validation**: Sanitize all inputs
5. **HTTPS**: Use HTTPS in production

## 📚 File Structure

```
Core-Integrator/
├── main.py                          # FastAPI app
├── src/
│   ├── agents/
│   │   ├── video.py                 # NEW: Video agent
│   │   ├── finance.py
│   │   ├── education.py
│   │   └── creator.py
│   ├── utils/
│   │   ├── video_bridge_client.py   # NEW: Video client
│   │   ├── bridge_client.py
│   │   └── ...
│   └── ...
├── frontend/                        # NEW: React app
│   ├── src/
│   │   ├── App.jsx                  # NEW: Main component
│   │   ├── App.css                  # NEW: Styling
│   │   └── ...
│   └── package.json
└── ...
```

## 🎉 Success Criteria

Your demo is working when:

- ✅ Frontend loads at http://localhost:3000
- ✅ Can enter text and click "Generate Video"
- ✅ Status updates show "Processing..."
- ✅ Video displays when ready
- ✅ Can rate video (1-5 stars)
- ✅ Can submit feedback
- ✅ History shows previous videos
- ✅ No console errors
- ✅ All services respond to health checks

## 🚀 Next Steps

1. **Customize Styling**: Update App.css with your branding
2. **Add More Features**: Implement video editing, sharing
3. **Optimize Performance**: Add caching, compression
4. **Deploy**: Use Docker, Kubernetes for production
5. **Monitor**: Add logging, metrics, alerts

## 📞 Support

If you encounter issues:

1. Check service logs
2. Verify all ports are correct
3. Ensure all services are running
4. Check network connectivity
5. Review error messages in browser console

---

**Ready to demo? Start with "Quick Start" above!**
