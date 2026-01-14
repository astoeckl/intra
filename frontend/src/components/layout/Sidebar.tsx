import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Target,
  CheckSquare,
  Mail,
  Phone,
  Settings,
  FileText,
  TrendingUp,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Callcenter', href: '/callcenter', icon: Phone },
  { name: 'Leads', href: '/leads', icon: Target },
  { name: 'Opportunities', href: '/opportunities', icon: TrendingUp },
  { name: 'Kontakte', href: '/contacts', icon: Users },
  { name: 'Aufgaben', href: '/tasks', icon: CheckSquare },
  { name: 'E-Mail Vorlagen', href: '/templates', icon: Mail },
  { name: 'Landing Pages', href: '/landing-pages', icon: FileText },
]

const bottomNavigation = [
  { name: 'Einstellungen', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  return (
    <aside className="flex w-64 flex-col border-r bg-card">
      <div className="flex h-16 items-center gap-2 px-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
          <span className="font-display text-lg font-bold text-primary-foreground">A</span>
        </div>
        <div>
          <h1 className="font-display text-lg font-semibold">Atikon</h1>
          <p className="text-xs text-muted-foreground">CRM/Intranet</p>
        </div>
      </div>

      <Separator />

      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </ScrollArea>

      <Separator />

      <div className="p-3">
        {bottomNavigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.name}
          </NavLink>
        ))}
      </div>
    </aside>
  )
}