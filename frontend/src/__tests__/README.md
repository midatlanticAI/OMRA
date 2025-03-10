# OpenManus Frontend Tests

This directory contains tests for the OpenManus Appliance Repair Business Automation System frontend.

## Test Structure

- `components/`: Tests for React components
- `services/`: Tests for service modules
- `utils/`: Tests for utility functions

## Running Tests

To run the tests, use the following command from the frontend directory:

```bash
npm test
```

To run tests with coverage:

```bash
npm test -- --coverage
```

To run tests in watch mode during development:

```bash
npm test -- --watch
```

## Test Environment

Tests use Vitest with the JSDOM environment to simulate a browser environment. The setup file in `src/setupTests.js` provides mocks for browser APIs not available in JSDOM.

## Writing Tests

When writing tests:

1. Use React Testing Library for component tests
2. Focus on testing behavior rather than implementation details
3. Use descriptive test names that explain what is being tested
4. Mock external dependencies and API calls

Example component test:

```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MyComponent from '../MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('handles user interaction', () => {
    const handleClick = vi.fn();
    render(<MyComponent onClick={handleClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

## Continuous Integration

Tests are automatically run on GitHub Actions when changes are pushed to the repository. See the `.github/workflows/frontend-ci.yml` file for details. 