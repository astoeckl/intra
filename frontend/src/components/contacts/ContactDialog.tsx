/**
 * Contact Dialog Component Module
 *
 * Provides a modal dialog for creating and editing contact records.
 * Uses react-hook-form with Zod validation for form handling.
 *
 * @module components/contacts/ContactDialog
 */
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useCreateContact, useUpdateContact } from '@/hooks/use-contacts'
import type { ContactListItem } from '@/lib/types'
import { toast } from 'sonner'

/** Zod validation schema for contact form fields. */
const contactSchema = z.object({
  first_name: z.string().min(1, 'Vorname ist erforderlich'),
  last_name: z.string().min(1, 'Nachname ist erforderlich'),
  email: z.string().email('Ungültige E-Mail-Adresse').optional().or(z.literal('')),
  phone: z.string().optional(),
  mobile: z.string().optional(),
  position: z.string().optional(),
  department: z.string().optional(),
  salutation: z.string().optional(),
  title: z.string().optional(),
  company_id: z.number().optional().nullable(),
})

/** Form data type inferred from the contact validation schema. */
type ContactFormData = z.infer<typeof contactSchema>

/** Props for the ContactDialog component. */
interface ContactDialogProps {
  /** Whether the dialog is open. */
  open: boolean
  /** Callback to handle dialog open/close state changes. */
  onOpenChange: (open: boolean) => void
  /** Existing contact to edit, or null/undefined for creating a new contact. */
  contact?: ContactListItem | null
}

/**
 * Dialog component for creating or editing contacts.
 *
 * Supports both create and edit modes:
 * - When `contact` is provided, operates in edit mode with pre-filled fields
 * - When `contact` is null/undefined, operates in create mode
 *
 * Form fields include: salutation, title, name, email, phone, mobile, position, department.
 *
 * @param props - Component props
 * @param props.open - Whether the dialog is visible
 * @param props.onOpenChange - Callback when dialog visibility changes
 * @param props.contact - Optional contact to edit
 * @returns The contact dialog component
 */
export function ContactDialog({ open, onOpenChange, contact }: ContactDialogProps) {
  const createContact = useCreateContact()
  const updateContact = useUpdateContact()
  const isEditing = !!contact

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      mobile: '',
      position: '',
      department: '',
      salutation: '',
      title: '',
    },
  })

  useEffect(() => {
    if (contact) {
      reset({
        first_name: contact.first_name,
        last_name: contact.last_name,
        email: contact.email || '',
        phone: contact.phone || '',
        position: contact.position || '',
        company_id: contact.company_id,
      })
    } else {
      reset({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        mobile: '',
        position: '',
        department: '',
        salutation: '',
        title: '',
      })
    }
  }, [contact, reset])

  const onSubmit = async (data: ContactFormData) => {
    try {
      const submitData = {
        ...data,
        email: data.email || undefined,
      }

      if (isEditing && contact) {
        await updateContact.mutateAsync({ id: contact.id, data: submitData })
        toast.success('Kontakt wurde aktualisiert')
      } else {
        await createContact.mutateAsync(submitData)
        toast.success('Kontakt wurde erstellt')
      }
      onOpenChange(false)
    } catch {
      toast.error(isEditing ? 'Fehler beim Aktualisieren' : 'Fehler beim Erstellen')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? 'Kontakt bearbeiten' : 'Neuer Kontakt'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="salutation">Anrede</Label>
              <Input id="salutation" placeholder="Herr/Frau" {...register('salutation')} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="title">Titel</Label>
              <Input id="title" placeholder="Dr., Mag., ..." {...register('title')} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="first_name">Vorname *</Label>
              <Input
                id="first_name"
                {...register('first_name')}
                className={errors.first_name ? 'border-destructive' : ''}
              />
              {errors.first_name && (
                <p className="text-xs text-destructive">{errors.first_name.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="last_name">Nachname *</Label>
              <Input
                id="last_name"
                {...register('last_name')}
                className={errors.last_name ? 'border-destructive' : ''}
              />
              {errors.last_name && (
                <p className="text-xs text-destructive">{errors.last_name.message}</p>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">E-Mail</Label>
            <Input
              id="email"
              type="email"
              {...register('email')}
              className={errors.email ? 'border-destructive' : ''}
            />
            {errors.email && (
              <p className="text-xs text-destructive">{errors.email.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="phone">Telefon</Label>
              <Input id="phone" {...register('phone')} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="mobile">Mobil</Label>
              <Input id="mobile" {...register('mobile')} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="position">Position</Label>
              <Input id="position" {...register('position')} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="department">Abteilung</Label>
              <Input id="department" {...register('department')} />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Abbrechen
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Speichern...' : isEditing ? 'Aktualisieren' : 'Erstellen'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
