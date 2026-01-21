import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import Leads from '@/pages/Leads';
import { toast } from 'sonner';

// Mock the hooks
vi.mock('@/hooks/use-leads', () => ({
  useLeads: vi.fn(),
  useCreateLead: vi.fn(),
  useUpdateLead: vi.fn(),
}));

vi.mock('@/hooks/use-contacts', () => ({
  useContactSearch: vi.fn(),
}));

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock ConvertToOpportunityDialog
vi.mock('@/components/leads/ConvertToOpportunityDialog', () => ({
  ConvertToOpportunityDialog: () => null,
}));

describe('Lead Creation Flow Integration', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
  });

  const renderWithProviders = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>{component}</BrowserRouter>
      </QueryClientProvider>
    );
  };

  it('should load and display leads from API', async () => {
    // Arrange
    const mockLeads = {
      items: [
        {
          id: 1,
          status: 'cold',
          source: 'manual',
          contact_id: 1,
          contact_name: 'John Doe',
          contact_email: 'john@test.com',
          contact_phone: '+43 123456',
          contact_mobile: null,
          contact_position: 'Manager',
          company_name: 'Test Corp',
          campaign_id: null,
          campaign_name: null,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1,
    };

    const { useLeads } = await import('@/hooks/use-leads');
    vi.mocked(useLeads).mockReturnValue({
      data: mockLeads,
      isLoading: false,
      error: null,
    } as any);

    const { useUpdateLead, useCreateLead } = await import('@/hooks/use-leads');
    vi.mocked(useUpdateLead).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);
    vi.mocked(useCreateLead).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    const { useContactSearch } = await import('@/hooks/use-contacts');
    vi.mocked(useContactSearch).mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    // Act
    renderWithProviders(<Leads />);

    // Assert - wait for data to be displayed
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('should open create dialog when button is clicked', async () => {
    // Arrange
    const user = userEvent.setup();

    const { useLeads } = await import('@/hooks/use-leads');
    vi.mocked(useLeads).mockReturnValue({
      data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 },
      isLoading: false,
      error: null,
    } as any);

    const { useUpdateLead, useCreateLead } = await import('@/hooks/use-leads');
    vi.mocked(useUpdateLead).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);
    vi.mocked(useCreateLead).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    const { useContactSearch } = await import('@/hooks/use-contacts');
    vi.mocked(useContactSearch).mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    renderWithProviders(<Leads />);

    // Wait for page to load
    await waitFor(() => {
      expect(screen.getAllByRole('button', { name: /Neuer Lead/i })).toHaveLength(2);
    });

    // Act - click first create button (in header)
    const buttons = screen.getAllByRole('button', { name: /Neuer Lead/i });
    await user.click(buttons[0]);

    // Assert - dialog should open
    await waitFor(() => {
      expect(screen.getByText(/Neuen Lead erstellen/i)).toBeInTheDocument();
    });
  });

  it('should show disabled submit button when no contact selected', async () => {
    // Arrange
    const user = userEvent.setup();

    const { useLeads } = await import('@/hooks/use-leads');
    vi.mocked(useLeads).mockReturnValue({
      data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 },
      isLoading: false,
      error: null,
    } as any);

    const { useUpdateLead, useCreateLead } = await import('@/hooks/use-leads');
    vi.mocked(useUpdateLead).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);
    vi.mocked(useCreateLead).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    const { useContactSearch } = await import('@/hooks/use-contacts');
    vi.mocked(useContactSearch).mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    renderWithProviders(<Leads />);

    await waitFor(() => {
      expect(screen.getAllByRole('button', { name: /Neuer Lead/i })).toHaveLength(2);
    });

    // Click first button (in header)
    const buttons = screen.getAllByRole('button', { name: /Neuer Lead/i });
    await user.click(buttons[0]);

    await waitFor(() => {
      expect(screen.getByText(/Neuen Lead erstellen/i)).toBeInTheDocument();
    });

    // Act - check submit button
    const submitButton = screen.getByRole('button', { name: /Lead erstellen/i });
    
    // Assert - button should be disabled without contact
    expect(submitButton).toBeDisabled();
  });

  it('should display loading state while fetching leads', async () => {
    // Arrange
    const { useLeads } = await import('@/hooks/use-leads');
    vi.mocked(useLeads).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as any);

    const { useUpdateLead, useCreateLead } = await import('@/hooks/use-leads');
    vi.mocked(useUpdateLead).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);
    vi.mocked(useCreateLead).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    const { useContactSearch } = await import('@/hooks/use-contacts');
    vi.mocked(useContactSearch).mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    // Act
    renderWithProviders(<Leads />);

    // Assert - should show loading spinner
    await waitFor(() => {
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });
  });

  it('should show empty state when no leads exist', async () => {
    // Arrange
    const { useLeads } = await import('@/hooks/use-leads');
    vi.mocked(useLeads).mockReturnValue({
      data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 },
      isLoading: false,
      error: null,
    } as any);

    const { useUpdateLead, useCreateLead } = await import('@/hooks/use-leads');
    vi.mocked(useUpdateLead).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);
    vi.mocked(useCreateLead).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    const { useContactSearch } = await import('@/hooks/use-contacts');
    vi.mocked(useContactSearch).mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    // Act
    renderWithProviders(<Leads />);

    // Assert - should show empty state message
    await waitFor(() => {
      expect(screen.getByText(/Keine Leads gefunden/i)).toBeInTheDocument();
    });
  });
});
