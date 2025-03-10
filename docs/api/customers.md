# Customers API

The Customers API provides access to customer data within the OpenManus system. This includes creating, retrieving, updating, and deleting customer records.

## Table of Contents

1. [List Customers](#list-customers)
2. [Get Customer](#get-customer)
3. [Create Customer](#create-customer)
4. [Update Customer](#update-customer)
5. [Delete Customer](#delete-customer)
6. [Customer Object](#customer-object)

## List Customers

```http
GET /api/customers
```

Retrieves a paginated list of customers.

### Query Parameters

| Parameter | Type   | Description |
|-----------|--------|-------------|
| page      | number | Page number for pagination (default: 1) |
| limit     | number | Number of results per page (default: 20, max: 100) |
| search    | string | Search term to filter results by name, email, or phone |
| sort      | string | Field to sort by (e.g., `first_name`, `last_name`, `created_at`) |
| order     | string | Sort order: `asc` or `desc` (default: `asc`) |

### Response

```json
{
  "items": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "phone": "555-123-4567",
      "address_line1": "123 Main St",
      "address_line2": null,
      "city": "Anytown",
      "state": "CA",
      "zip": "12345",
      "notes": "Prefers appointments in the morning",
      "created_at": "2023-03-15T10:30:00Z",
      "updated_at": "2023-03-15T10:30:00Z"
    },
    // More customer objects...
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total_items": 42,
    "total_pages": 3
  }
}
```

## Get Customer

```http
GET /api/customers/{id}
```

Retrieves a specific customer by ID.

### Path Parameters

| Parameter | Type   | Description |
|-----------|--------|-------------|
| id        | number | The unique identifier of the customer |

### Response

```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "555-123-4567",
  "address_line1": "123 Main St",
  "address_line2": null,
  "city": "Anytown",
  "state": "CA",
  "zip": "12345",
  "notes": "Prefers appointments in the morning",
  "created_at": "2023-03-15T10:30:00Z",
  "updated_at": "2023-03-15T10:30:00Z",
  "appliances": [
    {
      "id": 1,
      "type": "refrigerator",
      "brand": "GE",
      "model": "XYZ123",
      "serial_number": "ABC12345"
    }
  ],
  "service_requests": [
    {
      "id": 1,
      "status": "scheduled",
      "issue_description": "Not cooling properly"
    }
  ]
}
```

## Create Customer

```http
POST /api/customers
```

Creates a new customer.

### Request Body

| Field         | Type   | Required | Description |
|---------------|--------|----------|-------------|
| first_name    | string | Yes      | First name of the customer |
| last_name     | string | Yes      | Last name of the customer |
| email         | string | Yes      | Email address (must be unique) |
| phone         | string | No       | Phone number |
| address_line1 | string | No       | First line of the address |
| address_line2 | string | No       | Second line of the address |
| city          | string | No       | City |
| state         | string | No       | State or province |
| zip           | string | No       | ZIP or postal code |
| notes         | string | No       | Additional notes about the customer |

Example:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "555-123-4567",
  "address_line1": "123 Main St",
  "city": "Anytown",
  "state": "CA",
  "zip": "12345",
  "notes": "Prefers appointments in the morning"
}
```

### Response

Returns the created customer object with the HTTP status code 201 (Created).

## Update Customer

```http
PUT /api/customers/{id}
```

Updates an existing customer.

### Path Parameters

| Parameter | Type   | Description |
|-----------|--------|-------------|
| id        | number | The unique identifier of the customer |

### Request Body

The request body should contain the fields to update. All fields are optional, but at least one field must be provided.

Example:

```json
{
  "phone": "555-987-6543",
  "notes": "Updated notes for this customer"
}
```

### Response

Returns the updated customer object.

## Delete Customer

```http
DELETE /api/customers/{id}
```

Deletes a customer. This operation cannot be undone.

### Path Parameters

| Parameter | Type   | Description |
|-----------|--------|-------------|
| id        | number | The unique identifier of the customer |

### Response

Returns HTTP status code 204 (No Content) on successful deletion.

## Customer Object

| Field         | Type     | Description |
|---------------|----------|-------------|
| id            | number   | Unique identifier for the customer |
| first_name    | string   | First name |
| last_name     | string   | Last name |
| email         | string   | Email address |
| phone         | string   | Phone number |
| address_line1 | string   | First line of the address |
| address_line2 | string   | Second line of the address |
| city          | string   | City |
| state         | string   | State or province |
| zip           | string   | ZIP or postal code |
| notes         | string   | Additional notes |
| created_at    | datetime | When the customer was created |
| updated_at    | datetime | When the customer was last updated |
| appliances    | array    | List of appliances owned by the customer (included in detailed view) |
| service_requests | array | List of service requests for the customer (included in detailed view) | 