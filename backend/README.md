# Smart Rental Tracking System - Backend

Production-grade Django backend for an intelligent equipment rental platform with real-time tracking, telemetry ingestion, and ML-ready architecture.

## Features

### Phase 1 (Core Infrastructure)
- ✅ Custom User model with JWT authentication
- ✅ Role-based access control (ADMIN, MANAGER, OPERATOR, VIEWER)
- ✅ Equipment management with status tracking
- ✅ Site and Operator management
- ✅ Rental lifecycle management with state machine
- ✅ QR/RFID equipment identification
- ✅ Telemetry ingestion and processing
- ✅ Real-time equipment live state (Redis)
- ✅ WebSocket support (Django Channels)
- ✅ Celery task queue for background jobs
- ✅ Automated overdue/offline detection
- ✅ Dashboard with equipment summary
- ✅ Notification system
- ✅ Audit logging
- ✅ Health check endpoints

### Phase 2 (Analytics & ML Ready)
- 🔄 Analytics APIs (placeholder)
- 🔄 Demand forecasting (placeholder)
- 🔄 Anomaly detection (placeholder)
- 🔄 Equipment recommendations (placeholder)

### Phase 3 (Event-Driven)
- 🔄 Kafka integration
- 🔄 Event sourcing
- 🔄 Outbox pattern
- 🔄 Monitoring (Prometheus/Grafana)

## Technology Stack

- **Backend**: Python 3.11 + Django 4.2
- **API**: Django REST Framework
- **Database**: PostgreSQL
- **Cache/Broker**: Redis
- **Async**: Celery + Celery Beat
- **Real-time**: Django Channels + WebSockets
- **Authentication**: JWT (Simple JWT)
- **Testing**: pytest + pytest-django
- **Documentation**: OpenAPI/Swagger
- **Containerization**: Docker + Docker Compose

## Project Structure

```
backend/
├── config/              # Django configuration
│   ├── settings/        # Settings (base, dev, test, prod)
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── routing.py       # WebSocket routing
│   └── celery.py        # Celery configuration
├── apps/                # Django applications
│   ├── accounts/        # User management & authentication
│   ├── equipment/       # Equipment management
│   ├── sites/          # Site management
│   ├── operators/      # Operator management
│   ├── rentals/        # Rental lifecycle
│   ├── telemetry/      # Sensor data ingestion
│   ├── tracking/       # Dashboard & WebSocket
│   ├── notifications/  # Notification management
│   ├── audit/          # Audit logging
│   ├── analytics/      # Analytics (Phase 2)
│   ├── forecasting/    # Forecasting (Phase 2)
│   ├── anomaly_detection/ # Anomalies (Phase 2)
│   ├── recommendations/   # Recommendations (Phase 2)
│   └── common/         # Shared utilities
├── tests/              # Test suite
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container image
├── docker-compose.yml  # Multi-service setup
├── pytest.ini         # Test configuration
├── manage.py          # Django management
└── README.md          # This file
```

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (optional)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize database**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load seed data** (optional)
   ```bash
   python manage.py seed_data
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

Server will be available at `http://localhost:8000`

### Docker Setup

```bash
docker-compose up -d
```

This will start:
- Backend API on `http://localhost:8000`
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`
- Celery worker
- Celery Beat scheduler

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/me/` - Get current user profile

### Core APIs
- `GET/POST /api/equipment/` - Equipment management
- `POST /api/equipment/resolve-identifier/` - Resolve QR/RFID
- `GET/POST /api/sites/` - Site management
- `GET/POST /api/operators/` - Operator management
- `GET/POST /api/rentals/` - Rental management
- `POST /api/rentals/checkout/` - Checkout equipment
- `POST /api/rentals/checkin/` - Check in equipment
- `GET /api/telemetry/` - Telemetry data
- `POST /api/telemetry/ingest/` - Ingest telemetry events
- `GET /api/dashboard/summary/` - Equipment summary
- `GET /api/dashboard/live-assets/` - Live equipment state

### WebSocket Endpoints
- `ws://localhost:8000/ws/equipment/` - All equipment updates
- `ws://localhost:8000/ws/equipment/{equipment_id}/` - Specific equipment

### Documentation
- OpenAPI schema: `http://localhost:8000/api/schema/`
- Swagger UI: `http://localhost:8000/api/docs/`

### Health Checks
- Liveness: `GET /health/live/`
- Readiness: `GET /health/ready/`

## Testing

