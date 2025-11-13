'use client'

import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface UploadFilters {
  status?: string
  contract_type?: string
  min_risk_score?: number
  max_risk_score?: number
  min_contract_value?: number
  max_contract_value?: number
  currency?: string
  tags?: string[]
}

export default function ContractUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<UploadFilters>({
    status: '',
    contract_type: '',
    min_risk_score: undefined,
    max_risk_score: undefined,
    min_contract_value: undefined,
    max_contract_value: undefined,
    currency: 'USD',
    tags: []
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setResult(null)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      // Add filter metadata
      if (filters.status) formData.append('status', filters.status)
      if (filters.contract_type) formData.append('contract_type', filters.contract_type)
      if (filters.min_risk_score !== undefined) formData.append('min_risk_score', filters.min_risk_score.toString())
      if (filters.max_risk_score !== undefined) formData.append('max_risk_score', filters.max_risk_score.toString())
      if (filters.min_contract_value !== undefined) formData.append('min_contract_value', filters.min_contract_value.toString())
      if (filters.max_contract_value !== undefined) formData.append('max_contract_value', filters.max_contract_value.toString())
      if (filters.currency) formData.append('currency', filters.currency)
      if (filters.tags && filters.tags.length > 0) {
        formData.append('tags', JSON.stringify(filters.tags))
      }

      const response = await axios.post(
        `${API_URL}/api/v1/contracts/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      setResult(response.data)
      setFile(null)
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      // Reset filters
      setFilters({
        status: '',
        contract_type: '',
        min_risk_score: undefined,
        max_risk_score: undefined,
        min_contract_value: undefined,
        max_contract_value: undefined,
        currency: 'USD',
        tags: []
      })
      // Trigger refresh of contracts list
      window.dispatchEvent(new Event('contracts-updated'))
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg p-6 relative hover:border-neon-cyan transition-all duration-300">
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-30"></div>
      
      <h3 className="text-xl font-bold text-neon-cyan mb-6">
        Upload Contract
      </h3>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Select Document
          </label>
          <div className="border border-dark-border rounded p-4 hover:border-neon-cyan transition-colors">
            <input
              id="file-input"
              type="file"
              accept=".pdf,.docx,.doc,.txt"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-rajdhani file:bg-neon-cyan/20 file:text-neon-cyan hover:file:bg-neon-cyan/30 file:cursor-pointer cursor-pointer"
            />
            {file && (
              <p className="mt-2 text-xs text-neon-green font-orbitron">
                Selected: {file.name}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="px-4 py-2 text-sm text-neon-cyan border border-neon-cyan/30 rounded-lg hover:bg-neon-cyan/10 transition-all"
          >
            {showFilters ? 'Hide Filters' : 'Show Filters'} {showFilters ? '▲' : '▼'}
          </button>
        </div>

        {showFilters && (
          <div className="border border-dark-border rounded-lg p-4 bg-dark-bg space-y-4">
            <h4 className="text-sm font-semibold text-neon-cyan mb-3">Upload Filters & Metadata</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Status</label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => setFilters({...filters, status: e.target.value})}
                  className="w-full px-3 py-2 bg-dark-surface border border-dark-border rounded text-sm text-gray-300 focus:border-neon-cyan focus:outline-none"
                >
                  <option value="">Any</option>
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                  <option value="expired">Expired</option>
                  <option value="terminated">Terminated</option>
                  <option value="pending_renewal">Pending Renewal</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-gray-400 mb-1">Contract Type</label>
                <select
                  value={filters.contract_type || ''}
                  onChange={(e) => setFilters({...filters, contract_type: e.target.value})}
                  className="w-full px-3 py-2 bg-dark-surface border border-dark-border rounded text-sm text-gray-300 focus:border-neon-cyan focus:outline-none"
                >
                  <option value="">Any</option>
                  <option value="supplier">Supplier</option>
                  <option value="customer">Customer</option>
                  <option value="partnership">Partnership</option>
                  <option value="employment">Employment</option>
                  <option value="nda">NDA</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-gray-400 mb-1">Min Risk Score</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={filters.min_risk_score || ''}
                  onChange={(e) => setFilters({...filters, min_risk_score: e.target.value ? parseFloat(e.target.value) : undefined})}
                  className="w-full px-3 py-2 bg-dark-surface border border-dark-border rounded text-sm text-gray-300 focus:border-neon-cyan focus:outline-none"
                  placeholder="0"
                />
              </div>

              <div>
                <label className="block text-xs text-gray-400 mb-1">Max Risk Score</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={filters.max_risk_score || ''}
                  onChange={(e) => setFilters({...filters, max_risk_score: e.target.value ? parseFloat(e.target.value) : undefined})}
                  className="w-full px-3 py-2 bg-dark-surface border border-dark-border rounded text-sm text-gray-300 focus:border-neon-cyan focus:outline-none"
                  placeholder="100"
                />
              </div>

              <div>
                <label className="block text-xs text-gray-400 mb-1">Min Contract Value</label>
                <input
                  type="number"
                  min="0"
                  value={filters.min_contract_value || ''}
                  onChange={(e) => setFilters({...filters, min_contract_value: e.target.value ? parseFloat(e.target.value) : undefined})}
                  className="w-full px-3 py-2 bg-dark-surface border border-dark-border rounded text-sm text-gray-300 focus:border-neon-cyan focus:outline-none"
                  placeholder="0"
                />
              </div>

              <div>
                <label className="block text-xs text-gray-400 mb-1">Max Contract Value</label>
                <input
                  type="number"
                  min="0"
                  value={filters.max_contract_value || ''}
                  onChange={(e) => setFilters({...filters, max_contract_value: e.target.value ? parseFloat(e.target.value) : undefined})}
                  className="w-full px-3 py-2 bg-dark-surface border border-dark-border rounded text-sm text-gray-300 focus:border-neon-cyan focus:outline-none"
                  placeholder="No limit"
                />
              </div>

              <div>
                <label className="block text-xs text-gray-400 mb-1">Currency</label>
                <select
                  value={filters.currency || 'USD'}
                  onChange={(e) => setFilters({...filters, currency: e.target.value})}
                  className="w-full px-3 py-2 bg-dark-surface border border-dark-border rounded text-sm text-gray-300 focus:border-neon-cyan focus:outline-none"
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="INR">INR</option>
                  <option value="JPY">JPY</option>
                </select>
              </div>
            </div>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full py-3 px-4 bg-gradient-to-r from-neon-cyan to-neon-blue text-dark-bg font-semibold rounded-lg hover:shadow-lg hover:shadow-neon-cyan/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? 'Processing...' : 'Upload & Analyze'}
        </button>

        {error && (
          <div className="p-4 bg-red-500/20 border border-red-500/50 rounded">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {result && (
          <div className="mt-6 space-y-4">
            <div className="p-4 bg-neon-green/10 border border-neon-green/50 rounded-lg">
              <p className="text-neon-green font-semibold mb-2">✓ Contract Analyzed</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-dark-bg border border-dark-border rounded-lg">
                <p className="text-xs text-gray-400 uppercase mb-1">Title</p>
                <p className="text-neon-cyan font-semibold">{result.title}</p>
              </div>

              <div className="p-4 bg-dark-bg border border-dark-border rounded-lg">
                <p className="text-xs text-gray-400 uppercase mb-1">Contract Number</p>
                <p className="text-neon-cyan">{result.contract_number || 'N/A'}</p>
              </div>

              <div className="p-4 bg-dark-bg border border-dark-border rounded-lg">
                <p className="text-xs text-gray-400 uppercase mb-1">Status</p>
                <p className="text-neon-green font-semibold">{result.status}</p>
              </div>

              <div className="p-4 bg-dark-bg border border-dark-border rounded-lg">
                <p className="text-xs text-gray-400 uppercase mb-1">Risk Score</p>
                <p className="text-neon-cyan text-2xl font-bold">{result.risk_score?.toFixed(1)}%</p>
              </div>

              <div className="p-4 bg-dark-bg border border-dark-border rounded-lg">
                <p className="text-xs text-gray-400 uppercase mb-1">Party A</p>
                <p className="text-neon-blue">{result.party_a}</p>
              </div>

              <div className="p-4 bg-dark-bg border border-dark-border rounded-lg">
                <p className="text-xs text-gray-400 uppercase mb-1">Party B</p>
                <p className="text-neon-blue">{result.party_b}</p>
              </div>

              {result.contract_value && (
                <div className="p-4 bg-dark-bg border border-dark-border rounded-lg">
                  <p className="text-xs text-gray-400 uppercase mb-1">Contract Value</p>
                  <p className="text-neon-green font-semibold">${result.contract_value.toLocaleString()} {result.currency}</p>
                </div>
              )}

              {result.expiration_date && (
                <div className="p-4 bg-dark-bg border border-dark-border rounded-lg">
                  <p className="text-xs text-gray-400 uppercase mb-1">Expiration Date</p>
                  <p className="text-neon-cyan">
                    {new Date(result.expiration_date).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>

            {result.risk_factors && result.risk_factors.length > 0 && (
              <div className="p-4 bg-dark-bg border border-dark-border rounded-lg">
                <p className="text-xs text-gray-400 uppercase mb-2">Risk Factors</p>
                <ul className="space-y-1">
                  {result.risk_factors.map((factor: string, idx: number) => (
                    <li key={idx} className="text-neon-blue text-sm">
                      • {factor}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {result.tags && result.tags.length > 0 && (
              <div className="p-4 bg-dark-bg border border-dark-border rounded-lg">
                <p className="text-xs text-gray-400 uppercase mb-2">Tags</p>
                <div className="flex flex-wrap gap-2">
                  {result.tags.map((tag: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50 rounded text-xs font-mono"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

