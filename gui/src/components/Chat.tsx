import React, { useEffect, useRef, useState } from 'react'
import { FiSend } from 'react-icons/fi'
import { postChat } from '../services/chat'

type Message = { id: string; role: 'user' | 'assistant'; text: string }

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const listRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    // initial greeting
    setMessages([
      { id: 'm1', role: 'assistant', text: 'Halo! Saya Sarah — tanya apa saja tentang status komputer Anda.' }
    ])
  }, [])

  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight
  }, [messages])

  async function send() {
    if (!input.trim()) return
    const userMsg: Message = { id: Date.now().toString(), role: 'user', text: input }
    setMessages((s) => [...s, userMsg])
    setInput('')
    setSending(true)
    try {
      const res = await postChat({ message: userMsg.text })
      const assistant: Message = { id: 'a' + Date.now().toString(), role: 'assistant', text: res.reply || 'Tidak ada balasan.' }
      setMessages((s) => [...s, assistant])
    } catch (e: any) {
      setMessages((s) => [...s, { id: 'err' + Date.now().toString(), role: 'assistant', text: 'Gagal terhubung ke server.' }])
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="glass-card flex flex-col h-full">
      <div className="flex items-center justify-between mb-3">
        <div className="text-white font-semibold">Chat dengan Sarah</div>
        <div className="text-sm text-white/70">Jarvis mode</div>
      </div>

      <div ref={listRef} className="flex-1 overflow-auto mb-3 space-y-3 px-2">
        {messages.map((m) => (
          <div key={m.id} className={m.role === 'user' ? 'message-user' : 'message-assistant'}>
            <div className="message-bubble">{m.text}</div>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          className="chat-input"
          placeholder="Tanyakan sesuatu, mis. 'Status RAM'"
        />
        <button
          onClick={send}
          disabled={sending}
          className="bg-accent hover:bg-indigo-500 text-white rounded-full p-3 flex items-center justify-center"
        >
          <FiSend />
        </button>
      </div>
    </div>
  )
}
