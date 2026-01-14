import { useState } from 'react'
import { Plus, Search, MoreHorizontal, Mail, Phone, Building2 } from 'lucide-react'
import { useContacts, useDeleteContact } from '@/hooks/use-contacts'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ContactDialog } from '@/components/contacts/ContactDialog'
import type { ContactListItem } from '@/lib/types'
import { toast } from 'sonner'

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

  const deleteContact = useDeleteContact()

  const handleEdit = (contact: ContactListItem) => {
    setSelectedContact(contact)
    setIsDialogOpen(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await deleteContact.mutateAsync(id)
      toast.success('Kontakt wurde deaktiviert')
    } catch {
      toast.error('Fehler beim Deaktivieren des Kontakts')
    }
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

      {/* Contacts Grid */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="pb-3">
                <div className="h-5 bg-muted rounded w-3/4" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-4 bg-muted rounded w-1/2" />
                  <div className="h-4 bg-muted rounded w-2/3" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
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
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {data?.items.map((contact) => (
              <Card
                key={contact.id}
                className="cursor-pointer transition-shadow hover:shadow-md"
                onClick={() => handleEdit(contact)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">
                      {contact.first_name} {contact.last_name}
                    </CardTitle>
                    <Badge variant={contact.is_active ? 'success' : 'secondary'}>
                      {contact.is_active ? 'Aktiv' : 'Inaktiv'}
                    </Badge>
                  </div>
                  {contact.position && (
                    <p className="text-sm text-muted-foreground">{contact.position}</p>
                  )}
                </CardHeader>
                <CardContent className="space-y-2">
                  {contact.company_name && (
                    <div className="flex items-center gap-2 text-sm">
                      <Building2 className="h-4 w-4 text-muted-foreground" />
                      <span>{contact.company_name}</span>
                    </div>
                  )}
                  {contact.email && (
                    <div className="flex items-center gap-2 text-sm">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <span className="truncate">{contact.email}</span>
                    </div>
                  )}
                  {contact.phone && (
                    <div className="flex items-center gap-2 text-sm">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                      <span>{contact.phone}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

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
        </>
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
