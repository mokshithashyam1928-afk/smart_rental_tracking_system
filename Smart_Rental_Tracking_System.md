# SMART RENTAL TRACKING SYSTEM

## 3-Member Work Allocation, GitHub Collaboration & Implementation Guide

### Hackathon Engineering Execution Document

- Purpose of This Document

This document defines exactly how the three team members will divide, implement, test, and contribute the Smart Rental Tracking System to one shared GitHub repository. It is intended to be understandable by every team member and to prevent duplicated work, merge conflicts, unclear ownership, and integration problems.

- Project Goal

Build an intelligent rental platform for construction and mining equipment that tracks assets in real time, manages rentals and QR/RFID check-in/check-out, records equipment usage, detects overdue and abnormal behavior, forecasts demand, and recommends better asset allocation.

- Locked Technology Stack

- Team Structure

The project is divided by engineering responsibility, not by phase. All three members contribute during all phases.

- Important Ownership Rule

Ownership means that the member is responsible for implementing, testing, documenting, and maintaining that area. It does not mean other members cannot contribute. Any cross-module change must be discussed before implementation and should be delivered through a Pull Request.

- Repository Structure

The repository should follow this structure:

```text

smart-rental-tracking/
├── frontend/                  # Member 2 primary owner
├── backend/                   # Member 1 primary owner
│   ├── config/
│   ├── apps/
│   │   ├── accounts/
│   │   ├── equipment/
│   │   ├── sites/
│   │   ├── operators/
│   │   ├── rentals/
│   │   ├── telemetry/
│   │   ├── tracking/
│   │   ├── analytics/
│   │   ├── forecasting/
│   │   ├── anomaly_detection/
│   │   ├── notifications/
│   │   └── audit/
│   └── manage.py
├── simulator/                 # Member 3
├── ml-service/                # Member 3
├── infrastructure/            # Member 3
│   ├── mqtt/
│   ├── kafka/
│   ├── prometheus/
│   └── grafana/
├── docs/                      # All members
├── .github/
│   └── workflows/             # Member 3
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md

- GitHub Collaboration Rules

### 7.1 Branch Strategy

Nobody works directly on main. The recommended flow is:

main
  │
  └── develop
       ├── feature/backend-equipment
       ├── feature/backend-rental
       ├── feature/frontend-dashboard
       ├── feature/frontend-map
       ├── feature/iot-simulator
       ├── feature/ml-forecast
       └── feature/devops-ci

### 7.2 Standard Workflow for Every Member

- git checkout develop
2. git pull origin develop
3. git checkout -b feature/<short-description>
4. Implement only the assigned task
5. Run tests/lint/build locally
6. git add .
7. git commit -m "feat: <clear description>"
8. git push origin feature/<short-description>
9. Open Pull Request → develop
10. Fix review/CI issues if any
11. Get review approval
12. Merge into develop

### 7.3 Commit Convention

feat: add equipment management API

feat: implement QR checkout flow

fix: prevent duplicate telemetry records

test: add rental lifecycle tests

docs: update API documentation

chore: configure Redis service

ci: add backend test workflow

refactor: separate rental business service

### 7.4 Pull Request Rules

PR title must clearly describe the change.

PR description must state what changed, how it was tested, and whether another module is affected.

Do not mix unrelated features in one PR.

All CI checks must pass before merge.

At least one other member reviews significant PRs.

Resolve merge conflicts on the feature branch, then push the updated branch.

After merge, delete the feature branch unless it is intentionally long-lived.

Never commit .env, passwords, JWT secrets, private keys, database dumps, or generated credentials.

- Member 1 — Backend & Database Engineer / Technical Lead

Primary goal: build the secure, reliable Django business layer and database.

Phase 1 Tasks

Initialize Django project and environment configuration.

Configure PostgreSQL and Django ORM.

Create accounts module: users, authentication, JWT and roles.

Implement RBAC: ADMIN, MANAGER, OPERATOR, VIEWER.

Create Site, Equipment, Operator, Rental, Telemetry, LiveState, Notification and AuditLog models.

Create Django migrations and database constraints.

Implement equipment CRUD APIs.

Implement site and operator APIs.

Implement rental lifecycle APIs: checkout, active, check-in, overdue and cancellation rules.

Implement QR/RFID business validation. QR/RFID input is only an identifier; backend remains responsible for authorization and state transitions.

Implement dashboard summary APIs.

Create health/readiness endpoints.

Implement WebSocket backend integration with Django Channels.

Add API tests for authentication, permissions, equipment and rental workflows.

Document API contracts in docs/api/.

Phase 2 Tasks

Create analytics API module.

Implement utilization, idle, fuel, downtime and availability calculations.

Create storage models for forecasts, anomalies and recommendations.

Expose forecast, anomaly and recommendation APIs.

Implement alert status transitions and acknowledgement APIs.

Integrate ML outputs produced by Member 3.

Add authorization to analytics and management endpoints.

Write integration tests covering analytics and recommendation flows.

Phase 3 Tasks

Define/version domain event contracts with Member 3.

Implement Kafka-facing business event integration where appropriate.

Implement idempotency and event deduplication at business boundaries.

Implement database transaction boundaries and the outbox pattern for critical events.

Optimize PostgreSQL indexes and high-volume queries.

Ensure Django application remains stateless for horizontal scaling.

Lead architecture reviews and final backend integration.

Member 1 Deliverables

Working Django backend

PostgreSQL schema and migrations

REST API implementation

Authentication/RBAC

Rental state machine

API documentation

Backend tests

Database and event design documentation

- Member 2 — Frontend & UX Engineer

Primary goal: build a fast, clear and impressive dashboard that makes the system easy to demonstrate.

Phase 1 Tasks

Initialize React + TypeScript application.

Configure routing, API client, authentication state and reusable UI components.

Build login/register screens.

Build role-aware navigation.

Build main dashboard with total, available, rented, in-use, idle, overdue and offline cards.

Build equipment list, filters, details, add and edit screens.

Build site and operator management screens.

Build rental list and rental details.

Build QR scanning/check-in/check-out UI.

Build live equipment map using Leaflet.

Connect WebSocket events and update markers/status without page refresh.

Build notification center.

Add responsive design for laptop/tablet/mobile.

Write frontend tests for critical components and workflows.

Phase 2 Tasks

Build analytics dashboard.

Build daily/weekly/monthly utilization charts.

Build site-wise, equipment-wise and operator-wise charts.

Build fuel/idle/downtime visualizations.

Build demand forecasting dashboard.

Build anomaly dashboard with severity, reason and status.

Build recommendation cards including current utilization, predicted demand and suggested reallocation.

Build acknowledge/dismiss/resolve actions.

Add CSV export UI where supported by the backend.

Phase 3 Tasks

Build advanced real-time event views.

Build system health/operational dashboard.

Visualize telemetry throughput, alerts and system status where APIs expose it.

Polish notification and recommendation workflows.

Optimize frontend performance for large equipment lists and live updates.

Complete responsive and demo-ready UX.

Lead final UI integration and hackathon presentation flow.

Member 2 Deliverables

Complete React dashboard

Authentication UI

Equipment/rental management UI

QR workflow

Live map

Analytics and ML dashboards

Notification center

Responsive UI

Frontend tests

## 10. Member 3 — IoT, ML & DevOps Engineer

Primary goal: create the telemetry pipeline, intelligence layer, local infrastructure and automation.

Phase 1 Tasks

Set up MQTT broker, preferably Mosquitto for local development.

Build configurable equipment simulator.

Generate realistic location, engine-hours, idle-hours, fuel, speed and operator telemetry.

Define and document MQTT telemetry payload schema.

Implement telemetry ingestion integration with the Django backend.

Configure Redis for live state/cache and Celery.

Configure Celery worker and Celery Beat.

Implement scheduled offline equipment and overdue checks where appropriate.

Create Dockerfiles and docker-compose.yml for the complete local stack.

Create GitHub Actions CI workflows for backend/frontend tests, lint and Docker builds.

Document local development and infrastructure setup.

Phase 2 Tasks

Build historical data extraction and feature engineering pipeline.

Implement utilization/analytics data preparation where ML is involved.

Implement demand forecasting baseline.

Implement XGBoost forecasting when sufficient data exists.

Implement Isolation Forest anomaly detection.

Implement rule-based anomaly detection for obvious misuse/impossible conditions.

Implement anomaly scoring and severity.

Create Celery jobs for forecasting, anomaly detection and recommendation generation.

Version model metadata and prediction results.

Create deterministic ML tests using fixture data.

Integrate ML output contracts with Member 1's Django APIs.

Phase 3 Tasks

Introduce Kafka between telemetry ingestion and independent consumers.

Create versioned Kafka topics and event envelopes.

Implement telemetry, analytics, alert and ML consumers.

Implement idempotent consumers and dead-letter handling.

Add retry/backoff and failure recovery.

Create Prometheus metrics and Grafana dashboards.

Perform controlled load tests using the equipment simulator.

Create production-oriented Docker configuration.

Extend GitHub Actions to build immutable images, push to a registry, deploy staging, run smoke tests and support controlled production promotion.

Document rollback, backup/restore and operational procedures.

Member 3 Deliverables

Equipment simulator

MQTT infrastructure

Redis/Celery infrastructure

ML pipeline and models

Kafka event pipeline

Docker environment

GitHub Actions CI/CD

Prometheus/Grafana monitoring

Load and resilience tests

## 11. Phase-by-Phase Team Integration

Phase 1 — Core Working Product

Definition of Done: all three members can clone the repository, run the documented Docker environment, log in, manage equipment, execute a rental, simulate telemetry, and see live equipment state on the dashboard.

Phase 2 — Intelligent Product

Definition of Done: the system explains utilization, detects under-utilized assets and anomalies, forecasts demand, and presents actionable recommendations.

Member 3 produces validated ML results.

Member 1 exposes/stores those results through secure APIs.

Member 2 visualizes them in decision-oriented dashboards.

All three test one end-to-end scenario together before the phase is marked complete.

Phase 3 — Scalable Production Architecture

Definition of Done: telemetry can flow through MQTT → Kafka → independent consumers, operational metrics are visible, failures can be recovered, and the application can be built/deployed through GitHub Actions.

Member 3 owns Kafka/monitoring/deployment implementation.

Member 1 owns business event consistency and data integrity.

Member 2 owns real-time visualization and operational UI.

All three perform the final scale/failure demonstration.

## 12. GitHub Issues / Task Board

Create GitHub Issues using these labels:

backend — Member 1

frontend — Member 2

iot — Member 3

ml — Member 3

devops — Member 3

database — Member 1

realtime — Members 1 + 2

integration — All

bug

documentation

phase-1

phase-2

phase-3

priority-critical / priority-high / priority-medium

Recommended GitHub Project columns:

Backlog

Ready

In Progress

Code Review

Integration

Testing

Done

## 13. Cross-Member Contracts

To reduce merge conflicts, agree on contracts before parallel implementation.

### 13.1 API Contract

Member 1 publishes endpoint, request and response schema before Member 2 integrates it.

Member 2 should not hard-code database fields that are not part of the API contract.

Breaking API changes require a PR discussion and documentation update.

### 13.2 Telemetry Contract

{
  "event_id": "uuid",
  "equipment_id": "EQX1001",
  "timestamp": "ISO-8601",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "engine_hours": 7.5,
  "idle_hours": 1.2,
  "fuel_level": 72,
  "speed": 10.4,
  "operator_id": "OP101"
}

### 13.3 Status Contract

AVAILABLE — equipment can be rented

RENTED — rental exists and asset is assigned

IN_USE — operating telemetry indicates active use

IDLE — equipment is connected but not actively operating

MAINTENANCE — unavailable for rental

OVERDUE — rental due time has passed without check-in

OFFLINE — telemetry heartbeat has not been received within the configured threshold

## 14. Testing Responsibility

## 15. Definition of Done for Every Task

Code is implemented in the correct module.

Relevant tests are written or updated.

No hard-coded secrets or environment-specific credentials are committed.

README/docs are updated if setup/API behavior changed.

Local lint/build/test passes.

Feature branch is pushed to GitHub.

Pull Request is opened against develop.

CI passes.

At least one teammate reviews significant changes.

Feature is verified after merge into develop.

## 16. Recommended Daily Team Routine

10-minute sync: each member states yesterday's progress, today's task and blockers.

Before coding: pull the latest develop branch.

Before changing a shared contract: communicate in the team channel.

Push small, logically complete commits instead of one huge commit.

Open PRs early enough for review; do not wait until the final hour.

After a major merge, all three pull develop and run the integration environment.

Keep the GitHub Project board updated so everyone knows what is actually in progress.

## 17. Final Hackathon Demo Flow

The team should demonstrate the product as one continuous story:

- Admin logs in.

- Admin creates/views equipment and assigns it to a site.

- Operator scans the equipment QR and performs check-out.

- Equipment simulator starts sending telemetry through MQTT.

- Live dashboard updates location, status, engine hours, idle time and fuel.

- Manager views rental and usage analytics.

- System flags an overdue/under-utilized asset.

- ML system detects an anomaly.

- Demand forecast shows higher future demand at another site.

## 10. Recommendation engine suggests reallocating the under-utilized asset.

## 11. Phase 3 demonstration shows MQTT → Kafka → consumers and Grafana monitoring.

## 12. GitHub Actions demonstrates automated test/build/deployment pipeline.

## 18. Final Responsibility Matrix

## 19. Golden Rule

BUILD IN PARALLEL, INTEGRATE CONTINUOUSLY, AND MERGE ONLY THROUGH PULL REQUESTS.

The team should never wait until the end of a phase to discover integration problems. Phase 1 must finish as one working system; Phase 2 must extend that same system; Phase 3 must scale and harden it. The GitHub repository is the single source of truth.

## 20. Immediate Next Actions

Create/confirm main and develop branches.

Protect main from direct pushes.

Create GitHub Project with Backlog → Ready → In Progress → Code Review → Integration → Testing → Done.

Create Phase 1 issues and assign them to Members 1, 2 and 3.

Member 1 initializes Django + PostgreSQL structure.

Member 2 initializes React + TypeScript structure.

Member 3 initializes Docker + MQTT + simulator + GitHub Actions.

Agree on API, telemetry and status contracts before parallel feature work.

Merge the three foundation PRs into develop.

Run the complete Phase 1 stack together before starting Phase 2.

End of Team Work Allocation Document
