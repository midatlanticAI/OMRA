# OpenManus Backend Tests

This directory contains tests for the OpenManus Appliance Repair Business Automation System backend.

## Test Structure

- `api/`: Tests for API endpoints
- `integrations/`: Tests for third-party integrations
- `conftest.py`: Pytest configuration and fixtures

## Running Tests

To run the tests, use the following command from the backend directory:

```bash
pytest
```

For more verbose output:

```bash
pytest -v
```

To run tests with coverage:

```bash
pytest --cov=. --cov-report=term
```

## Test Environment

Tests use an in-memory SQLite database by default. This can be overridden by setting the `DATABASE_URL` environment variable.

## Writing Tests

When writing tests:

1. Use the fixtures defined in `conftest.py` for database access and API clients
2. Group tests by functionality in appropriate directories
3. Use descriptive test names that explain what is being tested
4. Mock external dependencies when testing integrations

## Continuous Integration

Tests are automatically run on GitHub Actions when changes are pushed to the repository. See the `.github/workflows/backend-ci.yml` file for details. 