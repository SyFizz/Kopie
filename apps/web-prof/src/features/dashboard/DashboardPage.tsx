import { useNavigate } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'

/**
 * Placeholder tableau de bord enseignant (Story 1.4).
 *
 * Au MVP cette page se contente de confirmer la connexion et d'exposer un
 * bouton de déconnexion. Les widgets analytiques arriveront dans les
 * stories Epic 5 (résultats / journal) — voir epics.md.
 */
export function DashboardPage() {
  const { accessToken, logout } = useAuth()
  const navigate = useNavigate()

  const onLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <main className="min-h-screen bg-[hsl(var(--background))] text-[hsl(var(--foreground))] px-4 py-12">
      <section className="mx-auto max-w-3xl space-y-6 rounded-xl border border-[hsl(var(--border))] bg-white p-8 shadow-sm">
        <header className="space-y-1">
          <h1 className="text-2xl font-semibold">Tableau de bord</h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Vous êtes connecté à votre espace enseignant Kopie.
          </p>
        </header>

        <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))]/50 px-4 py-3 text-sm">
          <p className="font-medium">Session active</p>
          <p className="text-[hsl(var(--muted-foreground))]">
            Vos évaluations et accès élèves apparaîtront ici prochainement.
          </p>
        </div>

        <button
          type="button"
          onClick={onLogout}
          disabled={accessToken === null}
          className="rounded-md border border-[hsl(var(--border))] bg-white px-4 py-2 text-sm font-medium shadow-sm transition hover:bg-[hsl(var(--accent))] disabled:cursor-not-allowed disabled:opacity-60"
        >
          Se déconnecter
        </button>
      </section>
    </main>
  )
}

export default DashboardPage
