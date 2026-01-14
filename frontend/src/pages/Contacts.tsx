import { useState } from 'react'
import { Plus, Search, Mail, Phone } from 'lucide-react'
import { useContacts } from '@/hooks/use-contacts'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ContactDialog } from '@/components/contacts/ContactDialog'
import type { ContactListItem } from '@/lib/types'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'

export default function Contacts() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [selectedContact, setSelectedContact] = useState<ContactListItem | null>(null)

  const { data, isLoading } = useContacts({
    page,
    page_size: 20,
    search: search || undefined,
  })

  const handleEdit = (contact: ContactListItem) => {
    setSelectedContact(contact)
    setIsDialogOpen(true)
  }

  const handleDialogClose = () => {
    setIsDialogOpen(false)
    setSelectedContact(null)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-display">Kontakte</h1>
          <p className="text-muted-foreground">
            Verwalten Sie alle Ihre Kontakte und Ansprechpartner
          </p>
        </div>
        <Button onClick={() => setIsDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Neuer Kontakt
        </Button>
      </div>

      {/* Search */}
      <div className="relative w-96">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Suche nach Name, E-Mail..."
          className="pl-10"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value)
            setPage(1)
          }}
        />
      </div>

      {/* Contacts Table */}
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
            <p className="text-muted-foreground mb-4">Keine Kontakte gefunden</p>
            <Button onClick={() => setIsDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Ersten Kontakt anlegen
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <table className="w-full">
              <thead className="border-b bg-muted/50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Kontaktdaten</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Firma / Position</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Erstellt</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((contact) => (
                  <tr
                    key={contact.id}
                    className="border-b last:border-0 hover:bg-muted/50 cursor-pointer"
                    onClick={() => handleEdit(contact)}
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium">
                        {contact.first_name} {contact.last_name}
                      </p>
                    </td>
                    <td className="px-4 py-3">
                      <div className="space-y-1">
                        {contact.email && (
                          <div className="flex items-center gap-2 text-sm">
                            <Mail className="h-3 w-3 text-muted-foreground" />
                            <span>{contact.email}</span>
                          </div>
                        )}
                        {contact.phone && (
                          <div className="flex items-center gap-2 text-sm">
                            <Phone className="h-3 w-3 text-muted-foreground" />
                            <span>{contact.phone}</span>
                          </div>
                        )}
                        {!contact.email && !contact.phone && (
                          <span className="text-sm text-muted-foreground">-</span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div>
                        <p className="text-sm">{contact.company_name || '-'}</p>
                        {contact.position && (
                          <p className="text-sm text-muted-foreground">{contact.position}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={contact.is_active ? 'default' : 'secondary'}>
                        {contact.is_active ? 'Aktiv' : 'Inaktiv'}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {format(new Date(contact.created_at), 'dd.MM.yyyy', { locale: de })}
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

      {/* Contact Dialog */}
      <ContactDialog
        open={isDialogOpen}
        onOpenChange={handleDialogClose}
        contact={selectedContact}
      />
    </div>
  )
}
