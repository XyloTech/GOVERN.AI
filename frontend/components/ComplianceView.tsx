'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'
import ComplianceChart from './ComplianceChart'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ComplianceView() {
  const [dashboard, setDashboard] = useState<any>(null)
  const [frameworks, setFrameworks] = useState<any[]>([])
  const [records, setRecords] = useState<any[]>([])
  const [alerts, setAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [dashboardRes, frameworksRes, recordsRes, alertsRes] = await Promise.all([
        axios.get(`${API_URL}/api/v1/compliance/dashboard`),
        axios.get(`${API_URL}/api/v1/compliance/frameworks`),
        axios.get(`${API_URL}/api/v1/compliance/records`),
        axios.get(`${API_URL}/api/v1/compliance/alerts`)
      ])
      setDashboard(dashboardRes.data)
      setFrameworks(frameworksRes.data)
      setRecords(recordsRes.data)
      setAlerts(alertsRes.data)
    } catch (error) {
      console.error('Error fetching compliance data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      compliant: 'bg-neon-green/20 text-neon-green border border-neon-green/50',
      non_compliant: 'bg-red-500/20 text-red-400 border border-red-500/50',
      at_risk: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50',
      pending_review: 'bg-gray-500/20 text-gray-400 border border-gray-500/50',
    }
    return colors[status] || 'bg-gray-500/20 text-gray-400 border border-gray-500/50'
  }

  if (loading) {
    return (
      <div className="text-center py-12">
          <div className="text-neon-cyan text-lg animate-glow">Loading compliance data...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <p className="text-xs font-medium text-gray-400 uppercase mb-2">Total Records</p>
          <p className="text-3xl font-bold text-neon-cyan">{dashboard?.total_records || 0}</p>
        </div>
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <p className="text-xs font-medium text-gray-400 uppercase mb-2">Compliant</p>
          <p className="text-3xl font-bold text-neon-green">{dashboard?.compliant || 0}</p>
        </div>
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <p className="text-xs font-medium text-gray-400 uppercase mb-2">Non-Compliant</p>
          <p className="text-3xl font-bold text-red-400">{dashboard?.non_compliant || 0}</p>
        </div>
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <p className="text-xs font-medium text-gray-400 uppercase mb-2">Active Alerts</p>
          <p className="text-3xl font-bold text-yellow-400">{dashboard?.active_alerts || 0}</p>
        </div>
      </div>

      {/* Chart */}
      <ComplianceChart />

      {/* Frameworks */}
      <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-neon-cyan mb-4">
          Compliance Frameworks
        </h3>
        {frameworks.length === 0 ? (
          <div className="text-center py-8 text-gray-400">No frameworks configured</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {frameworks.map((framework) => (
              <div key={framework.id} className="p-4 bg-dark-bg border border-dark-border rounded-lg">
                <h4 className="font-semibold text-neon-cyan mb-1">{framework.name}</h4>
                <p className="text-xs text-gray-400">{framework.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-neon-cyan mb-4">
          Active Alerts
        </h3>
          <div className="space-y-3">
            {alerts.slice(0, 5).map((alert) => (
              <div key={alert.id} className="p-4 bg-dark-bg border border-dark-border rounded">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-neon-cyan">{alert.title}</h4>
                    <p className="text-xs text-gray-400 mt-1">{alert.message}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    alert.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                    alert.severity === 'high' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {alert.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

