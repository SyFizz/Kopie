import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { useAuth } from './AuthContext'
import { loginTeacher } from './api'

const loginSchema = z.object({
  email: z.string().email('Email invalide.'),
  password: z.string().min(1, 'Le mot de passe est requis.'),
})

export type LoginFormData = z.infer<typeof loginSchema>

export function LoginPage() {
  const { setAccessToken } = useAuth()
  const navigate = useNavigate()
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })

  const onSubmit = async (data: LoginFormData) => {
    setServerError(null)
    const result = await loginTeacher(data)
    if (result.ok) {
      setAccessToken(result.data.access_token)
      navigate('/dashboard', { replace: true })
      return
    }
    if (result.status === 0) {
      setServerError(result.error.message)
    } else if (result.status === 401) {
      setServerError('Email ou mot de passe incorrect.')
    } else if (result.status === 403) {
      setServerError(
        'Votre compte n\'est pas encore activé. Vérifiez votre boîte mail.',
      )
    } else if (result.status === 422) {
      setServerError('Données invalides : vérifiez vos champs.')
    } else if (result.status === 429) {
      setServerError(
        'Trop de tentatives. Veuillez réessayer dans quelques instants.',
      )
    } else {
      setServerError('Une erreur est survenue. Veuillez réessayer.')
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))] text-[hsl(var(--foreground))] px-4">
      <section className="w-full max-w-md rounded-xl border border-[hsl(var(--border))] bg-white p-8 shadow-sm space-y-6">
        <header className="space-y-2 text-center">
          <h1 className="text-2xl font-semibold">Connexion à votre espace enseignant</h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Bienvenue&nbsp;! Identifiez-vous pour accéder à votre tableau de bord.
          </p>
        </header>

        <form
          onSubmit={handleSubmit(onSubmit)}
          noValidate
          className="space-y-4"
          aria-describedby={serverError ? 'login-server-error' : undefined}
        >
          <div className="space-y-1">
            <label htmlFor="login-email" className="block text-sm font-medium">
              Adresse email
            </label>
            <input
              id="login-email"
              type="email"
              autoComplete="email"
              aria-invalid={errors.email ? 'true' : 'false'}
              aria-describedby={errors.email ? 'login-email-error' : undefined}
              className="w-full rounded-md border border-[hsl(var(--border))] bg-white px-3 py-2 text-sm shadow-sm focus:border-[hsl(var(--primary))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]/30"
              {...register('email')}
            />
            {errors.email ? (
              <p
                id="login-email-error"
                role="alert"
                className="text-sm text-[hsl(var(--destructive))]"
              >
                {errors.email.message}
              </p>
            ) : null}
          </div>

          <div className="space-y-1">
            <label
              htmlFor="login-password"
              className="block text-sm font-medium"
            >
              Mot de passe
            </label>
            <input
              id="login-password"
              type="password"
              autoComplete="current-password"
              aria-invalid={errors.password ? 'true' : 'false'}
              aria-describedby={
                errors.password ? 'login-password-error' : undefined
              }
              className="w-full rounded-md border border-[hsl(var(--border))] bg-white px-3 py-2 text-sm shadow-sm focus:border-[hsl(var(--primary))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]/30"
              {...register('password')}
            />
            {errors.password ? (
              <p
                id="login-password-error"
                role="alert"
                className="text-sm text-[hsl(var(--destructive))]"
              >
                {errors.password.message}
              </p>
            ) : null}
          </div>

          {serverError ? (
            <p
              id="login-server-error"
              role="alert"
              className="rounded-md border border-[hsl(var(--destructive))]/30 bg-[hsl(var(--destructive))]/5 px-3 py-2 text-sm text-[hsl(var(--destructive))]"
            >
              {serverError}
            </p>
          ) : null}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? 'Connexion en cours…' : 'Se connecter'}
          </button>
        </form>

        <footer className="text-center text-sm text-[hsl(var(--muted-foreground))] space-y-1">
          <p>
            Pas encore de compte ?{' '}
            <Link
              to="/register"
              className="font-medium text-[hsl(var(--primary))] hover:underline"
            >
              S&apos;inscrire
            </Link>
          </p>
          <p>
            <span
              aria-disabled="true"
              className="cursor-not-allowed text-[hsl(var(--muted-foreground))]"
              title="Bientôt disponible"
            >
              Mot de passe oublié&nbsp;?
            </span>
          </p>
        </footer>
      </section>
    </main>
  )
}

export default LoginPage
