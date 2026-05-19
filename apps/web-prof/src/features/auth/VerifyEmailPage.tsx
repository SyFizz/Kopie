import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { verifyTeacherEmail } from './api'

type Status = 'pending' | 'success' | 'error'

export function VerifyEmailPage() {
  const [params] = useSearchParams()
  const token = params.get('token') ?? ''
  const [status, setStatus] = useState<Status>('pending')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function run() {
      if (!token) {
        setStatus('error')
        setErrorMessage('Lien de vérification incomplet.')
        return
      }
      const result = await verifyTeacherEmail(token)
      if (cancelled) return
      if (result.ok) {
        setStatus('success')
      } else {
        setStatus('error')
        setErrorMessage(
          result.status === 400
            ? 'Ce lien est invalide ou expiré. Veuillez vous réinscrire.'
            : 'Une erreur est survenue. Veuillez réessayer.',
        )
      }
    }

    void run()
    return () => {
      cancelled = true
    }
  }, [token])

  return (
    <main className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))] text-[hsl(var(--foreground))] px-4">
      <section
        role="status"
        aria-live="polite"
        className="max-w-md text-center space-y-4 rounded-xl border border-[hsl(var(--border))] bg-white p-8 shadow-sm"
      >
        {status === 'pending' ? (
          <>
            <h1 className="text-2xl font-semibold">
              Vérification en cours…
            </h1>
            <p className="text-[hsl(var(--muted-foreground))]">
              Merci de patienter.
            </p>
          </>
        ) : null}

        {status === 'success' ? (
          <>
            <h1 className="text-2xl font-semibold">Votre email est confirmé</h1>
            <p className="text-[hsl(var(--muted-foreground))]">
              Vous pouvez maintenant vous connecter à votre espace enseignant.
            </p>
            <Link
              to="/"
              className="inline-flex items-center justify-center rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] hover:opacity-90"
            >
              Retour à l&apos;accueil
            </Link>
          </>
        ) : null}

        {status === 'error' ? (
          <>
            <h1 className="text-2xl font-semibold">Lien invalide</h1>
            <p
              role="alert"
              className="text-sm text-[hsl(var(--destructive))]"
            >
              {errorMessage}
            </p>
            <Link
              to="/register"
              className="inline-flex items-center justify-center rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] hover:opacity-90"
            >
              Recommencer l&apos;inscription
            </Link>
          </>
        ) : null}
      </section>
    </main>
  )
}

export default VerifyEmailPage
