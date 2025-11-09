import React, { useEffect, useState } from 'react'
import SystemCard from './SystemCard'
import { getStatus } from '../services/api'
import { StatusResponse } from '../types'

export default function Dashboard() {
  const [data, setData] = useState<StatusResponse['data'] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const res = await getStatus()
      setData(res.data)
    } catch (e: any) {
      setError(e?.message || 'Error fetching data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const id = setInterval(load, 5000)
    return () => clearInterval(id)
  }, [])

  if (loading) return <div className="loading">Memuat data sistem...</div>
  if (error) return <div className="card" style={{ color: '#ef4444' }}>Gagal memuat data sistem: {error}</div>
  if (!data) return null

  const { ram, cpu, gpu } = data

  return (
    <div className="system-grid-container p-4">
      <h2 className="jarvis-title mb-4">System Monitor</h2>

      <div className="sys-grid">
        <SystemCard
          title="💾 RAM"
          rows={[
            { label: 'Total', value: `${ram.total_gb} GB` },
            { label: 'Digunakan', value: `${ram.used_gb} GB` },
            { label: 'Tersedia', value: `${ram.available_gb} GB` },
            { label: 'Penggunaan', value: `${ram.percent}%` }
          ]}
        />

        <SystemCard
          title="⚙️ CPU"
          rows={[
            { label: 'Penggunaan', value: `${cpu.percent}%` },
            { label: 'Core Fisik', value: cpu.cores_physical },
            { label: 'Core Logical', value: cpu.cores_logical },
            { label: 'Frekuensi', value: `${cpu.freq_current_mhz} MHz` }
          ]}
        />

        <SystemCard
          title="🎮 GPU"
          rows={[
            { label: 'Nama', value: <span style={{ fontSize: '0.9rem' }}>{gpu.name}</span> },
            { label: 'Suhu', value: `${gpu.temperature_c}°C` },
            { label: 'Penggunaan', value: `${gpu.utilization_percent}%` },
            { label: 'Memory', value: `${(gpu.memory_used_mb / 1024).toFixed(2)} GB / ${(gpu.memory_total_mb / 1024).toFixed(2)} GB` }
          ]}
        />
      </div>
      <div className="mt-4 text-sm text-white/70">Auto-refresh setiap 5 detik</div>
    </div>
  )
}
