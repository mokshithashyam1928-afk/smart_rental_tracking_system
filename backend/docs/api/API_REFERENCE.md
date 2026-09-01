# Smart Rental Tracking System — Backend API Reference

Comprehensive documentation for all REST API endpoints across Phase 1, Phase 2, and Phase 3.

---

## 1. Authentication & RBAC (`/api/auth/`)
- `POST /api/auth/register/`: Register a new user account (returns user object + JWT tokens).
- `POST /api/auth/login/`: Authenticate with email/password (returns JWT access and refresh tokens).
- `POST /api/auth/token/refresh/`: Refresh an expired access token.
- `GET /api/auth/me/`: Retrieve current authenticated user profile and role (`ADMIN`, `MANAGER`, `OPERATOR`, `VIEWER`).

---

## 2. Equipment Management (`/api/equipment/`)
- `GET /api/equipment/`: List equipment with filtering (`status`, `equipment_type`, `site`).
- `POST /api/equipment/`: Register new equipment.
- `GET /api/equipment/{id}/`: Retrieve equipment details with live state.
- `PUT /api/equipment/{id}/`: Update equipment metadata.
- `DELETE /api/equipment/{id}/`: Archive/remove equipment.
- `GET /api/equipment/{id}/qr_code/`: Retrieve or generate QR code string.

---

## 3. Job Sites (`/api/sites/`)
- `GET /api/sites/`: List construction sites with coordinates and status.
- `POST /api/sites/`: Create new site.
- `GET /api/sites/{id}/`: Retrieve site details.
- `PUT /api/sites/{id}/`: Update site information.

---

## 4. Operators (`/api/operators/`)
- `GET /api/operators/`: List certified machine operators.
- `POST /api/operators/`: Register operator.
- `GET /api/operators/{id}/`: Retrieve operator details.

---

## 5. Rental Lifecycle (`/api/rentals/`)
- `GET /api/rentals/`: List rentals with filtering (`status`, `equipment`, `operator`, `site`).
- `POST /api/rentals/checkout/`: Check out equipment for rental (validates availability, updates status to `RENTED`).
- `POST /api/rentals/checkin/`: Return rented equipment (transitions status to `CHECKED_IN`, frees machine to `AVAILABLE`).
- `POST /api/rentals/cancel/`: Cancel an active or pending rental.
- `GET /api/rentals/history/`: Retrieve rental history for current user or operator.

---

## 6. IoT Telemetry & Live State (`/api/telemetry/`)
- `POST /api/telemetry/ingest/`: Ingest IoT telemetry event (coordinates, speed, engine hours, idle hours, fuel level, operator ID). Broadcasts live update over Channels WebSocket.
- `GET /api/telemetry/`: Query historical telemetry data points.
- `GET /api/telemetry/latest/`: Get latest live state snapshot for all equipment.
- `GET /api/telemetry/live_state/`: Equipment live states.

---

## 7. Dashboard & Real-Time Tracking (`/api/dashboard/`)
- `GET /api/dashboard/summary/`: High-level KPI counters (total, available, rented, in-use, idle, overdue, offline).
- `GET /api/dashboard/live_assets/`: Current live asset telemetry array for map rendering.

---

## 8. Analytics & Business Intelligence (`/api/analytics/`)
- `GET /api/analytics/`: Complete analytics overview (fleet summary, idle analysis, fuel efficiency, site breakdowns, 7-day time series).
- `GET /api/analytics/utilization/`: Fleet utilization percentage and breakdown.
- `GET /api/analytics/idle/`: Fleet idle hours, idle percentage, fuel waste liters, and financial impact.
- `GET /api/analytics/fuel/`: Fuel consumption and liters/hour efficiency by equipment type.
- `GET /api/analytics/breakdown/`: Per-site utilization and active rental counts.
- `GET /api/analytics/export/?type=fleet|rentals|sites`: Download analytics data as CSV file.

---

## 9. Demand Forecasting (`/api/forecasting/`)
- `GET /api/forecasting/`: List generated demand forecast horizons.
- `POST /api/forecasting/generate/`: Trigger ML demand forecast calculation for target horizons (7/14/30 days).
- `GET /api/forecasting/summary/`: 7-day total forecasted demand and confidence metrics.

---

## 10. Anomaly Detection (`/api/anomalies/`)
- `GET /api/anomalies/`: List detected equipment anomalies (filtered by `severity`, `status`, `equipment`).
- `POST /api/anomalies/scan/`: Trigger immediate telemetry scan across equipment for anomalies (speeding, rapid fuel drop, runaway idle, unauthorized movement).
- `POST /api/anomalies/{id}/acknowledge/`: Acknowledge an anomaly alert (status -> `ACKNOWLEDGED`).
- `POST /api/anomalies/{id}/resolve/`: Resolve an anomaly (status -> `RESOLVED` / `FALSE_POSITIVE`).

---

## 11. Smart Recommendations (`/api/recommendations/`)
- `GET /api/recommendations/`: List asset reallocation recommendations.
- `POST /api/recommendations/generate/`: Run reallocation optimizer matching surplus idle machines with high-demand sites.
- `POST /api/recommendations/{id}/accept/`: Accept recommendation (automatically reassigns equipment to target site).
- `POST /api/recommendations/{id}/dismiss/`: Dismiss recommendation.

---

## 12. Notifications (`/api/notifications/`)
- `GET /api/notifications/`: List system and equipment alert notifications.
- `POST /api/notifications/{id}/read/`: Mark notification as read.
- `GET /api/notifications/unread_count/`: Count of unread alerts.

---

## 13. Audit Trail (`/api/audit/`)
- `GET /api/audit/`: List immutable system audit logs recording all state transitions, user actions, and domain events.

---

## 14. Health Checks
- `GET /health/live/`: Kubernetes/Docker liveness probe.
- `GET /health/ready/`: Readiness probe checking PostgreSQL and Redis cache connectivity.
