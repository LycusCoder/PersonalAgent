import React from 'react'
import { render, screen } from '@testing-library/react'
import SystemCard from '../SystemCard'

describe('SystemCard', () => {
  it('renders title and rows', () => {
    render(
      <SystemCard
        title="Test Card"
        rows={[{ label: 'One', value: '1' }, { label: 'Two', value: '2' }]}
      />
    )

    expect(screen.getByText('Test Card')).toBeInTheDocument()
    expect(screen.getByText('One')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })
})
