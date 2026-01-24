# 🎬 Text-to-Video Integration - Complete Guide

## 📖 What This Is

A complete guide to integrate your friend's **text-to-video service** into the **Core Integrator** system and connect a **React frontend** for a working demo.

## 🎯 What You'll Have

```
A complete end-to-end system:

Frontend (React)
    ↓
Core Integrator API (FastAPI)
    ↓
Video Service (Your Friend's)
    ↓
Database (SQLite/MongoDB)

With:
✅ Beautiful UI for text input
✅ Real-time video generation
✅ Video playback
✅ Rating & feedback system
✅ Generation history
✅ Database persistence
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `QUICK_REFERENCE.md` | 3-step quick start |
| `TEXT_TO_VIDEO_INTEGRATION_GUIDE.md` | Detailed integration steps |
| `DEMO_SETUP_GUIDE.md` | Complete setup instructions |
| `INTEGRATION_SUMMARY.md` | Overview & workflow |
| `ARCHITECTURE_DIAGRAM.md` | Visual system architecture |
| `PROJECT_DETAILED_EXPLANATION.md` | System deep dive |

## 🚀 Quick Start (5 minutes)

### 1. Prepare Your Friend's Service

Your friend's text-to-video project needs to run on **port 5002** and expose 4 endpoints:

```bash
# Start video service
cd text-to-video-project
python app.py  # Runs on port 5002
```

**Required endpoints:**
- `POST /generate-video` - Generate video from text
- `GET /status/{id}` - Check generation status
- `POST /feedback` - Accept user feedback
- `GET /health` - Health check

### 2. Update Core Integrator

Edit `src/core/gateway.py` and add 2 lines:

```python
self.agents["video"] = VideoAgent()
self.video_bridge_client = VideoBridgeClient()
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm start  # Opens http://localhost:3000
```

## 🎬 Running the Demo

**Terminal 1: Video Service**
```bash
cd text-to-video-project
python app.py
```

**Terminal 2: Core Integrator** (Already running)
```bash
python main.py
```

**Terminal 3: Frontend**
```bash
cd frontend
npm start
```

Then open: **http://localhost:3000**

## 📊 System Ports

| Service | Port | Status |
|---------|------|--------|
| Frontend | 3000 | Ready |
| Core Integrator | 8001 | ✅ Running |
| CreatorCore | 5001 | ✅ Running |
| Video Service | 5002 | ⏳ Setup needed |

## 🔌 How It Works

```
1. User enters text in frontend
2. Clicks "Generate Video"
3. Frontend sends request to Core Integrator
4. Core Integrator routes to VideoAgent
5. VideoAgent calls VideoBridgeClient
6. VideoBridgeClient calls your friend's service
7. Service generates video
8. Frontend polls for status
9. Video displays when ready
10. User rates and submits feedback
11. Feedback stored in database
```

## 📁 Files Created

**New Agent:**
- `src/agents/video.py` - Handles video requests

**New Client:**
- `src/utils/video_bridge_client.py` - Communicates with video service

**Frontend:**
- `frontend/src/App.jsx` - React component
- `frontend/src/App.css` - Styling

## ✅ Testing

### Test Video Service
```bash
curl -X POST http://localhost:5002/generate-video \
  -H "Content-Type: application/json" \
  -d '{"text": "A robot dancing"}'
```

### Test Core Integrator
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

### Test Frontend
Open http://localhost:3000 and test the UI

## 🎯 Demo Workflow

```
User enters: "A robot dancing in a disco"
    ↓
Clicks "Generate Video"
    ↓
Status shows "Processing..."
    ↓
Video displays (after generation)
    ↓
User clicks stars to rate
    ↓
User clicks "Submit Feedback"
    ↓
Video added to history
    ↓
Ready for next video!
```

## 🔐 Security

For demo: Minimal security
For production:
- Enable SSPL authentication
- Add JWT tokens
- Implement rate limiting
- Validate all inputs
- Use HTTPS

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS error | Add CORS middleware to FastAPI |
| Can't connect | Check port/firewall |
| Video not generating | Check video service logs |
| Timeout | Increase timeout value |
| Database error | Restart service |

## 📈 Performance

- Video generation: 30-300 seconds (depends on service)
- Frontend polling: Every 1-5 seconds
- Database: SQLite (local) or MongoDB (cloud)
- Caching: Implemented for video URLs

## 🚀 Deployment

For production:
1. Use Gunicorn/uWSGI for FastAPI
2. Use Nginx as reverse proxy
3. Deploy to AWS/GCP/Azure
4. Use MongoDB Atlas for database
5. Use CDN for video delivery
6. Enable HTTPS/SSL
7. Setup monitoring & logging

## 📚 Full Documentation

For detailed information, see:

- **Quick Start**: `QUICK_REFERENCE.md`
- **Integration Guide**: `TEXT_TO_VIDEO_INTEGRATION_GUIDE.md`
- **Setup Instructions**: `DEMO_SETUP_GUIDE.md`
- **System Overview**: `INTEGRATION_SUMMARY.md`
- **Architecture**: `ARCHITECTURE_DIAGRAM.md`
- **Deep Dive**: `PROJECT_DETAILED_EXPLANATION.md`

## 🎉 Success Criteria

Your demo is working when:

✅ Frontend loads at http://localhost:3000  
✅ Can enter text and generate videos  
✅ Videos display when ready  
✅ Can rate and submit feedback  
✅ History shows previous videos  
✅ No errors in console  
✅ All services healthy  

## 📞 Next Steps

1. **Prepare your friend's service** - Implement 4 endpoints
2. **Update gateway** - Add video agent (2 lines)
3. **Setup frontend** - Run npm start
4. **Test each component** - Use curl commands
5. **Run complete demo** - Open frontend and test
6. **Customize** - Add your branding
7. **Deploy** - Move to production

## 🎬 Ready?

1. Start video service: `python app.py` (port 5002)
2. Start frontend: `npm start` (port 3000)
3. Open http://localhost:3000
4. Enter text and generate videos!

---

**That's it! You now have a complete working demo!**

For more details, check the documentation files listed above.
