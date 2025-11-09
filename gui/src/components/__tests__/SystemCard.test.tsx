import React from 'react'
import { describe, it, expect } from 'vitest'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import SystemCard from '../SystemCard'

describe('SystemCard', () => {
  it('renders title and rows and exposes an accessible region', () => {
    render(
      <SystemCard
        title="System Status"
        rows={[{ label: 'CPU', value: '10%' }, { label: 'RAM', value: '2GB' }]}
      />
    )

    // accessible region with the card title as name
    expect(screen.getByRole('region', { name: /system status/i })).toBeInTheDocument()

    // content checks
    expect(screen.getByText('CPU')).toBeInTheDocument()
    expect(screen.getByText('10%')).toBeInTheDocument()
    expect(screen.getByText('RAM')).toBeInTheDocument()
    expect(screen.getByText('2GB')).toBeInTheDocument()
  })
})
