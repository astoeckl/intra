import { useState } from 'react'
import { Plus, Filter, Clock, AlertTriangle, CheckCircle2, PauseCircle, Pencil, Trash2 } from 'lucide-react'
import { useTasks, useUpdateTask, useCompleteTask, useDeleteTask } from '@/hooks/use-tasks'
import { TaskDialog } from '@/components/tasks/TaskDialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import type { TaskStatus, TaskPriority, TaskListItem } from '@/lib/types'
import { toast } from 'sonner'
import { format, isPast, isToday, isTomorrow } from 'date-fns'
import { de } from 'date-fns/locale'

const statusLabels: Record<TaskStatus, string> = {
  open: 'Offen',
  in_progress: 'In Bearbeitung',
  deferred: 'Verschoben',
  completed: 'Erledigt',
  cancelled: 'Abgebrochen',
}

const priorityLabels: Record<TaskPriority, string> = {
  low: 'Niedrig',
  medium: 'Mittel',
  high: 'Hoch',
  urgent: 'Dringend',
}

const priorityColors: Record<TaskPriority, string> = {
  low: 'bg-slate-100 text-slate-700',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  urgent: 'bg-red-100 text-red-700',
}

function getDueDateLabel(dueDate: string | undefined): { label: string; color: string } {
  if (!dueDate) return { label: 'Kein Datum', color: 'text-muted-foreground' }

  const date = new Date(dueDate)
  if (isToday(date)) return { label: 'Heute', color: 'text-orange-600 font-medium' }
  if (isTomorrow(date)) return { label: 'Morgen', color: 'text-blue-600' }
  if (isPast(date)) return { label: format(date, 'dd.MM.', { locale: de }), color: 'text-red-600 font-medium' }
  return { label: format(date, 'dd.MM.', { locale: de }), color: 'text-muted-foreground' }
}

