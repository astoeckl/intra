import { useState } from 'react'
import {
  useLookupCategories,
  useLookupValues,
  useCreateLookupValue,
  useUpdateLookupValue,
  useDeleteLookupValue,
} from '@/hooks/use-settings'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
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
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import { Loader2, Plus, Pencil, Trash2, RotateCcw } from 'lucide-react'
import type { LookupValue } from '@/lib/types'

const CATEGORY_LABELS: Record<string, string> = {
  lead_status: 'Lead Status',
  potential_category: 'Potenzial-Kategorien',
  industry: 'Branchen',
  country: 'Länder',
  salutation: 'Anreden',
  title: 'Titel',
  contact_lead_status: 'Kontakt-Lead-Status',
  task_priority: 'Aufgaben-Prioritäten',
  campaign_type: 'Kampagnen-Typen',
  campaign_source: 'Kampagnen-Quellen',
}

interface LookupFormData {
  value: string
  label: string
  sort_order: number
}

export default function LookupValuesTab() {
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [showInactive, setShowInactive] = useState(false)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingLookup, setEditingLookup] = useState<LookupValue | null>(null)
  const [formData, setFormData] = useState<LookupFormData>({
    value: '',
    label: '',
    sort_order: 0,
  })

  const { data: categories, isLoading: categoriesLoading } = useLookupCategories()
  const { data: lookupValues, isLoading: valuesLoading } = useLookupValues(
    selectedCategory,
    showInactive
  )
  const createLookup = useCreateLookupValue()
  const updateLookup = useUpdateLookupValue()
  const deleteLookup = useDeleteLookupValue()

  const handleOpenDialog = (lookup?: LookupValue) => {
    if (lookup) {
      setEditingLookup(lookup)
      setFormData({
        value: lookup.value,
        label: lookup.label,
        sort_order: lookup.sort_order,
      })
    } else {
      setEditingLookup(null)
      const maxSortOrder = lookupValues?.reduce(
        (max, lv) => Math.max(max, lv.sort_order),
        -1
      ) ?? -1
      setFormData({
        value: '',
        label: '',
        sort_order: maxSortOrder + 1,
      })
    }
    setIsDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setIsDialogOpen(false)
    setEditingLookup(null)
    setFormData({ value: '', label: '', sort_order: 0 })
  }

  const handleSave = async () => {
    try {
      if (editingLookup) {
        await updateLookup.mutateAsync({
          id: editingLookup.id,
          data: {
            value: formData.value,
            label: formData.label,
            sort_order: formData.sort_order,
          },
          category: selectedCategory,
        })
        toast.success('Wert aktualisiert')
      } else {
        await createLookup.mutateAsync({
          category: selectedCategory,
          value: formData.value,
          label: formData.label,
          sort_order: formData.sort_order,
        })
        toast.success('Wert erstellt')
      }
      handleCloseDialog()
    } catch (error) {
      toast.error('Fehler beim Speichern')
      console.error('Error saving lookup value:', error)
    }
  }

  const handleDelete = async (lookup: LookupValue) => {
    if (!confirm(`Möchten Sie "${lookup.label}" wirklich deaktivieren?`)) return

    try {
      await deleteLookup.mutateAsync({
        id: lookup.id,
        category: selectedCategory,
      })
      toast.success('Wert deaktiviert')
    } catch (error) {
      toast.error('Fehler beim Deaktivieren')
      console.error('Error deleting lookup value:', error)
    }
  }

  const handleReactivate = async (lookup: LookupValue) => {
    try {
      await updateLookup.mutateAsync({
        id: lookup.id,
        data: { is_active: true },
        category: selectedCategory,
      })
      toast.success('Wert reaktiviert')
    } catch (error) {
      toast.error('Fehler beim Reaktivieren')
      console.error('Error reactivating lookup value:', error)
    }
  }

  const isLoading = categoriesLoading || valuesLoading

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Dropdown-Werte</CardTitle>
          <CardDescription>
            Verwalten Sie die Auswahloptionen für Dropdown-Felder in der Anwendung.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Category Selector */}
          <div className="flex flex-wrap items-end gap-4">
            <div className="flex-1 min-w-[200px]">
              <Label htmlFor="category">Kategorie</Label>
              <Select
                value={selectedCategory}
                onValueChange={setSelectedCategory}
              >
                <SelectTrigger id="category">
                  <SelectValue placeholder="Kategorie auswählen" />
                </SelectTrigger>
                <SelectContent>
                  {categories?.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {CATEGORY_LABELS[cat] || cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="showInactive"
                checked={showInactive}
                onChange={(e) => setShowInactive(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300"
              />
              <Label htmlFor="showInactive" className="text-sm cursor-pointer">
                Inaktive anzeigen
              </Label>
            </div>

            {selectedCategory && (
              <Button onClick={() => handleOpenDialog()}>
                <Plus className="mr-2 h-4 w-4" />
                Hinzufügen
              </Button>
            )}
          </div>

          {/* Values Table */}
          {selectedCategory ? (
            isLoading ? (
              <div className="flex items-center justify-center py-10">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[60px]">#</TableHead>
                      <TableHead>Wert</TableHead>
                      <TableHead>Bezeichnung</TableHead>
                      <TableHead className="w-[100px]">Status</TableHead>
                      <TableHead className="w-[120px]">Aktionen</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {lookupValues && lookupValues.length > 0 ? (
                      lookupValues.map((lookup) => (
                        <TableRow
                          key={lookup.id}
                          className={!lookup.is_active ? 'opacity-50' : undefined}
                        >
                          <TableCell className="text-muted-foreground">
                            {lookup.sort_order}
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {lookup.value}
                          </TableCell>
                          <TableCell>{lookup.label}</TableCell>
                          <TableCell>
                            <Badge
                              variant={lookup.is_active ? 'default' : 'secondary'}
                            >
                              {lookup.is_active ? 'Aktiv' : 'Inaktiv'}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-1">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleOpenDialog(lookup)}
                                title="Bearbeiten"
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              {lookup.is_active ? (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleDelete(lookup)}
                                  title="Deaktivieren"
                                >
                                  <Trash2 className="h-4 w-4 text-destructive" />
                                </Button>
                              ) : (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleReactivate(lookup)}
                                  title="Reaktivieren"
                                >
                                  <RotateCcw className="h-4 w-4 text-green-600" />
                                </Button>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell
                          colSpan={5}
                          className="text-center text-muted-foreground py-10"
                        >
                          Keine Werte in dieser Kategorie
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            )
          ) : (
            <div className="text-center text-muted-foreground py-10">
              Wählen Sie eine Kategorie aus, um die Werte anzuzeigen.
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add/Edit Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingLookup ? 'Wert bearbeiten' : 'Neuen Wert hinzufügen'}
            </DialogTitle>
            <DialogDescription>
              {editingLookup
                ? 'Bearbeiten Sie den ausgewählten Dropdown-Wert.'
                : `Fügen Sie einen neuen Wert zur Kategorie "${CATEGORY_LABELS[selectedCategory] || selectedCategory}" hinzu.`}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="value">Wert (intern)</Label>
              <Input
                id="value"
                value={formData.value}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, value: e.target.value }))
                }
                placeholder="z.B. tax_advisor"
                disabled={!!editingLookup}
              />
              <p className="text-xs text-muted-foreground">
                Der interne Wert wird in der Datenbank gespeichert.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="label">Bezeichnung (angezeigt)</Label>
              <Input
                id="label"
                value={formData.label}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, label: e.target.value }))
                }
                placeholder="z.B. Steuerberater"
              />
              <p className="text-xs text-muted-foreground">
                Diese Bezeichnung wird den Benutzern angezeigt.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="sort_order">Reihenfolge</Label>
              <Input
                id="sort_order"
                type="number"
                min="0"
                value={formData.sort_order}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    sort_order: parseInt(e.target.value) || 0,
                  }))
                }
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleCloseDialog}>
              Abbrechen
            </Button>
            <Button
              onClick={handleSave}
              disabled={
                !formData.value ||
                !formData.label ||
                createLookup.isPending ||
                updateLookup.isPending
              }
            >
              {(createLookup.isPending || updateLookup.isPending) && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              {editingLookup ? 'Speichern' : 'Hinzufügen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
