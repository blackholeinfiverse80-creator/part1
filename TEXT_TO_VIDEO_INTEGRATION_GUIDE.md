# Text-to-Video Integration Guide

## 🎬 Overview

This guide explains how to integrate your friend's text-to-video project into the Core Integrator system and connect a frontend for a working demo.

## 📊 Current System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React/Vue)                      │
│                    (To be created)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │   Core Integrator API      │
            │   (FastAPI, Port 8001)     │
            └────────────┬───────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    ┌────────┐      ┌──────────┐    ┌──────────┐
    │Finance │      │Education │    │ Creator  │
    │Agent   │      │Agent     │    │Agent     │
    └────────┘      └──────────┘    └────┬─────┘
                                         │
                                    ┌────▼─────┐
                                    │Bridge    │
                                    │Client    │
                                    └────┬─────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │                                │                                │
        ▼                                ▼                                ▼
    ┌──────────┐                  ┌──────────────┐              ┌──────────────┐
    │CreatorCore                  │Text-to-Video │              │ Database     │
    │Backend                      │Service       │              │(MongoDB/SQLite)
    │(Port 5001)                  │(Port 5002)   │              │              │
    │                             │(NEW)         │              │              │
    └──────────┘                  └──────────────┘              └──────────────┘
```

## 🔧 Step 1: Prepare Your Text-to-Video Service

Your friend's text-to-video project needs to expose a REST API. Here's the required interface:

### Required Endpoints

**POST /generate-video**
```json
Request:
{
  "text": "string (required) - Text to convert to video",
  "topic": "string (optional) - Video topic",
  "style": "string (optional) - Video style/theme",
  "duration": "integer (optional) - Video duration in seconds",
  "language": "string (optional) - Language code"
}

Response:
{
  "generation_id": "string (REQUIRED - unique video ID)",
  "video_url": "string - URL to generated video",
  "video_path": "string - Local file path",
  "duration": "integer - Actual video duration",
  "status": "completed|processing|failed",
  "metadata": {
    "model": "string",
    "timestamp": "ISO 8601",
    "frames": "integer"
  }
}
```

**POST /feedback**
```json
Request:
{
  "generation_id": "string (required)",
  "rating": "integer (1-5)",
  "comment": "string (optional)"
}

Response:
{
  "status": "success|error",
  "message": "string"
}
```

**GET /health**
```json
Response:
{
  "status": "healthy|unhealthy",
  "timestamp": "ISO 8601",
  "components": {
    "video_encoder": "healthy|unhealthy",
    "storage": "healthy|unhealthy"
  }
}
```

## 🔌 Step 2: Create a Video Agent

Create `src/agents/video.py`:

```python
from typing import Dict, Any, List
from .base import BaseAgent
from ..utils.logger import setup_logger

