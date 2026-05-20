import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '../App'
import { AuthProvider } from '../features/auth/AuthContext'

function renderApp(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('App (web-prof) — routing', () => {
  it("rend la home par défaut", () => {
    renderApp('/')
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      /Kopie.*Espace enseignant/i,
    )
  })

  it('affiche la page d\'inscription sur /register', () => {
    renderApp('/register')
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      /Créer un compte enseignant/i,
    )
  })

  it('affiche la page de connexion sur /login', () => {
    renderApp('/login')
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      /Connexion à votre espace enseignant/i,
    )
  })

  it('redirige /dashboard vers /login sans access token (PrivateRoute)', () => {
    renderApp('/dashboard')
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      /Connexion à votre espace enseignant/i,
    )
  })
})
