---
name: fe-integration-test-writer
description: Write integration tests for TypeScript/React frontend features. Use when creating tests that involve multiple components working together, user flows, form submissions, or API interactions with mocked backends.
---

# Frontend Integration Test Writer

Write comprehensive **integration tests** for TypeScript/React frontend features, testing component interactions, user flows, and API integrations.

## When to Use

- Testing user flows that span multiple components
- Testing form submissions with validation
- Testing components that fetch data from APIs
- Testing navigation and routing behavior
- Testing complex interactions between parent/child components

## Framework & Tools

- **Vitest** or **Jest** for test running
- **React Testing Library** for component interaction
- **MSW (Mock Service Worker)** for API mocking
- **user-event** for realistic user interactions

## Test File Organization

| Test Type | File Pattern | Purpose |
|-----------|--------------|---------|
| Feature tests | `*.integration.test.tsx` | Multi-component flows |
| Page tests | `*.page.test.tsx` | Full page behavior |
| Flow tests | `*.flow.test.tsx` | User journey tests |

## MSW Setup for API Mocking

```typescript
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: 1, name: 'John Doe' },
      { id: 2, name: 'Jane Smith' },
    ]);
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: 3, ...body }, { status: 201 });
  }),

  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'John Doe' });
  }),
];
```

```typescript
// src/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

```typescript
// vitest.setup.ts or jest.setup.ts
import { server } from './src/mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## User Flow Test Pattern

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserManagement } from './UserManagement';

describe('UserManagement', () => {
  it('should load and display users from API', async () => {
    render(<UserManagement />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    
    // Verify users are displayed
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('should create new user and update list', async () => {
    const user = userEvent.setup();
    render(<UserManagement />);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    
    // Open create form
    await user.click(screen.getByRole('button', { name: 'Add User' }));
    
    // Fill form
    await user.type(screen.getByLabelText('Name'), 'New User');
    await user.type(screen.getByLabelText('Email'), 'new@example.com');
    
    // Submit
    await user.click(screen.getByRole('button', { name: 'Save' }));
    
    // Verify success
    await waitFor(() => {
      expect(screen.getByText('User created successfully')).toBeInTheDocument();
    });
  });
});
```

## Form Validation Test Pattern

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ContactForm } from './ContactForm';

describe('ContactForm', () => {
  it('should show validation errors for empty required fields', async () => {
    const user = userEvent.setup();
    render(<ContactForm />);
    
    // Submit without filling form
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    
    // Check for validation errors
    expect(screen.getByText('Name is required')).toBeInTheDocument();
    expect(screen.getByText('Email is required')).toBeInTheDocument();
  });

  it('should show error for invalid email format', async () => {
    const user = userEvent.setup();
    render(<ContactForm />);
    
    await user.type(screen.getByLabelText('Email'), 'invalid-email');
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    
    expect(screen.getByText('Invalid email format')).toBeInTheDocument();
  });

  it('should submit form with valid data', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ContactForm onSubmit={onSubmit} />);
    
    await user.type(screen.getByLabelText('Name'), 'John Doe');
    await user.type(screen.getByLabelText('Email'), 'john@example.com');
    await user.type(screen.getByLabelText('Message'), 'Hello!');
    
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com',
        message: 'Hello!',
      });
    });
  });
});
```

## Error Handling Test Pattern

```typescript
import { http, HttpResponse } from 'msw';
import { server } from '../mocks/server';

describe('UserList error handling', () => {
  it('should display error message when API fails', async () => {
    // Override handler for this test
    server.use(
      http.get('/api/users', () => {
        return HttpResponse.json(
          { message: 'Internal Server Error' },
          { status: 500 }
        );
      })
    );
    
    render(<UserList />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load users')).toBeInTheDocument();
    });
    
    // Verify retry button exists
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
  });

  it('should show not found message for 404', async () => {
    server.use(
      http.get('/api/users/:id', () => {
        return HttpResponse.json(
          { message: 'User not found' },
          { status: 404 }
        );
      })
    );
    
    render(<UserDetail userId="999" />);
    
    await waitFor(() => {
      expect(screen.getByText('User not found')).toBeInTheDocument();
    });
  });
});
```

## Required Test Categories

For each feature, write tests covering:

1. **Happy path** — complete user flow works correctly
2. **Loading states** — spinners/skeletons shown during API calls
3. **Error states** — API failures handled gracefully
4. **Validation** — form validation prevents invalid submissions
5. **Edge cases** — empty data, network timeouts, rapid interactions

## Using user-event vs fireEvent

Prefer `userEvent` for realistic interactions:

```typescript
import userEvent from '@testing-library/user-event';

// Setup user-event
const user = userEvent.setup();

// Realistic typing (includes focus, keydown, keyup)
await user.type(input, 'hello');

// Realistic click (includes hover, mousedown, mouseup)
await user.click(button);

// Clear and type
await user.clear(input);
await user.type(input, 'new value');

// Select from dropdown
await user.selectOptions(select, 'option-value');
```

## Running Tests

```bash
cd frontend
npm test                                # Run all tests
npm test -- *.integration.test.tsx      # Run integration tests
npm test -- UserManagement.test.tsx     # Run specific file
npm test -- --watch                     # Watch mode
```

## Quality Checklist

- [ ] User flows are tested end-to-end
- [ ] Loading states are verified
- [ ] Error scenarios are covered
- [ ] Form validation is tested
- [ ] API mocks return realistic data
- [ ] Tests use userEvent for interactions
- [ ] Async operations properly awaited
- [ ] MSW handlers are reset between tests

## Anti-Patterns to Avoid

- **Testing implementation details** — test user-visible behavior
- **Hardcoded timeouts** — use `waitFor` instead of `setTimeout`
- **Missing error scenarios** — always test failure paths
- **Overly coupled tests** — tests should be independent
- **Not resetting mocks** — use `afterEach` to reset MSW handlers
- **Ignoring loading states** — verify UX during async operations
