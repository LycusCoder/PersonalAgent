import React from 'react'
import { FiMenu } from 'react-icons/fi'

export default function Header({ onToggleSidebar }: { onToggleSidebar?: () => void }) {
  return (
    <header className="header flex items-center justify-between mb-4">
      <div className="flex items-center gap-3">
        <button aria-label="Open menu" onClick={onToggleSidebar} className="p-2 rounded-md bg-white/5">
          <FiMenu />
        </button>
        <div>
          <h1 className="text-lg font-semibold">🤖 Agent Pribadi (AG)</h1>
          <p className="text-sm">Dashboard Monitoring Sistem - Sekretaris Sarah</p>
        </div>
      </div>
    </header>
  )
}
