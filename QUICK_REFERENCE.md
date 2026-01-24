# 🚀 Quick Reference Card

## 3-Step Integration

### Step 1: Your Friend's Service (Port 5002)
```bash
cd text-to-video-project
python app.py
```

Needs these endpoints:
- `POST /generate-video` → Returns `generation_id`
- `GET /status/{id}` → Returns video status
- `POST /feedback` → Accepts rating
- `GET /health` → Health check

### Step 2: Update Gateway (2 lines)
Edit `src/core/gateway.py`:
```python
self.agents["video"] = VideoAgent()
self.video_bridge_client = VideoBridgeClient()
```

### Step 3: Start Frontend (Port 3000)
```bash
cd frontend
npm install
npm start
```

## 🎯 Running Demo

```bash
# Terminal 1: Video Service
cd text-to-video-project && python app.py

# Terminal 2: Core Integrator (already running)
python main.py

# Terminal 3: Frontend
cd frontend && npm start
```

Then open: **http://localhost:3000**

## 📊 System Ports

| Service | Port | Status |
|---------|------|--------|
| Frontend | 3000 | Ready to start |
| Core Integrator | 8001 | ✅ Running |
| CreatorCore | 5001 | ✅ Running |
| Video Service | 5002 | ⏳ Needs setup |

## 🔌 API Calls

### Generate Video
```bash
curl -X POST http://localhost:8001/core \
  -H "Content-Type: application/json" \
  -d '{
    "module": "video",
    "intent": "generate",
    "user_id": "user_123",
    "data": {"text": "A robot dancing"}
  }'
```

### Check Status
```bash
curl -X POST http://localhost:8001/core \
  -H "Content-Type: application/json" \
  -d '{
    "module": "video",
    "intent": "get_status",
    "user_id": "user_123",
    "data": {"generation_id": "vid_123"}
  }'
```

### Submit Feedback
```bash
curl -X POST http://localhost:8001/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": "vid_123",
    "command": "+1",
    "user_id": "user_123"
  }'
```

## 📁 Files Created

```
src/agents/video.py                    # Video agent
src/utils/video_bridge_client.py       # Video client
frontend/src/App.jsx                   # React UI
frontend/src/App.css                   # Styling
```

## ✅ Verification

```bash
# Check all services
curl http://localhost:3000              # Frontend
curl http://localhost:8001/system/health  # Core Integrator
curl http://localhost:5001/              # CreatorCore
curl http://localhost:5002/health        # Video Service
```

## 🎬 Demo Flow

```
User enters text
    ↓
Clicks "Generate"
    ↓
Frontend → Core Integrator
    ↓
Core Integrator → Video Service
    ↓
Video Service generates video
    ↓
Frontend polls for status
    ↓
Video displays
    ↓
User rates & submits feedback
    ↓
Done!
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| CORS error | Add CORS middleware |
| Can't connect | Check port/firewall |
| Video not generating | Check video service logs |
| Timeout | Increase timeout value |
| Database error | Restart service |

## 📚 Full Guides

- `TEXT_TO_VIDEO_INTEGRATION_GUIDE.md` - Complete guide
- `DEMO_SETUP_GUIDE.md` - Detailed setup
- `INTEGRATION_SUMMARY.md` - Overview
- `PROJECT_DETAILED_EXPLANATION.md` - Architecture

## 🎉 Success = All 3 Running

✅ Video Service (5002)  
✅ Core Integrator (8001)  
✅ Frontend (3000)  

Then: Open http://localhost:3000 and test!

---

**Need help? Check the full guides above!**
