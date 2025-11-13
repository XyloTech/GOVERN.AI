'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  timestamp?: Date
  data?: any // For structured data like contracts, compliance, etc.
  file?: {
    name: string
    size: number
    type: string
  }
  uploadResult?: any
}

interface Filters {
  contracts: {
    status?: string
    contract_type?: string
    min_risk_score?: number
    max_risk_score?: number
    min_contract_value?: number
    max_contract_value?: number
  }
  compliance: {
    framework_id?: number
    status?: string
  }
  reports: {
    report_type?: string
  }
  dashboard: {
    period_start?: string
    period_end?: string
  }
}

// Simple markdown-like text formatter
const formatMessage = (text: string) => {
  let formatted = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code class="bg-dark-bg px-1.5 py-0.5 rounded text-neon-cyan font-mono text-sm">$1</code>')
    .replace(/```([\s\S]*?)```/g, '<pre class="bg-dark-bg p-3 rounded-lg border border-dark-border overflow-x-auto my-2"><code class="text-neon-cyan font-mono text-sm">$1</code></pre>')
    .replace(/\n/g, '<br />')
  
  return formatted
}

export default function CopilotView() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [streamingText, setStreamingText] = useState('')
  const [showHelp, setShowHelp] = useState(false)
  const [showPayment, setShowPayment] = useState(false)
  const [queryCount, setQueryCount] = useState(0)
  const [isPaid, setIsPaid] = useState(false)
  const [filters] = useState<Filters>({
    contracts: {},
    compliance: {},
    reports: {},
    dashboard: {}
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [dragActive, setDragActive] = useState(false)

  // Load usage count from localStorage
  useEffect(() => {
    const savedCount = localStorage.getItem('governai_query_count')
    const savedPaid = localStorage.getItem('governai_paid')
    if (savedCount) {
      setQueryCount(parseInt(savedCount))
    }
    if (savedPaid === 'true') {
      setIsPaid(true)
    }
  }, [])


  // Save usage count to localStorage
  const incrementQueryCount = () => {
    const newCount = queryCount + 1
    setQueryCount(newCount)
    localStorage.setItem('governai_query_count', newCount.toString())
    
    // Show payment prompt after 5 queries if not paid
    if (newCount >= 5 && !isPaid) {
      setShowPayment(true)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const applyFiltersAndQuery = async (query: string) => {
    // Build context with filters
    const context: any = {
      filters: filters
    }

    try {
      const response = await axios.post(`${API_URL}/api/v1/copilot/query`, {
        query: query,
        context: context
      })

      // Response structure: { query, response: { answer, sources, data }, sources, data }
      const responseData = response.data.response || {}
      
      let assistantMessage: Message = {
        role: 'assistant',
        content: responseData.answer || response.data.answer || 'No response received',
        sources: response.data.sources || responseData.sources || [],
        timestamp: new Date()
      }

      // If response includes structured data, add it
      if (response.data.data || responseData.data) {
        assistantMessage.data = response.data.data || responseData.data
      }

      return assistantMessage
    } catch (error: any) {
      throw error
    }
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return

    // Check if user has reached limit and not paid
    if (queryCount >= 5 && !isPaid) {
      setShowPayment(true)
      return
    }

    const userMessage: Message = { 
      role: 'user', 
      content: input.trim(),
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    const currentInput = input.trim()
    setInput('')
    setLoading(true)
    setStreamingText('')

    // Increment query count (only for actual queries, not uploads)
    incrementQueryCount()

    try {
      const assistantMessage = await applyFiltersAndQuery(currentInput)
      
      // Simulate streaming effect for better UX
      if (assistantMessage.content) {
        const words = assistantMessage.content.split(' ')
        let currentText = ''
        
        // Show streaming text
        for (let i = 0; i < words.length; i++) {
          currentText += (i > 0 ? ' ' : '') + words[i]
          setStreamingText(currentText)
          await new Promise(resolve => setTimeout(resolve, 20))
        }
        
        // Small delay before finalizing
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
      setMessages(prev => [...prev, assistantMessage])
      setStreamingText('')
    } catch (error: any) {
      console.error('Error:', error)
      let errorMessage = 'I encountered an issue processing your request.'
      
      if (error.code === 'ERR_NETWORK' || error.message?.includes('Network')) {
        errorMessage = '**Connection Error**\n\nI couldn\'t reach the server. Please check:\n- The backend server is running on port 8000\n- Your internet connection is stable\n- Try again in a moment'
      } else if (error.response?.status === 500) {
        errorMessage = '**Server Error**\n\nThe server encountered an issue. Please try again or contact support if the problem persists.'
      } else if (error.response?.data?.detail) {
        errorMessage = `**Error**\n\n${error.response.data.detail}`
      } else if (error.message) {
        errorMessage = `**Error**\n\n${error.message}`
      }
      
      const errorMsg: Message = {
        role: 'assistant',
        content: errorMessage,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMsg])
      setStreamingText('')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleQuickQuery = async (query: string) => {
    setInput(query)
    // Auto-send after a brief delay
    setTimeout(() => {
      handleSend()
    }, 100)
  }

  const handleFileUpload = async (file: File) => {
    if (!file) return

    // Check if user has reached limit and not paid
    if (queryCount >= 5 && !isPaid) {
      setShowPayment(true)
      return
    }

    // Add user message showing file being uploaded
    const userMessage: Message = {
      role: 'user',
      content: `📄 Uploading: ${file.name}`,
      file: {
        name: file.name,
        size: file.size,
        type: file.type
      },
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setUploading(true)
    setUploadProgress(0)

    // Increment query count for uploads too
    incrementQueryCount()

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      // Add filter metadata if available
      if (filters.contracts.status) formData.append('status', filters.contracts.status)
      if (filters.contracts.contract_type) formData.append('contract_type', filters.contracts.contract_type)
      if (filters.contracts.min_risk_score !== undefined) formData.append('min_risk_score', filters.contracts.min_risk_score.toString())
      if (filters.contracts.max_risk_score !== undefined) formData.append('max_risk_score', filters.contracts.max_risk_score.toString())
      if (filters.contracts.min_contract_value !== undefined) formData.append('min_contract_value', filters.contracts.min_contract_value.toString())
      if (filters.contracts.max_contract_value !== undefined) formData.append('max_contract_value', filters.contracts.max_contract_value.toString())

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      const response = await axios.post(
        `${API_URL}/api/v1/contracts/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              setUploadProgress(percentCompleted)
            }
          }
        }
      )

      clearInterval(progressInterval)
      setUploadProgress(100)

      // Create assistant message with upload results
      const contract = response.data
      const resultMessage: Message = {
        role: 'assistant',
        content: `✅ **Contract Uploaded Successfully!**\n\n**Title:** ${contract.title}\n**Contract Number:** ${contract.contract_number || 'N/A'}\n**Status:** ${contract.status}\n**Type:** ${contract.type}\n**Risk Score:** ${contract.risk_score?.toFixed(1)}%\n**Parties:** ${contract.party_a} ↔ ${contract.party_b}${contract.contract_value ? `\n**Value:** ${contract.currency || 'USD'} ${contract.contract_value.toLocaleString()}` : ''}${contract.expiration_date ? `\n**Expiration:** ${new Date(contract.expiration_date).toLocaleDateString()}` : ''}\n\nContract has been analyzed and added to your system.`,
        uploadResult: contract,
        timestamp: new Date()
      }

      // Show streaming effect
      if (resultMessage.content) {
        const words = resultMessage.content.split(' ')
        let currentText = ''
        
        for (let i = 0; i < words.length; i++) {
          currentText += (i > 0 ? ' ' : '') + words[i]
          setStreamingText(currentText)
          await new Promise(resolve => setTimeout(resolve, 15))
        }
        
        await new Promise(resolve => setTimeout(resolve, 100))
      }

      setMessages(prev => [...prev, resultMessage])
      setStreamingText('')
      
      // Trigger refresh
      window.dispatchEvent(new Event('contracts-updated'))
    } catch (error: any) {
      console.error('Upload error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: `❌ **Upload Failed**\n\n${error.response?.data?.detail || error.message || 'Failed to upload contract. Please try again.'}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setUploading(false)
      setUploadProgress(0)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0])
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0])
    }
  }

  const renderDataCard = (data: any, title: string) => {
    if (!data) return null

    // Render Contracts
    if (data.contracts && Array.isArray(data.contracts)) {
      return (
        <div className="mt-4 p-4 bg-dark-surface border border-dark-border rounded-lg">
          <h4 className="text-sm font-semibold text-neon-cyan mb-3 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Contracts ({data.contracts.length})
          </h4>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {data.contracts.map((contract: any, idx: number) => (
              <div key={idx} className="p-3 bg-dark-bg rounded-lg border border-dark-border hover:border-neon-cyan/30 transition-all">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h5 className="text-sm font-semibold text-neon-cyan mb-1">{contract.title || 'Untitled Contract'}</h5>
                    {contract.contract_number && (
                      <p className="text-xs text-gray-400 font-mono">#{contract.contract_number}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      contract.status === 'active' ? 'bg-neon-green/20 text-neon-green' :
                      contract.status === 'expired' ? 'bg-red-500/20 text-red-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {contract.status}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      contract.risk_score > 70 ? 'text-red-400' :
                      contract.risk_score > 40 ? 'text-yellow-400' :
                      'text-neon-green'
                    }`}>
                      {contract.risk_score?.toFixed(0) || 0}%
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs mt-2">
                  <div>
                    <span className="text-gray-400">Type:</span>
                    <span className="ml-2 text-gray-300 capitalize">{contract.type || 'other'}</span>
                  </div>
                  {contract.contract_value && (
                    <div>
                      <span className="text-gray-400">Value:</span>
                      <span className="ml-2 text-neon-green font-semibold">
                        ${contract.contract_value.toLocaleString()}
                      </span>
                    </div>
                  )}
                  <div className="col-span-2">
                    <span className="text-gray-400">Parties:</span>
                    <span className="ml-2 text-gray-300">{contract.party_a} ↔ {contract.party_b}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    }

    // Render Compliance Records
    if (data.compliance && Array.isArray(data.compliance)) {
      return (
        <div className="mt-4 p-4 bg-dark-surface border border-dark-border rounded-lg">
          <h4 className="text-sm font-semibold text-neon-cyan mb-3 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Compliance Records ({data.compliance.length})
          </h4>
          <div className="space-y-2">
            {data.compliance.map((record: any, idx: number) => (
              <div key={idx} className="p-3 bg-dark-bg rounded-lg border border-dark-border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-300">Record #{record.id}</p>
                    <p className="text-xs text-gray-400 mt-1">Framework ID: {record.framework_id || 'N/A'}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    record.status === 'compliant' ? 'bg-neon-green/20 text-neon-green' :
                    record.status === 'non_compliant' ? 'bg-red-500/20 text-red-400' :
                    'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {record.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    }

    // Render Reports
    if (data.reports && Array.isArray(data.reports)) {
      const handleDownload = async (reportId: number, format: string = 'json') => {
        try {
          const response = await axios.get(
            `${API_URL}/api/v1/reports/${reportId}/download?format=${format}`,
            {
              responseType: format === 'json' ? 'json' : 'blob',
            }
          )
          
          if (format === 'json') {
            // Download as JSON
            const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `${response.data.title || 'report'}.json`
            document.body.appendChild(a)
            a.click()
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)
          } else {
            // Download as PDF/Excel
            const blob = new Blob([response.data], { type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `report_${reportId}.${format}`
            document.body.appendChild(a)
            a.click()
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)
          }
        } catch (error: any) {
          console.error('Download error:', error)
          alert(`Failed to download report: ${error.message}`)
        }
      }

      return (
        <div className="mt-4 p-4 bg-dark-surface border border-dark-border rounded-lg">
          <h4 className="text-sm font-semibold text-neon-cyan mb-3 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Reports ({data.reports.length})
          </h4>
          <div className="space-y-3">
            {data.reports.map((report: any, idx: number) => (
              <div key={idx} className="p-3 bg-dark-bg rounded-lg border border-dark-border hover:border-neon-cyan/30 transition-all">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h5 className="text-sm font-semibold text-gray-300 mb-1">{report.title || 'Untitled Report'}</h5>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="px-2 py-0.5 bg-neon-blue/20 text-neon-blue border border-neon-blue/50 rounded text-xs">
                        {report.type || 'general'}
                      </span>
                      {report.created_at && (
                        <span className="text-xs text-gray-400">
                          {new Date(report.created_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-3 pt-3 border-t border-dark-border">
                  <button
                    onClick={() => handleDownload(report.id, 'json')}
                    className="px-3 py-1.5 bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50 rounded text-xs hover:bg-neon-cyan/30 transition-all flex items-center gap-1"
                    title="Download as JSON"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Download JSON
                  </button>
                  <button
                    onClick={() => handleDownload(report.id, 'pdf')}
                    className="px-3 py-1.5 bg-dark-surface text-gray-400 border border-dark-border rounded text-xs hover:border-neon-cyan/50 hover:text-neon-cyan transition-all flex items-center gap-1"
                    title="Download as PDF"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    Download PDF
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    }

    // Render Dashboard Data
    if (data.dashboard) {
      return (
        <div className="mt-4 p-4 bg-dark-surface border border-dark-border rounded-lg">
          <h4 className="text-sm font-semibold text-neon-cyan mb-3 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Dashboard Summary
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
              <p className="text-xs text-gray-400 mb-1">Total Contracts</p>
              <p className="text-xl font-bold text-neon-cyan">{data.dashboard.total_contracts || 0}</p>
              <p className="text-xs text-gray-500 mt-1">{data.dashboard.active_contracts || 0} active</p>
            </div>
            <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
              <p className="text-xs text-gray-400 mb-1">Compliance Rate</p>
              <p className="text-xl font-bold text-neon-green">
                {data.dashboard.compliance_rate?.toFixed(1) || 0}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {data.dashboard.compliant_records || 0} / {data.dashboard.total_compliance_records || 0}
              </p>
            </div>
            <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
              <p className="text-xs text-gray-400 mb-1">Compliance Records</p>
              <p className="text-xl font-bold text-neon-blue">
                {data.dashboard.total_compliance_records || 0}
              </p>
            </div>
            <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
              <p className="text-xs text-gray-400 mb-1">Total Reports</p>
              <p className="text-xl font-bold text-neon-purple">
                {data.dashboard.total_reports || 0}
              </p>
            </div>
          </div>
        </div>
      )
    }

    // Fallback for other data types
    return (
      <div className="mt-4 p-4 bg-dark-surface border border-dark-border rounded-lg">
        <h4 className="text-sm font-semibold text-neon-cyan mb-3">{title}</h4>
        <pre className="text-xs text-gray-300 overflow-x-auto bg-dark-bg p-3 rounded">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full max-h-screen bg-dark-bg">
      {/* Top Bar - Minimal Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-dark-border bg-dark-surface">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-neon-cyan to-neon-blue flex items-center justify-center">
            <svg className="w-6 h-6 text-dark-bg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-neon-cyan">GovernAI Copilot</h1>
            <p className="text-xs text-gray-400">Natural language querying for Contracts, Compliance, Reports & Dashboard</p>
          </div>
        </div>
        <button
          onClick={() => setShowHelp(!showHelp)}
          className="px-4 py-2 text-sm text-neon-cyan border border-neon-cyan/30 rounded-lg hover:bg-neon-cyan/10 transition-all flex items-center gap-2"
          title="Show help and usage guide"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {showHelp ? 'Hide Help' : 'Help'}
        </button>
      </div>

      {/* Help Panel */}
      {showHelp && (
        <div className="border-b border-dark-border bg-dark-surface px-6 py-6 max-h-[60vh] overflow-y-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-neon-cyan flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                How to Use GovernAI Copilot
              </h2>
              <button
                onClick={() => setShowHelp(false)}
                className="text-gray-400 hover:text-neon-cyan transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Feature Categories */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Contracts Section */}
              <div className="bg-dark-bg border border-dark-border rounded-xl p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-neon-cyan/20 flex items-center justify-center">
                    <svg className="w-6 h-6 text-neon-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-neon-cyan">Contracts</h3>
                    <p className="text-xs text-gray-400">Upload, analyze, and query contracts</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-gray-300 space-y-1">
                    <p className="font-medium text-neon-cyan mb-2">Example Queries:</p>
                    <ul className="space-y-1 ml-4 list-disc">
                      <li>"Show me all active contracts"</li>
                      <li>"List contracts with high risk scores"</li>
                      <li>"Show contracts expiring soon"</li>
                      <li>"What contracts have risk score above 50?"</li>
                    </ul>
                  </div>
                  <div className="mt-3 pt-3 border-t border-dark-border">
                    <p className="text-xs text-gray-400">
                      <strong className="text-neon-cyan">💡 Upload:</strong> Drag & drop contract files or click the upload button (📎) to analyze contracts automatically.
                    </p>
                  </div>
                </div>
              </div>

              {/* Compliance Section */}
              <div className="bg-dark-bg border border-dark-border rounded-xl p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-neon-green/20 flex items-center justify-center">
                    <svg className="w-6 h-6 text-neon-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-neon-green">Compliance</h3>
                    <p className="text-xs text-gray-400">Track regulatory compliance and frameworks</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-gray-300 space-y-1">
                    <p className="font-medium text-neon-green mb-2">Example Queries:</p>
                    <ul className="space-y-1 ml-4 list-disc">
                      <li>"What is our compliance rate?"</li>
                      <li>"Show compliance dashboard"</li>
                      <li>"List all non-compliant records"</li>
                      <li>"Show GDPR compliance status"</li>
                    </ul>
                  </div>
                  <div className="mt-3 pt-3 border-t border-dark-border">
                    <p className="text-xs text-gray-400">
                      <strong className="text-neon-green">💡 Filters:</strong> Use filters to check specific compliance frameworks (GDPR, ISO, SOC2, HIPAA, etc.)
                    </p>
                  </div>
                </div>
              </div>

              {/* Reports Section */}
              <div className="bg-dark-bg border border-dark-border rounded-xl p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-neon-blue/20 flex items-center justify-center">
                    <svg className="w-6 h-6 text-neon-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-neon-blue">Reports</h3>
                    <p className="text-xs text-gray-400">Generate and download AI-powered reports</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-gray-300 space-y-1">
                    <p className="font-medium text-neon-blue mb-2">Example Queries:</p>
                    <ul className="space-y-1 ml-4 list-disc">
                      <li>"Show all available reports"</li>
                      <li>"Generate a financial report"</li>
                      <li>"Generate operational report"</li>
                      <li>"List reports by type"</li>
                    </ul>
                  </div>
                  <div className="mt-3 pt-3 border-t border-dark-border">
                    <p className="text-xs text-gray-400">
                      <strong className="text-neon-blue">💡 Download:</strong> Click "Download JSON" or "Download PDF" buttons on any report to save it.
                    </p>
                  </div>
                </div>
              </div>

              {/* Dashboard Section */}
              <div className="bg-dark-bg border border-dark-border rounded-xl p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-neon-purple/20 flex items-center justify-center">
                    <svg className="w-6 h-6 text-neon-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-neon-purple">Dashboard</h3>
                    <p className="text-xs text-gray-400">View overall statistics and summaries</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-gray-300 space-y-1">
                    <p className="font-medium text-neon-purple mb-2">Example Queries:</p>
                    <ul className="space-y-1 ml-4 list-disc">
                      <li>"Show dashboard summary"</li>
                      <li>"What are the main risk factors?"</li>
                      <li>"Show overall statistics"</li>
                      <li>"Get KPI overview"</li>
                    </ul>
                  </div>
                  <div className="mt-3 pt-3 border-t border-dark-border">
                    <p className="text-xs text-gray-400">
                      <strong className="text-neon-purple">💡 Filters:</strong> Use date filters to view dashboard data for specific periods.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Tips */}
            <div className="mt-6 bg-dark-bg border border-dark-border rounded-xl p-4">
              <h4 className="text-sm font-semibold text-neon-cyan mb-3 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Quick Tips
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-gray-400">
                <div>
                  <strong className="text-neon-cyan block mb-1">📄 Upload Contracts</strong>
                  <p>Drag & drop files or click the upload button (📎). Contracts are automatically analyzed with AI.</p>
                </div>
                <div>
                  <strong className="text-neon-green block mb-1">🔍 Use Filters</strong>
                  <p>Click "Show Filters" to refine queries by status, type, risk score, dates, compliance frameworks, etc.</p>
                </div>
                <div>
                  <strong className="text-neon-blue block mb-1">💬 Natural Language</strong>
                  <p>Ask questions in plain English. The AI understands context and applies your active filters automatically.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="mb-6">
              <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-neon-cyan/20 to-neon-blue/20 flex items-center justify-center border border-neon-cyan/30">
                <svg className="w-10 h-10 text-neon-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
            </div>
            <h2 className="text-3xl font-semibold text-gray-100 mb-2">GovernAI Copilot</h2>
            <p className="text-gray-400 text-sm mb-8 max-w-md">
              Ask me anything about your contracts, compliance, reports, and dashboard. Use filters to refine your queries.
            </p>
            
            {/* Simple Example Queries */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-3xl w-full">
              {[
                'Show me all active contracts',
                'What is our compliance rate?',
                'Show all available reports',
                'Show dashboard summary'
              ].map((query, idx) => (
                <button
                  key={idx}
                  onClick={() => handleQuickQuery(query)}
                  className="px-4 py-3 bg-dark-surface border border-dark-border rounded-xl text-sm text-gray-300 hover:border-neon-cyan/50 hover:bg-dark-surface/80 transition-all text-left group"
                >
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-gray-500 group-hover:text-neon-cyan transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <span>{query}</span>
                  </div>
                </button>
              ))}
            </div>
            
            <p className="text-xs text-gray-500 mt-6 text-center">
              Click the <strong className="text-neon-cyan">Help</strong> button above to see detailed usage guide for Contracts, Compliance, Reports & Dashboard
            </p>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex gap-4 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-neon-cyan to-neon-blue flex items-center justify-center mt-1">
                    <svg className="w-5 h-5 text-dark-bg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                )}
                
                <div className={`flex flex-col ${
                  message.role === 'user' ? 'items-end max-w-[80%]' : 'items-start max-w-[85%]'
                } animate-fade-in`}>
                  <div className={`rounded-2xl px-4 py-3 shadow-lg transition-all duration-300 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-br from-neon-cyan to-neon-blue text-dark-bg rounded-tr-sm hover:shadow-neon-cyan/30'
                      : 'bg-dark-surface border border-dark-border text-gray-100 rounded-tl-sm hover:border-neon-cyan/50'
                  }`}>
                    {message.file && (
                      <div className="mb-2 flex items-center gap-2 text-sm opacity-90">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span>{message.file.name}</span>
                        <span className="text-xs opacity-75">({(message.file.size / 1024).toFixed(1)} KB)</span>
                      </div>
                    )}
                    <div 
                      className="prose prose-invert max-w-none leading-relaxed"
                      dangerouslySetInnerHTML={{ 
                        __html: formatMessage(message.content) 
                      }}
                    />
                    {message.uploadResult && (
                      <div className="mt-4 p-4 bg-dark-bg/50 rounded-lg border border-dark-border">
                        <h4 className="text-sm font-semibold text-neon-cyan mb-3 flex items-center gap-2">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          Contract Details
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                          {/* Basic Info */}
                          <div className="space-y-2">
                            <div>
                              <span className="text-gray-400 block mb-1">Contract ID:</span>
                              <span className="text-neon-cyan font-mono">#{message.uploadResult.id}</span>
                            </div>
                            {message.uploadResult.contract_number && (
                              <div>
                                <span className="text-gray-400 block mb-1">Contract Number:</span>
                                <span className="text-neon-blue">{message.uploadResult.contract_number}</span>
                              </div>
                            )}
                            {message.uploadResult.effective_date && (
                              <div>
                                <span className="text-gray-400 block mb-1">Effective Date:</span>
                                <span className="text-gray-300">{new Date(message.uploadResult.effective_date).toLocaleDateString()}</span>
                              </div>
                            )}
                            {message.uploadResult.renewal_date && (
                              <div>
                                <span className="text-gray-400 block mb-1">Renewal Date:</span>
                                <span className="text-gray-300">{new Date(message.uploadResult.renewal_date).toLocaleDateString()}</span>
                              </div>
                            )}
                          </div>

                          {/* Risk & Classification */}
                          <div className="space-y-2">
                            <div>
                              <span className="text-gray-400 block mb-1">Risk Score:</span>
                              <div className="flex items-center gap-2">
                                <span className={`text-lg font-bold ${
                                  message.uploadResult.risk_score > 70 ? 'text-red-400' :
                                  message.uploadResult.risk_score > 40 ? 'text-yellow-400' :
                                  'text-neon-green'
                                }`}>
                                  {message.uploadResult.risk_score?.toFixed(1)}%
                                </span>
                                <div className="flex-1 bg-dark-bg rounded-full h-2">
                                  <div 
                                    className={`h-2 rounded-full transition-all ${
                                      message.uploadResult.risk_score > 70 ? 'bg-red-400' :
                                      message.uploadResult.risk_score > 40 ? 'bg-yellow-400' :
                                      'bg-neon-green'
                                    }`}
                                    style={{ width: `${Math.min(message.uploadResult.risk_score || 0, 100)}%` }}
                                  ></div>
                                </div>
                              </div>
                            </div>
                            {message.uploadResult.file_name && (
                              <div>
                                <span className="text-gray-400 block mb-1">File:</span>
                                <span className="text-gray-300 truncate block">{message.uploadResult.file_name}</span>
                              </div>
                            )}
                            {message.uploadResult.file_type && (
                              <div>
                                <span className="text-gray-400 block mb-1">File Type:</span>
                                <span className="text-gray-300">{message.uploadResult.file_type}</span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Risk Factors */}
                        {message.uploadResult.risk_factors && message.uploadResult.risk_factors.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-dark-border">
                            <span className="text-gray-400 block mb-2 text-xs">Risk Factors:</span>
                            <ul className="space-y-1.5">
                              {message.uploadResult.risk_factors.map((factor: string, idx: number) => (
                                <li key={idx} className="flex items-start gap-2 text-xs">
                                  <span className="text-red-400 mt-0.5">⚠</span>
                                  <span className="text-neon-blue flex-1">{factor}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Tags */}
                        {message.uploadResult.tags && message.uploadResult.tags.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-dark-border">
                            <span className="text-gray-400 block mb-2 text-xs">Tags:</span>
                            <div className="flex flex-wrap gap-2">
                              {message.uploadResult.tags.map((tag: string, idx: number) => (
                                <span key={idx} className="px-2 py-1 bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50 rounded text-xs font-medium">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Clauses Preview */}
                        {message.uploadResult.extracted_clauses && message.uploadResult.extracted_clauses.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-dark-border">
                            <span className="text-gray-400 block mb-2 text-xs">Extracted Clauses ({message.uploadResult.extracted_clauses.length}):</span>
                            <div className="space-y-1">
                              {message.uploadResult.extracted_clauses.slice(0, 3).map((clause: any, idx: number) => (
                                <div key={idx} className="p-2 bg-dark-bg rounded text-xs">
                                  <span className="text-neon-cyan font-medium">{clause.type || 'General'}:</span>
                                  <p className="text-gray-300 mt-1 line-clamp-2">{clause.text || clause.description || 'N/A'}</p>
                                </div>
                              ))}
                              {message.uploadResult.extracted_clauses.length > 3 && (
                                <p className="text-gray-500 text-xs mt-2">+ {message.uploadResult.extracted_clauses.length - 3} more clauses</p>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Actions */}
                        <div className="mt-4 pt-4 border-t border-dark-border flex gap-2">
                          <button 
                            onClick={() => {
                              // Navigate to contract details or show more info
                              window.dispatchEvent(new CustomEvent('view-contract', { detail: message.uploadResult.id }))
                            }}
                            className="px-3 py-1.5 bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50 rounded text-xs hover:bg-neon-cyan/30 transition-all"
                          >
                            View Full Details
                          </button>
                          <button 
                            onClick={() => {
                              // Copy contract number
                              navigator.clipboard.writeText(message.uploadResult.contract_number || message.uploadResult.id.toString())
                            }}
                            className="px-3 py-1.5 bg-dark-bg text-gray-400 border border-dark-border rounded text-xs hover:border-neon-cyan/50 hover:text-neon-cyan transition-all"
                          >
                            Copy Contract #
                          </button>
                        </div>
                      </div>
                    )}
                    {message.data && renderDataCard(message.data, 'Query Results')}
                  </div>
                  
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {message.sources.map((source, sidx) => (
                        <span
                          key={sidx}
                          className="px-2 py-1 bg-neon-blue/20 text-neon-blue border border-neon-blue/50 rounded-lg text-xs font-mono"
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center mt-1">
                    <span className="text-xs font-semibold text-gray-200">U</span>
                  </div>
                )}
              </div>
            ))}
            
            {(loading || uploading) && (
              <div className="flex gap-4 justify-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-neon-cyan to-neon-blue flex items-center justify-center mt-1 animate-pulse">
                  {uploading ? (
                    <svg className="w-5 h-5 text-dark-bg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 text-dark-bg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  )}
                </div>
                <div className="bg-dark-surface border border-dark-border rounded-2xl rounded-tl-sm px-4 py-3 min-w-[120px]">
                  {uploading ? (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                        <span className="text-gray-400 text-sm ml-2">Uploading and analyzing...</span>
                      </div>
                      <div className="w-full bg-dark-bg rounded-full h-1.5">
                        <div 
                          className="bg-gradient-to-r from-neon-cyan to-neon-blue h-1.5 rounded-full transition-all duration-300"
                          style={{ width: `${uploadProgress}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500">{uploadProgress}%</span>
                    </div>
                  ) : streamingText ? (
                    <div className="text-gray-100">
                      <div 
                        className="prose prose-invert max-w-none"
                        dangerouslySetInnerHTML={{ 
                          __html: formatMessage(streamingText) 
                        }}
                      />
                      <span className="inline-block w-2 h-4 bg-neon-cyan ml-1 animate-pulse"></span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                      <span className="text-gray-400 text-sm ml-2">Analyzing your query...</span>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Payment Modal */}
      {showPayment && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-dark-surface border border-neon-cyan/50 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-neon-cyan">Upgrade Required</h3>
              <button
                onClick={() => setShowPayment(false)}
                className="text-gray-400 hover:text-neon-cyan transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-4">
              <div className="bg-dark-bg border border-dark-border rounded-lg p-4">
                <p className="text-gray-300 text-sm mb-2">
                  You've used <strong className="text-neon-cyan">{queryCount} free queries</strong>. 
                  To continue using GovernAI Copilot, please upgrade to a paid plan.
                </p>
                <div className="flex items-center gap-2 text-xs text-gray-400 mt-3">
                  <svg className="w-4 h-4 text-neon-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Unlimited queries after payment</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-400 mt-1">
                  <svg className="w-4 h-4 text-neon-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Priority support</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-400 mt-1">
                  <svg className="w-4 h-4 text-neon-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Advanced features</span>
                </div>
              </div>
              
              <div className="bg-dark-bg border border-dark-border rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-3 text-center">Secure payment powered by Razorpay</p>
                <div 
                  dangerouslySetInnerHTML={{ 
                    __html: '<form><script src="https://checkout.razorpay.com/v1/payment-button.js" data-payment_button_id="pl_QpF5wRtpOcyF4t" async></script></form>' 
                  }}
                  className="flex justify-center"
                />
              </div>

              <button
                onClick={() => {
                  // Mark as paid after successful payment (in real app, this would be verified via webhook)
                  setIsPaid(true)
                  localStorage.setItem('governai_paid', 'true')
                  setShowPayment(false)
                }}
                className="w-full px-4 py-2 bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50 rounded-lg hover:bg-neon-cyan/30 transition-all text-sm"
              >
                I've Already Paid
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Usage Counter */}
      {!isPaid && queryCount > 0 && (
        <div className="border-b border-dark-border bg-dark-surface px-6 py-2">
          <div className="max-w-4xl mx-auto flex items-center justify-between text-xs">
            <span className="text-gray-400">
              Free queries used: <strong className="text-neon-cyan">{queryCount}/5</strong>
            </span>
            {queryCount >= 5 && (
              <button
                onClick={() => setShowPayment(true)}
                className="text-neon-cyan hover:text-neon-blue transition-colors font-medium"
              >
                Upgrade Now →
              </button>
            )}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div 
        className={`border-t border-dark-border bg-dark-bg ${dragActive ? 'bg-dark-surface/50' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="max-w-4xl mx-auto px-4 py-4">
          {dragActive && (
            <div className="mb-4 p-8 border-2 border-dashed border-neon-cyan rounded-2xl bg-neon-cyan/10 text-center">
              <svg className="w-12 h-12 mx-auto mb-2 text-neon-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="text-neon-cyan font-semibold">Drop your file here to upload</p>
              <p className="text-gray-400 text-sm mt-1">Supports PDF, DOCX, DOC, TXT</p>
            </div>
          )}
          <div className="relative flex items-end gap-3 bg-dark-surface border border-dark-border rounded-2xl px-4 py-3 shadow-lg transition-all hover:border-neon-cyan/30 focus-within:border-neon-cyan/50">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.doc,.txt"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload-input"
            />
            <label
              htmlFor="file-upload-input"
              className="flex-shrink-0 w-10 h-10 rounded-full bg-dark-bg border border-dark-border hover:border-neon-cyan/50 text-gray-400 hover:text-neon-cyan flex items-center justify-center transition-all cursor-pointer hover:bg-dark-surface"
              title="Upload file"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            </label>
            <div className="flex-1">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value)
                  e.target.style.height = 'auto'
                  e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`
                }}
                onKeyPress={handleKeyPress}
                placeholder="Ask about contracts, compliance, reports, or dashboard... (or drag & drop a file)"
                rows={1}
                className="w-full bg-transparent text-gray-100 placeholder-gray-500 resize-none focus:outline-none text-sm leading-relaxed max-h-[200px] overflow-y-auto"
                disabled={loading || uploading}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading || uploading || (queryCount >= 5 && !isPaid)}
              className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-neon-cyan to-neon-blue hover:from-neon-cyan/90 hover:to-neon-blue/90 text-dark-bg flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:from-neon-cyan disabled:hover:to-neon-blue shadow-lg hover:shadow-neon-cyan/30 hover:scale-105 active:scale-95"
              title={queryCount >= 5 && !isPaid ? "Upgrade required to continue" : "Send message"}
            >
              {loading || uploading ? (
                <div className="w-5 h-5 border-2 border-dark-bg border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <svg className="w-5 h-5 transform rotate-0 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </div>
          
          {input.trim() && (
            <div className="mt-2 text-xs text-gray-500 text-center">
              Press <kbd className="px-2 py-1 bg-dark-surface border border-dark-border rounded text-neon-cyan">Enter</kbd> to send, <kbd className="px-2 py-1 bg-dark-surface border border-dark-border rounded text-neon-cyan">Shift + Enter</kbd> for new line
            </div>
          )}
          
          {/* Powered by footer */}
          <div className="flex items-center justify-center mt-3">
            <p className="text-xs text-gray-500 flex items-center gap-1">
              Powered by{' '}
              <a 
                href="https://xylotech.in" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-neon-cyan hover:text-neon-cyan/80 transition-colors font-medium"
              >
                xylotech.in
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
