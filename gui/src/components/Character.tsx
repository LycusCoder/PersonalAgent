import React from 'react'
import { FaRobot } from 'react-icons/fa'

interface CharacterProps {
  speaking?: boolean
  className?: string
  variant?: 'card' | 'background'
  // increment this prop to trigger a reaction animation
  reactionKey?: number
}

export default function Character({ speaking = false, className = '', variant = 'card' }: CharacterProps) {
  if (variant === 'background') {
    return (
      <div className={`character-bg ${className}`} aria-hidden>
        <div className="character-vignette" />
        <div className="character-graphic" />
      </div>
    )
  }
  // compact card variant (used inside Chat)
  return (
    <div className={`glass-card flex flex-col items-center text-center ${className}`}>
      <div className={`avatar-ring mb-3`}>
        <div className="w-20 h-20 md:w-24 md:h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
          <FaRobot className="text-white text-2xl md:text-3xl" />
        </div>
      </div>
      <div className="jarvis-title text-base md:text-lg">Sarah — Sekretaris Digital</div>
      <div className="jarvis-sub text-sm mt-1">Tanyakan sesuatu tentang komputer Anda.</div>
      <div className="mt-3 text-sm text-white/80">{speaking ? 'Mendengar...' : 'Siap membantu'}</div>
    </div>
  )
}
