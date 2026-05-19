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

export type RegisterResult =
  | { ok: true; data: TeacherCreated }
  | { ok: false; status: number; error: ApiError['error'] }

export async function registerTeacher(
  payload: RegisterRequest,
): Promise<RegisterResult> {
  const response = await fetch(buildUrl('/api/v1/auth/register'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (response.status === 201) {
    const data = (await response.json()) as TeacherCreated
    return { ok: true, data }
  }
  let error: ApiError['error']
  try {
    const body = (await response.json()) as ApiError
    error = body.error
  } catch {
    error = { code: 'NETWORK_ERROR', message: 'Erreur réseau inattendue.' }
  }
  return { ok: false, status: response.status, error }
}

export type VerifyEmailResult =
  | { ok: true }
  | { ok: false; status: number; error: ApiError['error'] }

export async function verifyTeacherEmail(
  token: string,
): Promise<VerifyEmailResult> {
  const url = `${buildUrl('/api/v1/auth/verify-email')}?token=${encodeURIComponent(token)}`
  const response = await fetch(url)
  if (response.status === 200) {
    return { ok: true }
  }
  let error: ApiError['error']
  try {
    const body = (await response.json()) as ApiError
    error = body.error
  } catch {
    error = { code: 'NETWORK_ERROR', message: 'Erreur réseau inattendue.' }
  }
  return { ok: false, status: response.status, error }
}
