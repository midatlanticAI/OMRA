/// <reference types="cypress" />

describe('Authentication Tests', () => {
  beforeEach(() => {
    // Reset the app state before each test
    cy.clearLocalStorage();
    cy.clearCookies();
    cy.visit('/login');
  });

  it('should show login form', () => {
    cy.get('[data-testid=login-form]').should('be.visible');
    cy.get('[data-testid=email-input]').should('be.visible');
    cy.get('[data-testid=password-input]').should('be.visible');
    cy.get('[data-testid=login-button]').should('be.visible');
  });

  it('should validate login form inputs', () => {
    // Click login without entering any data
    cy.get('[data-testid=login-button]').click();
    cy.get('[data-testid=email-error]').should('be.visible');
    cy.get('[data-testid=password-error]').should('be.visible');

    // Enter invalid email
    cy.get('[data-testid=email-input]').type('invalid-email');
    cy.get('[data-testid=login-button]').click();
    cy.get('[data-testid=email-error]').should('be.visible');

    // Enter valid email but no password
    cy.get('[data-testid=email-input]').clear().type('admin@example.com');
    cy.get('[data-testid=login-button]').click();
    cy.get('[data-testid=email-error]').should('not.exist');
    cy.get('[data-testid=password-error]').should('be.visible');
  });

  it('should login successfully with valid credentials', () => {
    // This test assumes there's a test user in the system
    cy.get('[data-testid=email-input]').type('admin@example.com');
    cy.get('[data-testid=password-input]').type('password123');
    cy.get('[data-testid=login-button]').click();

    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid=user-menu]').should('be.visible');
  });

  it('should show error with invalid credentials', () => {
    cy.get('[data-testid=email-input]').type('admin@example.com');
    cy.get('[data-testid=password-input]').type('wrongpassword');
    cy.get('[data-testid=login-button]').click();

    // Should show error message
    cy.get('[data-testid=login-error]').should('be.visible');
    cy.url().should('include', '/login');
  });

  it('should logout successfully', () => {
    // Login first
    cy.get('[data-testid=email-input]').type('admin@example.com');
    cy.get('[data-testid=password-input]').type('password123');
    cy.get('[data-testid=login-button]').click();

    // Should be on dashboard
    cy.url().should('include', '/dashboard');

    // Click on user menu
    cy.get('[data-testid=user-menu]').click();
    cy.get('[data-testid=logout-button]').click();

    // Should redirect to login page
    cy.url().should('include', '/login');
  });
}); 