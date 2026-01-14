import { useState } from 'react'
import { Plus, Filter, TrendingUp, DollarSign, Target, Percent, LayoutGrid, List } from 'lucide-react'
import { useOpportunities, usePipelineStats } from '@/hooks/use-opportunities'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { OpportunityStage, OpportunityListItem } from '@/lib/types'
import { STAGE_LABELS, STAGE_COLORS } from '@/lib/types'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'
import { OpportunityDialog } from '@/components/opportunities/OpportunityDialog'
import { PipelineKanban } from '@/components/opportunities/PipelineKanban'

function formatCurrency(value: number | undefined): string {
  if (value === undefined || value === null) return '-'
  return new Intl.NumberFormat('de-AT', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

type ViewMode = 'list' | 'kanban'

export default function Opportunities() {
  const [page, setPage] = useState(1)
  const [stageFilter, setStageFilter] = useState<OpportunityStage | 'all'>('all')
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [selectedOpportunity, setSelectedOpportunity] = useState<OpportunityListItem | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('kanban')

  const { data, isLoading } = useOpportunities({
    page,
    page_size: 20,
    stage: stageFilter === 'all' ? undefined : stageFilter,
  })

  const { data: stats } = usePipelineStats()

  const handleEdit = (opp: OpportunityListItem) => {
    setSelectedOpportunity(opp)
    setIsDialogOpen(true)
  }

  const handleCreate = () => {
    setSelectedOpportunity(null)
    setIsDialogOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-display">Opportunities</h1>
          <p className="text-muted-foreground">Verwalten Sie Ihre Verkaufschancen</p>
        </div>
        <div className="flex items-center gap-3">
          <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as ViewMode)}>
            <TabsList>
              <TabsTrigger value="kanban" className="gap-2">
                <LayoutGrid className="h-4 w-4" />
                Pipeline
              </TabsTrigger>
              <TabsTrigger value="list" className="gap-2">
                <List className="h-4 w-4" />
                Liste
              </TabsTrigger>
            </TabsList>
          </Tabs>
          <Button onClick={handleCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Neue Opportunity
          </Button>
        </div>
      </div>

      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="rounded-full bg-blue-100 p-3">
                <Target className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Opportunities</p>
                <p className="text-2xl font-bold">{stats.total_opportunities}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="rounded-full bg-emerald-100 p-3">
                <DollarSign className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Pipeline-Wert</p>
                <p className="text-2xl font-bold">{formatCurrency(stats.total_value)}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="rounded-full bg-amber-100 p-3">
                <TrendingUp className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Gewichteter Wert</p>
                <p className="text-2xl font-bold">{formatCurrency(stats.weighted_value)}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="rounded-full bg-purple-100 p-3">
                <Percent className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Win Rate</p>
                <p className="text-2xl font-bold">{stats.win_rate.toFixed(0)}%</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {viewMode === 'kanban' ? (
        <PipelineKanban onCardClick={handleEdit} />
      ) : (
        <>
          <div className="flex items-center gap-4">
            <Select
              value={stageFilter}
              onValueChange={(value) => {
                setStageFilter(value as OpportunityStage | 'all')
                setPage(1)
              }}
            >
              <SelectTrigger className="w-48">
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Stage filtern" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Alle Stages</SelectItem>
                <SelectItem value="qualification">Qualifizierung</SelectItem>
                <SelectItem value="discovery">Bedarfsanalyse</SelectItem>
                <SelectItem value="proposal">Angebot</SelectItem>
                <SelectItem value="negotiation">Verhandlung</SelectItem>
                <SelectItem value="closed_won">Gewonnen</SelectItem>
                <SelectItem value="closed_lost">Verloren</SelectItem>
              </SelectContent>
            </Select>
          </div>

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
                <p className="text-muted-foreground mb-4">Keine Opportunities gefunden</p>
                <Button onClick={handleCreate}>
                  <Plus className="mr-2 h-4 w-4" />
                  Erste Opportunity erstellen
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
                      <th className="px-4 py-3 text-left text-sm font-medium">Firma</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Wert</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Stage</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Wahrsch.</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Abschluss</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data?.items.map((opp) => (
                      <tr
                        key={opp.id}
                        className="border-b last:border-0 hover:bg-muted/50 cursor-pointer"
                        onClick={() => handleEdit(opp)}
                      >
                        <td className="px-4 py-3">
                          <div>
                            <p className="font-medium">{opp.name}</p>
                            {opp.contact_name && (
                              <p className="text-sm text-muted-foreground">{opp.contact_name}</p>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm">{opp.company_name || '-'}</td>
                        <td className="px-4 py-3 text-sm font-medium">
                          {formatCurrency(opp.expected_value)}
                        </td>
                        <td className="px-4 py-3">
                          <Badge className={STAGE_COLORS[opp.stage] + ' text-white'}>
                            {STAGE_LABELS[opp.stage]}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-sm">{opp.probability}%</td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">
                          {opp.expected_close_date
                            ? format(new Date(opp.expected_close_date), 'dd.MM.yyyy', { locale: de })
                            : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}

          {data && data.total_pages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                Zurueck
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

      <OpportunityDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        opportunity={selectedOpportunity}
      />
    </div>
  )
}
