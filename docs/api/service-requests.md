# Service Requests API

The Service Requests API provides access to service request data within the OpenManus system. This includes creating, retrieving, updating, and managing service requests for customer appliance repairs.

## Table of Contents

1. [List Service Requests](#list-service-requests)
2. [Get Service Request](#get-service-request)
3. [Create Service Request](#create-service-request)
4. [Update Service Request](#update-service-request)
5. [Delete Service Request](#delete-service-request)
6. [Assign Technician](#assign-technician)
7. [Update Status](#update-status)
8. [Service Request Object](#service-request-object)

## List Service Requests

```http
GET /api/service-requests
```

Retrieves a paginated list of service requests.

### Query Parameters

| Parameter   | Type   | Description |
|-------------|--------|-------------|
| page        | number | Page number for pagination (default: 1) |
| limit       | number | Number of results per page (default: 20, max: 100) |
| status      | string | Filter by status (`pending`, `scheduled`, `in_progress`, `completed`, `cancelled`) |
| priority    | string | Filter by priority (`low`, `medium`, `high`, `urgent`) |
| customer_id | number | Filter by customer ID |
| technician_id | number | Filter by assigned technician ID |
| start_date  | string | Filter by start date (format: YYYY-MM-DD) |
| end_date    | string | Filter by end date (format: YYYY-MM-DD) |
| sort        | string | Field to sort by (e.g., `created_at`, `priority`, `status`) |
| order       | string | Sort order: `asc` or `desc` (default: `desc` for dates, `asc` for other fields) |

### Response

```json
{
  "items": [
    {
      "id": 1,
      "customer_id": 1,
      "customer": {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe"
      },
      "appliance_id": 1,
      "appliance": {
        "id": 1,
        "type": "refrigerator",
        "brand": "GE",
        "model": "XYZ123"
      },
      "status": "scheduled",
      "priority": "medium",
      "issue_description": "Not cooling properly",
      "technician_id": 2,
      "technician": {
        "id": 2,
        "first_name": "Jane",
        "last_name": "Smith"
      },
      "created_at": "2023-03-15T10:30:00Z",
      "updated_at": "2023-03-15T14:45:00Z",
      "scheduled_date": "2023-03-20T09:00:00Z"
    },
    // More service request objects...
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total_items": 35,
    "total_pages": 2
  }
}
```

## Get Service Request

```http
GET /api/service-requests/{id}
```

Retrieves a specific service request by ID.

### Path Parameters

| Parameter | Type   | Description |
|-----------|--------|-------------|
| id        | number | The unique identifier of the service request |

### Response

```json
{
  "id": 1,
  "customer_id": 1,
  "customer": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "555-123-4567"
  },
  "appliance_id": 1,
  "appliance": {
    "id": 1,
    "type": "refrigerator",
    "brand": "GE",
    "model": "XYZ123",
    "serial_number": "ABC12345"
  },
  "status": "scheduled",
  "priority": "medium",
  "issue_description": "Not cooling properly",
  "diagnosis": "Possible compressor issue",
  "resolution": null,
  "technician_id": 2,
  "technician": {
    "id": 2,
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "phone": "555-987-6543"
  },
  "appointments": [
    {
      "id": 1,
      "start_time": "2023-03-20T09:00:00Z",
      "end_time": "2023-03-20T11:00:00Z",
      "status": "scheduled"
    }
  ],
  "parts_used": [],
  "created_at": "2023-03-15T10:30:00Z",
  "updated_at": "2023-03-15T14:45:00Z",
  "scheduled_date": "2023-03-20T09:00:00Z"
}
```

## Create Service Request

```http
POST /api/service-requests
```

Creates a new service request.

### Request Body

| Field           | Type   | Required | Description |
|-----------------|--------|----------|-------------|
| customer_id     | number | Yes      | ID of the customer |
| appliance_id    | number | No       | ID of the appliance (if not provided, a new appliance will be created) |
| status          | string | No       | Status of the request (default: `pending`) |
| priority        | string | No       | Priority level (default: `medium`) |
| issue_description | string | Yes    | Description of the issue |
| technician_id   | number | No       | ID of the assigned technician |
| scheduled_date  | string | No       | Scheduled date and time (ISO 8601 format) |
| appliance_type  | string | No       | Type of appliance (required if appliance_id not provided) |
| appliance_brand | string | No       | Brand of appliance (optional if appliance_id not provided) |
| appliance_model | string | No       | Model of appliance (optional if appliance_id not provided) |

Example:

```json
{
  "customer_id": 1,
  "status": "pending",
  "priority": "medium",
  "issue_description": "Not cooling properly",
  "appliance_type": "refrigerator",
  "appliance_brand": "GE",
  "appliance_model": "XYZ123"
}
```

### Response

Returns the created service request object with the HTTP status code 201 (Created).

## Update Service Request

```http
PUT /api/service-requests/{id}
```

Updates an existing service request.

### Path Parameters

| Parameter | Type   | Description |
|-----------|--------|-------------|
| id        | number | The unique identifier of the service request |

### Request Body

The request body should contain the fields to update. All fields are optional, but at least one field must be provided.

Example:

```json
{
  "status": "in_progress",
  "diagnosis": "Compressor failure confirmed",
  "technician_id": 3
}
```

### Response

Returns the updated service request object.

## Delete Service Request

```http
DELETE /api/service-requests/{id}
```

Deletes a service request. This operation cannot be undone.

### Path Parameters

| Parameter | Type   | Description |
|-----------|--------|-------------|
| id        | number | The unique identifier of the service request |

### Response

Returns HTTP status code 204 (No Content) on successful deletion.

## Assign Technician

```http
POST /api/service-requests/{id}/assign
```

Assigns a technician to a service request.

### Path Parameters

| Parameter | Type   | Description |
|-----------|--------|-------------|
| id        | number | The unique identifier of the service request |

### Request Body

| Field         | Type   | Required | Description |
|---------------|--------|----------|-------------|
| technician_id | number | Yes      | ID of the technician to assign |

Example:

```json
{
  "technician_id": 2
}
```

### Response

Returns the updated service request object.

## Update Status

```http
POST /api/service-requests/{id}/status
```

Updates the status of a service request.

### Path Parameters

| Parameter | Type   | Description |
|-----------|--------|-------------|
| id        | number | The unique identifier of the service request |

### Request Body

| Field        | Type   | Required | Description |
|--------------|--------|----------|-------------|
| status       | string | Yes      | New status (`pending`, `scheduled`, `in_progress`, `completed`, `cancelled`) |
| notes        | string | No       | Notes about the status change |

Example:

```json
{
  "status": "completed",
  "notes": "Repaired compressor and refilled refrigerant"
}
```

### Response

Returns the updated service request object.

## Service Request Object

| Field             | Type     | Description |
|-------------------|----------|-------------|
| id                | number   | Unique identifier for the service request |
| customer_id       | number   | ID of the customer |
| customer          | object   | Customer details |
| appliance_id      | number   | ID of the appliance |
| appliance         | object   | Appliance details |
| status            | string   | Status of the request (`pending`, `scheduled`, `in_progress`, `completed`, `cancelled`) |
| priority          | string   | Priority level (`low`, `medium`, `high`, `urgent`) |
| issue_description | string   | Description of the issue |
| diagnosis         | string   | Diagnosis of the problem (nullable) |
| resolution        | string   | Resolution of the issue (nullable) |
| technician_id     | number   | ID of the assigned technician (nullable) |
| technician        | object   | Technician details (nullable) |
| created_at        | datetime | When the service request was created |
| updated_at        | datetime | When the service request was last updated |
| scheduled_date    | datetime | When the service is scheduled (nullable) |
| appointments      | array    | List of appointments for this service request |
| parts_used        | array    | List of parts used in the repair | 