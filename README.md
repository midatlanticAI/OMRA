# OpenManus Appliance Repair Business Automation System

OpenManus is a comprehensive business automation system designed specifically for appliance repair businesses. It streamlines customer management, service requests, scheduling, and integrates with popular CRM systems.

## Features

- **Customer Management**: Store and manage customer information
- **Service Request Tracking**: Track service requests from creation to completion
- **Scheduling**: Manage technician schedules and appointments
- **CRM Integration**: Sync with Go High Level (GHL) and Kickserv
- **AI Agent System**: Hierarchical AI agents for task automation
- **Document Storage**: MongoDB-based document storage
- **Reporting**: Generate reports on business performance
- **Mobile-Friendly Interface**: Access the system from any device

## Project Structure

- `backend/`: FastAPI backend application
  - `api/`: API routes and endpoints
  - `models/`: Database models
  - `schemas/`: Pydantic schemas for validation
  - `services/`: Business logic services
  - `integrations/`: Third-party integrations
  - `agents/`: AI agent system
  - `tests/`: Backend tests

- `frontend/`: React frontend application
  - `src/components/`: React components
  - `src/context/`: React context providers
  - `src/services/`: API services
  - `src/__tests__/`: Frontend tests

- `.github/workflows/`: CI/CD configuration

## Technology Stack

### Backend
- Python 3.10+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- MongoDB
- Pydantic
- Pytest
- Anthropic Claude 3.7 Sonnet
- OpenAI GPT-4o and GPT-4o-mini

### Frontend
- React
- Axios
- React Router
- Formik
- Vitest for testing

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL
- MongoDB
- Docker and Docker Compose (optional)

### Backend Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/openmanus.git
   cd openmanus
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials, API keys, and other settings
   ```

5. Run migrations
   ```bash
   alembic upgrade head
   ```

6. Start the backend server
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Install dependencies
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server
   ```bash
   npm run dev
   ```

### Docker Setup (Alternative)

1. Build and start the containers
   ```bash
   docker-compose up -d
   ```

2. Access the application at http://localhost

## Testing

### Backend Tests

1. Run all tests
   ```bash
   cd backend
   pytest
   ```

2. Run tests with coverage
   ```bash
   pytest --cov=. --cov-report=term
   ```

3. Run specific test categories
   ```bash
   pytest tests/api/  # Only API tests
   pytest tests/integrations/  # Only integration tests
   pytest tests/agents/  # Only agent tests
   ```

### Frontend Tests

1. Run all tests
   ```bash
   cd frontend
   npm test
   ```

2. Run tests with coverage
   ```bash
   npm test -- --coverage
   ```

3. Run tests in watch mode (good for development)
   ```bash
   npm test -- --watch
   ```

## API Documentation

When the backend is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

The project includes GitHub Actions workflows for CI/CD. See the `.github/workflows/` directory for configuration details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the amazing web framework
- React team for the frontend library
- Anthropic and OpenAI for the AI models
- All contributors who have helped shape this project 