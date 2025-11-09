export async function postChat(payload: { message: string }): Promise<{ reply?: string }> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  // expected server: { success: true, reply: '...' }
  if (!data) throw new Error('Invalid response')
  return { reply: data.reply ?? data.message ?? '' }
}
