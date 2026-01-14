import { useState } from 'react'
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
} from 'lucide-react'
import { useContactSearch, useContact } from '@/hooks/use-contacts'
import { useContactHistory, useAddNote, useAddCall } from '@/hooks/use-history'
import { useTasks, useCreateTask } from '@/hooks/use-tasks'
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
import type { ContactSearchResult, HistoryType } from '@/lib/types'
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

export default function Callcenter() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null)
  const [isNoteDialogOpen, setIsNoteDialogOpen] = useState(false)
  const [isCallDialogOpen, setIsCallDialogOpen] = useState(false)
  const [isTaskDialogOpen, setIsTaskDialogOpen] = useState(false)
  const [noteContent, setNoteContent] = useState('')
  const [callContent, setCallContent] = useState('')
  const [taskTitle, setTaskTitle] = useState('')

  const { data: searchResults } = useContactSearch(searchQuery)
  const { data: contact, isLoading: isContactLoading } = useContact(selectedContactId)
  const { data: history } = useContactHistory(selectedContactId)
  const { data: contactTasks } = useTasks({ contact_id: selectedContactId || undefined })

  const addNote = useAddNote()
  const addCall = useAddCall()
  const createTask = useCreateTask()

  const handleSelectContact = (result: ContactSearchResult) => {
    setSelectedContactId(result.id)
    setSearchQuery('')
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
        contact_id: selectedContactId,
      })
      toast.success('Aufgabe wurde erstellt')
      setIsTaskDialogOpen(false)
      setTaskTitle('')
    } catch {
      toast.error('Fehler beim Erstellen der Aufgabe')
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Left Column: Search */}
      <div className="w-80 flex-shrink-0 space-y-4">
        <Card className="h-full">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Kontaktsuche</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Name, E-Mail oder Firma..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {searchQuery.length >= 2 && searchResults && searchResults.length > 0 && (
              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {searchResults.map((result) => (
                    <div
                      key={result.id}
                      className="cursor-pointer rounded-md border p-3 transition-colors hover:bg-accent"
                      onClick={() => handleSelectContact(result)}
                    >
                      <p className="font-medium">{result.full_name}</p>
                      {result.company_name && (
                        <p className="text-sm text-muted-foreground">{result.company_name}</p>
                      )}
                      {result.email && (
                        <p className="text-sm text-muted-foreground">{result.email}</p>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            )}

            {/* Selected Contact Quick Info */}
            {contact && (
              <div className="rounded-lg bg-muted p-4 space-y-2">
                <p className="font-semibold">{contact.full_name}</p>
                {contact.company && (
                  <div className="flex items-center gap-2 text-sm">
                    <Building2 className="h-4 w-4" />
                    <span>{contact.company.name}</span>
                  </div>
                )}
                {contact.email && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-4 w-4" />
                    <span>{contact.email}</span>
                  </div>
                )}
                {contact.phone && (
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="h-4 w-4" />
                    <span>{contact.phone}</span>
                  </div>
                )}
              </div>
            )}
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
                        return (
                          <div key={item.id} className="flex gap-3">
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                              <Icon className="h-4 w-4" />
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center justify-between">
                                <p className="font-medium">{item.title}</p>
                                <span className="text-xs text-muted-foreground">
                                  {format(new Date(item.created_at), 'dd.MM.yy HH:mm', { locale: de })}
                                </span>
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
                <TabsContent value="details">
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
              disabled={!selectedContactId}
            >
              <Mail className="mr-2 h-4 w-4" />
              E-Mail senden
            </Button>
          </CardContent>
        </Card>

        {/* Tasks */}
        <Card className="flex-1">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Aufgaben</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-48">
              <div className="space-y-2">
                {contactTasks?.items.map((task) => (
                  <div key={task.id} className="rounded border p-2">
                    <p className="text-sm font-medium">{task.title}</p>
                    {task.due_date && (
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {format(new Date(task.due_date), 'dd.MM.yy', { locale: de })}
                      </div>
                    )}
                  </div>
                ))}
                {(!contactTasks || contactTasks.items.length === 0) && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    {selectedContactId ? 'Keine Aufgaben' : 'Kontakt auswählen'}
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
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Aufgabe erstellen</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Titel</Label>
              <Input
                placeholder="Aufgabentitel..."
                value={taskTitle}
                onChange={(e) => setTaskTitle(e.target.value)}
              />
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
    </div>
  )
}
