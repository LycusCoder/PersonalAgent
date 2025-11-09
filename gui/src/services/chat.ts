export async function postChat(payload: { message: string }): Promise<any> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (!data) throw new Error('Invalid response')

  // Return the entire server response so frontend can inspect 'action' and other fields
  return data
}
