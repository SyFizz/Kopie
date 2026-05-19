import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import { registerTeacher } from './api'

const registerSchema = z.object({
  email: z.string().email('Email invalide.'),
  password: z
    .string()
    .min(12, 'Minimum 12 caractères.')
    .max(200, 'Maximum 200 caractères.'),
})

export type RegisterFormData = z.infer<typeof registerSchema>

export function RegisterPage() {
  const [successEmail, setSuccessEmail] = useState<string | null>(null)
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: '', password: '' },
  })

  const onSubmit = async (data: RegisterFormData) => {
    setServerError(null)
    const result = await registerTeacher(data)
    if (result.ok) {
      setSuccessEmail(data.email)
      return
    }
    if (result.status === 409) {
      setServerError('Cet email est déjà utilisé.')
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

  if (successEmail) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))] text-[hsl(var(--foreground))] px-4">
        <section
          role="status"
          className="max-w-md text-center space-y-3 rounded-xl border border-[hsl(var(--border))] bg-white p-8 shadow-sm"
        >
          <h1 className="text-2xl font-semibold">Vérifiez votre boîte mail</h1>
          <p className="text-[hsl(var(--muted-foreground))]">
            Un lien de confirmation vient d&apos;être envoyé à{' '}
            <strong>{successEmail}</strong>. Cliquez dessus pour activer votre
            compte (lien valable 24&nbsp;heures).
          </p>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Pensez à vérifier vos courriers indésirables.
          </p>
        </section>
      </main>
    )
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))] text-[hsl(var(--foreground))] px-4">
      <section className="w-full max-w-md rounded-xl border border-[hsl(var(--border))] bg-white p-8 shadow-sm space-y-6">
        <header className="space-y-2 text-center">
          <h1 className="text-2xl font-semibold">Créer un compte enseignant</h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Renseignez votre adresse professionnelle pour rejoindre Kopie.
          </p>
        </header>

        <form
          onSubmit={handleSubmit(onSubmit)}
          noValidate
          className="space-y-4"
          aria-describedby={serverError ? 'register-server-error' : undefined}
        >
          <div className="space-y-1">
            <label
              htmlFor="register-email"
              className="block text-sm font-medium"
            >
              Adresse email
            </label>
            <input
              id="register-email"
              type="email"
              autoComplete="email"
              aria-invalid={errors.email ? 'true' : 'false'}
              aria-describedby={errors.email ? 'register-email-error' : undefined}
              className="w-full rounded-md border border-[hsl(var(--border))] bg-white px-3 py-2 text-sm shadow-sm focus:border-[hsl(var(--primary))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]/30"
              {...register('email')}
            />
            {errors.email ? (
              <p
                id="register-email-error"
                role="alert"
                className="text-sm text-[hsl(var(--destructive))]"
              >
                {errors.email.message}
              </p>
            ) : null}
          </div>

          <div className="space-y-1">
            <label
              htmlFor="register-password"
              className="block text-sm font-medium"
            >
              Mot de passe
            </label>
            <input
              id="register-password"
              type="password"
              autoComplete="new-password"
              aria-invalid={errors.password ? 'true' : 'false'}
              aria-describedby={
                errors.password ? 'register-password-error' : 'register-password-hint'
              }
              className="w-full rounded-md border border-[hsl(var(--border))] bg-white px-3 py-2 text-sm shadow-sm focus:border-[hsl(var(--primary))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]/30"
              {...register('password')}
            />
            {errors.password ? (
              <p
                id="register-password-error"
                role="alert"
                className="text-sm text-[hsl(var(--destructive))]"
              >
                {errors.password.message}
              </p>
            ) : (
              <p
                id="register-password-hint"
                className="text-xs text-[hsl(var(--muted-foreground))]"
              >
                Minimum 12 caractères.
              </p>
            )}
          </div>

          {serverError ? (
            <p
              id="register-server-error"
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
            {isSubmitting ? 'Création du compte…' : "S'inscrire"}
          </button>
        </form>
      </section>
    </main>
  )
}

export default RegisterPage
