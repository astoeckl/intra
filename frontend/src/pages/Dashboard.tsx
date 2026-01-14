import { useQuery } from '@tanstack/react-query'
import {
  Users,
  Target,
  CheckSquare,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { healthCheck } from '@/lib/api'

interface StatCardProps {
  title: string
  value: string
  change: string
  trend: 'up' | 'down'
  icon: React.ElementType
}

function StatCard({ title, value, change, trend, icon: Icon }: StatCardProps) {
  return (
    <Card className="animate-fade-in">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
          <Icon className="h-4 w-4 text-primary" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold font-display">{value}</div>
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
      </CardContent>
    </Card>
  )
}

export default function Dashboard() {
  const { data: health, isLoading } = useQuery({
    queryKey: ['health'],
    queryFn: healthCheck,
    retry: false,
  })

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
              isLoading
                ? 'bg-yellow-500 animate-pulse'
                : health?.status === 'healthy'
                ? 'bg-accent'
                : 'bg-destructive'
            }`}
          />
          <span className="text-sm">
            API Status:{' '}
            {isLoading ? 'Verbinde...' : health?.status || 'Nicht erreichbar'}
          </span>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Aktive Leads"
          value="124"
          change="+12.5%"
          trend="up"
          icon={Target}
        />
        <StatCard
          title="Kontakte"
          value="2,456"
          change="+8.2%"
          trend="up"
          icon={Users}
        />
        <StatCard
          title="Offene Aufgaben"
          value="38"
          change="-5.4%"
          trend="down"
          icon={CheckSquare}
        />
        <StatCard
          title="Conversion Rate"
          value="68%"
          change="+4.1%"
          trend="up"
          icon={TrendingUp}
        />
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Letzte Aktivitäten</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Noch keine Aktivitäten vorhanden.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Anstehende Aufgaben</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Keine offenen Aufgaben.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
