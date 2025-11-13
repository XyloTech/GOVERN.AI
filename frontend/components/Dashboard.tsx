'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'
import StatCard from './StatCard'
import ComplianceChart from './ComplianceChart'
import RecentContracts from './RecentContracts'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalContracts: 0,
    activeContracts: 0,
    complianceRate: 0,
    activeAlerts: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    
    // Listen for contract updates
    const handleUpdate = () => {
      fetchDashboardData()
    }
    window.addEventListener('contracts-updated', handleUpdate)
    
    return () => {
      window.removeEventListener('contracts-updated', handleUpdate)
    }
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      // Fetch contracts
      const contractsRes = await axios.get(`${API_URL}/api/v1/contracts/`)
      const contracts = contractsRes.data || []
      
      // Fetch compliance dashboard
      const complianceRes = await axios.get(`${API_URL}/api/v1/compliance/dashboard`)
      const compliance = complianceRes.data || {}

      setStats({
        totalContracts: contracts.length || 0,
        activeContracts: contracts.filter((c: any) => c.status === 'active').length || 0,
        complianceRate: compliance.compliance_rate || 0,
        activeAlerts: compliance.active_alerts || 0,
      })
    } catch (error: any) {
      console.error('Error fetching dashboard data:', error)
      // Set default values on error
      setStats({
        totalContracts: 0,
        activeContracts: 0,
        complianceRate: 0,
        activeAlerts: 0,
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block">
          <div className="text-neon-cyan text-lg animate-glow">Loading system...</div>
          <div className="mt-4 w-64 h-1 bg-dark-border rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-neon-cyan to-neon-blue animate-pulse"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="mb-8 fade-in">
        <h2 className="text-3xl font-bold text-neon-cyan mb-2">
          Dashboard
        </h2>
        <p className="text-gray-400 text-sm">Enterprise governance overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Contracts"
          value={stats.totalContracts}
          icon="▣"
          trend="+12%"
          trendUp={true}
        />
        <StatCard
          title="Active Contracts"
          value={stats.activeContracts}
          icon="◉"
          trend="+5%"
          trendUp={true}
        />
        <StatCard
          title="Compliance Rate"
          value={`${stats.complianceRate.toFixed(1)}%`}
          icon="◈"
          trend="+2.3%"
          trendUp={true}
        />
        <StatCard
          title="Active Alerts"
          value={stats.activeAlerts}
          icon="⚠"
          trend="-3"
          trendUp={false}
        />
      </div>

      {/* Charts and Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ComplianceChart />
        <RecentContracts />
      </div>
    </div>
  )
}

