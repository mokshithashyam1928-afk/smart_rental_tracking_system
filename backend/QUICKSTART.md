# Quick Start Guide

Get the Smart Rental Tracking System backend running in 5 minutes!

## Option 1: Docker (Recommended - Fastest)

### Prerequisites
- Docker Desktop installed

### Steps

1. **Clone & navigate**
   ```bash
   cd backend
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Create admin user** (in another terminal)
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **Load sample data**
   ```bash
   docker-compose exec backend python manage.py seed_data
   ```

5. **Access the API**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs/
   - Admin Panel: http://localhost:8000/admin/

### Test Credentials
- Email: `admin@example.com`
- Password: `admin123456`

### Stop Services
```bash
docker-compose down
```

---

## Option 2: Local Development (Requires manual setup)

### Prerequisites
- Python 3.11+
- PostgreSQL
- Redis

### Steps

1. **Clone & navigate**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database/Redis settings
   ```

5. **Setup database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Load sample data** (optional)
   ```bash
   python manage.py seed_data
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **In separate terminals, start background services**

   Terminal 2 - Celery Worker:
   ```bash
   celery -A config worker -l info
   ```

   Terminal 3 - Celery Beat:
   ```bash
   celery -A config beat -l info
   ```

API available at: http://localhost:8000

---

## Making Your First API Call

### 1. Register a new user

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "myuser@example.com",
    "first_name": "My",
    "last_name": "User",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "role": "OPERATOR"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 2,
      "email": "myuser@example.com",
      "first_name": "My",
      "role": "OPERATOR"
    }
  }
}
```

Save the `access` token!

### 2. Get your profile

```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### 3. List all equipment

```bash
curl -X GET http://localhost:8000/api/equipment/ \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### 4. Checkout equipment

```bash
curl -X POST http://localhost:8000/api/rentals/checkout/ \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "EQX0001",
    "operator_id": "OP0001",
    "site_id": 1,
    "due_at": "2024-01-20T18:00:00Z"
  }'
```

---

## API Documentation

Full API docs available at:
- **Interactive Docs**: http://localhost:8000/api/docs/
- **API Schema**: http://localhost:8000/api/schema/

Quick reference:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/register/` | POST | Create new user |
| `/api/auth/login/` | POST | Login user |
| `/api/auth/me/` | GET | Get current user |
| `/api/equipment/` | GET/POST | Equipment CRUD |
| `/api/equipment/{id}/` | GET/PATCH/DELETE | Equipment detail |
| `/api/sites/` | GET/POST | Sites CRUD |
| `/api/operators/` | GET/POST | Operators CRUD |
| `/api/rentals/` | GET | List rentals |
| `/api/rentals/checkout/` | POST | Checkout equipment |
| `/api/rentals/checkin/` | POST | Check in equipment |
| `/api/telemetry/ingest/` | POST | Ingest telemetry data |
| `/api/dashboard/summary/` | GET | Equipment summary |
| `/api/health/live/` | GET | Health check |

---

## Troubleshooting

### Docker won't start
```bash
# Check Docker is running
docker ps

# View logs
docker-compose logs backend

# Remove containers and try again
docker-compose down -v
docker-compose up -d
```

### Database migration errors
```bash
# Reset database (WARNING: deletes all data)
python manage.py migrate zero
python manage.py migrate
```

### Redis connection refused
```bash
# Check Redis is running
redis-cli ping

# On macOS
brew services start redis

# On Linux
sudo service redis-server start
```

### Port 8000 already in use
```bash
# Use different port
python manage.py runserver 8080
```

### Celery tasks not running
```bash
# Check Celery worker is running
celery -A config worker -l info

# Check Redis connection
redis-cli PING
```

---

## Project Structure

```
backend/
├── config/           # Django configuration
├── apps/             # 13 Django applications
│   ├── accounts/     # Authentication
│   ├── equipment/    # Equipment management
│   ├── sites/        # Sites
│   ├── operators/    # Operators
│   ├── rentals/      # Rentals
│   ├── telemetry/    # Sensor data
│   ├── tracking/     # Dashboard
│   ├── audit/        # Audit logs
│   ├── notifications/# Notifications
│   ├── analytics/    # Analytics (Phase 2)
│   ├── forecasting/  # Forecasting (Phase 2)
│   ├── anomaly_detection/ # Anomalies
│   ├── recommendations/   # Recommendations
│   └── common/       # Shared utilities
├── tests/            # Test suite
├── manage.py         # Django CLI
├── requirements.txt  # Python dependencies
├── docker-compose.yml # Multi-container setup
└── README.md         # Full documentation
```

---

## Next Steps

1. **Read the docs**: Check [README.md](../README.md) for complete documentation
2. **Explore APIs**: Visit http://localhost:8000/api/docs/
3. **Write tests**: Add test cases in `tests/`
4. **Deploy**: Follow [DEPLOYMENT.md](../docs/DEPLOYMENT.md)

---

## Common Tasks

### Add a new Django app

```bash
python manage.py startapp newapp apps/newapp
```

Then register in `config/settings/base.py` under `INSTALLED_APPS`.

### Run tests

```bash
pytest
pytest -v -s  # Verbose with print statements
pytest tests/test_auth.py  # Single file
```

### Create database backup

```bash
docker-compose exec postgres pg_dump -U postgres smart_rental_db > backup.sql
```

### Reset everything (Docker)

```bash
docker-compose down -v
docker-compose up -d
```

### View API logs

```bash
docker-compose logs -f backend
```

---

## Getting Help

- **API Docs**: http://localhost:8000/api/docs/
- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

## Performance Tips

- Use list view pagination to avoid loading thousands of records
- Use `/api/telemetry/latest/` for live state instead of full history
- WebSocket `/ws/equipment/` provides real-time updates efficiently
- Database indexes on frequently filtered fields improve query speed

---

## Security Tips

- Never commit `.env` file with secrets
- Use strong passwords for test accounts
- Change `SECRET_KEY` in production
- Use HTTPS in production
- Rotate JWT tokens regularly
- Enable CORS only for trusted domains

---

Happy coding! 🚀
