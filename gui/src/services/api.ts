import { StatusResponse } from '../types'

export async function getStatus(): Promise<StatusResponse> {
  const resp = await fetch('/api/status')
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
  const payload = await resp.json()
  if (!payload.success) throw new Error('API error')
  return payload as StatusResponse
}
