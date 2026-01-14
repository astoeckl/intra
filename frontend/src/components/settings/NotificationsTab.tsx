import { useState, useEffect } from 'react'
import { useSettings, useUpdateSetting, useCreateSetting } from '@/hooks/use-settings'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'
import { Loader2, Save, Bell } from 'lucide-react'

interface NotificationSettings {
  taskReminderInterval: string
  emailOnTaskAssignment: boolean
  emailOnLeadUpdate: boolean
  emailOnCampaignComplete: boolean
}

export default function NotificationsTab() {
  const { data: settings, isLoading } = useSettings('notifications')
  const updateSetting = useUpdateSetting()
  const createSetting = useCreateSetting()

  const [localSettings, setLocalSettings] = useState<NotificationSettings>({
    taskReminderInterval: '30',
    emailOnTaskAssignment: true,
    emailOnLeadUpdate: false,
    emailOnCampaignComplete: false,
  })
  const [hasChanges, setHasChanges] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  // Load settings from API
  useEffect(() => {
    if (settings) {
      const newSettings = { ...localSettings }
      settings.forEach((s) => {
        switch (s.key) {
          case 'notifications.task_reminder_interval':
            newSettings.taskReminderInterval = s.value || '30'
            break
          case 'notifications.email_on_task_assignment':
            newSettings.emailOnTaskAssignment = s.value === 'true'
            break
          case 'notifications.email_on_lead_update':
            newSettings.emailOnLeadUpdate = s.value === 'true'
            break
          case 'notifications.email_on_campaign_complete':
            newSettings.emailOnCampaignComplete = s.value === 'true'
            break
        }
      })
      setLocalSettings(newSettings)
      setHasChanges(false)
    }
  }, [settings])

  const handleChange = (
    key: keyof NotificationSettings,
    value: string | boolean
  ) => {
    setLocalSettings((prev) => ({ ...prev, [key]: value }))
    setHasChanges(true)
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const settingsToSave = [
        {
          key: 'notifications.task_reminder_interval',
          value: localSettings.taskReminderInterval,
        },
        {
          key: 'notifications.email_on_task_assignment',
          value: String(localSettings.emailOnTaskAssignment),
        },
        {
          key: 'notifications.email_on_lead_update',
          value: String(localSettings.emailOnLeadUpdate),
        },
        {
          key: 'notifications.email_on_campaign_complete',
          value: String(localSettings.emailOnCampaignComplete),
        },
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
            category: 'notifications',
            value: setting.value,
            value_type: setting.key.includes('interval') ? 'number' : 'boolean',
          })
        }
      }

      toast.success('Benachrichtigungseinstellungen gespeichert')
      setHasChanges(false)
    } catch (error) {
      toast.error('Fehler beim Speichern')
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
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Benachrichtigungen
        </CardTitle>
        <CardDescription>
          Konfigurieren Sie Benachrichtigungen und Erinnerungen.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Task Reminder Interval */}
        <div className="space-y-2">
          <Label htmlFor="reminderInterval">
            Aufgaben-Erinnerungsintervall (Minuten)
          </Label>
          <Input
            id="reminderInterval"
            type="number"
            min="5"
            max="1440"
            value={localSettings.taskReminderInterval}
            onChange={(e) =>
              handleChange('taskReminderInterval', e.target.value)
            }
            className="max-w-[200px]"
          />
          <p className="text-xs text-muted-foreground">
            Wie oft sollen Erinnerungen für fällige Aufgaben gesendet werden.
          </p>
        </div>

        {/* Email Notification Toggles */}
        <div className="space-y-4 border-t pt-6">
          <h4 className="text-sm font-medium">E-Mail-Benachrichtigungen</h4>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Bei Aufgabenzuweisung</p>
              <p className="text-xs text-muted-foreground">
                E-Mail senden, wenn eine Aufgabe zugewiesen wird
              </p>
            </div>
            <input
              type="checkbox"
              checked={localSettings.emailOnTaskAssignment}
              onChange={(e) =>
                handleChange('emailOnTaskAssignment', e.target.checked)
              }
              className="h-5 w-5 rounded border-gray-300"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Bei Lead-Aktualisierung</p>
              <p className="text-xs text-muted-foreground">
                E-Mail senden, wenn ein Lead aktualisiert wird
              </p>
            </div>
            <input
              type="checkbox"
              checked={localSettings.emailOnLeadUpdate}
              onChange={(e) =>
                handleChange('emailOnLeadUpdate', e.target.checked)
              }
              className="h-5 w-5 rounded border-gray-300"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Bei Kampagnen-Abschluss</p>
              <p className="text-xs text-muted-foreground">
                E-Mail senden, wenn eine Kampagne abgeschlossen wird
              </p>
            </div>
            <input
              type="checkbox"
              checked={localSettings.emailOnCampaignComplete}
              onChange={(e) =>
                handleChange('emailOnCampaignComplete', e.target.checked)
              }
              className="h-5 w-5 rounded border-gray-300"
            />
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end border-t pt-6">
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
  )
}
