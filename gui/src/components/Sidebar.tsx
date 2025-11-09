import React from 'react'

export default function Sidebar() {
  return (
    <aside style={{ marginBottom: 20 }}>
      <div className="card">
        <h2>Menu</h2>
        <div style={{ padding: '8px 0' }}>
          <div className="stat">Dashboard</div>
          <div className="stat">Logs</div>
          <div className="stat">Settings</div>
        </div>
      </div>
    </aside>
  )
}
