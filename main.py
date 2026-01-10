from fastapi import FastAPI, HTTPException, Depends, Request
from typing import List, Dict, Any, Optional
import os
import sqlite3
from pathlib import Path
from src.core.models import CoreRequest, CoreResponse
from src.core.feedback_models import FeedbackRequest
from src.core.gateway import Gateway
from src.db.memory import ContextMemory
from config.config import DB_PATH
from src.utils.security_hardening import security_middleware, validate_user_request, security

# Optional SSPL - can be disabled for testing
SSPL_ENABLED = os.getenv("SSPL_ENABLED", "false").lower() in ("true", "1", "yes")

if SSPL_ENABLED:
    from src.utils.sspl_dependency import require_sspl
else:
    async def require_sspl():
        return True

app = FastAPI(
    title="Unified Backend Bridge",
    description="Central orchestration layer for Finance, Education, and Creator agents",
    version="1.0.0"
)

# Add security middleware
app.middleware("http")(security_middleware)

# Initialize gateway and memory
gateway = Gateway()
memory = ContextMemory(DB_PATH)

@app.post("/core", response_model=CoreResponse)
async def core_endpoint(request: CoreRequest, http_request: Request, _sspl=Depends(require_sspl)) -> CoreResponse:
    """Main gateway endpoint for processing agent requests"""
    try:
        # Security validation
        validated_user_id = validate_user_request(request.user_id, http_request)
        
        response = gateway.process_request(
            module=request.module,
            intent=request.intent, 
            user_id=validated_user_id,
            data=request.data
        )
        
        # Validate response structure
        if not isinstance(response, dict) or 'status' not in response:
            raise HTTPException(status_code=500, detail="Processing failed")
        
        # Sanitize response
        sanitized_response = security.sanitize_response(response)
        sanitized_response.setdefault('message', 'Request processed')
        sanitized_response.setdefault('result', {})
        
        return CoreResponse(**sanitized_response)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Processing failed")

@app.get("/get-history")
async def get_history(user_id: str, request: Request) -> List[Dict[str, Any]]:
    """Get full interaction history for a user"""
    try:
        # Security validation
        validated_user_id = validate_user_request(user_id, request)
        
        history = memory.get_user_history(validated_user_id)
        
        # Limit and sanitize history
        limited_history = history[:10]  # Limit to 10 most recent
        sanitized_history = []
        
        for item in limited_history:
            sanitized_item = {
                "module": item.get("module"),
                "timestamp": item.get("timestamp"),
                "response": security.sanitize_response(item.get("response", {}))
            }
            sanitized_history.append(sanitized_item)
            
        return sanitized_history
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="History retrieval failed")

@app.get("/get-context") 
async def get_context(user_id: str, request: Request) -> List[Dict[str, Any]]:
    """Get recent context (last 3 interactions) for a user"""
    try:
        # Security validation
        validated_user_id = validate_user_request(user_id, request)
        
        context = memory.get_context(validated_user_id)
        
        # Sanitize context data
        sanitized_context = []
        for item in context:
            sanitized_item = {
                "module": item.get("module"),
                "timestamp": item.get("timestamp"),
                "response": security.sanitize_response(item.get("response", {}))
            }
            sanitized_context.append(sanitized_item)
            
        return sanitized_context
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Context retrieval failed")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Unified Backend Bridge API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/system/health")
async def system_health():
    """System health check - minimal information disclosure"""
    try:
        # Basic health checks only
        database_healthy = False
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("SELECT 1").fetchone()
            database_healthy = True
        except:
            pass
            
        gateway_healthy = gateway is not None
        
        overall_status = "healthy" if (database_healthy and gateway_healthy) else "degraded"
        
        # Minimal response - no internal details
        return {
            "status": overall_status,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat() + 'Z'
        }
    except Exception:
        return {
            "status": "unhealthy",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat() + 'Z'
        }

@app.get("/system/diagnostics")
async def system_diagnostics():
    """System diagnostics - limited information disclosure"""
    try:
        # Basic integration checks only
        modules_loaded = len(gateway.agents) > 0
        database_accessible = True
        gateway_initialized = gateway is not None
        
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("SELECT 1").fetchone()
        except:
            database_accessible = False
            
        integration_checks = {
            "core_modules_loaded": modules_loaded,
            "database_accessible": database_accessible,
            "gateway_initialized": gateway_initialized
        }
        
        integration_ready = all(integration_checks.values())
        integration_score = sum(integration_checks.values()) / len(integration_checks)
        
        # Minimal response - no internal details
        return {
            "integration_ready": integration_ready,
            "integration_score": round(integration_score, 3),
            "timestamp": __import__('datetime').datetime.utcnow().isoformat() + 'Z'
        }
    except Exception:
        return {
            "integration_ready": False,
            "integration_score": 0.0,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat() + 'Z'
        }

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest, http_request: Request, _sspl=Depends(require_sspl)):
    """Submit feedback for generated content"""
    try:
        # Security validation
        user_id = request.user_id or "anonymous"
        if user_id != "anonymous":
            user_id = validate_user_request(user_id, http_request)
            
        response = gateway.process_request(
            module="creator",
            intent="feedback",
            user_id=user_id,
            data=request.dict()
        )
        
        # Sanitize response
        sanitized_response = security.sanitize_response(response)
        return sanitized_response
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Feedback processing failed")

@app.get("/creator/history")
async def get_creator_history(user_id: str, request: Request):
    """Get creator generation history"""
    try:
        # Security validation - no "all" access allowed
        if user_id == "all":
            raise HTTPException(status_code=400, detail="Invalid user identifier")
            
        validated_user_id = validate_user_request(user_id, request)
        
        response = gateway.process_request(
            module="creator",
            intent="history",
            user_id=validated_user_id,
            data={}
        )
        
        # Sanitize response
        sanitized_response = security.sanitize_response(response)
        return sanitized_response
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="History retrieval failed")

@app.get("/system/logs/latest")
async def system_logs_latest(limit: int = 50):
    """Get latest log entries"""
    log_dir = Path("logs/bridge")
    if not log_dir.exists():
        return {"logs": [], "message": "No logs available"}
    
    log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not log_files:
        return {"logs": [], "message": "No log files found"}
    
    latest_log = log_files[0]
    try:
        with open(latest_log, 'r') as f:
            lines = f.readlines()[-limit:]
        return {
            "log_file": str(latest_log),
            "entries": [line.strip() for line in lines],
            "count": len(lines)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)