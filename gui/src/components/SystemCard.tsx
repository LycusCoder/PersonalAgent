import React from 'react'

type Row = { label: string; value: React.ReactNode };

interface SystemCardProps {
  title: string
  rows: Row[]
  className?: string
}

export default function SystemCard({ title, rows, className }: SystemCardProps) {
  const id = `systemcard-${title.replace(/\s+/g, '-').toLowerCase()}`

  return (
    <section className={`card ${className ?? ''}`} role="region" aria-labelledby={id}>
      <h3 id={id} className="card-title">
        {title}
      </h3>
      <dl>
        {rows.map((r, i) => (
          <div className="stat" key={i}>
            <dt className="stat-label">{r.label}</dt>
            <dd className="stat-value">{r.value}</dd>
          </div>
        ))}
      </dl>
    </section>
  )
}
