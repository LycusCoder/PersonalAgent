import React from 'react'
import Header from './components/Header'
import Dashboard from './components/Dashboard'

export default function App() {
  return (
    <div className="app-root">
      <div className="jarvis-shell">
        <Header />
        <main>
          <Dashboard />
        </main>
      </div>
    </div>
  )
}
