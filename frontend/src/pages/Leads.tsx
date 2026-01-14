import { useState } from 'react'
import { Plus, Search, Filter, Loader2, Phone, Mail, TrendingUp, MoreHorizontal } from 'lucide-react'
import { useLeads, useUpdateLead, useCreateLead } from '@/hooks/use-leads'
import { useContactSearch } from '@/hooks/use-contacts'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import type { LeadStatus, LeadListItem, ContactSearchResult } from '@/lib/types'
import { toast } from 'sonner'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'
import { ConvertToOpportunityDialog } from '@/components/leads/ConvertToOpportunityDialog'

const statusLabels: Record<LeadStatus, string> = {
  cold: 'Cold',
  warm: 'Warm',
  hot: 'Hot',
  to_be_done: 'To Be Done',
  converted: 'Converted',
  disqualified: 'Disqualified',
}

type BadgeVariant = 'default' | 'secondary' | 'outline' | 'destructive';

const statusColors: Record<LeadStatus, BadgeVariant> = {
  cold: 'secondary',
  warm: 'outline',
  hot: 'default',
  to_be_done: 'default',
  converted: 'default',
  disqualified: 'destructive',
}

export default function Leads() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<LeadStatus | 'all'>('all')
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [selectedLead, setSelectedLead] = useState<LeadListItem | null>(null)
  const [convertLead, setConvertLead] = useState<LeadListItem | null>(null)
  
  // State für Lead-Erstellung
  const [contactSearch, setContactSearch] = useState('')
  const [selectedContact, setSelectedContact] = useState<ContactSearchResult | null>(null)
  const [newLeadStatus, setNewLeadStatus] = useState<LeadStatus>('cold')
  const [newLeadSource, setNewLeadSource] = useState('')
  const [newLeadNotes, setNewLeadNotes] = useState('')
  const [showContactResults, setShowContactResults] = useState(false)

  const { data, isLoading } = useLeads({
    page,
    page_size: 20,
    status: statusFilter === 'all' ? undefined : statusFilter,
  })

  const updateLead = useUpdateLead()
  const createLead = useCreateLead()
  const { data: contactResults, isLoading: isSearching } = useContactSearch(contactSearch)

  const handleStatusChange = async (leadId: number, newStatus: LeadStatus) => {
    try {
      await updateLead.mutateAsync({ id: leadId, data: { status: newStatus } })
      toast.success('Status wurde aktualisiert')
    } catch {
      toast.error('Fehler beim Aktualisieren des Status')
    }
  }

  const handleSelectContact = (contact: ContactSearchResult) => {
    setSelectedContact(contact)
    setContactSearch('')
    setShowContactResults(false)
  }

  const handleCreateLead = async () => {
    if (!selectedContact) {
      toast.error('Bitte wählen Sie einen Kontakt aus')
      return
    }

    try {
      await createLead.mutateAsync({
        contact_id: selectedContact.id,
        status: newLeadStatus,
        source: newLeadSource || 'manual',
        notes: newLeadNotes || undefined,
      })
      toast.success('Lead wurde erstellt')
      setIsCreateOpen(false)
      resetCreateForm()
    } catch {
      toast.error('Fehler beim Erstellen des Leads')
    }
  }

  const resetCreateForm = () => {
    setSelectedContact(null)
    setContactSearch('')
    setNewLeadStatus('cold')
    setNewLeadSource('')
    setNewLeadNotes('')
    setShowContactResults(false)
  }

  const handleConvertClick = (lead: LeadListItem, e: React.MouseEvent) => {
    e.stopPropagation()
    setConvertLead(lead)
  }

  const canConvert = (lead: LeadListItem) => {
    return lead.status !== 'converted' && lead.status !== 'disqualified'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-display">Leads</h1>
          <p className="text-muted-foreground">
            Verwalten und qualifizieren Sie Ihre Leads
          </p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Neuer Lead
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <Select
          value={statusFilter}
          onValueChange={(value) => {
            setStatusFilter(value as LeadStatus | 'all')
            setPage(1)
          }}
        >
          <SelectTrigger className="w-48">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Status filtern" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Status</SelectItem>
            <SelectItem value="cold">Cold</SelectItem>
            <SelectItem value="warm">Warm</SelectItem>
            <SelectItem value="hot">Hot</SelectItem>
            <SelectItem value="to_be_done">To Be Done</SelectItem>
            <SelectItem value="converted">Converted</SelectItem>
            <SelectItem value="disqualified">Disqualified</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Leads Table */}
      {isLoading ? (
        <Card>
          <CardContent className="py-8">
            <div className="flex items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          </CardContent>
        </Card>
      ) : data?.items.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <p className="text-muted-foreground mb-4">Keine Leads gefunden</p>
            <Button onClick={() => setIsCreateOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Neuer Lead
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <table className="w-full">
              <thead className="border-b bg-muted/50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">Kontakt</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Kontaktdaten</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Firma / Position</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Quelle</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Erstellt</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">Aktionen</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((lead) => (
                  <tr
                    key={lead.id}
                    className="border-b last:border-0 hover:bg-muted/50"
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium">{lead.contact_name}</p>
                    </td>
                    <td className="px-4 py-3">
                      <div className="space-y-1">
                        {lead.contact_email && (
                          <div className="flex items-center gap-2 text-sm">
                            <Mail className="h-3 w-3 text-muted-foreground" />
                            <span>{lead.contact_email}</span>
                          </div>
                        )}
                        {(lead.contact_phone || lead.contact_mobile) && (
                          <div className="flex items-center gap-2 text-sm">
                            <Phone className="h-3 w-3 text-muted-foreground" />
                            <span>{lead.contact_phone || lead.contact_mobile}</span>
                          </div>
                        )}
                        {!lead.contact_email && !lead.contact_phone && !lead.contact_mobile && (
                          <span className="text-sm text-muted-foreground">-</span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div>
                        <p className="text-sm">{lead.company_name || '-'}</p>
                        {lead.contact_position && (
                          <p className="text-sm text-muted-foreground">{lead.contact_position}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Select
                        value={lead.status}
                        onValueChange={(value) => handleStatusChange(lead.id, value as LeadStatus)}
                      >
                        <SelectTrigger className="w-36" onClick={(e) => e.stopPropagation()}>
                          <Badge variant={statusColors[lead.status]}>
                            {statusLabels[lead.status]}
                          </Badge>
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="cold">Cold</SelectItem>
                          <SelectItem value="warm">Warm</SelectItem>
                          <SelectItem value="hot">Hot</SelectItem>
                          <SelectItem value="to_be_done">To Be Done</SelectItem>
                          <SelectItem value="converted">Converted</SelectItem>
                          <SelectItem value="disqualified">Disqualified</SelectItem>
                        </SelectContent>
                      </Select>
                    </td>
                    <td className="px-4 py-3 text-sm">{lead.source || '-'}</td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {format(new Date(lead.created_at), 'dd.MM.yyyy', { locale: de })}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {canConvert(lead) && (
                            <>
                              <DropdownMenuItem
                                onClick={(e) => handleConvertClick(lead, e)}
                                className="text-emerald-600"
                              >
                                <TrendingUp className="mr-2 h-4 w-4" />
                                In Opportunity konvertieren
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                            </>
                          )}
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.stopPropagation()
                              handleStatusChange(lead.id, 'hot')
                            }}
                            disabled={lead.status === 'hot'}
                          >
                            Als Hot markieren
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.stopPropagation()
                              handleStatusChange(lead.id, 'disqualified')
                            }}
                            disabled={lead.status === 'disqualified'}
                            className="text-destructive"
                          >
                            Disqualifizieren
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
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

      {/* Create Lead Dialog */}
      <Dialog open={isCreateOpen} onOpenChange={(open) => {
        setIsCreateOpen(open)
        if (!open) resetCreateForm()
      }}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Neuen Lead erstellen</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {/* Kontakt-Suche */}
            <div className="space-y-2">
              <Label htmlFor="contact-search">Kontakt auswählen *</Label>
              {selectedContact ? (
                <div className="flex items-center justify-between rounded-md border p-3 bg-muted/50">
                  <div>
                    <p className="font-medium">
                      {selectedContact.full_name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {selectedContact.email || 'Keine E-Mail'}
                      {selectedContact.company_name && ` • ${selectedContact.company_name}`}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedContact(null)}
                  >
                    Ändern
                  </Button>
                </div>
              ) : (
                <div className="relative">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="contact-search"
                      placeholder="Nach Kontakt suchen..."
                      value={contactSearch}
                      onChange={(e) => {
                        setContactSearch(e.target.value)
                        setShowContactResults(true)
                      }}
                      onFocus={() => setShowContactResults(true)}
                      className="pl-10"
                    />
                  </div>
                  {showContactResults && contactSearch.length >= 2 && (
                    <div className="absolute z-10 mt-1 w-full rounded-md border bg-popover shadow-lg">
                      {isSearching ? (
                        <div className="flex items-center justify-center p-4">
                          <Loader2 className="h-4 w-4 animate-spin" />
                        </div>
                      ) : contactResults && contactResults.length > 0 ? (
                        <ul className="max-h-60 overflow-auto py-1">
                          {contactResults.map((contact) => (
                            <li
                              key={contact.id}
                              className="cursor-pointer px-3 py-2 hover:bg-muted"
                              onClick={() => handleSelectContact(contact)}
                            >
                              <p className="font-medium">
                                {contact.full_name}
                              </p>
                              <p className="text-sm text-muted-foreground">
                                {contact.email || 'Keine E-Mail'}
                                {contact.company_name && ` • ${contact.company_name}`}
                              </p>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="p-4 text-sm text-muted-foreground">
                          Keine Kontakte gefunden
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Status */}
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select value={newLeadStatus} onValueChange={(value) => setNewLeadStatus(value as LeadStatus)}>
                <SelectTrigger>
                  <SelectValue placeholder="Status auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cold">Cold</SelectItem>
                  <SelectItem value="warm">Warm</SelectItem>
                  <SelectItem value="hot">Hot</SelectItem>
                  <SelectItem value="to_be_done">To Be Done</SelectItem>
                  <SelectItem value="disqualified">Disqualified</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Quelle */}
            <div className="space-y-2">
              <Label htmlFor="source">Quelle</Label>
              <Select value={newLeadSource} onValueChange={setNewLeadSource}>
                <SelectTrigger>
                  <SelectValue placeholder="Quelle auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="manual">Manuell</SelectItem>
                  <SelectItem value="website">Website</SelectItem>
                  <SelectItem value="referral">Empfehlung</SelectItem>
                  <SelectItem value="event">Veranstaltung</SelectItem>
                  <SelectItem value="cold_call">Kaltakquise</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Notizen */}
            <div className="space-y-2">
              <Label htmlFor="notes">Notizen</Label>
              <Textarea
                id="notes"
                placeholder="Zusätzliche Informationen..."
                value={newLeadNotes}
                onChange={(e) => setNewLeadNotes(e.target.value)}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
              Abbrechen
            </Button>
            <Button
              onClick={handleCreateLead}
              disabled={!selectedContact || createLead.isPending}
            >
              {createLead.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Erstelle...
                </>
              ) : (
                'Lead erstellen'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Convert to Opportunity Dialog */}
      <ConvertToOpportunityDialog
        open={!!convertLead}
        onOpenChange={(open) => {
          if (!open) setConvertLead(null)
        }}
        lead={convertLead}
      />
    </div>
  )
}
