# Deployment Guide

## Deployment Environments

The system supports three deployment environments:

### Development
- SQLite database or local PostgreSQL
- Debug mode enabled
- Hot code reloading
- All hosts allowed
- CORS relaxed

### Testing
- In-memory SQLite
- Celery eager mode
- No migrations run
- Used by pytest

### Production
- PostgreSQL only
- Debug disabled
- SSL/HTTPS required
- Secure cookies
- CORS restricted
- Environment validation

## Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (for containerized deployment)
- Nginx or similar reverse proxy (for production)

## Local Development Deployment

### 1. Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your settings
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb smart_rental_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py seed_data
```

### 3. Start Services

```bash
# Terminal 1: Django development server
python manage.py runserver

# Terminal 2: Celery worker
celery -A config worker -l info

# Terminal 3: Celery Beat scheduler
celery -A config beat -l info

# Terminal 4: Redis (if not running as service)
redis-server
```

API available at: http://localhost:8000

## Docker Deployment

### Development with Docker Compose

```bash
# Start all services
docker-compose up -d

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load sample data
docker-compose exec backend python manage.py seed_data

# View logs
docker-compose logs -f backend
```

Services will be available at:
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Production Container Build

```bash
# Build image
docker build -t smart-rental-backend:1.0.0 .

# Run container
docker run -d \
  --name smart-rental \
  -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=<your-secret-key> \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  smart-rental-backend:1.0.0
```

## Production Deployment

### Environment Configuration

Create `.env` in production environment:

```env
# Django Settings
DEBUG=False
SECRET_KEY=<generate-strong-key>
ALLOWED_HOSTS=api.yourdomain.com,api2.yourdomain.com
ENVIRONMENT=production

# Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=smart_rental_db
DATABASE_USER=<db-user>
DATABASE_PASSWORD=<db-password>
DATABASE_HOST=<db-host>
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://<redis-host>:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# JWT
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=<generate-strong-key>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-password>

# Celery
CELERY_BROKER_URL=redis://<redis-host>:6379/0
CELERY_RESULT_BACKEND=redis://<redis-host>:6379/0

# Telemetry
EQUIPMENT_OFFLINE_THRESHOLD_SECONDS=300
```

### 1. Server Preparation

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
  python3.11 \
  python3.11-venv \
  python3-pip \
  postgresql \
  postgresql-contrib \
  redis-server \
  nginx \
  supervisor \
  git

# Create application user
sudo useradd -m -s /bin/bash appuser
sudo su - appuser
```

### 2. Application Deployment

```bash
# Clone repository
git clone <repo-url>
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with production settings

# Run migrations
python manage.py migrate

# Create superuser
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin@yourdomain.com', 'secure_password', role='ADMIN')" | python manage.py shell

# Collect static files
python manage.py collectstatic --noinput

# Test deployment
python manage.py check --deploy
```

### 3. Database Setup

```bash
# As postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE smart_rental_db;
CREATE USER appuser WITH PASSWORD 'secure_password';
ALTER ROLE appuser SET client_encoding TO 'utf8';
ALTER ROLE appuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE appuser SET default_transaction_deferrable TO on;
ALTER ROLE appuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE smart_rental_db TO appuser;
\q

# Enable PostgreSQL service
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 4. Redis Setup

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Set:
# requirepass <strong-password>
# maxmemory 1gb
# maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### 5. Gunicorn/Daphne Configuration

Create `/home/appuser/gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 30
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

Create `/home/appuser/daphne.conf.py`:

```python
bind = ["127.0.0.1:8001"]
workers = 2
timeout = 30
```

### 6. Supervisor Configuration

Create `/etc/supervisor/conf.d/smart-rental.conf`:

