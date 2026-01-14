import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Users,
  Target,
  CheckSquare,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  Percent,
  BarChart3,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { healthCheck } from '@/lib/api'
import { usePipelineStats, useOpportunities } from '@/hooks/use-opportunities'
import { STAGE_LABELS, STAGE_COLORS } from '@/lib/types'
import type { PipelineStageStats, OpportunityListItem } from '@/lib/types'

function formatCurrency(value: number | undefined): string {
  if (value === undefined || value === null) return '€ 0'
  return new Intl.NumberFormat('de-AT', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

interface StatCardProps {
  title: string
  value: string
  change?: string
  trend?: 'up' | 'down'
  icon: React.ElementType
  iconColor?: string
  link?: string
}

function StatCard({ title, value, change, trend, icon: Icon, iconColor = 'bg-primary/10 text-primary', link }: StatCardProps) {
  const content = (
    <Card className="animate-fade-in hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${iconColor}`}>
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold font-display">{value}</div>
        {change && trend && (
          <p className="mt-1 flex items-center gap-1 text-xs">
            {trend === 'up' ? (
              <ArrowUpRight className="h-3 w-3 text-accent" />
            ) : (
              <ArrowDownRight className="h-3 w-3 text-destructive" />
            )}
            <span className={trend === 'up' ? 'text-accent' : 'text-destructive'}>
              {change}
            </span>
            <span className="text-muted-foreground">vs. letzter Monat</span>
          </p>
        )}
      </CardContent>
    </Card>
  )

  if (link) {
    return <Link to={link}>{content}</Link>
  }

  return content
}

function PipelineOverview({ stages }: { stages: PipelineStageStats[] }) {
  const activeStages = stages.filter(s => !['closed_won', 'closed_lost'].includes(s.stage))
  const maxValue = Math.max(...activeStages.map(s => s.total_value), 1)

  return (
    <div className="space-y-3">
      {activeStages.map((stage) => (
        <div key={stage.stage} className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">{STAGE_LABELS[stage.stage]}</span>
            <span className="text-muted-foreground">
              {stage.count} · {formatCurrency(stage.total_value)}
            </span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div
              className={`h-full rounded-full ${STAGE_COLORS[stage.stage]}`}
              style={{ width: `${(stage.total_value / maxValue) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

function RecentOpportunities({ opportunities }: { opportunities: OpportunityListItem[] }) {
  if (opportunities.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-4">
        Keine Opportunities vorhanden.
      </p>
    )
  }

  return (
    <div className="space-y-3">
      {opportunities.slice(0, 5).map((opp) => (
        <div key={opp.id} className="flex items-center justify-between">
          <div className="min-w-0 flex-1">
            <p className="font-medium text-sm truncate">{opp.name}</p>
            <p className="text-xs text-muted-foreground">
              {opp.company_name || opp.contact_name || 'Kein Kontakt'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-emerald-600">
              {formatCurrency(opp.expected_value)}
            </span>
            <Badge className={STAGE_COLORS[opp.stage] + ' text-white text-xs'}>
              {STAGE_LABELS[opp.stage]}
            </Badge>
          </div>
        </div>
      ))}
    </div>
  )
}

export default function Dashboard() {
  const { data: health, isLoading: isHealthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: healthCheck,
    retry: false,
  })

  const { data: stats, isLoading: isStatsLoading } = usePipelineStats()
  const { data: opportunities } = useOpportunities({ page_size: 5 })

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold font-display">Dashboard</h1>
        <p className="text-muted-foreground">
          Willkommen im Atikon CRM/Intranet System
        </p>
      </div>

      {/* API Status */}
      <Card className="border-dashed">
        <CardContent className="flex items-center gap-3 py-3">
          <div
            className={`h-2 w-2 rounded-full ${
              isHealthLoading
                ? 'bg-yellow-500 animate-pulse'
                : health?.status === 'healthy'
                ? 'bg-accent'
                : 'bg-destructive'
            }`}
          />
          <span className="text-sm">
            API Status:{' '}
            {isHealthLoading ? 'Verbinde...' : health?.status || 'Nicht erreichbar'}
          </span>
        </CardContent>
      </Card>

      {/* Opportunity Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Offene Opportunities"
          value={isStatsLoading ? '...' : String(stats?.total_opportunities || 0)}
          icon={Target}
          iconColor="bg-blue-100 text-blue-600"
          link="/opportunities"
        />
        <StatCard
          title="Pipeline-Wert"
          value={isStatsLoading ? '...' : formatCurrency(stats?.total_value)}
          icon={DollarSign}
          iconColor="bg-emerald-100 text-emerald-600"
          link="/opportunities"
        />
        <StatCard
          title="Gewichteter Wert"
          value={isStatsLoading ? '...' : formatCurrency(stats?.weighted_value)}
          icon={TrendingUp}
          iconColor="bg-amber-100 text-amber-600"
          link="/opportunities"
        />
        <StatCard
          title="Win Rate"
          value={isStatsLoading ? '...' : `${(stats?.win_rate || 0).toFixed(0)}%`}
          icon={Percent}
          iconColor="bg-purple-100 text-purple-600"
          link="/opportunities"
        />
      </div>

      {/* Pipeline Overview & Recent Opportunities */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Pipeline Übersicht
            </CardTitle>
            <Button variant="outline" size="sm" asChild>
              <Link to="/opportunities">Alle anzeigen</Link>
            </Button>
          </CardHeader>
          <CardContent>
            {isStatsLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              </div>
            ) : stats?.stages && stats.stages.length > 0 ? (
              <PipelineOverview stages={stats.stages} />
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                Keine Pipeline-Daten vorhanden.
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Neueste Opportunities
            </CardTitle>
            <Button variant="outline" size="sm" asChild>
              <Link to="/opportunities">Alle anzeigen</Link>
            </Button>
          </CardHeader>
          <CardContent>
            <RecentOpportunities opportunities={opportunities?.items || []} />
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Durchschn. Deal-Größe"
          value={isStatsLoading ? '...' : formatCurrency(stats?.average_deal_size)}
          icon={DollarSign}
          iconColor="bg-slate-100 text-slate-600"
        />
        <StatCard
          title="Kontakte"
          value="—"
          icon={Users}
          iconColor="bg-indigo-100 text-indigo-600"
          link="/contacts"
        />
        <StatCard
          title="Offene Aufgaben"
          value="—"
          icon={CheckSquare}
          iconColor="bg-rose-100 text-rose-600"
          link="/tasks"
        />
        <StatCard
          title="Aktive Leads"
          value="—"
          icon={TrendingUp}
          iconColor="bg-cyan-100 text-cyan-600"
          link="/leads"
        />
      </div>
    </div>
  )
}
