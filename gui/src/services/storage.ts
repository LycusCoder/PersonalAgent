// Small storage helper for chat history
const CHAT_KEY = 'personalagent.chat.history'

export type StoredMessage = {
  id: string
  role: 'user' | 'assistant'
  text: string
  ts?: string
}

export function loadChatHistory(): StoredMessage[] {
  try {
    const raw = localStorage.getItem(CHAT_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed
  } catch (e) {
    console.warn('Failed to load chat history', e)
    return []
  }
}

export function saveChatHistory(messages: StoredMessage[]) {
  try {
    localStorage.setItem(CHAT_KEY, JSON.stringify(messages))
  } catch (e) {
    console.warn('Failed to save chat history', e)
  }
}

export function clearChatHistory() {
  try {
    localStorage.removeItem(CHAT_KEY)
  } catch (e) {
    console.warn('Failed to clear chat history', e)
  }
}

export function exportChatHistory(messages: StoredMessage[]) {
  const blob = new Blob([JSON.stringify(messages, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `chat-history-${new Date().toISOString()}.json`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export default { loadChatHistory, saveChatHistory, clearChatHistory, exportChatHistory }
