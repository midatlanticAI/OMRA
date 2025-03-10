# OpenManus Developer Guide

Welcome to the OpenManus Developer Guide. This guide provides comprehensive information for developers working with the OpenManus Appliance Repair Business Automation System codebase.

## Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Development Environment Setup](#development-environment-setup)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Agent Architecture](#agent-architecture)
7. [Database Schema](#database-schema)
8. [API Reference](#api-reference)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [Contribution Guidelines](#contribution-guidelines)
12. [Troubleshooting](#troubleshooting)

## Introduction

OpenManus is a comprehensive business automation system designed specifically for appliance repair businesses. The system consists of a backend API built with FastAPI, a frontend application built with React, and an AI-powered agent system for process automation.

This guide is intended for developers who want to:
- Set up a development environment for OpenManus
- Understand the system architecture
- Contribute to the codebase
- Extend the system with new features
- Fix issues or bugs

## System Architecture

OpenManus follows a modern, microservices-oriented architecture with clear separation of concerns:

![System Architecture](images/system-architecture.png)

### Key Components

1. **Backend API**: FastAPI-based REST API for all CRUD operations
2. **Frontend Application**: React-based single-page application
3. **Agent System**: AI-powered automation engine
4. **Databases**: PostgreSQL for structured data, MongoDB for unstructured data
5. **Integration Services**: Connectors for third-party services
6. **Authentication Service**: JWT-based authentication and authorization
7. **Task Queue**: Asynchronous job processing
8. **Caching Layer**: Redis-based caching for performance optimization

See [System Architecture](architecture.md) for detailed information.

## Development Environment Setup

This section provides instructions for setting up a development environment for OpenManus.

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL 14+
- MongoDB 6+
- Redis 7+

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/openmanus/openmanus.git
   cd openmanus
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Start the development environment with Docker Compose:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

5. Run the backend in development mode:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

6. Run the frontend in development mode:
   ```bash
   cd frontend
   npm run dev
   ```

See [Development Environment Setup](development-environment.md) for detailed instructions.

## Backend Development

The backend of OpenManus is built with FastAPI, a modern, fast, web framework for building APIs with Python 3.7+.

### Project Structure

```
backend/
├── api/                # API routes
├── core/               # Core functionality
├── db/                 # Database models and session management
├── integrations/       # Third-party integrations
├── agents/             # Agent system
├── models/             # Pydantic models
├── schemas/            # API schema definitions
├── services/           # Business logic
├── tests/              # Tests
├── utils/              # Utility functions
├── main.py             # Application entry point
└── requirements.txt    # Dependencies
```

### Key Technologies

- **FastAPI**: Web framework
- **SQLAlchemy**: ORM for PostgreSQL
- **Motor**: MongoDB driver
- **Pydantic**: Data validation
- **JWT**: Authentication
- **Pytest**: Testing
- **Alembic**: Database migrations

See [Backend Development](backend-development.md) for detailed information.

## Frontend Development

The frontend of OpenManus is built with React, a popular JavaScript library for building user interfaces.

### Project Structure

```
frontend/
├── public/             # Static assets
├── src/
│   ├── components/     # Reusable components
│   ├── contexts/       # React contexts
│   ├── hooks/          # Custom hooks
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── utils/          # Utility functions
│   ├── App.jsx         # Main application component
│   └── main.jsx        # Application entry point
├── tests/              # Tests
├── package.json        # Dependencies
└── vite.config.js      # Vite configuration
```

### Key Technologies

- **React**: UI library
- **Material-UI**: Component library
- **React Router**: Routing
- **Axios**: HTTP client
- **Formik**: Form handling
- **Yup**: Form validation
- **Chart.js**: Data visualization
- **Vite**: Build tool
- **Vitest**: Testing

See [Frontend Development](frontend-development.md) for detailed information.

## Agent Architecture

The Agent Architecture is a core component of OpenManus that provides AI-powered automation for various business processes.

### Components

- **Agent Manager**: Manages agent execution and communication
- **Executive Agent**: Handles decision-making and task delegation
- **Task Agent**: Performs specific tasks
- **Workflow Engine**: Manages business process workflows
- **Tool Registry**: Provides tools for agents to use

See [Agent Architecture](agent-architecture.md) for detailed information.

## Database Schema

OpenManus uses two databases:

1. **PostgreSQL**: For structured data like customers, service requests, etc.
2. **MongoDB**: For unstructured data like documents, agent states, etc.

See [Database Schema](database-schema.md) for detailed information.

## API Reference

The OpenManus API is a RESTful API that follows modern API design principles.

See [API Reference](../api/README.md) for detailed information.

## Testing

OpenManus has a comprehensive testing suite that includes unit tests, integration tests, end-to-end tests, performance tests, and security tests.

See [Testing](testing.md) for detailed information.

## Deployment

OpenManus can be deployed in various environments, from single-server setups to distributed cloud deployments.

See [Deployment](../deployment/README.md) for detailed information.

## Contribution Guidelines

We welcome contributions to OpenManus! Please follow these guidelines when contributing:

- **Code Style**: Follow the established code style and conventions
- **Testing**: Write tests for new features and bug fixes
- **Documentation**: Update documentation for changes
- **Pull Requests**: Create a pull request with a clear description of the changes
- **Issues**: Report issues with a clear description and steps to reproduce

See [Contribution Guidelines](contribution-guidelines.md) for detailed information.

## Troubleshooting

This section provides solutions to common issues you might encounter during development.

See [Troubleshooting](troubleshooting.md) for more information. 