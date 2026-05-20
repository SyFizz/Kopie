import { describe, expect, it, vi, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import LoginPage from '../features/auth/LoginPage'
import { AuthProvider, useAuth } from '../features/auth/AuthContext'

function mockFetchOnce(status: number, body: unknown): typeof fetch {
  return vi.fn(async () => {
    return new Response(JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    })
  }) as unknown as typeof fetch
}

function renderLogin(initialPath = '/login') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<DashboardSpy />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  )
}

// Composant sentinelle pour vérifier la redirection post-login et la valeur
// de l'access token stocké dans l'AuthContext (sans dépendre de DashboardPage).
function DashboardSpy() {
  const { accessToken } = useAuth()
  return <div data-testid="dashboard">token={accessToken ?? 'none'}</div>
}

describe('LoginPage', () => {
  const originalFetch = globalThis.fetch

  afterEach(() => {
    globalThis.fetch = originalFetch
  })

  it('valide localement un email mal formé', async () => {
    const user = userEvent.setup()
    renderLogin()
    await user.type(screen.getByLabelText(/Adresse email/i), 'pas-un-email')
    await user.type(screen.getByLabelText(/Mot de passe/i), 'motdepasse')
    await user.click(screen.getByRole('button', { name: /se connecter/i }))

    expect(await screen.findByText(/Email invalide/i)).toBeInTheDocument()
  })

  it('valide localement un mot de passe vide', async () => {
    const user = userEvent.setup()
    renderLogin()
    await user.type(screen.getByLabelText(/Adresse email/i), 'a@b.fr')
    await user.click(screen.getByRole('button', { name: /se connecter/i }))

    expect(
      await screen.findByText(/Le mot de passe est requis/i),
    ).toBeInTheDocument()
  })

  it('redirige vers /dashboard et stocke l\'access token sur 200', async () => {
    globalThis.fetch = mockFetchOnce(200, {
      access_token: 'jwt.value.signed',
      token_type: 'bearer',
    })

    const user = userEvent.setup()
    renderLogin()
    await user.type(screen.getByLabelText(/Adresse email/i), 'prof@example.fr')
    await user.type(screen.getByLabelText(/Mot de passe/i), 'motdepasse123456')
    await user.click(screen.getByRole('button', { name: /se connecter/i }))

    const dashboard = await screen.findByTestId('dashboard')
    expect(dashboard).toHaveTextContent('token=jwt.value.signed')
  })

  it('affiche le message « credentials invalides » sur 401', async () => {
    globalThis.fetch = mockFetchOnce(401, {
      error: {
        code: 'INVALID_CREDENTIALS',
        message: 'Email ou mot de passe incorrect.',
      },
    })

    const user = userEvent.setup()
    renderLogin()
    await user.type(screen.getByLabelText(/Adresse email/i), 'prof@example.fr')
    await user.type(screen.getByLabelText(/Mot de passe/i), 'mauvais-mdp')
    await user.click(screen.getByRole('button', { name: /se connecter/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/Email ou mot de passe incorrect/i),
      ).toBeInTheDocument()
    })
  })

  it('affiche le message « compte non actif » sur 403', async () => {
    globalThis.fetch = mockFetchOnce(403, {
      error: {
        code: 'ACCOUNT_NOT_ACTIVE',
        message: 'pending',
      },
    })

    const user = userEvent.setup()
    renderLogin()
    await user.type(screen.getByLabelText(/Adresse email/i), 'pending@example.fr')
    await user.type(screen.getByLabelText(/Mot de passe/i), 'motdepasse123456')
    await user.click(screen.getByRole('button', { name: /se connecter/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/n'est pas encore activé/i),
      ).toBeInTheDocument()
    })
  })

  it('affiche le message dédié sur 429', async () => {
    globalThis.fetch = mockFetchOnce(429, {
      error: { code: 'RATE_LIMIT_EXCEEDED', message: 'trop de req' },
    })

    const user = userEvent.setup()
    renderLogin()
    await user.type(screen.getByLabelText(/Adresse email/i), 'a@b.fr')
    await user.type(screen.getByLabelText(/Mot de passe/i), 'motdepasse')
    await user.click(screen.getByRole('button', { name: /se connecter/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/Trop de tentatives/i),
      ).toBeInTheDocument()
    })
  })

  it('affiche un message générique sur erreur réseau (fetch rejette)', async () => {
    globalThis.fetch = vi.fn(async () => {
      throw new TypeError('Failed to fetch')
    }) as unknown as typeof fetch

    const user = userEvent.setup()
    renderLogin()
    await user.type(screen.getByLabelText(/Adresse email/i), 'a@b.fr')
    await user.type(screen.getByLabelText(/Mot de passe/i), 'motdepasse')
    await user.click(screen.getByRole('button', { name: /se connecter/i }))

    expect(
      await screen.findByText(/Impossible de joindre le serveur/i),
    ).toBeInTheDocument()
  })

  it('envoie le fetch avec credentials:include (cookie refresh)', async () => {
    const fetchMock = vi.fn(async () => {
      return new Response(
        JSON.stringify({ access_token: 'x', token_type: 'bearer' }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      )
    })
    globalThis.fetch = fetchMock as unknown as typeof fetch

    const user = userEvent.setup()
    renderLogin()
    await user.type(screen.getByLabelText(/Adresse email/i), 'prof@example.fr')
    await user.type(screen.getByLabelText(/Mot de passe/i), 'motdepasse123456')
    await user.click(screen.getByRole('button', { name: /se connecter/i }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalled())
    const call = fetchMock.mock.calls[0] as unknown as [string, RequestInit]
    expect(call[1].credentials).toBe('include')
    expect(call[1].method).toBe('POST')
  })
})
