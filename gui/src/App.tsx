import React, { useState, useRef, useEffect, useCallback } from 'react'
import { FiList as List, FiX as X } from 'react-icons/fi'

// Impor semua komponen yang kita butuhkan
import Dashboard from './components/Dashboard'
import Chat from './components/Chat'
import Sidebar from './components/Sidebar'

// Asumsi kita punya gambar karakter di /static/gui/assets/karakter.jpg
const CHARACTER_BACKGROUND_URL = '/static/gui/assets/image_63dc3a.jpg'

// Tipe Modal yang bisa aktif
type ModalView = 'DASHBOARD' | 'TOOLS' | null

export default function App() {
  const [currentModal, setCurrentModal] = useState<ModalView>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const modalRef = useRef<HTMLDivElement | null>(null)
  const previouslyFocused = useRef<HTMLElement | null>(null)

  // Fungsi ini akan dipanggil oleh Chat.tsx
  const handleAgentAction = (action: any) => {
    if (action?.type === 'OPEN_MODAL' && action?.view === 'DASHBOARD') {
      setCurrentModal('DASHBOARD')
    }
    // Tambahkan logic lain di sini, misal 'TOOLS'
  }

  // Fungsi ini akan dipanggil oleh Sidebar.tsx
  const handleSidebarCommand = (command: string) => {
    // Di sini kita bisa kirim 'command' ke Chat.tsx (logic lebih advanced)
    // Untuk sekarang, kita trigger modal-nya langsung
    if (command === 'Tampilkan Status Sistem') {
      setCurrentModal('DASHBOARD')
    }
    setIsSidebarOpen(false)
  }

  // Focus trap & ESC handling for modal
  const onKeyDown = useCallback((e: KeyboardEvent) => {
    if (!modalRef.current) return
    if (e.key === 'Escape') {
      setCurrentModal(null)
      return
    }
    if (e.key === 'Tab') {
      const focusable = modalRef.current.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'
      )
      if (focusable.length === 0) {
        e.preventDefault()
        return
      }
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault()
          last.focus()
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault()
          first.focus()
        }
      }
    }
  }, [modalRef])

  useEffect(() => {
    if (currentModal) {
      // store focused element
      previouslyFocused.current = document.activeElement as HTMLElement
      // add listener
      document.addEventListener('keydown', onKeyDown)
      // focus first focusable inside modal (after a tick)
      setTimeout(() => {
        if (!modalRef.current) return
        const focusable = modalRef.current.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'
        )
        if (focusable.length) focusable[0].focus()
      }, 50)
      // hide inert background from assistive tech
      document.body.style.overflow = 'hidden'
    } else {
      document.removeEventListener('keydown', onKeyDown)
      document.body.style.overflow = ''
      // restore focus
      try {
        previouslyFocused.current?.focus()
      } catch (e) {
        // ignore
      }
    }
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.body.style.overflow = ''
    }
  }, [currentModal, onKeyDown])

  return (
    <div className="app-root relative min-h-screen w-full flex flex-col">
      {/* === LAYER 1: BACKGROUND KARAKTER === */}
      <div
        className="absolute inset-0 z-0 bg-cover bg-center"
        style={{
          backgroundImage: `linear-gradient(rgba(15, 23, 42, 0.7), rgba(11, 18, 32, 0.9)), url(${CHARACTER_BACKGROUND_URL})`,
        }}
      />

  {/* === LAYER 2: CHAT INTERFACE === */}
  <div className="relative z-10 flex-1 flex flex-col h-full" aria-hidden={currentModal !== null}>
        {/* Tombol Menu Pojok Kiri Atas */}
        <button
          onClick={() => setIsSidebarOpen(true)}
          className="absolute top-4 left-4 z-30 p-2 text-white/70 hover:text-white"
          aria-label="Buka Menu"
        >
          <List size={24} />
        </button>

        <div className="w-full max-w-3xl mx-auto flex-1 flex flex-col py-16">
          <Chat onAgentAction={handleAgentAction} disabled={currentModal !== null} />
        </div>
      </div>

      {/* === LAYER 3: MODAL (Wireframe 3) === */}
      {currentModal && (
        <div
          className="absolute inset-0 z-40 bg-black/50 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setCurrentModal(null)}
        >
          <div
            className="jarvis-shell w-full max-w-4xl max-h-[90vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
            ref={modalRef}
            role="dialog"
            aria-modal="true"
            aria-label={currentModal === 'DASHBOARD' ? 'System Monitor' : 'Modal Dialog'}
          >
            <button
              onClick={() => setCurrentModal(null)}
              className="absolute top-4 right-4 z-50 p-2 text-white/70 hover:text-white"
              aria-label="Tutup Modal"
            >
              <X size={24} />
            </button>

            {currentModal === 'DASHBOARD' && <Dashboard />}
            {currentModal === 'TOOLS' && (
              <div>
                <h2>Tool Management</h2>
              </div>
            )}
          </div>
        </div>
      )}

      {/* === LAYER 4: SIDEBAR (Wireframe 2) === */}
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} onCommandClick={handleSidebarCommand} />
    </div>
  )
}
