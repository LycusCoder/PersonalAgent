import React from 'react'

export default function Widget({ title, children }: { title: string; children?: React.ReactNode }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div>{children}</div>
    </div>
  )
}
