// Import necessary testing libraries
import '@testing-library/jest-dom';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Clean up after each test to avoid test state leakage
afterEach(() => {
  cleanup();
});

// Mock for ResizeObserver which isn't available in JSDOM
global.ResizeObserver = class ResizeObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock for window.matchMedia which isn't available in JSDOM
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock localStorage
const localStorageMock = (function() {
  let store = {};
  return {
    getItem: key => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    removeItem: key => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
    length: Object.keys(store).length,
    key: index => Object.keys(store)[index],
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock scrollIntoView which isn't available in JSDOM
Element.prototype.scrollIntoView = vi.fn(); 