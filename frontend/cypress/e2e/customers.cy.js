/// <reference types="cypress" />

describe('Customer Management Tests', () => {
  const testCustomer = {
    first_name: 'Test',
    last_name: 'Customer',
    email: 'test.customer@example.com',
    phone: '555-123-4567',
    address_line1: '123 Main St',
    city: 'Anytown',
    state: 'CA',
    zip: '12345',
  };

  beforeEach(() => {
    // Login using the custom command
    cy.login('admin@example.com', 'password123');
    cy.navigateToCustomers();
  });

  it('should display customer list', () => {
    cy.get('[data-testid=customer-list]').should('be.visible');
    cy.get('[data-testid=add-customer-button]').should('be.visible');
  });

  it('should open and validate add customer form', () => {
    cy.get('[data-testid=add-customer-button]').click();
    cy.get('[data-testid=customer-form]').should('be.visible');
    
    // Test form validation
    cy.get('[data-testid=save-customer-button]').click();
    cy.get('[data-testid=first-name-error]').should('be.visible');
    cy.get('[data-testid=last-name-error]').should('be.visible');
    cy.get('[data-testid=email-error]').should('be.visible');
  });

  it('should add a new customer', () => {
    // Open add customer form
    cy.get('[data-testid=add-customer-button]').click();
    
    // Fill the form
    cy.get('[data-testid=first-name-input]').type(testCustomer.first_name);
    cy.get('[data-testid=last-name-input]').type(testCustomer.last_name);
    cy.get('[data-testid=email-input]').type(testCustomer.email);
    cy.get('[data-testid=phone-input]').type(testCustomer.phone);
    cy.get('[data-testid=address-line1-input]').type(testCustomer.address_line1);
    cy.get('[data-testid=city-input]').type(testCustomer.city);
    cy.get('[data-testid=state-input]').type(testCustomer.state);
    cy.get('[data-testid=zip-input]').type(testCustomer.zip);
    
    // Submit the form
    cy.get('[data-testid=save-customer-button]').click();
    
    // Verify success message
    cy.get('[data-testid=success-alert]').should('be.visible');
    
    // Verify the customer appears in the list
    cy.get('[data-testid=customer-list]').contains(`${testCustomer.first_name} ${testCustomer.last_name}`);
  });

  it('should search for a customer', () => {
    // Ensure our test customer exists
    cy.createCustomer(testCustomer);
    cy.reload();
    
    // Search for the customer
    cy.get('[data-testid=customer-search-input]').type(testCustomer.email);
    cy.get('[data-testid=search-button]').click();
    
    // Verify search results
    cy.get('[data-testid=customer-list]').contains(`${testCustomer.first_name} ${testCustomer.last_name}`);
    cy.get('[data-testid=customer-list]').contains(testCustomer.email);
  });

  it('should view customer details', () => {
    // Ensure our test customer exists
    cy.createCustomer(testCustomer);
    cy.reload();
    
    // Find and click on the customer
    cy.get('[data-testid=customer-list]')
      .contains(`${testCustomer.first_name} ${testCustomer.last_name}`)
      .closest('[data-testid=customer-row]')
      .find('[data-testid=view-customer-button]')
      .click();
    
    // Verify customer details
    cy.get('[data-testid=customer-details]').should('be.visible');
    cy.get('[data-testid=customer-details]').contains(testCustomer.email);
    cy.get('[data-testid=customer-details]').contains(testCustomer.phone);
    cy.get('[data-testid=customer-details]').contains(testCustomer.address_line1);
  });

  it('should edit a customer', () => {
    // Ensure our test customer exists
    cy.createCustomer(testCustomer);
    cy.reload();
    
    // Find and click on the customer edit button
    cy.get('[data-testid=customer-list]')
      .contains(`${testCustomer.first_name} ${testCustomer.last_name}`)
      .closest('[data-testid=customer-row]')
      .find('[data-testid=edit-customer-button]')
      .click();
    
    // Edit the customer
    const updatedPhone = '555-987-6543';
    cy.get('[data-testid=phone-input]').clear().type(updatedPhone);
    
    // Save the changes
    cy.get('[data-testid=save-customer-button]').click();
    
    // Verify success message
    cy.get('[data-testid=success-alert]').should('be.visible');
    
    // Verify the customer was updated
    cy.get('[data-testid=customer-list]').contains(updatedPhone);
  });
}); 