'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const COLORS = ['#00ff80', '#0080ff', '#ff0080', '#8000ff']

export default function ComplianceChart() {
  const [data, setData] = useState([
    { name: 'Compliant', value: 0 },
    { name: 'Non-Compliant', value: 0 },
    { name: 'At Risk', value: 0 },
    { name: 'Pending', value: 0 },
  ])

  useEffect(() => {
    fetchComplianceData()
  }, [])

  const fetchComplianceData = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/v1/compliance/dashboard`)
      setData([
        { name: 'Compliant', value: res.data.compliant || 0 },
        { name: 'Non-Compliant', value: res.data.non_compliant || 0 },
        { name: 'At Risk', value: res.data.at_risk || 0 },
        { name: 'Pending', value: res.data.total_records - (res.data.compliant + res.data.non_compliant + res.data.at_risk) || 0 },
      ])
    } catch (error) {
      console.error('Error fetching compliance data:', error)
    }
  }

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg p-6 relative hover:border-neon-cyan transition-all duration-300">
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-30"></div>
      <h3 className="text-lg font-semibold text-neon-cyan mb-6">Compliance Status</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

