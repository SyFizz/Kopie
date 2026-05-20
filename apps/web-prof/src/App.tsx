import { GraduationCap } from 'lucide-react'
import { Link, Navigate, Outlet, Route, Routes } from 'react-router-dom'

import { useAuth } from './features/auth/AuthContext'
import LoginPage from './features/auth/LoginPage'
import RegisterPage from './features/auth/RegisterPage'
import VerifyEmailPage from './features/auth/VerifyEmailPage'
import DashboardPage from './features/dashboard/DashboardPage'

function HomePage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))] text-[hsl(var(--foreground))]">
      <section className="text-center space-y-4">
        <GraduationCap
          aria-hidden="true"
          size={48}
          className="mx-auto text-[hsl(var(--primary))]"
        />
        <h1 className="text-3xl font-semibold">Kopie — Espace enseignant</h1>
        <p className="text-[hsl(var(--muted-foreground))]">
          Plateforme d&apos;évaluation sécurisée.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link
            to="/login"
            className="inline-flex items-center justify-center rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] hover:opacity-90"
          >
            Se connecter
          </Link>
          <Link
            to="/register"
            className="inline-flex items-center justify-center rounded-md border border-[hsl(var(--border))] bg-white px-4 py-2 text-sm font-medium hover:bg-[hsl(var(--accent))]"
          >
            Créer mon compte
          </Link>
        </div>
      </section>
    </main>
  )
}

/**
 * Garde de route : si l'utilisateur n'a pas d'access token en mémoire,
 * redirige vers ``/login``. Sans persistance (intentionnel — story 1.4),
 * un rafraîchissement de page renverra l'utilisateur sur la page de
 * connexion ; le silent-refresh via cookie httpOnly sera traité en
 * Story 1.5 ou via un ``useEffect`` au montage de ``AuthProvider``.
 */
export function PrivateRoute() {
  const { accessToken } = useAuth()
  return accessToken !== null ? <Outlet /> : <Navigate to="/login" replace />
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route element={<PrivateRoute />}>
        <Route path="/dashboard" element={<DashboardPage />} />
      </Route>
    </Routes>
  )
}

export default App
