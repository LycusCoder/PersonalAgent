import { describe, it, expect, beforeEach } from 'vitest'
import { loadChatHistory, saveChatHistory, clearChatHistory, StoredMessage } from '../storage'

const sample: StoredMessage[] = [
  { id: '1', role: 'user', text: 'hello', ts: '2025-01-01T00:00:00Z' },
  { id: '2', role: 'assistant', text: 'hi', ts: '2025-01-01T00:00:01Z' }
]

describe('storage helper', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('saves and loads history', () => {
    saveChatHistory(sample)
    const loaded = loadChatHistory()
    expect(loaded).toHaveLength(2)
    expect(loaded[0].text).toBe('hello')
  })

  it('clears history', () => {
    saveChatHistory(sample)
    clearChatHistory()
    const loaded = loadChatHistory()
    expect(loaded).toHaveLength(0)
  })
})
