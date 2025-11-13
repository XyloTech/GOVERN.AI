'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'
import { format } from 'date-fns'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function RecentContracts() {
  const [contracts, setContracts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchContracts()
  }, [])

  const fetchContracts = async () => {
    try {
      setLoading(true)
      const res = await axios.get(`${API_URL}/api/v1/contracts/?limit=5`)
      setContracts(res.data || [])
    } catch (error: any) {
      console.error('Error fetching contracts:', error)
      setContracts([])
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-neon-green/20 text-neon-green border border-neon-green/50',
      expired: 'bg-red-500/20 text-red-400 border border-red-500/50',
      draft: 'bg-gray-500/20 text-gray-400 border border-gray-500/50',
      pending_renewal: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50',
    }
    return colors[status] || 'bg-gray-500/20 text-gray-400 border border-gray-500/50'
  }

  if (loading) {
    return (
      <div className="bg-dark-surface border border-dark-border rounded-lg p-6 relative">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-30"></div>
        <h3 className="text-lg font-semibold text-neon-cyan mb-4">Recent Contracts</h3>
        <div className="text-center py-8 text-gray-400">Loading...</div>
      </div>
    )
  }

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg p-6 relative hover:border-neon-cyan transition-all duration-300">
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-30"></div>
      <h3 className="text-lg font-semibold text-neon-cyan mb-6">Recent Contracts</h3>
      {contracts.length === 0 ? (
        <div className="text-center py-8 text-gray-400">No contracts found</div>
      ) : (
        <div className="space-y-4">
          {contracts.map((contract) => (
            <div key={contract.id} className="border-b border-dark-border pb-4 last:border-0 last:pb-0 hover:bg-dark-hover transition-colors rounded px-2 py-2 -mx-2">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="font-semibold text-neon-cyan text-sm">{contract.title}</h4>
                  <p className="text-xs text-gray-400 mt-1">
                    {contract.party_a} ↔ {contract.party_b}
                  </p>
                  {contract.created_at && (
                    <p className="text-xs text-gray-500 mt-1">
                      {format(new Date(contract.created_at), 'MMM dd, yyyy')}
                    </p>
                  )}
                </div>
                <span className={`px-3 py-1 rounded text-xs font-medium ${getStatusColor(contract.status)}`}>
                  {contract.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