export default function Tasks() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'all'>('all')
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | 'all'>('all')
  const [selectedTask, setSelectedTask] = useState<TaskListItem | null>(null)
  const [isTaskDialogOpen, setIsTaskDialogOpen] = useState(false)
  const [editingTask, setEditingTask] = useState<TaskListItem | null>(null)
  const [isCompleteDialogOpen, setIsCompleteDialogOpen] = useState(false)
  const [completionNotes, setCompletionNotes] = useState('')
  const [followUpTitle, setFollowUpTitle] = useState('')
  const [followUpDueDate, setFollowUpDueDate] = useState('')
  const [followUpPriority, setFollowUpPriority] = useState<TaskPriority>('medium')
  const [createFollowUp, setCreateFollowUp] = useState(false)
  const [deleteTaskId, setDeleteTaskId] = useState<number | null>(null)

  const { data, isLoading } = useTasks({
    page,
    page_size: 20,
    status: statusFilter === 'all' ? undefined : statusFilter,
    priority: priorityFilter === 'all' ? undefined : priorityFilter,
  })

  const updateTask = useUpdateTask()
  const completeTask = useCompleteTask()
  const deleteTask = useDeleteTask()

  const handleStatusChange = async (taskId: number, newStatus: TaskStatus) => {
    try {
      await updateTask.mutateAsync({ id: taskId, data: { status: newStatus } })
      toast.success('Status wurde aktualisiert')
    } catch {
      toast.error('Fehler beim Aktualisieren')
    }
  }

  const handleComplete = async () => {
    if (!selectedTask) return

    try {
      await completeTask.mutateAsync({
        id: selectedTask.id,
        data: {
          notes: completionNotes || undefined,
          create_follow_up: createFollowUp,
          follow_up_title: followUpTitle || undefined,
          follow_up_due_date: followUpDueDate ? `${followUpDueDate}T09:00:00` : undefined,
          follow_up_priority: createFollowUp ? followUpPriority : undefined,
        },
      })
      toast.success('Aufgabe wurde abgeschlossen')
      setIsCompleteDialogOpen(false)
      setSelectedTask(null)
      setCompletionNotes('')
      setFollowUpTitle('')
      setFollowUpDueDate('')
      setFollowUpPriority('medium')
      setCreateFollowUp(false)
    } catch {
      toast.error('Fehler beim Abschließen')
    }
  }

  const openCompleteDialog = (task: TaskListItem) => {
    setSelectedTask(task)
    setIsCompleteDialogOpen(true)
  }

  const openCreateDialog = () => {
    setEditingTask(null)
    setIsTaskDialogOpen(true)
  }

  const openEditDialog = (task: TaskListItem) => {
    setEditingTask(task)
    setIsTaskDialogOpen(true)
  }

  const handleDelete = async () => {
    if (!deleteTaskId) return
    try {
      await deleteTask.mutateAsync(deleteTaskId)
      toast.success('Aufgabe wurde gelöscht')
      setDeleteTaskId(null)
    } catch {
      toast.error('Fehler beim Löschen')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-display">Aufgaben</h1>
          <p className="text-muted-foreground">
            Verwalten Sie Ihre Aufgaben und Folgeaktivitäten
          </p>
        </div>
        <Button onClick={openCreateDialog}>
          <Plus className="mr-2 h-4 w-4" />
          Neue Aufgabe
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <Select
          value={statusFilter}
          onValueChange={(value) => {
            setStatusFilter(value as TaskStatus | 'all')
            setPage(1)
          }}
        >
          <SelectTrigger className="w-48">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Status filtern" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Status</SelectItem>
            <SelectItem value="open">Offen</SelectItem>
            <SelectItem value="in_progress">In Bearbeitung</SelectItem>
            <SelectItem value="deferred">Verschoben</SelectItem>
            <SelectItem value="completed">Erledigt</SelectItem>
            <SelectItem value="cancelled">Abgebrochen</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={priorityFilter}
          onValueChange={(value) => {
            setPriorityFilter(value as TaskPriority | 'all')
            setPage(1)
          }}
        >
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Priorität filtern" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Prioritäten</SelectItem>
            <SelectItem value="low">Niedrig</SelectItem>
            <SelectItem value="medium">Mittel</SelectItem>
            <SelectItem value="high">Hoch</SelectItem>
            <SelectItem value="urgent">Dringend</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Tasks List */}
      {isLoading ? (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="py-4">
                <div className="h-5 bg-muted rounded w-3/4" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : data?.items.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <CheckCircle2 className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-4">Keine Aufgaben gefunden</p>
            <Button onClick={openCreateDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Erste Aufgabe erstellen
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {data?.items.map((task) => {
            const dueInfo = getDueDateLabel(task.due_date)

            return (
              <Card
                key={task.id}
                className={`transition-all hover:shadow-md ${
                  task.status === 'completed' || task.status === 'deferred' ? 'opacity-60' : ''
                } ${task.is_overdue ? 'border-red-200' : ''} ${task.status === 'deferred' ? 'border-amber-200' : ''}`}
              >
                <CardContent className="flex items-center justify-between py-4">
                  <div className="flex items-center gap-4">
                    {task.status === 'completed' ? (
                      <CheckCircle2 className="h-5 w-5 text-accent" />
                    ) : task.status === 'deferred' ? (
                      <PauseCircle className="h-5 w-5 text-amber-500" />
                    ) : task.is_overdue ? (
                      <AlertTriangle className="h-5 w-5 text-destructive" />
                    ) : (
                      <Clock className="h-5 w-5 text-muted-foreground" />
                    )}
                    <div>
                      <p className={`font-medium ${task.status === 'completed' ? 'line-through' : ''}`}>
                        {task.title}
                      </p>
                      <div className="flex items-center gap-2 text-sm">
                        {task.contact_name && (
                          <span className="text-muted-foreground">{task.contact_name}</span>
                        )}
                        {task.assigned_to && (
                          <>
                            <span className="text-muted-foreground">•</span>
                            <span className="text-muted-foreground">{task.assigned_to}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className={priorityColors[task.priority] + ' px-2 py-0.5 rounded text-xs'}>
                      {priorityLabels[task.priority]}
                    </span>

                    <span className={`text-sm ${dueInfo.color}`}>
                      {dueInfo.label}
                    </span>

                    <Select
                      value={task.status}
                      onValueChange={(value) => handleStatusChange(task.id, value as TaskStatus)}
                    >
                      <SelectTrigger className="w-36">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="open">Offen</SelectItem>
                        <SelectItem value="in_progress">In Bearbeitung</SelectItem>
                        <SelectItem value="deferred">Verschoben</SelectItem>
                        <SelectItem value="completed">Erledigt</SelectItem>
                        <SelectItem value="cancelled">Abgebrochen</SelectItem>
                      </SelectContent>
                    </Select>

                    {task.status !== 'completed' && task.status !== 'cancelled' && task.status !== 'deferred' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openCompleteDialog(task)}
                      >
                        Erledigen
                      </Button>
                    )}

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEditDialog(task)}
                      title="Bearbeiten"
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteTaskId(task.id)}
                      title="Löschen"
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1}
            onClick={() => setPage(page - 1)}
          >
            Zurück
          </Button>
          <span className="text-sm text-muted-foreground">
            Seite {page} von {data.total_pages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page === data.total_pages}
            onClick={() => setPage(page + 1)}
          >
            Weiter
          </Button>
        </div>
      )}

      {/* Complete Task Dialog */}
      <Dialog open={isCompleteDialogOpen} onOpenChange={setIsCompleteDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Aufgabe abschließen</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {selectedTask && (
              <p className="text-sm font-medium">
                {selectedTask.title}
              </p>
            )}

            {/* Completion Notes */}
            <div className="space-y-2">
              <Label htmlFor="completionNotes">Abschlussnotiz</Label>
              <Textarea
                id="completionNotes"
                value={completionNotes}
                onChange={(e) => setCompletionNotes(e.target.value)}
                placeholder="Optionale Notizen zum Abschluss..."
                rows={3}
              />
            </div>

            {/* Follow-up Task */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="createFollowUp"
                checked={createFollowUp}
                onChange={(e) => setCreateFollowUp(e.target.checked)}
                className="rounded"
              />
              <Label htmlFor="createFollowUp">Folgeaufgabe erstellen</Label>
            </div>

            {createFollowUp && (
              <div className="space-y-4 rounded-lg border p-4">
                <div className="space-y-2">
                  <Label htmlFor="followUpTitle">Titel der Folgeaufgabe *</Label>
                  <Input
                    id="followUpTitle"
                    value={followUpTitle}
                    onChange={(e) => setFollowUpTitle(e.target.value)}
                    placeholder="z.B. Nachfassen bei..."
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="followUpDueDate">Fälligkeitsdatum</Label>
                    <Input
                      id="followUpDueDate"
                      type="date"
                      value={followUpDueDate}
                      onChange={(e) => setFollowUpDueDate(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Priorität</Label>
                    <Select
                      value={followUpPriority}
                      onValueChange={(value) => setFollowUpPriority(value as TaskPriority)}
                    >
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
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCompleteDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button
              onClick={handleComplete}
              disabled={createFollowUp && !followUpTitle}
            >
              Abschließen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Task Create/Edit Dialog */}
      <TaskDialog
        open={isTaskDialogOpen}
        onOpenChange={setIsTaskDialogOpen}
        task={editingTask}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteTaskId !== null} onOpenChange={() => setDeleteTaskId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Aufgabe löschen</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Sind Sie sicher, dass Sie diese Aufgabe löschen möchten?
            Diese Aktion kann nicht rückgängig gemacht werden.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTaskId(null)}>
              Abbrechen
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Löschen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
