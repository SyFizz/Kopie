import { StrictMode } from 'react'
import { describe, expect, it, vi, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import VerifyEmailPage from '../features/auth/VerifyEmailPage'

function mockFetchOnce(status: number, body: unknown): typeof fetch {
  return vi.fn(async () => {
    return new Response(JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    })
  }) as unknown as typeof fetch
}

describe('VerifyEmailPage', () => {
  const originalFetch = globalThis.fetch

  afterEach(() => {
    globalThis.fetch = originalFetch
  })

  it('affiche le succès après une réponse 200', async () => {
    globalThis.fetch = mockFetchOnce(200, { message: 'Email confirmé.' })

    render(
      <MemoryRouter initialEntries={['/verify-email?token=abc']}>
        <VerifyEmailPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: /Votre email est confirmé/i }),
      ).toBeInTheDocument()
    })
  })

  it('affiche le message d\'erreur sur 400 INVALID_OR_EXPIRED_TOKEN', async () => {
    globalThis.fetch = mockFetchOnce(400, {
      error: {
        code: 'INVALID_OR_EXPIRED_TOKEN',
        message: 'Ce lien est invalide ou expiré.',
      },
    })

    render(
      <MemoryRouter initialEntries={['/verify-email?token=bidon']}>
        <VerifyEmailPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: /Lien invalide/i }),
      ).toBeInTheDocument()
    })
    expect(
      screen.getByText(/Ce lien est invalide ou expiré/i),
    ).toBeInTheDocument()
  })

  it('affiche un message d\'erreur si le token est absent', async () => {
    render(
      <MemoryRouter initialEntries={['/verify-email']}>
        <VerifyEmailPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(
        screen.getByText(/Lien de vérification incomplet/i),
      ).toBeInTheDocument()
    })
  })

  it("ne consomme le token qu'une seule fois en StrictMode (effet non idempotent)", async () => {
    // En StrictMode dev, React monte deux fois l'effet. Le second call à
    // /verify-email échouerait en 400 (token déjà consommé) — on s'assure
    // ici que le composant n'effectue qu'un seul appel HTTP et reste sur
    // l'écran succès.
    let calls = 0
    globalThis.fetch = vi.fn(async () => {
      calls += 1
      if (calls === 1) {
        return new Response(JSON.stringify({ message: 'Email confirmé.' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        })
      }
      return new Response(
        JSON.stringify({
          error: {
            code: 'INVALID_OR_EXPIRED_TOKEN',
            message: 'Ce lien est invalide ou expiré.',
          },
        }),
        { status: 400, headers: { 'Content-Type': 'application/json' } },
      )
    }) as unknown as typeof fetch

    render(
      <StrictMode>
        <MemoryRouter initialEntries={['/verify-email?token=once']}>
          <VerifyEmailPage />
        </MemoryRouter>
      </StrictMode>,
    )

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: /Votre email est confirmé/i }),
      ).toBeInTheDocument()
    })
    expect(calls).toBe(1)
  })
})
