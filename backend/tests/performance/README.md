# OpenManus Performance Tests

This directory contains performance testing scripts for the OpenManus API using Locust.

## Prerequisites

- Python 3.8+
- Locust (`pip install locust`)
- Running instance of the OpenManus API

## Running Performance Tests

### Using Locust Web UI

To run the Locust tests with the web UI:

```bash
cd backend
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

Then open your browser to http://localhost:8089 to access the Locust web interface.

### Running Headless

To run Locust tests headless (e.g., for CI/CD pipelines):

```bash
cd backend
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless -u 50 -r 10 --run-time 1m
```

Parameters:
- `-u 50`: Simulates 50 users
- `-r 10`: Spawn rate of 10 users per second
- `--run-time 1m`: Run for 1 minute

## Performance Test Types

### User Types

- `OpenManusAPIUser`: Simulates a typical user who performs both read and write operations.
- `ReadOnlyUser`: Simulates a user who only reads data, never modifies it.

### API Endpoints Tested

- Health check (`/health`)
- Authentication (`/api/auth/login`)
- Customers management (`/api/customers`)
- Service requests management (`/api/service-requests`)
- Dashboard data (`/api/dashboard`)
- Technicians (`/api/technicians`)
- Appointments (`/api/appointments`)

## Running Specific Test Categories

You can run specific categories of tests using Locust tags:

```bash
# Run only customer-related tests
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --tags customers

# Run only service requests tests
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --tags service_requests
```

## Interpreting Results

After running the tests, Locust provides statistics including:
- Request count and failure rate
- Response time percentiles
- Requests per second
- Number of users

For a load testing baseline, we recommend the following metrics:
- Response time (median): < 200ms
- Response time (95th percentile): < 800ms
- Failure rate: < 1%

## Adding New Tests

To add new performance tests:
1. Add new tasks to the existing user classes in `locustfile.py`
2. Or create new user classes that extend `HttpUser` for different user behaviors
3. Use the `@task(weight)` decorator to control how frequently tasks are executed
4. Use the `@tag('category')` decorator to categorize tests 