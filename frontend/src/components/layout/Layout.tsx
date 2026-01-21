/**
 * Layout Component Module
 *
 * Provides the main application shell structure with sidebar navigation,
 * header, and content area. Uses React Router's Outlet for nested routing.
 *
 * @module components/layout/Layout
 */
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

/**
 * Main layout wrapper component for the application.
 *
 * Renders a three-part layout:
 * - Fixed sidebar navigation on the left
 * - Header bar at the top of the main content area
 * - Scrollable main content area using React Router's Outlet
 *
 * @returns The application layout shell
 */
export default function Layout() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
