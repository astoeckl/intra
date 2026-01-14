import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Calendar, Share2, Link } from 'lucide-react'

export default function IntegrationsTab() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Link className="h-5 w-5" />
            Integrationen
          </CardTitle>
          <CardDescription>
            Verbindungen zu externen Diensten und APIs.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Calendar Integration */}
          <div className="rounded-lg border p-4">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                  <Calendar className="h-5 w-5 text-muted-foreground" />
                </div>
                <div>
                  <h4 className="font-medium">Kalender-Integration</h4>
                  <p className="text-sm text-muted-foreground">
                    Synchronisieren Sie Aufgaben und Termine mit Microsoft 365 oder Google Calendar.
                  </p>
                </div>
              </div>
              <Badge variant="secondary">Demnächst</Badge>
            </div>
            <div className="mt-4 rounded bg-muted/50 p-3 text-sm text-muted-foreground">
              <p>
                Diese Funktion ermöglicht die bidirektionale Synchronisation von Terminen und
                Aufgaben mit externen Kalenderdiensten.
              </p>
              <ul className="mt-2 list-inside list-disc space-y-1">
                <li>Microsoft 365 / Outlook</li>
                <li>Google Calendar</li>
                <li>Apple Calendar (iCal)</li>
              </ul>
            </div>
          </div>

          {/* Meta Ads Integration */}
          <div className="rounded-lg border p-4">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                  <Share2 className="h-5 w-5 text-muted-foreground" />
                </div>
                <div>
                  <h4 className="font-medium">Meta Ads Integration</h4>
                  <p className="text-sm text-muted-foreground">
                    Verbinden Sie Facebook und Instagram Lead-Formulare mit dem CRM.
                  </p>
                </div>
              </div>
              <Badge variant="secondary">Demnächst</Badge>
            </div>
            <div className="mt-4 rounded bg-muted/50 p-3 text-sm text-muted-foreground">
              <p>
                Automatischer Import von Leads aus Facebook und Instagram Lead Ads.
              </p>
              <ul className="mt-2 list-inside list-disc space-y-1">
                <li>Facebook Lead Ads</li>
                <li>Instagram Lead Ads</li>
                <li>Automatische Kampagnen-Zuordnung</li>
              </ul>
            </div>
          </div>

          {/* Placeholder for future integrations */}
          <div className="rounded-lg border border-dashed p-4 text-center">
            <p className="text-sm text-muted-foreground">
              Weitere Integrationen werden in zukünftigen Versionen hinzugefügt.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
