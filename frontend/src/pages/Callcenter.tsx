import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Search,
  Phone,
  Mail,
  MessageSquare,
  CheckSquare,
  Building2,
  User,
  Clock,
  Target,
  Globe,
  Users,
  Briefcase,
  ExternalLink,
  Loader2,
  Pencil,
  Trash2,
  Check,
  MoreHorizontal,
} from 'lucide-react'
import { useInfiniteContacts, useContact } from '@/hooks/use-contacts'
import { useContactHistory, useAddNote, useAddCall, useUpdateHistoryEntry, useDeleteHistoryEntry } from '@/hooks/use-history'
import { useTasks, useCreateTask, useCompleteTask } from '@/hooks/use-tasks'
import { useEmailTemplates, useEmailPreview, useSendEmail } from '@/hooks/use-email-templates'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { ContactListItem, ContactHistoryItem, HistoryType, LeadStatus, TaskPriority, TaskListItem } from '@/lib/types'
import { toast } from 'sonner'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'

const historyTypeLabels: Record<HistoryType, string> = {
  note: 'Notiz',
  call: 'Anruf',
  email: 'E-Mail',
  meeting: 'Meeting',
  status_change: 'Status',
  task_created: 'Aufgabe',
  data_change: 'Änderung',
  lead_created: 'Lead',
}

const historyTypeIcons: Record<HistoryType, React.ElementType> = {
  note: MessageSquare,
  call: Phone,
  email: Mail,
  meeting: User,
  status_change: Target,
  task_created: CheckSquare,
  data_change: User,
  lead_created: Target,
}

const leadStatusLabels: Record<LeadStatus, string> = {
  new: 'Neu',
  contacted: 'Kontaktiert',
  qualified: 'Qualifiziert',
  converted: 'Konvertiert',
  disqualified: 'Disqualifiziert',
}

const leadStatusColors: Record<LeadStatus, string> = {
  new: 'bg-blue-100 text-blue-800',
  contacted: 'bg-yellow-100 text-yellow-800',
  qualified: 'bg-green-100 text-green-800',
  converted: 'bg-emerald-100 text-emerald-800',
  disqualified: 'bg-red-100 text-red-800',
}

const potentialCategoryColors: Record<string, string> = {
  A: 'bg-emerald-500 text-white',
  B: 'bg-blue-500 text-white',
  C: 'bg-yellow-500 text-white',
  D: 'bg-gray-500 text-white',
}

const priorityLabels: Record<TaskPriority, string> = {
  low: 'Niedrig',
  medium: 'Mittel',
  high: 'Hoch',
  urgent: 'Dringend',
}

const priorityColors: Record<TaskPriority, string> = {
  low: 'bg-gray-100 text-gray-700',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  urgent: 'bg-red-100 text-red-700',
}

// Custom hook for debouncing
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

