// Client HTTP minimal pour les endpoints d'authentification.
// Story 1.3 — fetch direct ; la version TanStack Query viendra avec Story 1.4.

import type { components } from '@kopie/shared-types'

export type RegisterRequest = components['schemas']['RegisterRequest']
export type TeacherCreated = components['schemas']['TeacherCreated']
export type ApiError = components['schemas']['Error']

const API_URL = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')

function buildUrl(path: string): string {
  return `${API_URL}${path}`
}

// `status: 0` est notre convention pour « pas de réponse HTTP » (DNS/CORS/offline).
// Les appelants doivent traiter ce cas comme une erreur réseau, pas un 4xx/5xx.
const NETWORK_ERROR = {
  code: 'NETWORK_ERROR',
  message: 'Impossible de joindre le serveur. Vérifiez votre connexion.',
} as const

async function parseErrorBody(
  response: Response,
): Promise<ApiError['error']> {
  try {
    const body = (await response.json()) as ApiError
    if (body?.error?.code && body.error.message) {
      return body.error
    }
  } catch {
    // ignore: corps non-JSON ou vide
  }
  return {
    code: 'UNEXPECTED_RESPONSE',
    message: 'Réponse inattendue du serveur.',
  }
}

export type RegisterResult =
  | { ok: true; data: TeacherCreated }
  | { ok: false; status: number; error: ApiError['error'] }

export async function registerTeacher(
  payload: RegisterRequest,
): Promise<RegisterResult> {
  let response: Response
  try {
    response = await fetch(buildUrl('/api/v1/auth/register'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch {
    return { ok: false, status: 0, error: { ...NETWORK_ERROR } }
  }

  if (response.status === 201) {
    try {
      const data = (await response.json()) as TeacherCreated
      return { ok: true, data }
    } catch {
      return { ok: false, status: response.status, error: { ...NETWORK_ERROR } }
    }
  }

  const error = await parseErrorBody(response)
  return { ok: false, status: response.status, error }
}

export type VerifyEmailResult =
  | { ok: true }
  | { ok: false; status: number; error: ApiError['error'] }

export async function verifyTeacherEmail(
  token: string,
): Promise<VerifyEmailResult> {
  const url = `${buildUrl('/api/v1/auth/verify-email')}?token=${encodeURIComponent(token)}`
  let response: Response
  try {
    response = await fetch(url)
  } catch {
    return { ok: false, status: 0, error: { ...NETWORK_ERROR } }
  }

  if (response.status === 200) {
    return { ok: true }
  }

  const error = await parseErrorBody(response)
  return { ok: false, status: response.status, error }
}
