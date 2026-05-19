import { describe, expect, it, vi, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'

import RegisterPage from '../features/auth/RegisterPage'

function mockFetchOnce(status: number, body: unknown): typeof fetch {
  return vi.fn(async () => {
    return new Response(JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    })
  }) as unknown as typeof fetch
}

describe('RegisterPage', () => {
  const originalFetch = globalThis.fetch

  afterEach(() => {
    globalThis.fetch = originalFetch
  })

  it('valide localement le mot de passe (< 12 caractères)', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>,
    )
    await user.type(screen.getByLabelText(/Adresse email/i), 'prof@example.fr')
    await user.type(screen.getByLabelText(/Mot de passe/i), 'court')
    await user.click(screen.getByRole('button', { name: /s'inscrire/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      /Minimum 12 caractères/i,
    )
  })

  it('affiche l\'écran de succès après une réponse 201', async () => {
    globalThis.fetch = mockFetchOnce(201, {
      id: '550e8400-e29b-41d4-a716-446655440000',
      email: 'prof@example.fr',
      status: 'pending',
    })

    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>,
    )
    await user.type(screen.getByLabelText(/Adresse email/i), 'prof@example.fr')
    await user.type(
      screen.getByLabelText(/Mot de passe/i),
      'motdepasse123456',
    )
    await user.click(screen.getByRole('button', { name: /s'inscrire/i }))

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: /Vérifiez votre boîte mail/i }),
      ).toBeInTheDocument()
    })
    expect(screen.getByText('prof@example.fr')).toBeInTheDocument()
  })

  it('affiche un message d\'erreur sur réponse 409', async () => {
    globalThis.fetch = mockFetchOnce(409, {
      error: {
        code: 'EMAIL_ALREADY_REGISTERED',
        message: 'Cet email est déjà utilisé.',
      },
    })

    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>,
    )
    await user.type(
      screen.getByLabelText(/Adresse email/i),
      'duplicate@example.fr',
    )
    await user.type(
      screen.getByLabelText(/Mot de passe/i),
      'motdepasse123456',
    )
    await user.click(screen.getByRole('button', { name: /s'inscrire/i }))

    expect(await screen.findByText(/Cet email est déjà utilisé/i)).toBeInTheDocument()
  })
})
