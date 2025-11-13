'use client'

import { useEffect, useState } from 'react'
import Dashboard from '@/components/Dashboard'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import ContractUpload from '@/components/ContractUpload'
import ContractsList from '@/components/ContractsList'
import ComplianceView from '@/components/ComplianceView'
import ReportsView from '@/components/ReportsView'
import CopilotView from '@/components/CopilotView'

export default function Home() {
  const [activeView, setActiveView] = useState('copilot') // Default to copilot

  // Full-screen copilot view without navigation
  if (activeView === 'copilot') {
    return (
      <div className="h-screen bg-dark-bg overflow-hidden">
        <CopilotView />
      </div>
    )
  }

  // Regular view with sidebar and header
  return (
    <div className="flex h-screen bg-dark-bg relative">
      <Sidebar activeView={activeView} setActiveView={setActiveView} />
      <div className="flex-1 flex flex-col overflow-hidden relative z-10 min-w-0">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 relative z-10">
          {activeView === 'dashboard' && <Dashboard />}
          {activeView === 'contracts' && (
            <div className="space-y-6 fade-in">
              <div className="mb-6">
                <h2 className="text-3xl font-bold text-neon-cyan mb-2">Contracts</h2>
                <p className="text-gray-400 text-sm">Upload and analyze contracts</p>
              </div>
              <ContractUpload />
              <ContractsList />
            </div>
          )}
          {activeView === 'compliance' && (
            <div className="space-y-6 fade-in">
              <div className="mb-6">
                <h2 className="text-3xl font-bold text-neon-cyan mb-2">Compliance</h2>
                <p className="text-gray-400 text-sm">Track regulatory compliance</p>
              </div>
              <ComplianceView />
            </div>
          )}
          {activeView === 'reports' && (
            <div className="space-y-6 fade-in">
              <div className="mb-6">
                <h2 className="text-3xl font-bold text-neon-cyan mb-2">Reports</h2>
                <p className="text-gray-400 text-sm">Generate AI-powered reports</p>
              </div>
              <ReportsView />
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

