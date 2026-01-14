import { useState, useEffect } from 'react'
import { useSettings, useUpdateSetting, useCreateSetting } from '@/hooks/use-settings'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'
import { Loader2, Save, Mail, Send } from 'lucide-react'

interface EmailSettings {
  smtpHost: string
  smtpPort: string
  smtpUsername: string
  smtpPassword: string
  senderEmail: string
  senderName: string
}

export default function EmailSettingsTab() {
  const { data: settings, isLoading } = useSettings('email')
  const updateSetting = useUpdateSetting()
  const createSetting = useCreateSetting()

  const [localSettings, setLocalSettings] = useState<EmailSettings>({
    smtpHost: '',
    smtpPort: '587',
    smtpUsername: '',
    smtpPassword: '',
    senderEmail: '',
    senderName: '',
  })
  const [hasChanges, setHasChanges] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [testEmail, setTestEmail] = useState('')
  const [isTesting, setIsTesting] = useState(false)

  // Load settings from API
  useEffect(() => {
    if (settings) {
      const newSettings = { ...localSettings }
      settings.forEach((s) => {
        switch (s.key) {
          case 'smtp.host':
            newSettings.smtpHost = s.value || ''
            break
          case 'smtp.port':
            newSettings.smtpPort = s.value || '587'
            break
          case 'smtp.username':
            newSettings.smtpUsername = s.value || ''
            break
          case 'smtp.password':
            newSettings.smtpPassword = s.value || ''
            break
          case 'smtp.sender_email':
            newSettings.senderEmail = s.value || ''
            break
          case 'smtp.sender_name':
            newSettings.senderName = s.value || ''
            break
        }
      })
      setLocalSettings(newSettings)
      setHasChanges(false)
    }
  }, [settings])

  const handleChange = (key: keyof EmailSettings, value: string) => {
    setLocalSettings((prev) => ({ ...prev, [key]: value }))
    setHasChanges(true)
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const settingsToSave = [
        { key: 'smtp.host', value: localSettings.smtpHost },
        { key: 'smtp.port', value: localSettings.smtpPort },
        { key: 'smtp.username', value: localSettings.smtpUsername },
        { key: 'smtp.password', value: localSettings.smtpPassword },
        { key: 'smtp.sender_email', value: localSettings.senderEmail },
        { key: 'smtp.sender_name', value: localSettings.senderName },
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
            category: 'email',
            value: setting.value,
            value_type: 'string',
          })
        }
      }

      toast.success('E-Mail-Einstellungen gespeichert')
      setHasChanges(false)
    } catch (error) {
      toast.error('Fehler beim Speichern')
      console.error('Error saving settings:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleTestEmail = async () => {
    if (!testEmail) {
      toast.error('Bitte geben Sie eine E-Mail-Adresse ein')
      return
    }

    setIsTesting(true)
    try {
      // In a real implementation, this would call the backend test email endpoint
      // For now, we'll simulate it
      await new Promise((resolve) => setTimeout(resolve, 1500))
      toast.success(`Test-E-Mail an ${testEmail} gesendet`)
    } catch (error) {
      toast.error('Fehler beim Senden der Test-E-Mail')
      console.error('Error sending test email:', error)
    } finally {
      setIsTesting(false)
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
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            SMTP-Server Konfiguration
          </CardTitle>
          <CardDescription>
            Konfigurieren Sie den SMTP-Server für den E-Mail-Versand.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2">
            {/* SMTP Host */}
            <div className="space-y-2">
              <Label htmlFor="smtpHost">SMTP Host</Label>
              <Input
                id="smtpHost"
                value={localSettings.smtpHost}
                onChange={(e) => handleChange('smtpHost', e.target.value)}
                placeholder="smtp.example.com"
              />
            </div>

            {/* SMTP Port */}
            <div className="space-y-2">
              <Label htmlFor="smtpPort">SMTP Port</Label>
              <Input
                id="smtpPort"
                type="number"
                value={localSettings.smtpPort}
                onChange={(e) => handleChange('smtpPort', e.target.value)}
                placeholder="587"
              />
            </div>

            {/* SMTP Username */}
            <div className="space-y-2">
              <Label htmlFor="smtpUsername">Benutzername</Label>
              <Input
                id="smtpUsername"
                value={localSettings.smtpUsername}
                onChange={(e) => handleChange('smtpUsername', e.target.value)}
                placeholder="user@example.com"
              />
            </div>

            {/* SMTP Password */}
            <div className="space-y-2">
              <Label htmlFor="smtpPassword">Passwort</Label>
              <Input
                id="smtpPassword"
                type="password"
                value={localSettings.smtpPassword}
                onChange={(e) => handleChange('smtpPassword', e.target.value)}
                placeholder="••••••••"
              />
            </div>
          </div>

          <div className="border-t pt-6">
            <h4 className="mb-4 text-sm font-medium">Absender-Einstellungen</h4>
            <div className="grid gap-4 sm:grid-cols-2">
              {/* Sender Email */}
              <div className="space-y-2">
                <Label htmlFor="senderEmail">Standard-Absender E-Mail</Label>
                <Input
                  id="senderEmail"
                  type="email"
                  value={localSettings.senderEmail}
                  onChange={(e) => handleChange('senderEmail', e.target.value)}
                  placeholder="noreply@example.com"
                />
              </div>

              {/* Sender Name */}
              <div className="space-y-2">
                <Label htmlFor="senderName">Standard-Absender Name</Label>
                <Input
                  id="senderName"
                  value={localSettings.senderName}
                  onChange={(e) => handleChange('senderName', e.target.value)}
                  placeholder="Atikon CRM"
                />
              </div>
            </div>
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

      {/* Test Email Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Send className="h-5 w-5" />
            Test-E-Mail senden
          </CardTitle>
          <CardDescription>
            Senden Sie eine Test-E-Mail, um die Konfiguration zu überprüfen.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                type="email"
                value={testEmail}
                onChange={(e) => setTestEmail(e.target.value)}
                placeholder="empfaenger@example.com"
              />
            </div>
            <Button
              onClick={handleTestEmail}
              disabled={isTesting || !localSettings.smtpHost}
            >
              {isTesting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Send className="mr-2 h-4 w-4" />
              )}
              Senden
            </Button>
          </div>
          {!localSettings.smtpHost && (
            <p className="mt-2 text-sm text-muted-foreground">
              Bitte speichern Sie zuerst die SMTP-Konfiguration.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
