'use client'

interface StatCardProps {
  title: string
  value: string | number
  icon: string
  trend?: string
  trendUp?: boolean
}

export default function StatCard({ title, value, icon, trend, trendUp }: StatCardProps) {
  return (
    <div className="bg-dark-surface border border-dark-border rounded-xl p-6 relative overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300 fade-in">
      <div className="flex items-center justify-between relative z-10">
        <div className="flex-1">
          <p className="text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">{title}</p>
          <p className="text-3xl font-bold text-neon-cyan mb-1">{value}</p>
          {trend && (
            <p className={`text-xs font-medium mt-2 flex items-center ${trendUp ? 'text-neon-green' : 'text-red-400'}`}>
              <span className="mr-1">{trendUp ? '↑' : '↓'}</span>
              <span>{trend}</span>
            </p>
          )}
        </div>
        <div className="text-4xl opacity-20 group-hover:opacity-30 transition-opacity">{icon}</div>
      </div>
    </div>
  )
}

