import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Search, X } from 'lucide-react'
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
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useCreateTask, useUpdateTask } from '@/hooks/use-tasks'
import { useContactSearch } from '@/hooks/use-contacts'
import type { TaskListItem, TaskPriority, ContactSearchResult } from '@/lib/types'
import { toast } from 'sonner'

const taskSchema = z.object({
  title: z.string().min(1, 'Titel ist erforderlich'),
  description: z.string().optional(),
  due_date: z.string().optional(),
  due_time: z.string().optional(),
  priority: z.enum(['low', 'medium', 'high', 'urgent']),
  assigned_to: z.string().optional(),
  contact_id: z.number().optional().nullable(),
})

type TaskFormData = z.infer<typeof taskSchema>

interface TaskDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  task?: TaskListItem | null
}

export function TaskDialog({ open, onOpenChange, task }: TaskDialogProps) {
  const createTask = useCreateTask()
  const updateTask = useUpdateTask()
  const isEditing = !!task

  // Contact search state
  const [contactQuery, setContactQuery] = useState('')
  const [selectedContact, setSelectedContact] = useState<ContactSearchResult | null>(null)
  const [showContactResults, setShowContactResults] = useState(false)
  const { data: contactResults = [] } = useContactSearch(contactQuery)

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: '',
      description: '',
      due_date: '',
      due_time: '',
      priority: 'medium',
      assigned_to: '',
      contact_id: null,
    },
  })

  const priority = watch('priority')

  useEffect(() => {
    if (task) {
      // Parse due_date into date and time if present
      let dateStr = ''
      let timeStr = ''
      if (task.due_date) {
        const date = new Date(task.due_date)
        dateStr = date.toISOString().split('T')[0]
        timeStr = date.toTimeString().slice(0, 5)
      }

      reset({
        title: task.title,
        description: '',
        due_date: dateStr,
        due_time: timeStr,
        priority: task.priority,
        assigned_to: task.assigned_to || '',
        contact_id: null,
      })

      // Set contact info if available
      if (task.contact_name) {
        setContactQuery(task.contact_name)
      } else {
        setContactQuery('')
        setSelectedContact(null)
      }
    } else {
      reset({
        title: '',
        description: '',
        due_date: '',
        due_time: '',
        priority: 'medium',
        assigned_to: '',
        contact_id: null,
      })
      setContactQuery('')
      setSelectedContact(null)
    }
  }, [task, reset])

  const handleContactSelect = (contact: ContactSearchResult) => {
    setSelectedContact(contact)
    setContactQuery(`${contact.first_name} ${contact.last_name}`)
    setValue('contact_id', contact.id)
    setShowContactResults(false)
  }

  const clearContact = () => {
    setSelectedContact(null)
    setContactQuery('')
    setValue('contact_id', null)
  }

  const onSubmit = async (data: TaskFormData) => {
    try {
      // Combine date and time
      let dueDatetime: string | undefined
      if (data.due_date) {
        const dateStr = data.due_date
        const timeStr = data.due_time || '09:00'
        dueDatetime = `${dateStr}T${timeStr}:00`
      }

      const submitData = {
        title: data.title,
        description: data.description || undefined,
        due_date: dueDatetime,
        priority: data.priority as TaskPriority,
        assigned_to: data.assigned_to || undefined,
        contact_id: data.contact_id || undefined,
      }

      if (isEditing && task) {
        await updateTask.mutateAsync({ id: task.id, data: submitData })
        toast.success('Aufgabe wurde aktualisiert')
      } else {
        await createTask.mutateAsync(submitData)
        toast.success('Aufgabe wurde erstellt')
      }
      onOpenChange(false)
    } catch {
      toast.error(isEditing ? 'Fehler beim Aktualisieren' : 'Fehler beim Erstellen')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] max-h-[85vh] overflow-hidden p-0">
        <div className="flex flex-col max-h-[85vh]">
          <DialogHeader className="flex-shrink-0 p-6 pb-0">
            <DialogTitle>
              {isEditing ? 'Aufgabe bearbeiten' : 'Neue Aufgabe'}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col flex-1 min-h-0 overflow-hidden">
            {/* Scrollable form content */}
            <div className="flex-1 overflow-y-auto space-y-4 px-6 py-4">
            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title">Titel *</Label>
              <Input
                id="title"
                placeholder="Aufgabentitel eingeben..."
                {...register('title')}
                className={errors.title ? 'border-destructive' : ''}
              />
              {errors.title && (
                <p className="text-xs text-destructive">{errors.title.message}</p>
              )}
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Beschreibung</Label>
              <Textarea
                id="description"
                placeholder="Optionale Beschreibung..."
                rows={3}
                {...register('description')}
              />
            </div>

            {/* Due Date and Time */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="due_date">Fälligkeitsdatum</Label>
                <Input
                  id="due_date"
                  type="date"
                  {...register('due_date')}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="due_time">Uhrzeit</Label>
                <Input
                  id="due_time"
                  type="time"
                  {...register('due_time')}
                />
              </div>
            </div>

            {/* Priority */}
            <div className="space-y-2">
              <Label>Priorität</Label>
              <Select
                value={priority}
                onValueChange={(value) => setValue('priority', value as TaskPriority)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Priorität wählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Niedrig</SelectItem>
                  <SelectItem value="medium">Mittel</SelectItem>
                  <SelectItem value="high">Hoch</SelectItem>
                  <SelectItem value="urgent">Dringend</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Assigned To */}
            <div className="space-y-2">
              <Label htmlFor="assigned_to">Zugewiesen an</Label>
              <Input
                id="assigned_to"
                placeholder="Mitarbeiter..."
                {...register('assigned_to')}
              />
            </div>

            {/* Contact Search */}
            <div className="space-y-2">
              <Label>Kontakt verknüpfen</Label>
              <div className="relative">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Kontakt suchen..."
                    value={contactQuery}
                    onChange={(e) => {
                      setContactQuery(e.target.value)
                      setShowContactResults(true)
                      if (!e.target.value) {
                        setSelectedContact(null)
                        setValue('contact_id', null)
                      }
                    }}
                    onFocus={() => setShowContactResults(true)}
                    className="pl-9 pr-9"
                  />
                  {selectedContact && (
                    <button
                      type="button"
                      onClick={clearContact}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>

                {/* Search Results Dropdown */}
                {showContactResults && contactResults.length > 0 && !selectedContact && (
                  <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-md">
                    <ul className="max-h-48 overflow-auto py-1">
                      {contactResults.map((contact) => (
                        <li
                          key={contact.id}
                          className="cursor-pointer px-3 py-2 text-sm hover:bg-accent"
                          onClick={() => handleContactSelect(contact)}
                        >
                          <div className="font-medium">
                            {contact.first_name} {contact.last_name}
                          </div>
                          {contact.company_name && (
                            <div className="text-xs text-muted-foreground">
                              {contact.company_name}
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              {selectedContact && (
                <p className="text-xs text-muted-foreground">
                  Verknüpft mit: {selectedContact.first_name} {selectedContact.last_name}
                  {selectedContact.company_name && ` (${selectedContact.company_name})`}
                </p>
              )}
            </div>
          </div>

            {/* Fixed footer */}
            <DialogFooter className="flex-shrink-0 p-6 pt-4 border-t">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Abbrechen
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Speichern...' : isEditing ? 'Aktualisieren' : 'Erstellen'}
              </Button>
            </DialogFooter>
          </form>
        </div>
      </DialogContent>
    </Dialog>
  )
}
