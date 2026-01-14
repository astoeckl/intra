import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/sonner'
import Layout from '@/components/layout/Layout'
import Dashboard from '@/pages/Dashboard'
import Contacts from '@/pages/Contacts'
import Leads from '@/pages/Leads'
import Tasks from '@/pages/Tasks'
import Callcenter from '@/pages/Callcenter'

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
        </Route>
      </Routes>
      <Toaster position="top-right" />
    </BrowserRouter>
  )
}

export default App
