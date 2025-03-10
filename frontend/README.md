# OpenManus Frontend

This is the frontend application for the OpenManus Appliance Repair Business Automation System. It provides a modern, responsive user interface built with React and Material UI.

## Features

- **Dashboard:** Real-time overview of business metrics, recent customers, and upcoming jobs
- **Customer Management:** Add, edit, and manage customer information with search and filtering
- **Service Requests:** Track and manage service requests through their lifecycle
- **Integrations:** Connect with third-party systems like Go High Level CRM and Kickserv
- **Responsive Design:** Works on desktop, tablet, and mobile devices

## Tech Stack

- React 18 with functional components and hooks
- Material UI for component design and theming
- React Router for navigation
- Formik and Yup for form handling and validation
- Axios for API communication
- Chart.js for data visualization
- Vite for build tooling
- Vitest for testing

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/openmanus.git
cd openmanus/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173` by default.

## Project Structure

```
frontend/
├── public/           # Static assets
├── src/
│   ├── assets/       # Images, fonts, etc.
│   ├── components/   # Reusable UI components
│   ├── context/      # React context providers
│   ├── hooks/        # Custom React hooks
│   ├── pages/        # Page components
│   ├── services/     # API services
│   ├── utils/        # Utility functions
│   ├── App.jsx       # Main application component
│   ├── main.jsx      # Application entry point
│   └── theme.js      # Material UI theme configuration
├── tests/            # Test files
├── .eslintrc.js      # ESLint configuration
├── package.json      # Project dependencies and scripts
├── vite.config.js    # Vite configuration
└── vitest.config.js  # Vitest configuration
```

## Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build the application for production
- `npm run preview` - Preview the production build locally
- `npm run test` - Run tests
- `npm run lint` - Lint the codebase

## Environment Variables

Create a `.env` file in the frontend directory with the following variables:

```
VITE_API_URL=http://localhost:8000  # Backend API URL
```

## Authentication

The application uses JWT-based authentication. The auth token is stored in localStorage and automatically included in API requests through an Axios interceptor.

## Testing

Tests are written using Vitest and React Testing Library. Run tests with:

```bash
npm run test
```

## Deployment

Build the application for production:

```bash
npm run build
```

The built files will be in the `dist` directory, ready to be deployed to any static hosting service.

## Integration with Backend

The frontend communicates with the OpenManus backend API. Make sure the backend server is running and configured correctly in the `.env` file.

## Contributing

Please refer to the main repository's contributing guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 