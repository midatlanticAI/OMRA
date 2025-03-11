# OMRA Lite - OpenManus Rapid Automation (Lite Version)

A lightweight, standalone version of the OpenManus system with a built-in dashboard, local MongoDB storage, and AI-powered agent automation.

## Features

- **10-Minute Setup**: Get up and running in under 10 minutes
- **All-in-One Package**: Combined backend, frontend, and database
- **Local MongoDB**: No external dependencies required
- **AI Agent System**: Intelligent automation for business processes
- **Built-in Dashboard**: Manage customers, service requests, and automation
- **CRM Extension Tools**: Customer management, service history, and more
- **Secure Authentication**: Pre-configured admin account
- **API Documentation**: Built-in Swagger UI

## Quick Start

### Prerequisites

- Python 3.9+ 
- Node.js 14+
- MongoDB (local installation)

### Installation

1. **Clone this repository**

```bash
git clone https://github.com/your-org/omra-lite.git
cd omra-lite
```

2. **Install dependencies**

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

3. **Start MongoDB**

Make sure MongoDB is running locally. If you need to install it:

- Windows: [Install MongoDB on Windows](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/)
- macOS: `brew install mongodb-community`
- Linux: [Install MongoDB on Linux](https://docs.mongodb.com/manual/administration/install-on-linux/)

4. **Start the application**

```bash
# Start the backend
cd backend
python main.py
```

In a new terminal:
```bash
# Start the frontend
cd frontend
npm start
```

5. **Access the dashboard**

Open your browser and go to http://localhost:3000

Login with:
- Username: `admin`
- Password: `admin1`

## Dashboard

The dashboard provides access to:

- **Customer Management**: View and manage customer information
- **Service Requests**: Create and track service requests
- **Technician Management**: Assign and schedule technicians
- **Agent System**: Manage AI agents and automation
- **Analytics**: View performance metrics and reports

## Agent System

OMRA Lite includes a simplified agent system that can:

- Assist with customer inquiries
- Help diagnose appliance issues
- Create and manage service requests
- Automate routine tasks

## API Documentation

API documentation is available at http://localhost:8000/docs

## Security

- Built-in authentication system
- Secure password storage
- JWT token-based API access
- Role-based access control

## Extending OMRA Lite

You can extend OMRA Lite by:

- Adding new tools to the agent system
- Creating custom dashboard widgets
- Integrating with other systems via the API
- Adding new data models and functionality

## License

[Your license information here] 