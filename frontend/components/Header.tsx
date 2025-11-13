'use client'

export default function Header() {
  return (
    <header className="bg-dark-surface border-b border-dark-border border-glow relative">
      <div className="px-6 py-4 relative z-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-neon-cyan glow-cyan tracking-tight">
              Govern<span className="text-neon-blue">AI</span>
            </h1>
            <p className="text-xs text-gray-400 font-normal tracking-wide mt-0.5">
              Enterprise AI Platform
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <button className="p-2 text-neon-cyan hover:text-neon-blue transition-colors border border-dark-border hover:border-neon-cyan rounded">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </button>
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-neon-cyan to-neon-blue flex items-center justify-center text-dark-bg font-orbitron font-bold border-2 border-neon-cyan shadow-lg shadow-neon-cyan/50">
              U
            </div>
          </div>
        </div>
      </div>
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-50"></div>
    </header>
  )
}

