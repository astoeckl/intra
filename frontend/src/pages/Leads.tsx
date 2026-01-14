import { useState, useCallback } from 'react'
import { Plus, Upload, Search, Filter } from 'lucide-react'
import { useLeads, useUpdateLead, useImportLeads } from '@/hooks/use-leads'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
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
import type { LeadStatus, LeadListItem } from '@/lib/types'
import { toast } from 'sonner'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'

const statusLabels: Record<LeadStatus, string> = {
  new: 'Neu',
  contacted: 'Kontaktiert',
  qualified: 'Qualifiziert',
  converted: 'Konvertiert',
  disqualified: 'Disqualifiziert',
}

const statusColors: Record<LeadStatus, 'default' | 'secondary' | 'success' | 'warning' | 'destructive'> = {
  new: 'default',
  contacted: 'secondary',
  qualified: 'warning',
  converted: 'success',
  disqualified: 'destructive',
}

export default function Leads() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<LeadStatus | 'all'>('all')
  const [isImportOpen, setIsImportOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedLead, setSelectedLead] = useState<LeadListItem | null>(null)

  const { data, isLoading } = useLeads({
    page,
    page_size: 20,
    status: statusFilter === 'all' ? undefined : statusFilter,
  })

  const updateLead = useUpdateLead()
  const importLeads = useImportLeads()

  const handleStatusChange = async (leadId: number, newStatus: LeadStatus) => {
    try {
      await updateLead.mutateAsync({ id: leadId, data: { status: newStatus } })
      toast.success('Status wurde aktualisiert')
    } catch {
      toast.error('Fehler beim Aktualisieren des Status')
    }
  }

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }, [])

  const handleImport = async () => {
    if (!selectedFile) return

    try {
      const result = await importLeads.mutateAsync({ file: selectedFile })
      toast.success(`${result.imported} von ${result.total_rows} Leads importiert`)
      if (result.errors.length > 0) {
        toast.warning(`${result.failed} Fehler: ${result.errors[0]}`)
      }
      setIsImportOpen(false)
      setSelectedFile(null)
    } catch {
      toast.error('Fehler beim Importieren')
    }
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
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setIsImportOpen(true)}>
            <Upload className="mr-2 h-4 w-4" />
            Importieren
          </Button>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Neuer Lead
          </Button>
        </div>
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
            <SelectItem value="new">Neu</SelectItem>
            <SelectItem value="contacted">Kontaktiert</SelectItem>
            <SelectItem value="qualified">Qualifiziert</SelectItem>
            <SelectItem value="converted">Konvertiert</SelectItem>
            <SelectItem value="disqualified">Disqualifiziert</SelectItem>
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
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setIsImportOpen(true)}>
                <Upload className="mr-2 h-4 w-4" />
                Leads importieren
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <table className="w-full">
              <thead className="border-b bg-muted/50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">Kontakt</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Firma</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Kampagne</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Erstellt</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((lead) => (
                  <tr
                    key={lead.id}
                    className="border-b last:border-0 hover:bg-muted/50 cursor-pointer"
                    onClick={() => setSelectedLead(lead)}
                  >
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium">{lead.contact_name}</p>
                        <p className="text-sm text-muted-foreground">{lead.contact_email}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">{lead.company_name || '-'}</td>
                    <td className="px-4 py-3 text-sm">{lead.campaign_name || '-'}</td>
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
                          <SelectItem value="new">Neu</SelectItem>
                          <SelectItem value="contacted">Kontaktiert</SelectItem>
                          <SelectItem value="qualified">Qualifiziert</SelectItem>
                          <SelectItem value="converted">Konvertiert</SelectItem>
                          <SelectItem value="disqualified">Disqualifiziert</SelectItem>
                        </SelectContent>
                      </Select>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {format(new Date(lead.created_at), 'dd.MM.yyyy', { locale: de })}
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

      {/* Import Dialog */}
      <Dialog open={isImportOpen} onOpenChange={setIsImportOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Leads importieren</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Laden Sie eine CSV oder Excel-Datei mit folgenden Spalten hoch:
              Vorname, Nachname, E-Mail, Telefon, Firma
            </p>
            <div className="flex items-center justify-center rounded-lg border-2 border-dashed p-8">
              <label className="cursor-pointer">
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  className="hidden"
                  onChange={handleFileSelect}
                />
                <div className="flex flex-col items-center gap-2">
                  <Upload className="h-8 w-8 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    {selectedFile ? selectedFile.name : 'Datei auswählen'}
                  </span>
                </div>
              </label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsImportOpen(false)}>
              Abbrechen
            </Button>
            <Button onClick={handleImport} disabled={!selectedFile || importLeads.isPending}>
              {importLeads.isPending ? 'Importiere...' : 'Importieren'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
