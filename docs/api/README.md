# OpenManus API Documentation

Welcome to the OpenManus API documentation. This guide provides comprehensive information about the OpenManus REST API endpoints, authentication, request/response formats, and examples.

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Versioning](#versioning)

## Introduction

The OpenManus API provides programmatic access to the OpenManus Appliance Repair Business Automation System. The API uses standard HTTP methods and returns JSON responses.

**Base URL**: `https://api.openmanus.io/api`

## Authentication

All API requests require authentication using JWT (JSON Web Tokens). To authenticate, you need to:

1. Obtain an access token by making a POST request to `/auth/login` with your credentials
2. Include the token in the Authorization header of subsequent requests

### Obtaining an Access Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using the Access Token

Include the token in the Authorization header of your requests:

```http
GET /api/customers
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API Endpoints

The OpenManus API is organized around the following main resources:

- [Authentication](authentication.md)
- [Customers](customers.md)
- [Service Requests](service-requests.md)
- [Technicians](technicians.md)
- [Appointments](appointments.md)
- [Invoices](invoices.md)
- [Integrations](integrations.md)
- [Dashboard](dashboard.md)
- [Users](users.md)

## Error Handling

The API uses conventional HTTP response codes to indicate the success or failure of an API request.

- `2xx`: Success
- `4xx`: Client error (invalid request, authentication, etc.)
- `5xx`: Server error

Error responses include a JSON object with details about the error:

```json
{
  "detail": "Error message describing the issue",
  "error_code": "ERROR_CODE",
  "path": "/api/resource"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400  | Bad Request - Invalid input data |
| 401  | Unauthorized - Missing or invalid authentication |
| 403  | Forbidden - Not enough permissions |
| 404  | Not Found - Resource does not exist |
| 422  | Validation Error - Input validation failed |
| 429  | Too Many Requests - Rate limit exceeded |
| 500  | Internal Server Error |

## Rate Limiting

The API implements rate limiting to ensure fair usage. Rate limits vary by endpoint, but most endpoints allow 100 requests per minute per API token.

Rate limit information is included in the response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1620000000
```

If you exceed the rate limit, you'll receive a 429 Too Many Requests response.

## Versioning

The current API version is v1. The version is included in the URL path:

```
https://api.openmanus.io/api/v1/resource
```

Future versions will be announced in advance to allow time for migration. 