```ini
[program:smart-rental-gunicorn]
directory=/home/appuser/backend
command=/home/appuser/backend/venv/bin/gunicorn \
  --config /home/appuser/gunicorn.conf.py \
  config.wsgi:application
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/smart-rental/gunicorn.log

[program:smart-rental-daphne]
directory=/home/appuser/backend
command=/home/appuser/backend/venv/bin/daphne \
  -b 127.0.0.1 \
  -p 8001 \
  config.asgi:application
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/smart-rental/daphne.log

[program:smart-rental-celery]
directory=/home/appuser/backend
command=/home/appuser/backend/venv/bin/celery \
  -A config worker \
  -l info
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/smart-rental/celery.log

[program:smart-rental-beat]
directory=/home/appuser/backend
command=/home/appuser/backend/venv/bin/celery \
  -A config beat \
  -l info \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/smart-rental/celery-beat.log

[group:smart-rental]
programs=smart-rental-gunicorn,smart-rental-daphne,smart-rental-celery,smart-rental-beat
```

Enable supervisor:
```bash
sudo mkdir -p /var/log/smart-rental
sudo chown appuser:appuser /var/log/smart-rental
sudo supervisorctl reread
sudo supervisorctl update
```

### 7. Nginx Configuration

Create `/etc/nginx/sites-available/smart-rental`:

```nginx
upstream smart_rental_app {
    server 127.0.0.1:8000;
}

upstream smart_rental_ws {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    client_max_body_size 10M;
    
    # HTTP API
    location / {
        proxy_pass http://smart_rental_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://smart_rental_ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket timeouts
        proxy_read_timeout 86400;
    }
    
    # Static files
    location /static/ {
        alias /home/appuser/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /home/appuser/backend/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/smart-rental /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 8. SSL Certificate Setup (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d api.yourdomain.com
```

### 9. Firewall Configuration

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Kubernetes Deployment

For Kubernetes deployment, use the provided Helm charts (not included in Phase 1).

## Monitoring & Logging

### Log Files

Access logs:
```bash
tail -f /var/log/smart-rental/gunicorn.log
tail -f /var/log/smart-rental/daphne.log
tail -f /var/log/smart-rental/celery.log
tail -f /var/log/smart-rental/celery-beat.log
```

### Health Checks

Test deployment:
```bash
# Liveness check
curl https://api.yourdomain.com/health/live/

# Readiness check
curl https://api.yourdomain.com/health/ready/
```

### Backup Strategy

```bash
# Daily database backup
0 2 * * * sudo -u postgres pg_dump smart_rental_db | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz

# Backup to cloud (AWS S3 example)
0 3 * * * aws s3 cp /backups/db-$(date +\%Y\%m\%d).sql.gz s3://your-backup-bucket/
```

## Maintenance

### Update Dependencies

```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all with caution
pip install --upgrade -r requirements.txt
```

### Database Maintenance

```bash
# Vacuum analyze
sudo -u postgres psql smart_rental_db -c "VACUUM ANALYZE;"

# Check table sizes
sudo -u postgres psql smart_rental_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

## Troubleshooting

### Application won't start

```bash
# Check logs
supervisorctl tail smart-rental-gunicorn
supervisorctl tail smart-rental-daphne

# Check database connection
python manage.py dbshell

# Check Redis connection
redis-cli ping
```

### High memory usage

```bash
# Check Celery queue size
redis-cli LLEN celery

# Clear stale tasks
redis-cli FLUSHDB
```

### Database performance issues

```bash
# Check slow queries (PostgreSQL)
sudo -u postgres psql smart_rental_db -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## Performance Optimization Checklist

- [ ] Enable database connection pooling
- [ ] Configure Redis properly (maxmemory, eviction policy)
- [ ] Use CDN for static files
- [ ] Enable gzip compression in Nginx
- [ ] Configure browser caching headers
- [ ] Monitor application performance
- [ ] Set up database replication
- [ ] Configure log rotation
- [ ] Regular backups scheduled
- [ ] DDoS protection enabled

## Rollback Procedure

```bash
# If deployment fails, revert to previous version
cd /home/appuser/backend
git checkout previous-version
pip install -r requirements.txt
python manage.py migrate
sudo supervisorctl restart all
```

## Version Management

Tag releases:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Disaster Recovery

1. Database failover: Use PostgreSQL replication
2. Redis failover: Use Redis Sentinel
3. Application failover: Multiple instances behind load balancer
4. Site failover: DNS configuration to backup site

## Support

For deployment issues or questions, contact DevOps team.
