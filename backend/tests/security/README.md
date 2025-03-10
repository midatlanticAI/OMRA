# OpenManus Security Tests

This directory contains security testing scripts for the OpenManus API.

## Overview

The security tests are designed to validate that the OpenManus application is protected against common security vulnerabilities and follows security best practices. The tests cover:

1. **Authentication and Authorization**
   - Token-based authentication
   - Permission checks
   - Protection against brute force attacks
   - Token validation and expiration

2. **API Security**
   - Input validation
   - Protection against injection attacks (SQL, NoSQL)
   - Cross-Site Scripting (XSS) protection
   - Boundary testing and rate limiting

## Prerequisites

- Python 3.8+
- pytest (`pip install pytest`)
- Running instance of the OpenManus API with test data

## Running Security Tests

### Running All Security Tests

To run all security tests:

```bash
cd backend
pytest tests/security/
```

### Running Specific Test Categories

To run specific test categories:

```bash
# Run only authentication tests
pytest tests/security/test_authentication.py

# Run only API security tests
pytest tests/security/test_api_security.py
```

### Running with Verbose Output

For more detailed output:

```bash
pytest tests/security/ -v
```

## Interpreting Results

After running the tests, pytest will provide a summary of passed and failed tests. For each failed test, pytest shows:

- The name of the failed test
- The line number where the test failed
- The assertion that failed
- Expected vs. actual values

## Adding New Security Tests

When adding new security tests:

1. Identify a security concern or vulnerability to test
2. Create a new test method in the appropriate test class
3. Use descriptive test names that explain what security aspect is being tested
4. Include clear assertions that validate the security control is working
5. Document any setup requirements or assumptions

## Security Testing Best Practices

- **Isolation**: Security tests should run in isolation and not interfere with each other
- **Test Data**: Use dedicated test data, never use production credentials
- **False Positives**: Be aware of false positives and validate findings
- **Coverage**: Try to cover all API endpoints and security controls
- **Documentation**: Document findings and recommended fixes

## Automated Security Testing

These tests are integrated into the CI/CD pipeline in `.github/workflows/backend-ci.yml` to automatically run on code changes.

## Manual Security Testing

In addition to these automated tests, periodic manual security testing is recommended using tools like:

- OWASP ZAP for web application security scanning
- SQLmap for SQL injection testing
- Burp Suite for comprehensive web security testing

## Security Reporting

If you find a security vulnerability, please report it to the security team at security@openmanus.io rather than creating a public issue. 