export default function Callcenter() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null)
  const [isNoteDialogOpen, setIsNoteDialogOpen] = useState(false)
  const [isCallDialogOpen, setIsCallDialogOpen] = useState(false)
  const [isTaskDialogOpen, setIsTaskDialogOpen] = useState(false)
  const [noteContent, setNoteContent] = useState('')
  const [callContent, setCallContent] = useState('')
  const [taskTitle, setTaskTitle] = useState('')
  const [taskDescription, setTaskDescription] = useState('')
  const [taskDueDate, setTaskDueDate] = useState('')
  const [taskPriority, setTaskPriority] = useState<TaskPriority>('medium')
  const [isEmailDialogOpen, setIsEmailDialogOpen] = useState(false)
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null)
  const [emailSubject, setEmailSubject] = useState('')
  const [emailBody, setEmailBody] = useState('')

  // History edit/delete state
  const [isEditHistoryDialogOpen, setIsEditHistoryDialogOpen] = useState(false)
  const [isDeleteHistoryDialogOpen, setIsDeleteHistoryDialogOpen] = useState(false)
  const [selectedHistoryEntry, setSelectedHistoryEntry] = useState<ContactHistoryItem | null>(null)
  const [editHistoryTitle, setEditHistoryTitle] = useState('')
  const [editHistoryContent, setEditHistoryContent] = useState('')

  // Task complete state
  const [isCompleteTaskDialogOpen, setIsCompleteTaskDialogOpen] = useState(false)
  const [selectedTask, setSelectedTask] = useState<TaskListItem | null>(null)
  const [completeTaskNotes, setCompleteTaskNotes] = useState('')
  const [createFollowUp, setCreateFollowUp] = useState(false)
  const [followUpTitle, setFollowUpTitle] = useState('')
  const [followUpDueDate, setFollowUpDueDate] = useState('')
  const [followUpPriority, setFollowUpPriority] = useState<TaskPriority>('medium')

  // Debounce search query for better performance
  const debouncedSearch = useDebounce(searchQuery, 300)

  // Infinite scroll for contacts
  const {
    data: contactsData,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading: isContactsLoading,
  } = useInfiniteContacts({
    search: debouncedSearch || undefined,
    page_size: 20,
  })

  const { data: contact, isLoading: isContactLoading } = useContact(selectedContactId)

  // Flatten pages into a single array
  const allContacts = contactsData?.pages.flatMap((page) => page.items) ?? []

  // Infinite scroll observer
  const loadMoreRef = useRef<HTMLDivElement>(null)
  
  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [target] = entries
      if (target.isIntersecting && hasNextPage && !isFetchingNextPage) {
        fetchNextPage()
      }
    },
    [fetchNextPage, hasNextPage, isFetchingNextPage]
  )

  useEffect(() => {
    const element = loadMoreRef.current
    if (!element) return

    const observer = new IntersectionObserver(handleObserver, {
      root: null,
      rootMargin: '100px',
      threshold: 0,
    })

    observer.observe(element)
    return () => observer.disconnect()
  }, [handleObserver])
  const { data: history } = useContactHistory(selectedContactId)
  const { data: contactTasks } = useTasks({ contact_id: selectedContactId || undefined })

  const addNote = useAddNote()
  const addCall = useAddCall()
  const createTask = useCreateTask()
  const updateHistoryEntry = useUpdateHistoryEntry()
  const deleteHistoryEntry = useDeleteHistoryEntry()
  const completeTask = useCompleteTask()
  const { data: emailTemplates } = useEmailTemplates({ is_active: true })
  const emailPreview = useEmailPreview()
  const sendEmail = useSendEmail()

  const handleSelectContact = (contactItem: ContactListItem) => {
    setSelectedContactId(contactItem.id)
  }

  const handleAddNote = async () => {
    if (!selectedContactId || !noteContent.trim()) return
    
    try {
      await addNote.mutateAsync({ contactId: selectedContactId, content: noteContent })
      toast.success('Notiz wurde hinzugefügt')
      setIsNoteDialogOpen(false)
      setNoteContent('')
    } catch {
      toast.error('Fehler beim Hinzufügen der Notiz')
    }
  }

  const handleAddCall = async () => {
    if (!selectedContactId || !callContent.trim()) return
    
    try {
      await addCall.mutateAsync({ contactId: selectedContactId, content: callContent })
      toast.success('Anruf wurde dokumentiert')
      setIsCallDialogOpen(false)
      setCallContent('')
    } catch {
      toast.error('Fehler beim Dokumentieren des Anrufs')
    }
  }

  const handleCreateTask = async () => {
    if (!selectedContactId || !taskTitle.trim()) return
    
    try {
      await createTask.mutateAsync({
        title: taskTitle,
        description: taskDescription || undefined,
        due_date: taskDueDate || undefined,
        priority: taskPriority,
        contact_id: selectedContactId,
      })
      toast.success('Aufgabe wurde erstellt')
      setIsTaskDialogOpen(false)
      setTaskTitle('')
      setTaskDescription('')
      setTaskDueDate('')
      setTaskPriority('medium')
    } catch {
      toast.error('Fehler beim Erstellen der Aufgabe')
    }
  }

  const handleSelectTemplate = async (templateId: string) => {
    const id = parseInt(templateId)
    setSelectedTemplateId(id)
    
    if (!selectedContactId) return
    
    try {
      const preview = await emailPreview.mutateAsync({
        template_id: id,
        contact_id: selectedContactId,
      })
      setEmailSubject(preview.subject)
      setEmailBody(preview.body)
    } catch {
      toast.error('Fehler beim Laden der Vorlage')
    }
  }

  const handleSendEmail = async () => {
    if (!selectedContactId || !contact?.email) {
      toast.error('Kontakt hat keine E-Mail-Adresse')
      return
    }
    
    // Use mailto: link as a simple solution
    const mailtoLink = `mailto:${contact.email}?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`
    window.open(mailtoLink, '_blank')
    
    // If a template was used, also log it to the backend
    if (selectedTemplateId) {
      try {
        await sendEmail.mutateAsync({
          template_id: selectedTemplateId,
          contact_id: selectedContactId,
          subject_override: emailSubject,
        })
      } catch {
        // Silent fail for logging - email was already sent via mailto
      }
    }
    
    toast.success('E-Mail-Client wurde geöffnet')
    setIsEmailDialogOpen(false)
    setSelectedTemplateId(null)
    setEmailSubject('')
    setEmailBody('')
  }

  const handleOpenEmailDialog = () => {
    setSelectedTemplateId(null)
    setEmailSubject('')
    setEmailBody('')
    setIsEmailDialogOpen(true)
  }

  // History entry edit/delete handlers
  const handleOpenEditHistoryDialog = (entry: ContactHistoryItem) => {
    setSelectedHistoryEntry(entry)
    setEditHistoryTitle(entry.title)
    setEditHistoryContent(entry.content || '')
    setIsEditHistoryDialogOpen(true)
  }

  const handleOpenDeleteHistoryDialog = (entry: ContactHistoryItem) => {
    setSelectedHistoryEntry(entry)
    setIsDeleteHistoryDialogOpen(true)
  }

  const handleUpdateHistoryEntry = async () => {
    if (!selectedHistoryEntry || !selectedContactId || !editHistoryTitle.trim()) return

    try {
      await updateHistoryEntry.mutateAsync({
        historyId: selectedHistoryEntry.id,
        contactId: selectedContactId,
        data: {
          title: editHistoryTitle,
          content: editHistoryContent || null,
        },
      })
      toast.success('Eintrag wurde aktualisiert')
      setIsEditHistoryDialogOpen(false)
      setSelectedHistoryEntry(null)
    } catch {
      toast.error('Fehler beim Aktualisieren des Eintrags')
    }
  }

  const handleDeleteHistoryEntry = async () => {
    if (!selectedHistoryEntry || !selectedContactId) return

    try {
      await deleteHistoryEntry.mutateAsync({
        historyId: selectedHistoryEntry.id,
        contactId: selectedContactId,
      })
      toast.success('Eintrag wurde gelöscht')
      setIsDeleteHistoryDialogOpen(false)
      setSelectedHistoryEntry(null)
    } catch {
      toast.error('Fehler beim Löschen des Eintrags')
    }
  }

  // Task complete handlers
  const handleOpenCompleteTaskDialog = (task: TaskListItem) => {
    setSelectedTask(task)
    setCompleteTaskNotes('')
    setCreateFollowUp(false)
    setFollowUpTitle('')
    setFollowUpDueDate('')
    setFollowUpPriority('medium')
    setIsCompleteTaskDialogOpen(true)
  }

  const handleCompleteTask = async () => {
    if (!selectedTask) return

    try {
      await completeTask.mutateAsync({
        id: selectedTask.id,
        data: {
          notes: completeTaskNotes || undefined,
          create_follow_up: createFollowUp,
          follow_up_title: createFollowUp ? followUpTitle : undefined,
          follow_up_due_date: createFollowUp && followUpDueDate ? followUpDueDate : undefined,
          follow_up_priority: createFollowUp ? followUpPriority : undefined,
        },
      })
      toast.success('Aufgabe wurde abgeschlossen')
      setIsCompleteTaskDialogOpen(false)
      setSelectedTask(null)
    } catch {
      toast.error('Fehler beim Abschließen der Aufgabe')
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Left Column: Contact List with Search Filter */}
      <div className="w-80 flex-shrink-0 flex flex-col h-full">
        <Card className="flex-1 flex flex-col overflow-hidden">
          <CardHeader className="pb-3 flex-shrink-0">
            <CardTitle className="text-lg">Kontakte</CardTitle>
            <div className="relative mt-2">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Kontakte filtern..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </CardHeader>
          <CardContent className="flex-1 overflow-hidden p-0">
            <ScrollArea className="h-full">
              <div className="space-y-1 p-4 pt-0">
                {isContactsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                  </div>
                ) : allContacts.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    {debouncedSearch ? 'Keine Kontakte gefunden' : 'Keine Kontakte vorhanden'}
                  </p>
                ) : (
                  <>
                    {allContacts.map((contactItem) => (
                      <div
                        key={contactItem.id}
                        className={`cursor-pointer rounded-md border p-3 transition-colors hover:bg-accent ${
                          selectedContactId === contactItem.id ? 'bg-accent border-primary' : ''
                        }`}
                        onClick={() => handleSelectContact(contactItem)}
                      >
                        <p className="font-medium">
                          {contactItem.first_name} {contactItem.last_name}
                        </p>
                        {contactItem.company_name && (
                          <p className="text-sm text-muted-foreground">{contactItem.company_name}</p>
                        )}
                        {contactItem.email && (
                          <p className="text-sm text-muted-foreground truncate">{contactItem.email}</p>
                        )}
                      </div>
                    ))}
                    {/* Infinite scroll trigger */}
                    <div ref={loadMoreRef} className="py-2">
                      {isFetchingNextPage && (
                        <div className="flex items-center justify-center">
                          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Center Column: Contact Details & Timeline */}
      <div className="flex-1 space-y-4">
        {!selectedContactId ? (
          <Card className="flex h-full items-center justify-center border-dashed">
            <div className="text-center">
              <Search className="mx-auto h-12 w-12 text-muted-foreground" />
              <p className="mt-4 text-muted-foreground">
                Wählen Sie einen Kontakt aus der Suche
              </p>
            </div>
          </Card>
        ) : isContactLoading ? (
          <Card className="flex h-full items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </Card>
        ) : contact ? (
          <Card className="h-full flex flex-col">
            <CardHeader className="flex-shrink-0">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{contact.full_name}</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {contact.position}
                    {contact.company && ` bei ${contact.company.name}`}
                  </p>
                </div>
                <Badge variant={contact.is_active ? 'success' : 'secondary'}>
                  {contact.is_active ? 'Aktiv' : 'Inaktiv'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <Tabs defaultValue="timeline" className="h-full flex flex-col">
                <TabsList>
                  <TabsTrigger value="timeline">Timeline</TabsTrigger>
                  <TabsTrigger value="details">Details</TabsTrigger>
                </TabsList>
                <TabsContent value="timeline" className="flex-1 overflow-hidden">
                  <ScrollArea className="h-[calc(100%-2rem)]">
                    <div className="space-y-4 pr-4">
                      {history?.items.map((item) => {
                        const Icon = historyTypeIcons[item.type]
                        const isEditable = item.type === 'note' || item.type === 'call'
                        return (
                          <div key={item.id} className="flex gap-3 group">
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                              <Icon className="h-4 w-4" />
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center justify-between gap-2">
                                <p className="font-medium">{item.title}</p>
                                <div className="flex items-center gap-1">
                                  {isEditable && (
                                    <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                                      <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-6 w-6"
                                        onClick={() => handleOpenEditHistoryDialog(item)}
                                      >
                                        <Pencil className="h-3 w-3" />
                                      </Button>
                                      <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-6 w-6 text-destructive hover:text-destructive"
                                        onClick={() => handleOpenDeleteHistoryDialog(item)}
                                      >
                                        <Trash2 className="h-3 w-3" />
                                      </Button>
                                    </div>
                                  )}
                                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                                    {format(new Date(item.created_at), 'dd.MM.yy HH:mm', { locale: de })}
                                  </span>
                                </div>
                              </div>
                              {item.content && (
                                <p className="mt-1 text-sm text-muted-foreground">{item.content}</p>
                              )}
                              {item.created_by && (
                                <p className="mt-1 text-xs text-muted-foreground">
                                  von {item.created_by}
                                </p>
                              )}
                            </div>
                          </div>
                        )
                      })}
                      {(!history || history.items.length === 0) && (
                        <p className="text-sm text-muted-foreground text-center py-8">
                          Noch keine Einträge vorhanden
                        </p>
                      )}
                    </div>
                  </ScrollArea>
                </TabsContent>
                <TabsContent value="details" className="flex-1 overflow-hidden">
                  <ScrollArea className="h-[calc(100%-2rem)]">
                    <div className="space-y-6 pr-4">
                      {/* Contact Details */}
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-muted-foreground">E-Mail</Label>
                          <p>{contact.email || '-'}</p>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">Telefon</Label>
                          <p>{contact.phone || '-'}</p>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">Mobil</Label>
                          <p>{contact.mobile || '-'}</p>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">Abteilung</Label>
                          <p>{contact.department || '-'}</p>
                        </div>
                      </div>

                      {/* Lead Status */}
                      {contact.leads && contact.leads.length > 0 && (
                        <div className="space-y-2">
                          <Label className="text-muted-foreground">Lead Status</Label>
                          <div className="flex flex-wrap gap-2">
                            {contact.leads.map((lead) => (
                              <span
                                key={lead.id}
                                className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${leadStatusColors[lead.status]}`}
                              >
                                {leadStatusLabels[lead.status]}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Company Details */}
                      {contact.company && (
                        <div className="rounded-lg border p-4 space-y-3">
                          <div className="flex items-center justify-between">
                            <h4 className="font-semibold">Firmendaten</h4>
                            {contact.company.potential_category && (
                              <span
                                className={`inline-flex items-center justify-center h-7 w-7 rounded-full text-sm font-bold ${potentialCategoryColors[contact.company.potential_category]}`}
                              >
                                {contact.company.potential_category}
                              </span>
                            )}
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="flex items-center gap-2 text-sm">
                              <Building2 className="h-4 w-4 text-muted-foreground" />
                              <span>{contact.company.name}</span>
                            </div>
                            {contact.company.industry && (
                              <div className="flex items-center gap-2 text-sm">
                                <Briefcase className="h-4 w-4 text-muted-foreground" />
                                <span>{contact.company.industry}</span>
                              </div>
                            )}
                            {contact.company.website && (
                              <div className="flex items-center gap-2 text-sm">
                                <Globe className="h-4 w-4 text-muted-foreground" />
                                <a
                                  href={contact.company.website.startsWith('http') ? contact.company.website : `https://${contact.company.website}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary hover:underline flex items-center gap-1"
                                >
                                  {contact.company.website}
                                  <ExternalLink className="h-3 w-3" />
                                </a>
                              </div>
                            )}
                            {contact.company.employee_count && (
                              <div className="flex items-center gap-2 text-sm">
                                <Users className="h-4 w-4 text-muted-foreground" />
                                <span>{contact.company.employee_count} Mitarbeiter</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </ScrollArea>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        ) : null}
      </div>

      {/* Right Column: Actions & Tasks */}
      <div className="w-80 flex-shrink-0 space-y-4">
        {/* Quick Actions */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button
              variant="outline"
              className="w-full justify-start"
              disabled={!selectedContactId}
              onClick={() => setIsNoteDialogOpen(true)}
            >
              <MessageSquare className="mr-2 h-4 w-4" />
              Notiz hinzufügen
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              disabled={!selectedContactId}
              onClick={() => setIsCallDialogOpen(true)}
            >
              <Phone className="mr-2 h-4 w-4" />
              Anruf dokumentieren
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              disabled={!selectedContactId}
              onClick={() => setIsTaskDialogOpen(true)}
            >
              <CheckSquare className="mr-2 h-4 w-4" />
              Aufgabe erstellen
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              disabled={!selectedContactId || !contact?.email}
              onClick={handleOpenEmailDialog}
            >
              <Mail className="mr-2 h-4 w-4" />
              E-Mail senden
            </Button>
          </CardContent>
        </Card>

        {/* Tasks - Only show open tasks */}
        <Card className="flex-1">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Offene Aufgaben</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              <div className="space-y-3">
                {contactTasks?.items
                  .filter((task) => task.status === 'open' || task.status === 'in_progress')
                  .map((task) => {
                    const isOverdue = task.is_overdue
                    return (
                      <div
                        key={task.id}
                        className={`rounded-lg border p-3 space-y-2 ${
                          isOverdue ? 'border-red-300 bg-red-50' : ''
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-sm font-medium leading-tight flex-1">{task.title}</p>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              className="h-7 px-2 text-green-600 hover:text-green-700 hover:bg-green-50 border-green-200"
                              onClick={() => handleOpenCompleteTaskDialog(task)}
                              title="Als erledigt markieren"
                            >
                              <Check className="h-4 w-4" />
                            </Button>
                            <span
                              className={`inline-flex shrink-0 items-center rounded-full px-2 py-0.5 text-xs font-medium ${priorityColors[task.priority]}`}
                            >
                              {priorityLabels[task.priority]}
                            </span>
                          </div>
                        </div>
                        {task.due_date && (
                          <div
                            className={`flex items-center gap-1 text-xs ${
                              isOverdue ? 'text-red-600 font-medium' : 'text-muted-foreground'
                            }`}
                          >
                            <Clock className="h-3 w-3" />
                            {format(new Date(task.due_date), 'dd.MM.yy', { locale: de })}
                            {isOverdue && ' (überfällig)'}
                          </div>
                        )}
                      </div>
                    )
                  })}
                {(!contactTasks ||
                  contactTasks.items.filter(
                    (task) => task.status === 'open' || task.status === 'in_progress'
                  ).length === 0) && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    {selectedContactId ? 'Keine offenen Aufgaben' : 'Kontakt auswählen'}
                  </p>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Note Dialog */}
      <Dialog open={isNoteDialogOpen} onOpenChange={setIsNoteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Notiz hinzufügen</DialogTitle>
          </DialogHeader>
          <Textarea
            placeholder="Notiz eingeben..."
            value={noteContent}
            onChange={(e) => setNoteContent(e.target.value)}
            className="min-h-32"
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsNoteDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button onClick={handleAddNote} disabled={!noteContent.trim()}>
              Speichern
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Call Dialog */}
      <Dialog open={isCallDialogOpen} onOpenChange={setIsCallDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Anruf dokumentieren</DialogTitle>
          </DialogHeader>
          <Textarea
            placeholder="Gesprächsnotizen..."
            value={callContent}
            onChange={(e) => setCallContent(e.target.value)}
            className="min-h-32"
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCallDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button onClick={handleAddCall} disabled={!callContent.trim()}>
              Speichern
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Task Dialog */}
      <Dialog open={isTaskDialogOpen} onOpenChange={setIsTaskDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Aufgabe erstellen</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Titel *</Label>
              <Input
                placeholder="Aufgabentitel..."
                value={taskTitle}
                onChange={(e) => setTaskTitle(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Beschreibung</Label>
              <Textarea
                placeholder="Beschreibung der Aufgabe..."
                value={taskDescription}
                onChange={(e) => setTaskDescription(e.target.value)}
                className="min-h-20"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Fälligkeitsdatum</Label>
                <Input
                  type="date"
                  value={taskDueDate}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={(e) => setTaskDueDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Priorität</Label>
                <Select value={taskPriority} onValueChange={(v) => setTaskPriority(v as TaskPriority)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Niedrig</SelectItem>
                    <SelectItem value="medium">Mittel</SelectItem>
                    <SelectItem value="high">Hoch</SelectItem>
                    <SelectItem value="urgent">Dringend</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsTaskDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button onClick={handleCreateTask} disabled={!taskTitle.trim()}>
              Erstellen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Email Dialog */}
      <Dialog open={isEmailDialogOpen} onOpenChange={setIsEmailDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>E-Mail senden</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>An</Label>
              <Input
                value={contact?.email || ''}
                disabled
                className="bg-muted"
              />
            </div>
            <div className="space-y-2">
              <Label>Vorlage auswählen</Label>
              <Select
                value={selectedTemplateId?.toString() || ''}
                onValueChange={handleSelectTemplate}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Vorlage wählen (optional)" />
                </SelectTrigger>
                <SelectContent>
                  {emailTemplates?.items.map((template) => (
                    <SelectItem key={template.id} value={template.id.toString()}>
                      {template.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Betreff</Label>
              <Input
                placeholder="E-Mail-Betreff..."
                value={emailSubject}
                onChange={(e) => setEmailSubject(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Nachricht</Label>
              <Textarea
                placeholder="E-Mail-Text..."
                value={emailBody}
                onChange={(e) => setEmailBody(e.target.value)}
                className="min-h-40"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEmailDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button
              onClick={handleSendEmail}
              disabled={!emailSubject.trim() || !emailBody.trim()}
            >
              <Mail className="mr-2 h-4 w-4" />
              E-Mail öffnen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit History Entry Dialog */}
      <Dialog open={isEditHistoryDialogOpen} onOpenChange={setIsEditHistoryDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Eintrag bearbeiten</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Titel</Label>
              <Input
                placeholder="Titel..."
                value={editHistoryTitle}
                onChange={(e) => setEditHistoryTitle(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Inhalt</Label>
              <Textarea
                placeholder="Inhalt..."
                value={editHistoryContent}
                onChange={(e) => setEditHistoryContent(e.target.value)}
                className="min-h-32"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditHistoryDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button 
              onClick={handleUpdateHistoryEntry} 
              disabled={!editHistoryTitle.trim() || updateHistoryEntry.isPending}
            >
              Speichern
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete History Entry Dialog */}
      <Dialog open={isDeleteHistoryDialogOpen} onOpenChange={setIsDeleteHistoryDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Eintrag löschen</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Möchten Sie diesen Eintrag wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.
          </p>
          {selectedHistoryEntry && (
            <div className="rounded-lg border p-3 bg-muted/50">
              <p className="font-medium">{selectedHistoryEntry.title}</p>
              {selectedHistoryEntry.content && (
                <p className="mt-1 text-sm text-muted-foreground">{selectedHistoryEntry.content}</p>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteHistoryDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button 
              variant="destructive" 
              onClick={handleDeleteHistoryEntry}
              disabled={deleteHistoryEntry.isPending}
            >
              Löschen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Complete Task Dialog */}
      <Dialog open={isCompleteTaskDialogOpen} onOpenChange={setIsCompleteTaskDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Aufgabe abschließen</DialogTitle>
          </DialogHeader>
          {selectedTask && (
            <div className="space-y-4">
              <div className="rounded-lg border p-3 bg-muted/50">
                <p className="font-medium">{selectedTask.title}</p>
                {selectedTask.due_date && (
                  <p className="mt-1 text-sm text-muted-foreground">
                    Fällig: {format(new Date(selectedTask.due_date), 'dd.MM.yyyy', { locale: de })}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label>Abschlussnotizen (optional)</Label>
                <Textarea
                  placeholder="Notizen zum Abschluss..."
                  value={completeTaskNotes}
                  onChange={(e) => setCompleteTaskNotes(e.target.value)}
                  className="min-h-20"
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="create-follow-up"
                  checked={createFollowUp}
                  onChange={(e) => setCreateFollowUp(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <Label htmlFor="create-follow-up" className="cursor-pointer">
                  Folgeaufgabe erstellen
                </Label>
              </div>
              {createFollowUp && (
                <div className="space-y-4 pl-6 border-l-2 border-muted">
                  <div className="space-y-2">
                    <Label>Titel der Folgeaufgabe *</Label>
                    <Input
                      placeholder="Titel..."
                      value={followUpTitle}
                      onChange={(e) => setFollowUpTitle(e.target.value)}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Fälligkeitsdatum</Label>
                      <Input
                        type="date"
                        value={followUpDueDate}
                        min={new Date().toISOString().split('T')[0]}
                        onChange={(e) => setFollowUpDueDate(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Priorität</Label>
                      <Select value={followUpPriority} onValueChange={(v) => setFollowUpPriority(v as TaskPriority)}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Niedrig</SelectItem>
                          <SelectItem value="medium">Mittel</SelectItem>
                          <SelectItem value="high">Hoch</SelectItem>
                          <SelectItem value="urgent">Dringend</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCompleteTaskDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button 
              onClick={handleCompleteTask}
              disabled={completeTask.isPending || (createFollowUp && !followUpTitle.trim())}
            >
              <Check className="mr-2 h-4 w-4" />
              Abschließen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
