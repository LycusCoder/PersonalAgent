import React from 'react'

export default function ChartPlaceholder({ text = 'Chart placeholder' }: { text?: string }) {
  return (
    <div className="card" style={{ textAlign: 'center', padding: 30 }}>
      <div style={{ opacity: 0.6 }}>{text}</div>
    </div>
  )
}
