# Render Deployment Guide - Core Integrator Sprint

## Prerequisites
- GitHub repository with your code
- Render account (free tier available)

## Step-by-Step Deployment

### 1. Prepare Repository
```bash
# Ensure all files are committed
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create Render Service

1. **Login to Render Dashboard**
   - Go to https://render.com
   - Sign in with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `Core-Integrator-Sprint-1.1-` directory

3. **Configure Service Settings**
   ```
   Name: core-integrator-sprint
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   ```

### 3. Environment Variables
Set these in Render Dashboard → Environment:

```
DB_PATH=data/context.db
NONCE_DB_PATH=data/nonce_store.db
SSPL_ENABLED=false
INTEGRATOR_USE_NOOPUR=false
USE_MONGODB=false
LOG_LEVEL=INFO
VIDEO_SERVICE_URL=http://localhost:5002
PORT=10000
```

### 4. Advanced Settings
```
Health Check Path: /system/health
Auto-Deploy: Yes
```

## Database Setup

### SQLite Configuration
- **Location**: `data/context.db` (persistent disk)
- **Backup**: Automatic with Render's persistent disk
- **Size Limit**: 1GB on free tier

### Database Initialization
The app automatically creates tables on first run:
- `interactions` - User interaction history
- `generations` - Generation ID mappings
- `nonces` - Security nonce storage

## Monitoring & Health Checks

### Health Endpoints
- **Health Check**: `GET /system/health`
- **Diagnostics**: `GET /system/diagnostics`
- **Logs**: `GET /system/logs/latest`

### Expected Response
```json
{
  "status": "ok",
  "dependencies": {
    "database": "up",
    "gateway": "up",
    "noopur": "disabled",
    "video_service": "disabled"
  }
}
```

## API Endpoints

### Core Functionality
- `POST /core` - Main processing endpoint
- `GET /get-history?user_id={id}` - User history
- `GET /get-context?user_id={id}` - Recent context

### Creator Module
- `POST /feedback` - Submit feedback
- `GET /creator/history?user_id={id}` - Creator history

## Testing Deployment

### 1. Health Check
```bash
curl https://your-app.onrender.com/system/health
```

### 2. Basic Request
```bash
curl -X POST https://your-app.onrender.com/core \
  -H "Content-Type: application/json" \
  -d '{
    "module": "sample_text",
    "intent": "generate",
    "user_id": "test_user",
    "data": {"text": "Hello World"}
  }'
```

## Troubleshooting

### Common Issues
1. **Database Connection**: Check DB_PATH environment variable
2. **Port Binding**: Ensure PORT environment variable is set
3. **Dependencies**: Verify requirements.txt is complete

### Logs Access
```bash
# View logs in Render Dashboard
# Or use API endpoint
curl https://your-app.onrender.com/system/logs/latest
```

## Production Considerations

### Security
- SSPL disabled for initial deployment
- Enable in production: `SSPL_ENABLED=true`
- Add API keys for external services

### Performance
- Free tier: 512MB RAM, shared CPU
- Upgrade to paid tier for production workloads
- Consider Redis for session storage

### Scaling
- Horizontal scaling available on paid tiers
- Database remains SQLite (single instance)
- Consider PostgreSQL for multi-instance deployments

## Deployment URL
Your app will be available at:
`https://core-integrator-sprint.onrender.com`

## Support
- Render Documentation: https://render.com/docs
- Health Check: `/system/health`
- API Documentation: `/docs`