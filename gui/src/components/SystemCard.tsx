import React from 'react'

type Row = { label: string; value: React.ReactNode };

export default function SystemCard({ title, rows }: { title: string; rows: Row[] }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {rows.map((r, i) => (
        <div className="stat" key={i}>
          <span className="stat-label">{r.label}</span>
          <span className="stat-value">{r.value}</span>
        </div>
      ))}
    </div>
  )
}