class VideoAgent(BaseAgent):
    """Agent for text-to-video generation"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def handle_request(self, intent: str, data: Dict[str, Any], 
                      context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle video generation requests"""
        
        if intent == "generate":
            return self._generate_video(data)
        elif intent == "get_status":
            return self._get_status(data)
        else:
            return {"status": "error", "message": f"Unknown intent: {intent}"}
    
    def _generate_video(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video from text"""
        try:
            text = data.get("text")
            if not text:
                return {"status": "error", "message": "Text is required"}
            
            return {
                "status": "success",
                "message": "Video generation started",
                "result": {
                    "generation_id": f"vid_{hash(text)}",
                    "status": "processing"
                }
            }
        except Exception as e:
            self.logger.error(f"Video generation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get video generation status"""
        generation_id = data.get("generation_id")
        return {
            "status": "success",
            "result": {
                "generation_id": generation_id,
                "status": "completed"
            }
        }
```

## 🌉 Step 3: Create Video BridgeClient Extension

Create `src/utils/video_bridge_client.py`:

```python
import requests
from typing import Dict, Any, Optional
from .logger import setup_logger

class VideoBridgeClient:
    """Client for text-to-video service integration"""
    
    def __init__(self, base_url: str = "http://localhost:5002"):
        self.base_url = base_url
        self.logger = setup_logger(__name__)
        self.timeout = 300  # 5 minutes for video generation
    
    def generate_video(self, text: str, **kwargs) -> Dict[str, Any]:
        """Generate video from text"""
        try:
            payload = {
                "text": text,
                **kwargs
            }
            response = requests.post(
                f"{self.base_url}/generate-video",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Video generation failed: {e}")
            return {
                "success": False,
                "error_type": "network",
                "error_message": str(e)
            }
    
    def get_video_status(self, generation_id: str) -> Dict[str, Any]:
        """Get video generation status"""
        try:
            response = requests.get(
                f"{self.base_url}/status/{generation_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check video service health"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.json()
        except Exception:
            return {"status": "unhealthy"}
```

## 🔄 Step 4: Update Gateway to Support Video Agent

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

## 📱 Step 5: Create Frontend (React Example)

Create `frontend/src/App.jsx`:

```jsx
import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8001';

function App() {
  const [text, setText] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [generationId, setGenerationId] = useState('');
  const [rating, setRating] = useState(0);

  const generateVideo = async () => {
    if (!text.trim()) {
      alert('Please enter text');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/core`, {
        module: 'video',
        intent: 'generate',
        user_id: 'user_123',
        data: {
          text: text,
          topic: 'general',
          style: 'cinematic'
        }
      });

      if (response.data.status === 'success') {
        const genId = response.data.result.generation_id;
        setGenerationId(genId);
        
        // Poll for video URL
        pollVideoStatus(genId);
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const pollVideoStatus = async (genId) => {
    let attempts = 0;
    const maxAttempts = 60; // 5 minutes with 5-second intervals

    const poll = async () => {
      try {
        const response = await axios.post(`${API_BASE}/core`, {
          module: 'video',
          intent: 'get_status',
          user_id: 'user_123',
          data: { generation_id: genId }
        });

        if (response.data.result.status === 'completed') {
          setVideoUrl(response.data.result.video_url);
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 5000);
        }
      } catch (error) {
        console.error('Poll error:', error);
      }
    };

    poll();
  };

  const submitFeedback = async () => {
    if (!generationId || rating === 0) {
      alert('Please rate the video');
      return;
    }

    try {
      await axios.post(`${API_BASE}/feedback`, {
        generation_id: generationId,
        command: rating > 3 ? '+1' : '-1',
        user_id: 'user_123'
      });
      alert('Feedback submitted!');
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  return (
    <div className="App">
      <h1>🎬 Text-to-Video Generator</h1>
      
      <div className="input-section">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to convert to video..."
          rows="4"
        />
        <button onClick={generateVideo} disabled={loading}>
          {loading ? 'Generating...' : 'Generate Video'}
        </button>
      </div>

      {videoUrl && (
        <div className="video-section">
          <h2>Generated Video</h2>
          <video width="400" controls>
            <source src={videoUrl} type="video/mp4" />
          </video>
          
          <div className="feedback-section">
            <h3>Rate this video:</h3>
            <div className="rating">
              {[1, 2, 3, 4, 5].map((star) => (
                <span
                  key={star}
                  onClick={() => setRating(star)}
                  className={star <= rating ? 'star active' : 'star'}
                >
                  ⭐
                </span>
              ))}
            </div>
            <button onClick={submitFeedback}>Submit Feedback</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
```

## 🚀 Step 6: Setup & Run Everything

### 1. Setup Text-to-Video Service
```bash
# In your friend's project directory
cd text-to-video-project
pip install -r requirements.txt
python app.py  # Should run on port 5002
```

### 2. Update Core Integrator
```bash
# In Core Integrator directory
pip install -r requirements.txt
python main.py  # Runs on port 8001
```

### 3. Setup Frontend
```bash
# Create React app
npx create-react-app frontend
cd frontend

# Install dependencies
npm install axios

# Copy App.jsx to src/
# Update App.css with styling

# Run frontend
npm start  # Runs on port 3000
```

## 📋 Configuration

### .env file
```bash
# Core Integrator
SSPL_ENABLED=false
USE_MONGODB=false

# Video Service
VIDEO_SERVICE_URL=http://localhost:5002
VIDEO_SERVICE_TIMEOUT=300

# Frontend
REACT_APP_API_URL=http://localhost:8001
```

## ✅ Testing the Integration

### 1. Test Video Service
```bash
curl -X POST http://localhost:5002/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "A robot walking through a futuristic city",
    "style": "cinematic"
  }'
```

### 2. Test Core Integrator
```bash
curl -X POST http://localhost:8001/core \
  -H "Content-Type: application/json" \
  -d '{
    "module": "video",
    "intent": "generate",
    "user_id": "user_123",
    "data": {
      "text": "A robot walking through a futuristic city"
    }
  }'
```

### 3. Test Frontend
- Open http://localhost:3000
- Enter text
- Click "Generate Video"
- Wait for video to generate
- Rate and submit feedback

## 🎯 Demo Workflow

1. **User enters text** in frontend
2. **Frontend sends request** to Core Integrator `/core` endpoint
3. **Gateway routes** to VideoAgent
4. **VideoAgent calls** VideoBridgeClient
5. **VideoBridgeClient** communicates with text-to-video service
6. **Service generates** video and returns generation_id
7. **Frontend polls** for video status
8. **Video displays** when ready
9. **User rates** video
10. **Feedback stored** in database for future improvements

## 📊 Data Flow Diagram

```
Frontend (React)
    │
    ├─ POST /core (generate request)
    │
    ▼
Core Integrator (FastAPI)
    │
    ├─ Gateway routes to VideoAgent
    │
    ▼
VideoAgent
    │
    ├─ Calls VideoBridgeClient
    │
    ▼
VideoBridgeClient
    │
    ├─ HTTP POST to text-to-video service
    │
    ▼
Text-to-Video Service
    │
    ├─ Generates video
    ├─ Returns generation_id + video_url
    │
    ▼
Response back through chain
    │
    ├─ Stored in database
    ├─ Returned to frontend
    │
    ▼
Frontend displays video
    │
    ├─ User rates video
    ├─ POST /feedback
    │
    ▼
Feedback stored for ML training
```

## 🔐 Security Considerations

1. **CORS Configuration** - Allow frontend origin
2. **Rate Limiting** - Prevent abuse
3. **Input Validation** - Sanitize text input
4. **File Storage** - Secure video storage
5. **Authentication** - Add user authentication

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS errors | Add CORS middleware to FastAPI |
| Video not generating | Check text-to-video service logs |
| Timeout errors | Increase timeout in VideoBridgeClient |
| Frontend can't reach API | Check firewall and CORS settings |
| Database errors | Ensure SQLite/MongoDB is running |

## 📚 Next Steps

1. Integrate your friend's text-to-video service
2. Test each component individually
3. Run the full demo
4. Add authentication
5. Deploy to production
6. Monitor performance and errors

---

**Ready to integrate? Start with Step 1!**
