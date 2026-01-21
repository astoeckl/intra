import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ContactDialog } from '@/components/contacts/ContactDialog';
import * as useContacts from '@/hooks/use-contacts';
import { toast } from 'sonner';

// Mock the hooks
vi.mock('@/hooks/use-contacts', () => ({
  useCreateContact: vi.fn(),
  useUpdateContact: vi.fn(),
}));

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('ContactDialog', () => {
  const mockCreateContact = {
    mutateAsync: vi.fn(),
  };

  const mockUpdateContact = {
    mutateAsync: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useContacts.useCreateContact).mockReturnValue(mockCreateContact as any);
    vi.mocked(useContacts.useUpdateContact).mockReturnValue(mockUpdateContact as any);
  });

  it('should render create dialog with correct title', () => {
    // Arrange
    const onOpenChange = vi.fn();

    // Act
    render(<ContactDialog open={true} onOpenChange={onOpenChange} />);

    // Assert
    expect(screen.getByText('Neuer Kontakt')).toBeInTheDocument();
  });

  it('should render edit dialog when contact is provided', () => {
    // Arrange
    const onOpenChange = vi.fn();
    const contact = {
      id: 1,
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@test.com',
      phone: '+43 123456',
      position: 'Manager',
      company_id: 1,
      company_name: 'Test Corp',
      is_active: true,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    };

    // Act
    render(<ContactDialog open={true} onOpenChange={onOpenChange} contact={contact} />);

    // Assert
    expect(screen.getByText('Kontakt bearbeiten')).toBeInTheDocument();
  });

  it('should display all form fields', () => {
    // Arrange
    const onOpenChange = vi.fn();

    // Act
    render(<ContactDialog open={true} onOpenChange={onOpenChange} />);

    // Assert
    expect(screen.getByLabelText(/Vorname/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Nachname/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/E-Mail/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Telefon/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Mobil/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Position/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Abteilung/i)).toBeInTheDocument();
  });

  it('should show validation errors for required fields', async () => {
    // Arrange
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    render(<ContactDialog open={true} onOpenChange={onOpenChange} />);

    // Act - submit empty form
    const submitButton = screen.getByRole('button', { name: /Erstellen/i });
    await user.click(submitButton);

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/Vorname ist erforderlich/i)).toBeInTheDocument();
      expect(screen.getByText(/Nachname ist erforderlich/i)).toBeInTheDocument();
    });
  });

  it('should call createContact mutation when submitting new contact', async () => {
    // Arrange
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    mockCreateContact.mutateAsync.mockResolvedValue({});

    render(<ContactDialog open={true} onOpenChange={onOpenChange} />);

    // Act - fill form
    await user.type(screen.getByLabelText(/Vorname/i), 'Jane');
    await user.type(screen.getByLabelText(/Nachname/i), 'Smith');
    await user.type(screen.getByLabelText(/E-Mail/i), 'jane@test.com');

    const submitButton = screen.getByRole('button', { name: /Erstellen/i });
    await user.click(submitButton);

    // Assert
    await waitFor(() => {
      expect(mockCreateContact.mutateAsync).toHaveBeenCalledWith(
        expect.objectContaining({
          first_name: 'Jane',
          last_name: 'Smith',
          email: 'jane@test.com',
        })
      );
    });
  });

  it('should call updateContact mutation when editing existing contact', async () => {
    // Arrange
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    const contact = {
      id: 1,
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@test.com',
      phone: '',
      position: '',
      company_id: null,
      company_name: null,
      is_active: true,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    };
    mockUpdateContact.mutateAsync.mockResolvedValue({});

    render(<ContactDialog open={true} onOpenChange={onOpenChange} contact={contact} />);

    // Act - change first name
    const firstNameInput = screen.getByLabelText(/Vorname/i);
    await user.clear(firstNameInput);
    await user.type(firstNameInput, 'Jane');

    const submitButton = screen.getByRole('button', { name: /Aktualisieren/i });
    await user.click(submitButton);

    // Assert
    await waitFor(() => {
      expect(mockUpdateContact.mutateAsync).toHaveBeenCalledWith({
        id: 1,
        data: expect.objectContaining({
          first_name: 'Jane',
        }),
      });
    });
  });

  it('should show success toast after creating contact', async () => {
    // Arrange
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    mockCreateContact.mutateAsync.mockResolvedValue({});

    render(<ContactDialog open={true} onOpenChange={onOpenChange} />);

    // Act
    await user.type(screen.getByLabelText(/Vorname/i), 'Jane');
    await user.type(screen.getByLabelText(/Nachname/i), 'Smith');
    await user.click(screen.getByRole('button', { name: /Erstellen/i }));

    // Assert
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Kontakt wurde erstellt');
      expect(onOpenChange).toHaveBeenCalledWith(false);
    });
  });

  it('should show error toast when creation fails', async () => {
    // Arrange
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    mockCreateContact.mutateAsync.mockRejectedValue(new Error('API Error'));

    render(<ContactDialog open={true} onOpenChange={onOpenChange} />);

    // Act
    await user.type(screen.getByLabelText(/Vorname/i), 'Jane');
    await user.type(screen.getByLabelText(/Nachname/i), 'Smith');
    await user.click(screen.getByRole('button', { name: /Erstellen/i }));

    // Assert
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Fehler beim Erstellen');
    });
  });

  it('should close dialog when cancel button is clicked', async () => {
    // Arrange
    const user = userEvent.setup();
    const onOpenChange = vi.fn();

    render(<ContactDialog open={true} onOpenChange={onOpenChange} />);

    // Act
    const cancelButton = screen.getByRole('button', { name: /Abbrechen/i });
    await user.click(cancelButton);

    // Assert
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('should validate email format', async () => {
    // Arrange
    const user = userEvent.setup();
    const onOpenChange = vi.fn();

    render(<ContactDialog open={true} onOpenChange={onOpenChange} />);

    // Act - enter valid required fields and invalid email
    await user.type(screen.getByLabelText(/Vorname/i), 'Jane');
    await user.type(screen.getByLabelText(/Nachname/i), 'Smith');
    await user.type(screen.getByLabelText(/E-Mail/i), 'invalid-email');
    await user.click(screen.getByRole('button', { name: /Erstellen/i }));

    // Assert - mutation should not be called due to validation error
    await waitFor(() => {
      expect(mockCreateContact.mutateAsync).not.toHaveBeenCalled();
    }, { timeout: 1000 });
  });

  it('should populate form fields when editing contact', () => {
    // Arrange
    const onOpenChange = vi.fn();
    const contact = {
      id: 1,
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@test.com',
      phone: '+43 123456',
      position: 'Manager',
      company_id: 1,
      company_name: 'Test Corp',
      is_active: true,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    };

    // Act
    render(<ContactDialog open={true} onOpenChange={onOpenChange} contact={contact} />);

    // Assert
    expect(screen.getByLabelText(/Vorname/i)).toHaveValue('John');
    expect(screen.getByLabelText(/Nachname/i)).toHaveValue('Doe');
    expect(screen.getByLabelText(/E-Mail/i)).toHaveValue('john@test.com');
    expect(screen.getByLabelText(/Telefon/i)).toHaveValue('+43 123456');
    expect(screen.getByLabelText(/Position/i)).toHaveValue('Manager');
  });
});
