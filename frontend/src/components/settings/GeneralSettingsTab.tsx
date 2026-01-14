import { useState, useEffect } from 'react'
import { useSettings, useUpdateSetting, useCreateSetting } from '@/hooks/use-settings'
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
import { toast } from 'sonner'
import { Loader2, Save, Info } from 'lucide-react'

const TIMEZONES = [
  { value: 'Europe/Vienna', label: 'Wien (Europe/Vienna)' },
  { value: 'Europe/Berlin', label: 'Berlin (Europe/Berlin)' },
  { value: 'Europe/Zurich', label: 'Zürich (Europe/Zurich)' },
  { value: 'UTC', label: 'UTC' },
]

const DATE_FORMATS = [
  { value: 'DD.MM.YYYY', label: 'DD.MM.YYYY (31.12.2026)' },
  { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (2026-12-31)' },
  { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY (12/31/2026)' },
]

const LANGUAGES = [
  { value: 'de', label: 'Deutsch' },
  { value: 'en', label: 'English' },
]

interface GeneralSettings {
  appName: string
  timezone: string
  dateFormat: string
  language: string
}

export default function GeneralSettingsTab() {
  const { data: settings, isLoading } = useSettings('general')
  const updateSetting = useUpdateSetting()
  const createSetting = useCreateSetting()
  
  const [localSettings, setLocalSettings] = useState<GeneralSettings>({
    appName: 'Atikon CRM',
    timezone: 'Europe/Vienna',
    dateFormat: 'DD.MM.YYYY',
    language: 'de',
  })
  const [hasChanges, setHasChanges] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  // Load settings from API
  useEffect(() => {
    if (settings) {
      const newSettings = { ...localSettings }
      settings.forEach((s) => {
        switch (s.key) {
          case 'app.name':
            newSettings.appName = s.value || 'Atikon CRM'
            break
          case 'app.timezone':
            newSettings.timezone = s.value || 'Europe/Vienna'
            break
          case 'app.date_format':
            newSettings.dateFormat = s.value || 'DD.MM.YYYY'
            break
          case 'app.language':
            newSettings.language = s.value || 'de'
            break
        }
      })
      setLocalSettings(newSettings)
      setHasChanges(false)
    }
  }, [settings])

  const handleChange = (key: keyof GeneralSettings, value: string) => {
    setLocalSettings((prev) => ({ ...prev, [key]: value }))
    setHasChanges(true)
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const settingsToSave = [
        { key: 'app.name', value: localSettings.appName },
        { key: 'app.timezone', value: localSettings.timezone },
        { key: 'app.date_format', value: localSettings.dateFormat },
        { key: 'app.language', value: localSettings.language },
      ]

      for (const setting of settingsToSave) {
        const existing = settings?.find((s) => s.key === setting.key)
        if (existing) {
          await updateSetting.mutateAsync({
            key: setting.key,
            data: { value: setting.value },
          })
        } else {
          await createSetting.mutateAsync({
            key: setting.key,
            category: 'general',
            value: setting.value,
            value_type: 'string',
          })
        }
      }

      toast.success('Einstellungen gespeichert')
      setHasChanges(false)
    } catch (error) {
      toast.error('Fehler beim Speichern der Einstellungen')
      console.error('Error saving settings:', error)
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-10">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Allgemeine Einstellungen</CardTitle>
          <CardDescription>
            Grundlegende Anwendungseinstellungen und Konfigurationen.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* App Name */}
          <div className="space-y-2">
            <Label htmlFor="appName">Anwendungsname</Label>
            <Input
              id="appName"
              value={localSettings.appName}
              onChange={(e) => handleChange('appName', e.target.value)}
              placeholder="Atikon CRM"
            />
            <p className="text-xs text-muted-foreground">
              Der Name wird in der Navigationsleiste und E-Mails angezeigt.
            </p>
          </div>

          {/* Timezone */}
          <div className="space-y-2">
            <Label htmlFor="timezone">Zeitzone</Label>
            <Select
              value={localSettings.timezone}
              onValueChange={(value) => handleChange('timezone', value)}
            >
              <SelectTrigger id="timezone">
                <SelectValue placeholder="Zeitzone auswählen" />
              </SelectTrigger>
              <SelectContent>
                {TIMEZONES.map((tz) => (
                  <SelectItem key={tz.value} value={tz.value}>
                    {tz.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Date Format */}
          <div className="space-y-2">
            <Label htmlFor="dateFormat">Datumsformat</Label>
            <Select
              value={localSettings.dateFormat}
              onValueChange={(value) => handleChange('dateFormat', value)}
            >
              <SelectTrigger id="dateFormat">
                <SelectValue placeholder="Datumsformat auswählen" />
              </SelectTrigger>
              <SelectContent>
                {DATE_FORMATS.map((df) => (
                  <SelectItem key={df.value} value={df.value}>
                    {df.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Language */}
          <div className="space-y-2">
            <Label htmlFor="language">Sprache</Label>
            <Select
              value={localSettings.language}
              onValueChange={(value) => handleChange('language', value)}
            >
              <SelectTrigger id="language">
                <SelectValue placeholder="Sprache auswählen" />
              </SelectTrigger>
              <SelectContent>
                {LANGUAGES.map((lang) => (
                  <SelectItem key={lang.value} value={lang.value}>
                    {lang.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button onClick={handleSave} disabled={!hasChanges || isSaving}>
              {isSaving ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Save className="mr-2 h-4 w-4" />
              )}
              Speichern
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* System Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5" />
            Systeminformationen
          </CardTitle>
          <CardDescription>
            Aktuelle Informationen über das System (nur lesbar).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1">
              <p className="text-sm font-medium">Version</p>
              <p className="text-sm text-muted-foreground">1.0.0</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium">Umgebung</p>
              <p className="text-sm text-muted-foreground">
                <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                  Development
                </span>
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium">Backend API</p>
              <p className="text-sm text-muted-foreground">
                {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium">Datenbank</p>
              <p className="text-sm text-muted-foreground">PostgreSQL</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
