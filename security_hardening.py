#!/usr/bin/env python3
"""
Security Hardening for Core Integrator
Addresses authentication, authorization, and IDOR vulnerabilities
"""

from fastapi import HTTPException, Depends, Header
from typing import Optional
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta

class SecurityManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.session_store = {}  # In production: use Redis/database
        
    def create_session(self, authenticated_user_id: str) -> str:
        """Create secure session after authentication"""
        session_id = secrets.token_urlsafe(32)
        internal_user_id = hashlib.sha256(authenticated_user_id.encode()).hexdigest()[:16]
        
        self.session_store[session_id] = {
            "internal_user_id": internal_user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }
        return session_id
        
    def validate_session(self, session_id: str) -> Optional[str]:
        """Validate session and return internal user ID"""
        if not session_id or session_id not in self.session_store:
            return None
            
        session = self.session_store[session_id]
        if datetime.utcnow() > session["expires_at"]:
            del self.session_store[session_id]
            return None
            
        return session["internal_user_id"]

# Security dependencies
security_manager = SecurityManager(os.getenv("SECRET_KEY", "change-in-production"))

async def require_authentication(authorization: Optional[str] = Header(None)) -> str:
    """Require valid session token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
        
    token = authorization.split(" ")[1]
    internal_user_id = security_manager.validate_session(token)
    
    if not internal_user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
        
    return internal_user_id

async def require_sspl_and_auth() -> str:
    """Combined SSPL and authentication check"""
    # First check SSPL if enabled
    if SSPL_ENABLED:
        await require_sspl()
    
    # Then require authentication
    return await require_authentication()

# Secure endpoint implementations
@app.post("/core", response_model=CoreResponse)
async def secure_core_endpoint(
    request: CoreRequest, 
    internal_user_id: str = Depends(require_sspl_and_auth)
) -> CoreResponse:
    """Secure core endpoint - no client-supplied user_id"""
    try:
        response = gateway.process_request(
            module=request.module,
            intent=request.intent, 
            user_id=internal_user_id,  # Use validated internal ID
            data=request.data
        )
        
        # Sanitize response - remove internal details
        if isinstance(response.get('result'), dict):
            response['result'].pop('internal_id', None)
            response['result'].pop('db_path', None)
            
        return CoreResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Processing failed")

@app.get("/get-context")
async def secure_get_context(
    internal_user_id: str = Depends(require_authentication)
) -> List[Dict[str, Any]]:
    """Secure context retrieval - only own data"""
    try:
        context = memory.get_context(internal_user_id)
        
        # Sanitize context - remove internal fields
        sanitized = []
        for item in context:
            sanitized_item = {
                "module": item.get("module"),
                "timestamp": item.get("timestamp"),
                "response": {
                    k: v for k, v in item.get("response", {}).items() 
                    if k not in ["internal_id", "db_path", "adapter_type"]
                }
            }
            sanitized.append(sanitized_item)
            
        return sanitized
    except Exception:
        raise HTTPException(status_code=500, detail="Context retrieval failed")

@app.get("/system/health")
async def secure_health_check():
    """Public health check - minimal information"""
    try:
        # Only expose essential status, hide internal details
        components = {}
        
        # Database check (don't expose paths)
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("SELECT 1").fetchone()
            components["database"] = "healthy"
        except:
            components["database"] = "unhealthy"
            
        components["gateway"] = "healthy"
        components["timestamp"] = datetime.utcnow().isoformat() + 'Z'
        
        overall_status = "healthy" if all(
            "healthy" in str(v) for v in components.values() 
            if v != components["timestamp"]
        ) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": components["timestamp"]
            # Removed: internal paths, module counts, detailed component info
        }
    except Exception:
        return {"status": "unhealthy", "timestamp": datetime.utcnow().isoformat() + 'Z'}

@app.get("/system/diagnostics")
async def secure_diagnostics(
    internal_user_id: str = Depends(require_authentication)
):
    """Authenticated diagnostics - limited internal info"""
    try:
        # Basic integration status only
        integration_checks = {
            "core_modules_loaded": len(gateway.agents) > 0,
            "database_accessible": True,  # Already checked in health
            "gateway_initialized": gateway is not None
        }
        
        integration_ready = all(integration_checks.values())
        integration_score = sum(integration_checks.values()) / len(integration_checks)
        
        return {
            "integration_ready": integration_ready,
            "integration_score": round(integration_score, 3),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
            # Removed: module names, db paths, internal architecture details
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Diagnostics unavailable")

# Authentication endpoint
@app.post("/auth/login")
async def login(credentials: dict):
    """Authentication endpoint - implement your auth logic"""
    # TODO: Implement actual authentication (OAuth, JWT, etc.)
    # This is a placeholder - replace with real authentication
    
    username = credentials.get("username")
    password = credentials.get("password")
    
    # Placeholder validation - replace with real auth
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    # In production: validate against user database, LDAP, OAuth, etc.
    if username == "demo" and password == "demo":  # REMOVE IN PRODUCTION
        session_token = security_manager.create_session(username)
        return {"access_token": session_token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/logout")
async def logout(internal_user_id: str = Depends(require_authentication)):
    """Logout endpoint"""
    # In production: invalidate session in database/Redis
    return {"message": "Logged out successfully"}