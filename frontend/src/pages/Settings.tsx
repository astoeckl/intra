import { useState } from 'react'
import { Settings as SettingsIcon, List, Mail, Bell, Link } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import GeneralSettingsTab from '@/components/settings/GeneralSettingsTab'
import LookupValuesTab from '@/components/settings/LookupValuesTab'
import EmailSettingsTab from '@/components/settings/EmailSettingsTab'
import NotificationsTab from '@/components/settings/NotificationsTab'
import IntegrationsTab from '@/components/settings/IntegrationsTab'

type SettingsTab = 'general' | 'lookups' | 'email' | 'notifications' | 'integrations'

export default function Settings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('general')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Einstellungen</h1>
        <p className="text-muted-foreground">
          Verwalten Sie die Anwendungseinstellungen und Konfigurationen.
        </p>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as SettingsTab)}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <SettingsIcon className="h-4 w-4" />
            <span className="hidden sm:inline">Allgemein</span>
          </TabsTrigger>
          <TabsTrigger value="lookups" className="flex items-center gap-2">
            <List className="h-4 w-4" />
            <span className="hidden sm:inline">Dropdown-Werte</span>
          </TabsTrigger>
          <TabsTrigger value="email" className="flex items-center gap-2">
            <Mail className="h-4 w-4" />
            <span className="hidden sm:inline">E-Mail/SMTP</span>
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            <span className="hidden sm:inline">Benachrichtigungen</span>
          </TabsTrigger>
          <TabsTrigger value="integrations" className="flex items-center gap-2">
            <Link className="h-4 w-4" />
            <span className="hidden sm:inline">Integrationen</span>
          </TabsTrigger>
        </TabsList>

        {/* General Settings Tab */}
        <TabsContent value="general" className="space-y-4">
          <GeneralSettingsTab />
        </TabsContent>

        {/* Lookup Values Tab */}
        <TabsContent value="lookups" className="space-y-4">
          <LookupValuesTab />
        </TabsContent>

        {/* Email/SMTP Tab */}
        <TabsContent value="email" className="space-y-4">
          <EmailSettingsTab />
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-4">
          <NotificationsTab />
        </TabsContent>

        {/* Integrations Tab */}
        <TabsContent value="integrations" className="space-y-4">
          <IntegrationsTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
