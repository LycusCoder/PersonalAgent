import React, { useEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react'
import { FiSend } from 'react-icons/fi'
import { FaRobot } from 'react-icons/fa'
import { postChat } from '../services/chat'
import storage, { StoredMessage } from '../services/storage'

type Message = { id: string; role: 'user' | 'assistant'; text: string }

export type ChatHandle = {
  sendPrompt: (text: string) => void
}

const Chat = forwardRef<ChatHandle, { onAgentAction?: (action: any) => void; disabled?: boolean }>(function ChatComponent(props, ref) {
  const { onAgentAction, disabled = false } = props
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(false)
  const [speaking, setSpeaking] = useState(false)
  const [reactionKey, setReactionKey] = useState(0)
  const [avatarReacting, setAvatarReacting] = useState(false)
  const listRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const hist = storage.loadChatHistory()
    if (hist && hist.length > 0) {
      setMessages(hist as Message[])
    } else {
      setMessages([
        { id: 'm1', role: 'assistant', text: 'Halo! Saya Sarah — tanya apa saja tentang status komputer Anda.' }
      ])
    }
  }, [])

  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight
  }, [messages])

  async function send(textArg?: string) {
    const text = typeof textArg === 'string' ? textArg : input
    if (!text.trim()) return
    const userMsg: Message = { id: Date.now().toString(), role: 'user', text }
    setMessages((s) => [...s, userMsg])
    if (typeof textArg !== 'string') setInput('')
    setSending(true)
    try {
      const res = await postChat({ message: userMsg.text })
      const assistant: Message = { id: 'a' + Date.now().toString(), role: 'assistant', text: res.reply || 'Tidak ada balasan.' }
      setMessages((s) => [...s, assistant])

  // trigger avatar reaction and optional TTS on assistant message
  setReactionKey((k) => k + 1)
  setAvatarReacting(true)
  setSpeaking(true)
      if (voiceEnabled && typeof window !== 'undefined' && 'speechSynthesis' in window) {
        try {
          const utter = new SpeechSynthesisUtterance(assistant.text)
          window.speechSynthesis.cancel()
          window.speechSynthesis.speak(utter)
        } catch (e) {
          console.warn('TTS error', e)
        }
      }
  setTimeout(() => setSpeaking(false), 900)

      // forward action to parent if provided
      if (res?.action && typeof onAgentAction === 'function') {
        try { onAgentAction(res.action) } catch (e) { /* swallow */ }
      }
    } catch (e: any) {
      setMessages((s) => [...s, { id: 'err' + Date.now().toString(), role: 'assistant', text: 'Gagal terhubung ke server.' }])
    } finally {
      setSending(false)
    }
  }

  useImperativeHandle(ref, () => ({
    sendPrompt(text: string) {
      send(text)
    }
  }))

  // persist history whenever messages change
  useEffect(() => {
    try {
      const toStore: StoredMessage[] = messages.map((m) => ({ id: m.id, role: m.role, text: m.text, ts: new Date().toISOString() }))
      storage.saveChatHistory(toStore)
    } catch (e) {
      // ignore
    }
  }, [messages])

  // Clear the avatar reacting flag after animation ends
  useEffect(() => {
    if (!avatarReacting) return
    const id = setTimeout(() => setAvatarReacting(false), 820)
    return () => clearTimeout(id)
  }, [avatarReacting])

  function handleClear() {
    storage.clearChatHistory()
    setMessages([{ id: 'm1', role: 'assistant', text: 'Riwayat dikosongkan. Halo! Saya Sarah siap membantu.' }])
  }

  function handleExport() {
    const toStore: StoredMessage[] = messages.map((m) => ({ id: m.id, role: m.role, text: m.text, ts: new Date().toISOString() }))
    storage.exportChatHistory(toStore)
  }

  return (
    <div className="glass-card flex flex-col h-full">
      <div className="flex items-center justify-between mb-3 flex-wrap">
        <div className="flex items-center gap-3">
          {/* compact responsive avatar */}
          <div className={`avatar-ring p-1 rounded-full flex items-center justify-center ${avatarReacting ? 'react' : ''}`}>
            <div className="w-12 h-12 md:w-16 md:h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
              <FaRobot className="text-white text-xl md:text-2xl" />
            </div>
          </div>
          <div className="min-w-0">
            <div className="text-white font-semibold truncate">Chat dengan Sarah</div>
            <div className="text-sm text-white/70 truncate hidden xs:block sm:block md:block">Jarvis mode</div>
          </div>
        </div>

        <div className="flex items-center gap-2 mt-2 md:mt-0">
          <button onClick={handleExport} className="text-white/80 hover:text-white text-sm px-2 py-1">Export</button>
          <button onClick={handleClear} className="text-white/80 hover:text-white text-sm px-2 py-1">Clear</button>
          <label className="text-sm text-white/70 flex items-center gap-2">
            <input type="checkbox" checked={voiceEnabled} onChange={(e) => setVoiceEnabled(e.target.checked)} />
            Voice
          </label>
        </div>
      </div>

      <div ref={listRef} role="log" aria-live="polite" aria-atomic="false" className="flex-1 overflow-auto mb-3 space-y-3 px-2 max-h-48 md:max-h-[420px]">
        {messages.map((m) => (
          <div key={m.id} className={m.role === 'user' ? 'message-user' : 'message-assistant'}>
            <div className="message-bubble">{m.text}</div>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          id="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          className="chat-input"
          placeholder="Tanyakan sesuatu, mis. 'Status RAM'"
          aria-label="Chat input"
          aria-disabled={disabled || sending}
          disabled={disabled || sending}
        />
        <button
          type="button"
          onClick={() => send()}
          disabled={sending || disabled}
          aria-label="Kirim pesan"
          title="Kirim"
          className="bg-accent hover:bg-indigo-500 text-white rounded-full p-3 flex items-center justify-center"
        >
          <FiSend />
        </button>
      </div>
    </div>
  )
})

export default Chat
