# Network Security Configuration Template

## Nginx Reverse Proxy Configuration (Required)

```nginx
# /etc/nginx/sites-available/core-integrator-secure
server {
    listen 443 ssl http2;
    server_name your-internal-domain.local;
    
    # SSL Configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # IP Allowlist (REQUIRED)
    allow 10.0.0.0/8;
    allow 192.168.0.0/16;
    allow 172.16.0.0/12;
    deny all;
    
    # Rate Limiting (Additional Layer)
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;
    limit_req zone=api burst=10 nodelay;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Hide Server Information
    server_tokens off;
    
    location / {
        # Basic Auth (REQUIRED - Add authentication layer)
        auth_basic "Core Integrator Access";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        # Proxy to Core Integrator
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Request size limits
        client_max_body_size 1M;
        
        # Timeout settings
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
    
    # Block sensitive endpoints from external access
    location ~ ^/(system/diagnostics|get-history) {
        # Extra restrictions for sensitive endpoints
        allow 10.0.0.0/24;  # More restrictive subnet
        deny all;
        
        auth_basic "Admin Access Required";
        auth_basic_user_file /etc/nginx/.htpasswd-admin;
        
        proxy_pass http://127.0.0.1:8001;
    }
}
```

## Firewall Rules (iptables)

```bash
#!/bin/bash
# Firewall configuration for Core Integrator

# Flush existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH (adjust port as needed)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTPS only from private networks
iptables -A INPUT -p tcp --dport 443 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -s 192.168.0.0/16 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -s 172.16.0.0/12 -j ACCEPT

# Block direct access to Core Integrator port
iptables -A INPUT -p tcp --dport 8001 -j DROP

# Log dropped packets
iptables -A INPUT -j LOG --log-prefix "DROPPED: "

# Save rules
iptables-save > /etc/iptables/rules.v4
```

## Docker Security Configuration

```yaml
# docker-compose.security.yml
version: '3.8'

services:
  core-integrator:
    build: .
    container_name: core-integrator-secure
    
    # Security settings
    read_only: true
    user: "1000:1000"  # Non-root user
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    
    # Network isolation
    networks:
      - internal-only
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
    
    # Environment security
    environment:
      - SECURITY_LOG_LEVEL=WARNING
      - RATE_LIMIT_ENABLED=true
      - ENUMERATION_DETECTION=true
    
    # Volume mounts (read-only where possible)
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config:ro
    
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/system/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx-proxy:
    image: nginx:alpine
    container_name: nginx-security-proxy
    
    ports:
      - "443:443"
    
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
      - ./.htpasswd:/etc/nginx/.htpasswd:ro
    
    networks:
      - internal-only
      - external
    
    depends_on:
      - core-integrator

networks:
  internal-only:
    driver: bridge
    internal: true
  external:
    driver: bridge
```

## Monitoring & Alerting

```bash
#!/bin/bash
# Security monitoring script

LOG_FILE="/var/log/core-integrator-security.log"
ALERT_EMAIL="security@yourcompany.com"

# Monitor for security events
tail -f /app/logs/security.log | while read line; do
    echo "$(date): $line" >> $LOG_FILE
    
    # Alert on enumeration attempts
    if echo "$line" | grep -q "enumeration"; then
        echo "SECURITY ALERT: User enumeration detected - $line" | \
        mail -s "Core Integrator Security Alert" $ALERT_EMAIL
    fi
    
    # Alert on rate limit violations
    if echo "$line" | grep -q "Rate limit exceeded"; then
        echo "SECURITY ALERT: Rate limit exceeded - $line" | \
        mail -s "Core Integrator Rate Limit Alert" $ALERT_EMAIL
    fi
done
```

## Environment Security

```bash
# .env.security (Additional security settings)

# Security logging
SECURITY_LOG_LEVEL=WARNING
SECURITY_LOG_FILE=/app/logs/security.log

# Rate limiting
RATE_LIMIT_ENABLED=true
IP_RATE_LIMIT=60
USER_RATE_LIMIT=30

# Enumeration detection
ENUMERATION_DETECTION=true
MAX_USERS_PER_IP=10
ENUMERATION_BLOCK_THRESHOLD=3

# Response sanitization
SANITIZE_RESPONSES=true
HIDE_INTERNAL_DETAILS=true
LIMIT_HISTORY_RESULTS=10

# Network restrictions
ALLOWED_IP_RANGES=10.0.0.0/8,192.168.0.0/16,172.16.0.0/12
REQUIRE_PROXY_HEADERS=true
```

---

**IMPORTANT**: These configurations provide additional security layers but do NOT fix the fundamental architectural vulnerabilities. The system still requires authentication and proper access controls for production use.