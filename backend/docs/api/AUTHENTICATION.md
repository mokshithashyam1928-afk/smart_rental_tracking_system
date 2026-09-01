# API Documentation - Authentication

## Overview
Authentication is handled via JWT (JSON Web Tokens). The API uses a standard Bearer token scheme.

## Token Lifecycle

1. User logs in → receives `access` and `refresh` tokens
2. `access` token (15 min expiry) used for API requests
3. When `access` expires → use `refresh` token to get new `access`
4. `refresh` token (7 days expiry) → user must re-login
5. Logout invalidates current session

## Endpoints

### Register New User
```
POST /api/auth/register/
```

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "role": "VIEWER"
}
```

**Role Options**: ADMIN, MANAGER, OPERATOR, VIEWER

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "VIEWER"
    }
  }
}
```

**Validation Rules**:
- Email must be unique
- Email must be valid format
- Password minimum 8 characters
- password_confirm must match password
- role must be one of: ADMIN, MANAGER, OPERATOR, VIEWER

**Error Responses**:
- 400: Invalid input or validation error
- 409: Email already exists

---

### Login
```
POST /api/auth/login/
```

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "VIEWER"
    }
  }
}
```

**Error Responses**:
- 401: Invalid email or password
- 400: Missing required fields

---

### Refresh Token
```
POST /api/auth/refresh/
```

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Error Responses**:
- 401: Invalid or expired refresh token
- 400: Missing refresh token

---

### Get Current User Profile
```
GET /api/auth/me/
```

**Authentication**: Required (Bearer token)

**Request Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "VIEWER",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses**:
- 401: Unauthorized (no token or invalid token)

---

### Change Password
```
POST /api/auth/change_password/
```

**Authentication**: Required (Bearer token)

**Request Headers**:
```
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "old_password": "currentpassword123",
  "new_password": "newpassword456",
  "new_password_confirm": "newpassword456"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Validation Rules**:
- old_password must be correct
- new_password minimum 8 characters
- new_password_confirm must match new_password

**Error Responses**:
- 400: Invalid old password
- 401: Unauthorized
- 422: Validation error

---

### Logout
```
POST /api/auth/logout/
```

**Authentication**: Required (Bearer token)

**Request Headers**:
```
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Error Responses**:
- 401: Unauthorized

---

## Example Workflows

### Complete Login Flow

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "role": "OPERATOR"
  }'

# Response includes access and refresh tokens
# Save tokens for subsequent requests

# 2. Make authenticated request
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"

# 3. When access token expires, refresh it
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'

# 4. Logout when done
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

## Error Response Format

All error responses follow this format:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": {}
  }
}
```

## Common Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| INVALID_CREDENTIALS | 401 | Email or password incorrect |
| INVALID_TOKEN | 401 | Token is invalid or expired |
| TOKEN_REQUIRED | 401 | No authentication token provided |
| VALIDATION_ERROR | 400 | Request validation failed |
| PERMISSION_DENIED | 403 | User lacks required permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists (e.g., email) |
| RATE_LIMITED | 429 | Too many requests |
| SERVER_ERROR | 500 | Internal server error |

## Authentication Headers

For all authenticated endpoints, include:
```
Authorization: Bearer <access_token>
```

The access token is a JWT that contains:
- User ID
- Email
- Role
- Issue time (iat)
- Expiration time (exp)

## Best Practices

1. **Store tokens securely**
   - Access token: Short-lived, can be in memory
   - Refresh token: Secure httpOnly cookie (if using web)

2. **Handle token expiration**
   - Implement automatic token refresh on 401
   - Redirect to login on refresh failure

3. **Use HTTPS in production**
   - Never send tokens over HTTP

4. **Implement logout**
   - Clear local token storage on logout
   - Backend invalidates refresh token

5. **Token rotation**
   - Each refresh returns new access token
   - Reduces exposure window if token leaked

## Rate Limiting

Authentication endpoints are rate limited:
- 5 login attempts per IP per minute
- 10 registration attempts per IP per hour

Exceeding limits returns 429 (Too Many Requests)

## Multi-Factor Authentication (MFA)

MFA support is planned for Phase 2. Currently not implemented.

## API Keys

API key authentication is planned for Phase 2. Currently only JWT is supported.
