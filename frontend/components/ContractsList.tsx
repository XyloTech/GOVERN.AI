'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'
import { format } from 'date-fns'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ContractsList() {
  const [contracts, setContracts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedContract, setSelectedContract] = useState<any>(null)

  useEffect(() => {
    fetchContracts()
    
    // Listen for contract updates
    const handleUpdate = () => {
      fetchContracts()
    }
    window.addEventListener('contracts-updated', handleUpdate)
    
    return () => {
      window.removeEventListener('contracts-updated', handleUpdate)
    }
  }, [])

  const fetchContracts = async () => {
    try {
      setLoading(true)
      const res = await axios.get(`${API_URL}/api/v1/contracts/`)
      setContracts(res.data || [])
    } catch (error: any) {
      console.error('Error fetching contracts:', error)
      // Show user-friendly error
      if (error.response) {
        console.error('API Error:', error.response.data)
      }
      setContracts([]) // Set empty array on error
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
      terminated: 'bg-red-600/20 text-red-500 border border-red-600/50',
    }
    return colors[status] || 'bg-gray-500/20 text-gray-400 border border-gray-500/50'
  }

  if (loading) {
    return (
      <div className="text-center py-12">
          <div className="text-neon-cyan text-lg animate-glow">Loading contracts...</div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-4">
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-neon-cyan mb-4">
          All Contracts ({contracts.length})
        </h3>
        {contracts.length === 0 ? (
          <div className="text-center py-8 text-gray-400">No contracts found</div>
          ) : (
            <div className="space-y-3">
              {contracts.map((contract) => (
                <div
                  key={contract.id}
                  onClick={() => setSelectedContract(contract)}
                  className={`p-4 border border-dark-border rounded cursor-pointer transition-all ${
                    selectedContract?.id === contract.id
                      ? 'bg-dark-hover border-neon-cyan'
                      : 'hover:bg-dark-hover hover:border-neon-blue'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="font-rajdhani font-semibold text-neon-cyan text-sm mb-1">
                        {contract.title}
                      </h4>
                      <p className="text-xs text-gray-400 font-rajdhani">
                        {contract.party_a} ↔ {contract.party_b}
                      </p>
                      {contract.contract_value && (
                        <p className="text-xs text-neon-green font-orbitron mt-1">
                          ${contract.contract_value.toLocaleString()} {contract.currency}
                        </p>
                      )}
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(contract.status)}`}>
                        {contract.status}
                      </span>
                      {contract.risk_score !== undefined && (
                        <span className={`text-xs font-medium ${
                          contract.risk_score > 70 ? 'text-red-400' :
                          contract.risk_score > 40 ? 'text-yellow-400' :
                          'text-neon-green'
                        }`}>
                          Risk: {contract.risk_score.toFixed(0)}%
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {selectedContract && (
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-neon-cyan mb-4">
            Contract Details
          </h3>
          <div className="space-y-4">
            <div>
              <p className="text-xs text-gray-400 uppercase mb-1">Title</p>
              <p className="text-neon-cyan font-semibold">{selectedContract.title}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 uppercase mb-1">Contract Number</p>
              <p className="text-neon-blue">{selectedContract.contract_number || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 uppercase mb-1">Parties</p>
              <p className="text-neon-blue text-sm">{selectedContract.party_a}</p>
              <p className="text-neon-blue text-sm">{selectedContract.party_b}</p>
            </div>
            {selectedContract.contract_value && (
              <div>
                <p className="text-xs text-gray-400 uppercase mb-1">Value</p>
                <p className="text-neon-green text-xl font-semibold">
                  ${selectedContract.contract_value.toLocaleString()} {selectedContract.currency}
                </p>
              </div>
            )}
            {selectedContract.risk_score !== undefined && (
              <div>
                <p className="text-xs text-gray-400 uppercase mb-1">Risk Score</p>
                <p className={`text-2xl font-bold ${
                  selectedContract.risk_score > 70 ? 'text-red-400' :
                  selectedContract.risk_score > 40 ? 'text-yellow-400' :
                  'text-neon-green'
                }`}>
                  {selectedContract.risk_score.toFixed(1)}%
                </p>
              </div>
            )}
            {selectedContract.expiration_date && (
              <div>
                <p className="text-xs text-gray-400 uppercase mb-1">Expiration</p>
                <p className="text-neon-cyan">
                  {format(new Date(selectedContract.expiration_date), 'MMM dd, yyyy')}
                </p>
              </div>
            )}
            {selectedContract.tags && selectedContract.tags.length > 0 && (
              <div>
                <p className="text-xs text-gray-400 uppercase mb-2">Tags</p>
                <div className="flex flex-wrap gap-2">
                  {selectedContract.tags.map((tag: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50 rounded text-xs font-mono"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

