---
name: fe-unit-test-writer
description: Write unit tests for TypeScript/React frontend components, hooks, and utilities. Use when creating tests for individual components in isolation, custom hooks, or utility functions.
---

# Frontend Unit Test Writer

Write comprehensive **unit tests** for TypeScript/React frontend code, focusing on components, hooks, and utilities tested in isolation.

## When to Use

- Creating tests for React components (rendering, props, basic interactions)
- Testing custom hooks in isolation
- Writing tests for utility functions and helpers
- Testing individual UI elements without API dependencies

## Framework & Tools

- **Vitest** or **Jest** for unit testing
- **React Testing Library** for component tests
- **@testing-library/react-hooks** for hook tests (if using older RTL)

## Test File Organization

| Test Type | File Pattern | Purpose |
|-----------|--------------|---------|
| Component tests | `*.test.tsx` | React component rendering and interactions |
| Hook tests | `*.test.ts` | Custom hook behavior |
| Utility tests | `*.test.ts` | Pure function logic |

## Naming Conventions

- **Test files**: `<ComponentName>.test.tsx` or `<module>.test.ts`
- **Test suites**: `describe('<ComponentName>', () => { ... })`
- **Test cases**: `it('should <expected behavior>', () => { ... })`

## Component Test Pattern

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('should render with provided label', () => {
    render(<Button label="Click me" />);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('should call onClick handler when clicked', () => {
    const handleClick = vi.fn();
    render(<Button label="Click" onClick={handleClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledOnce();
  });

  it('should be disabled when disabled prop is true', () => {
    render(<Button label="Click" disabled />);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

## Hook Test Pattern

```typescript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './use-counter';

describe('useCounter', () => {
  it('should initialize with default value', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  it('should increment count', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });

  it('should initialize with custom value', () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });
});
```

## Utility Test Pattern

```typescript
import { formatCurrency, truncateText } from './utils';

describe('formatCurrency', () => {
  it('should format number as USD currency', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
  });

  it('should handle zero', () => {
    expect(formatCurrency(0)).toBe('$0.00');
  });

  it('should handle negative numbers', () => {
    expect(formatCurrency(-50)).toBe('-$50.00');
  });
});

describe('truncateText', () => {
  it('should truncate text longer than max length', () => {
    expect(truncateText('Hello World', 5)).toBe('Hello...');
  });

  it('should not truncate text shorter than max length', () => {
    expect(truncateText('Hi', 10)).toBe('Hi');
  });
});
```

## Required Test Categories

For each component/hook/utility, write tests covering:

1. **Default rendering** — component renders without errors
2. **Props handling** — different prop combinations work correctly
3. **User interactions** — clicks, inputs, keyboard events
4. **Edge cases** — empty props, undefined values, boundary conditions
5. **Conditional rendering** — different states show correct UI

## Testing Query Priority

Use queries in this order of preference (per Testing Library best practices):

1. `getByRole` — accessible by role (button, textbox, etc.)
2. `getByLabelText` — form fields with labels
3. `getByPlaceholderText` — inputs with placeholders
4. `getByText` — non-interactive elements
5. `getByTestId` — last resort, requires data-testid

```typescript
// Preferred
screen.getByRole('button', { name: 'Submit' })
screen.getByLabelText('Email')

// Avoid unless necessary
screen.getByTestId('submit-button')
```

## Async Testing

For components with async behavior:

```typescript
import { render, screen, waitFor } from '@testing-library/react';

it('should show loading state then content', async () => {
  render(<AsyncComponent />);
  
  // Initially shows loading
  expect(screen.getByText('Loading...')).toBeInTheDocument();
  
  // Wait for content
  await waitFor(() => {
    expect(screen.getByText('Content loaded')).toBeInTheDocument();
  });
});
```

## Running Tests

```bash
cd frontend
npm test                        # Run all tests
npm test -- Button.test.tsx     # Run specific file
npm test -- --watch             # Watch mode
npm test -- --coverage          # With coverage report
```

## Quality Checklist

- [ ] Each component has at least one render test
- [ ] Interactive elements have interaction tests
- [ ] Props variations are tested
- [ ] Edge cases are identified and tested
- [ ] Tests are independent and can run in any order
- [ ] Descriptive test names using `should <behavior>` format
- [ ] Using accessible queries (getByRole, getByLabelText) over getByTestId

## Anti-Patterns to Avoid

- **Testing implementation details** — test behavior, not internal state
- **Snapshot overuse** — use sparingly, prefer explicit assertions
- **Querying by class/id** — use accessible queries instead
- **Missing async handling** — always await async operations
- **Shared mutable state** — reset mocks between tests
