import { GraduationCap } from 'lucide-react'
import { Link, Route, Routes } from 'react-router-dom'

import RegisterPage from './features/auth/RegisterPage'
import VerifyEmailPage from './features/auth/VerifyEmailPage'

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
        <p>
          <Link
            to="/register"
            className="inline-flex items-center justify-center rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] hover:opacity-90"
          >
            Créer mon compte
          </Link>
        </p>
      </section>
    </main>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
    </Routes>
  )
}

export default App
