import React from 'react'
import { FiX as X } from 'react-icons/fi'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
  onCommandClick: (command: string) => void
}

// Daftar perintah statis
const commands = [
  'Tampilkan Status Sistem',
  'Buka Tool Management',
  'Cek Status RAM',
  'Cek Status CPU',
]

export default function Sidebar({ isOpen, onClose, onCommandClick }: SidebarProps) {
  return (
    <>
      {/* Backdrop */}
      <div
        className={`fixed inset-0 z-40 bg-black/30 transition-opacity ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
      />

      {/* Konten Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-50 w-72 h-full bg-jarvisEnd shadow-lg transform transition-transform ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="flex justify-between items-center p-4 border-b border-white/10">
          <h2 className="text-lg font-semibold text-white">Menu Perintah</h2>
          <button onClick={onClose} className="p-1 text-white/70 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <nav className="p-4">
          <ul className="space-y-2">
            {commands.map((cmd) => (
              <li key={cmd}>
                <button
                  onClick={() => onCommandClick(cmd)}
                  className="w-full text-left p-2 rounded-md text-white/80 hover:bg-white/10 hover:text-white transition-colors"
                >
                  {cmd}
                </button>
              </li>
            ))}
          </ul>
        </nav>
      </aside>
    </>
  )
}
