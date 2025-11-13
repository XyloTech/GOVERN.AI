'use client'

interface SidebarProps {
  activeView: string
  setActiveView: (view: string) => void
}

export default function Sidebar({ activeView, setActiveView }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'contracts', label: 'Contracts', icon: '📄' },
    { id: 'compliance', label: 'Compliance', icon: '✅' },
    { id: 'reports', label: 'Reports', icon: '📈' },
    { id: 'copilot', label: 'AI Copilot', icon: '🤖' },
  ]

  return (
    <aside className="w-64 bg-dark-surface border-r border-dark-border relative hidden md:block">
      <nav className="mt-8 px-3">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`w-full flex items-center px-4 py-3 text-left transition-all rounded-lg mb-1 group ${
              activeView === item.id
                ? 'bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/30'
                : 'text-gray-400 hover:text-neon-blue hover:bg-dark-hover border border-transparent'
            }`}
          >
            <span className="mr-3 text-lg">{item.icon}</span>
            <span className={`font-medium text-sm ${activeView === item.id ? 'text-neon-cyan' : ''}`}>
              {item.label}
            </span>
          </button>
        ))}
      </nav>
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-dark-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-neon-green rounded-full mr-2 animate-glow"></div>
            <span className="text-xs text-gray-400">System Online</span>
          </div>
        </div>
      </div>
    </aside>
  )
}

