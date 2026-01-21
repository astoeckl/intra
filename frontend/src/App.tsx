/**
 * Main Application Component
 *
 * Configures React Router with the application's route hierarchy.
 * All main pages are rendered within the Layout component shell.
 *
 * @module App
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/sonner'
import Layout from '@/components/layout/Layout'
import Dashboard from '@/pages/Dashboard'
import Contacts from '@/pages/Contacts'
import Leads from '@/pages/Leads'
import Tasks from '@/pages/Tasks'
import Callcenter from '@/pages/Callcenter'
import Settings from '@/pages/Settings'

/**
 * Root application component with routing configuration.
 *
 * Route structure:
 * - `/` - Dashboard (index route)
 * - `/callcenter` - Call center workspace
 * - `/contacts` - Contact management
 * - `/leads` - Lead management
 * - `/tasks` - Task management
 * - `/settings` - Application settings
 *
 * Includes a global toast notification container positioned at top-right.
 *
 * @returns The root application with router and toast notifications
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="callcenter" element={<Callcenter />} />
          <Route path="contacts" element={<Contacts />} />
          <Route path="leads" element={<Leads />} />
          <Route path="tasks" element={<Tasks />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
      <Toaster position="top-right" />
    </BrowserRouter>
  )
}

export default App
