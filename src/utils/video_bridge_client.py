import requests
from typing import Dict, Any, Optional
from .logger import setup_logger
import os


class VideoBridgeClient:
    """Client for text-to-video service integration"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv(
            "VIDEO_SERVICE_URL",
            "http://localhost:5002"
        )
        self.logger = setup_logger(__name__)
        self.timeout = int(os.getenv("VIDEO_SERVICE_TIMEOUT", "300"))
        self.max_retries = 3
    
    def generate_video(self, text: str, **kwargs) -> Dict[str, Any]:
        """Generate video from text"""
        try:
            if not text or not text.strip():
                return {
                    "success": False,
                    "error_type": "schema",
                    "error_message": "Text cannot be empty",
                    "endpoint": "/generate-video",
                    "fallback_used": False
                }
            
            payload = {
                "text": text,
                "topic": kwargs.get("topic", "general"),
                "style": kwargs.get("style", "default"),
                "duration": kwargs.get("duration", 30),
                "language": kwargs.get("language", "en")
            }
            
            self.logger.info(f"Generating video: {text[:50]}...")
            
            response = requests.post(
                f"{self.base_url}/generate-video",
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            result = response.json()
            
            self.logger.info(f"Video generation started: {result.get('generation_id')}")
            return result
            
        except requests.exceptions.Timeout:
            self.logger.error("Video generation timeout")
            return {
                "success": False,
                "error_type": "network",
                "error_message": "Video service timeout",
                "endpoint": "/generate-video",
                "fallback_used": True
            }
        except requests.exceptions.ConnectionError:
            self.logger.error("Cannot connect to video service")
            return {
                "success": False,
                "error_type": "network",
                "error_message": "Cannot connect to video service",
                "endpoint": "/generate-video",
                "fallback_used": True
            }
        except Exception as e:
            self.logger.error(f"Video generation failed: {e}")
            return {
                "success": False,
                "error_type": "unexpected",
                "error_message": str(e),
                "endpoint": "/generate-video",
                "fallback_used": True
            }
    
    def get_video_status(self, generation_id: str) -> Dict[str, Any]:
        """Get video generation status"""
        try:
            if not generation_id:
                return {
                    "success": False,
                    "error_type": "schema",
                    "error_message": "generation_id is required"
                }
            
            response = requests.get(
                f"{self.base_url}/status/{generation_id}",
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return {
                "success": False,
                "error_type": "network",
                "error_message": str(e)
            }
    
    def submit_feedback(self, generation_id: str, rating: int, 
                       comment: Optional[str] = None) -> Dict[str, Any]:
        """Submit feedback for generated video"""
        try:
            if not generation_id:
                return {
                    "success": False,
                    "error_type": "schema",
                    "error_message": "generation_id is required"
                }
            
            if not 1 <= rating <= 5:
                return {
                    "success": False,
                    "error_type": "schema",
                    "error_message": "Rating must be between 1 and 5"
                }
            
            payload = {
                "generation_id": generation_id,
                "rating": rating,
                "comment": comment or ""
            }
            
            response = requests.post(
                f"{self.base_url}/feedback",
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Feedback submission failed: {e}")
            return {
                "success": False,
                "error_type": "network",
                "error_message": str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check video service health"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def is_healthy(self) -> bool:
        """Check if video service is healthy"""
        health = self.health_check()
        return health.get("status") == "healthy"
