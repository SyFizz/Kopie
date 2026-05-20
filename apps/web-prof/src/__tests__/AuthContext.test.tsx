import { describe, expect, it, vi, afterEach } from 'vitest'
import { act, render, renderHook, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { AuthProvider, useAuth } from '../features/auth/AuthContext'
import { PrivateRoute } from '../App'

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <MemoryRouter>
    <AuthProvider>{children}</AuthProvider>
  </MemoryRouter>
)

describe('AuthContext', () => {
  const originalFetch = globalThis.fetch

  afterEach(() => {
    globalThis.fetch = originalFetch
  })

  it('expose accessToken=null initialement', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    expect(result.current.accessToken).toBeNull()
  })

  it('setAccessToken met à jour la valeur en mémoire', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    act(() => {
      result.current.setAccessToken('jwt.abc')
    })
    expect(result.current.accessToken).toBe('jwt.abc')
  })

  it('logout efface l\'access token même si l\'API échoue', async () => {
    globalThis.fetch = vi.fn(async () => {
      throw new TypeError('Failed to fetch')
    }) as unknown as typeof fetch

    const { result } = renderHook(() => useAuth(), { wrapper })
    act(() => {
      result.current.setAccessToken('jwt.abc')
    })

    await act(async () => {
      await result.current.logout()
    })

    expect(result.current.accessToken).toBeNull()
  })

  it('logout appelle POST /api/v1/auth/logout avec credentials:include', async () => {
    const fetchMock = vi.fn(async () => {
      return new Response(JSON.stringify({ message: 'Déconnecté.' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    })
    globalThis.fetch = fetchMock as unknown as typeof fetch

    const { result } = renderHook(() => useAuth(), { wrapper })
    act(() => result.current.setAccessToken('jwt.abc'))
    await act(async () => {
      await result.current.logout()
    })

    expect(fetchMock).toHaveBeenCalledTimes(1)
    const call = fetchMock.mock.calls[0] as unknown as [string, RequestInit]
    const [url, init] = call
    expect(url).toContain('/api/v1/auth/logout')
    expect(init.method).toBe('POST')
    expect(init.credentials).toBe('include')
    expect(result.current.accessToken).toBeNull()
  })

  it('useAuth hors AuthProvider lève une erreur explicite', () => {
    const consoleError = vi
      .spyOn(console, 'error')
      .mockImplementation(() => undefined)
    try {
      expect(() => renderHook(() => useAuth())).toThrow(
        /useAuth doit être utilisé/i,
      )
    } finally {
      consoleError.mockRestore()
    }
  })
})

describe('PrivateRoute', () => {
  function LoginPlaceholder() {
    return <div data-testid="login-page">login</div>
  }

  function ProtectedPlaceholder() {
    return <div data-testid="protected">contenu protégé</div>
  }

  it('redirige vers /login si aucun access token', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPlaceholder />} />
            <Route element={<PrivateRoute />}>
              <Route path="/dashboard" element={<ProtectedPlaceholder />} />
            </Route>
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    )
    expect(screen.getByTestId('login-page')).toBeInTheDocument()
    expect(screen.queryByTestId('protected')).not.toBeInTheDocument()
  })

  it('rend la route protégée quand un access token est présent', () => {
    // ``initialAccessToken`` court-circuite le flux login : il est utilisé
    // par les tests et sera réutilisé par la story 1.5 (rehydratation
    // silencieuse via ``/auth/refresh`` au démarrage).
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <AuthProvider initialAccessToken="jwt.value">
          <Routes>
            <Route path="/login" element={<LoginPlaceholder />} />
            <Route element={<PrivateRoute />}>
              <Route path="/dashboard" element={<ProtectedPlaceholder />} />
            </Route>
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    )
    expect(screen.getByTestId('protected')).toBeInTheDocument()
    expect(screen.queryByTestId('login-page')).not.toBeInTheDocument()
  })
})
