import React from 'react'
import { FaRobot } from 'react-icons/fa'

export default function Character({ speaking = false }: { speaking?: boolean }) {
  return (
    <div className="glass-card flex flex-col items-center text-center">
      <div className="avatar-ring mb-3">
        <div className="w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
          <FaRobot className="text-white text-3xl" />
        </div>
      </div>
      <div className="jarvis-title">Sarah — Sekretaris Digital</div>
      <div className="jarvis-sub text-sm mt-1">Tanyakan sesuatu tentang komputer Anda.</div>
      <div className="mt-3 text-sm text-white/80">{speaking ? 'Mendengar...' : 'Siap membantu'}</div>
    </div>
  )
}
