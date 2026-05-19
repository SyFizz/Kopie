import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

describe('App (web-eleve)', () => {
  it('rend le titre de l\'évaluation', () => {
    render(<App />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      /Kopie.*Évaluation/i,
    )
  })
})