Run all tests with coverage:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_equipment.py
```

Run with verbose output:
```bash
pytest -v
```

## Database Migrations

Create migrations after model changes:
```bash
python manage.py makemigrations
```

Apply migrations:
```bash
python manage.py migrate
```

View migration status:
```bash
python manage.py showmigrations
```

## Celery Tasks

### Background Jobs

**Overdue Rental Detection** (every 5 minutes)
- Checks for rentals past due date
- Updates rental status to OVERDUE
- Creates notifications

**Offline Equipment Detection** (every 5 minutes)
- Checks for equipment not reporting telemetry
- Marks equipment as OFFLINE
- Creates notifications

**Daily Usage Aggregation** (midnight UTC)
- Aggregates daily usage statistics
- Stores metrics snapshot

### Running Celery

Worker:
```bash
celery -A config worker -l info
```

Beat scheduler:
```bash
celery -A config beat -l info
```

Or with Docker Compose, services start automatically.

## Environment Variables

Key variables in `.env`:

```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/smart_rental_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-jwt-secret
CORS_ALLOWED_ORIGINS=http://localhost:3000
EQUIPMENT_OFFLINE_THRESHOLD_SECONDS=300
```

## Security

- JWT token-based authentication
- Role-based access control (RBAC)
- SQL injection protection (Django ORM)
- CORS configuration
- Environment-based secrets (no hardcoding)
- Secure password hashing
- Audit logging for sensitive operations
- Permission checks at API level

## Performance

- Database query optimization (select_related, prefetch_related)
- Pagination for large result sets
- Redis caching
- Async task processing with Celery
- Database indexes on frequently queried fields
- Connection pooling

## Monitoring & Logging

- Structured logging with request IDs
- Audit trail for all sensitive operations
- Health check endpoints
- Dashboard metrics snapshots
- Error tracking and exception handling

## API Contracts

### Equipment Status
- AVAILABLE: Ready for rental
- RENTED: Currently rented
- IN_USE: Actively in use
- IDLE: Not in use but available
- MAINTENANCE: Under maintenance
- OVERDUE: Rental overdue
- OFFLINE: Not reporting telemetry

### Rental Status
- CREATED: Rental created but not checked out
- CHECKED_OUT: Equipment checked out
- ACTIVE: Rental in progress
- CHECKED_IN: Rental completed
- OVERDUE: Rental past due date
- CANCELLED: Rental cancelled

### User Roles
- ADMIN: Full system access
- MANAGER: Equipment and rental management
- OPERATOR: Checkout/checkin, view assigned equipment
- VIEWER: Read-only dashboard access

## Phase Roadmap

**Phase 1** (Current): Core rental platform with real-time tracking
**Phase 2**: Analytics, forecasting, anomaly detection, recommendations
**Phase 3**: Kafka event streaming, distributed architecture, monitoring

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and write tests
3. Run tests and linting
4. Commit: `git commit -m "feat: description"`
5. Push: `git push origin feature/your-feature`
6. Create Pull Request

## License

Proprietary - All rights reserved

## Support

For issues and questions, contact the development team.

## API Contract Notes for Frontend (Member 2)

The API maintains stable contracts with:
- Consistent JSON response format
- Paginated list endpoints (20 items per page by default)
- Standard HTTP status codes
- Detailed error responses with error codes
- OpenAPI documentation

Frontend developers can build against:
- Stable REST API contracts
- WebSocket for real-time updates
- OpenAPI specification for auto-generation

## Telemetry Contract Notes for IoT/ML (Member 3)

Telemetry service is designed for:
- MQTT consumer integration
- REST endpoint ingestion
- Future Kafka consumer support
- Deduplication by event_id
- Automatic live state updates
- No tight coupling to transport mechanism

Expected telemetry format:
```json
{
  "event_id": "unique-id",
  "equipment_id": "EQX1001",
  "timestamp": "2024-01-15T10:30:00Z",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "engine_hours": 1523.5,
  "idle_hours": 45.2,
  "fuel_level": 75,
  "speed": 12.5,
  "operator_id": "OP0101"
}
```

## Deployment

### Production Deployment

1. Use production settings: `DJANGO_SETTINGS_MODULE=config.settings.production`
2. Set `DEBUG=False`
3. Configure allowed hosts and CORS origins
4. Use strong SECRET_KEY
5. Configure database with proper credentials
6. Set up Redis with authentication
7. Run migrations: `python manage.py migrate`
8. Collect static files: `python manage.py collectstatic`
9. Use Gunicorn/uWSGI for WSGI
10. Use Daphne for ASGI (WebSocket)
11. Enable HTTPS and secure cookies
12. Set up monitoring and logging

### Horizontal Scaling

- Multiple backend instances behind load balancer
- PostgreSQL replication for data redundancy
- Redis Sentinel for cache redundancy
- Celery worker scaling
- Docker orchestration (Kubernetes ready)

## Known Limitations (Phase 1)

- Kafka not integrated (Phase 3)
- Limited analytics APIs (Phase 2)
- No ML integration (Phase 3)
- Single-region deployment
- No distributed tracing (Phase 3)
- Basic monitoring (Phase 3)

## Next Steps

1. Implement comprehensive test suite
2. Add API rate limiting
3. Implement WebSocket broadcasting for live updates
4. Set up CI/CD pipeline
5. Configure monitoring and alerting
6. Implement Phase 2 analytics
7. Integrate ML components
