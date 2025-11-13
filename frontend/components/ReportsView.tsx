'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'
import { format } from 'date-fns'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ReportsView() {
  const [reports, setReports] = useState<any[]>([])
  const [templates, setTemplates] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [showGenerate, setShowGenerate] = useState(false)
  const [newReport, setNewReport] = useState({
    title: '',
    report_type: 'financial',
    template_id: null as number | null,
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [reportsRes, templatesRes] = await Promise.all([
        axios.get(`${API_URL}/api/v1/reports`),
        axios.get(`${API_URL}/api/v1/reports/templates`)
      ])
      setReports(reportsRes.data)
      setTemplates(templatesRes.data)
    } catch (error) {
      console.error('Error fetching reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    if (!newReport.title) {
      alert('Please enter a report title')
      return
    }

    setGenerating(true)
    try {
      const response = await axios.post(`${API_URL}/api/v1/reports/generate`, newReport)
      setReports([response.data, ...reports])
      setShowGenerate(false)
      setNewReport({ title: '', report_type: 'financial', template_id: null })
    } catch (error: any) {
      console.error('Error generating report:', error)
      alert(error.response?.data?.detail || 'Failed to generate report')
    } finally {
      setGenerating(false)
    }
  }

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      financial: 'bg-neon-green/20 text-neon-green border border-neon-green/50',
      compliance: 'bg-neon-blue/20 text-neon-blue border border-neon-blue/50',
      contract: 'bg-neon-purple/20 text-neon-purple border border-neon-purple/50',
      operational: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50',
    }
    return colors[type] || 'bg-gray-500/20 text-gray-400 border border-gray-500/50'
  }

  if (loading) {
    return (
      <div className="text-center py-12">
          <div className="text-neon-cyan text-lg animate-glow">Loading reports...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div></div>
        <button
          onClick={() => setShowGenerate(!showGenerate)}
          className="px-6 py-3 bg-gradient-to-r from-neon-cyan to-neon-blue text-dark-bg font-semibold rounded-lg hover:shadow-lg hover:shadow-neon-cyan/30 transition-all"
        >
          {showGenerate ? 'Cancel' : 'Generate Report'}
        </button>
      </div>

      {showGenerate && (
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-neon-cyan mb-4">
            Generate New Report
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Report Title</label>
              <input
                type="text"
                value={newReport.title}
                onChange={(e) => setNewReport({ ...newReport, title: e.target.value })}
                className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-neon-cyan focus:border-neon-cyan focus:outline-none"
                placeholder="Enter report title"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Report Type</label>
              <select
                value={newReport.report_type}
                onChange={(e) => setNewReport({ ...newReport, report_type: e.target.value })}
                className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-neon-cyan focus:border-neon-cyan focus:outline-none"
              >
                <option value="financial">Financial</option>
                <option value="compliance">Compliance</option>
                <option value="contract">Contract</option>
                <option value="operational">Operational</option>
              </select>
            </div>
            <button
              onClick={handleGenerate}
              disabled={generating || !newReport.title}
              className="w-full py-3 px-4 bg-gradient-to-r from-neon-cyan to-neon-blue text-dark-bg font-semibold rounded-lg hover:shadow-lg hover:shadow-neon-cyan/30 transition-all disabled:opacity-50"
            >
              {generating ? 'Generating...' : 'Generate Report'}
            </button>
          </div>
        </div>
      )}

      <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-neon-cyan mb-4">
          All Reports ({reports.length})
        </h3>
        {reports.length === 0 ? (
          <div className="text-center py-8 text-gray-400">No reports generated</div>
        ) : (
          <div className="space-y-3">
            {reports.map((report) => (
              <div key={report.id} className="p-4 bg-dark-bg border border-dark-border rounded hover:border-neon-cyan transition-all">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-neon-cyan mb-1">{report.title}</h4>
                    <p className="text-xs text-gray-400">
                      {format(new Date(report.created_at), 'MMM dd, yyyy HH:mm')}
                    </p>
                    {report.summary && (
                      <p className="text-sm text-gray-300 mt-2 line-clamp-2">{report.summary}</p>
                    )}
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <span className={`px-3 py-1 rounded text-xs font-medium ${getTypeColor(report.report_type)}`}>
                      {report.report_type}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      report.status === 'published' ? 'bg-neon-green/20 text-neon-green' :
                      report.status === 'generated' ? 'bg-neon-blue/20 text-neon-blue' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {report.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

