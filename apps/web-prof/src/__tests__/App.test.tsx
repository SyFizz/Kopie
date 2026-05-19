import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

describe('App (web-prof)', () => {
  it('rend le titre de l\'espace enseignant', () => {
    render(<App />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      /Kopie.*Espace enseignant/i,
    )
  })
})
