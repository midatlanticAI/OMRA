// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// -- This is a parent command --
Cypress.Commands.add('login', (email, password) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/login`,
    body: {
      email,
      password,
    },
  }).then((response) => {
    localStorage.setItem('token', response.body.access_token);
    localStorage.setItem('user', JSON.stringify(response.body.user));
    return response;
  });
});

// Custom command to navigate to dashboard
Cypress.Commands.add('navigateToDashboard', () => {
  cy.visit('/dashboard');
  cy.url().should('include', '/dashboard');
  cy.get('[data-testid=dashboard-title]').should('be.visible');
});

// Custom command to navigate to customers page
Cypress.Commands.add('navigateToCustomers', () => {
  cy.visit('/customers');
  cy.url().should('include', '/customers');
  cy.get('[data-testid=customers-title]').should('be.visible');
});

// Custom command to navigate to service requests page
Cypress.Commands.add('navigateToServiceRequests', () => {
  cy.visit('/service-requests');
  cy.url().should('include', '/service-requests');
  cy.get('[data-testid=service-requests-title]').should('be.visible');
});

// Custom command to create a customer
Cypress.Commands.add('createCustomer', (customerData) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/customers`,
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: customerData,
  });
});

// Custom command to create a service request
Cypress.Commands.add('createServiceRequest', (serviceRequestData) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/service-requests`,
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: serviceRequestData,
  });
}); 