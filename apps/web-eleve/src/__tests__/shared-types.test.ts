import { describe, expect, it } from 'vitest'
import type { ApiError, Teacher } from '../lib/api-types'

describe('@kopie/shared-types — contract types', () => {
  it('Teacher type accepts a valid object', () => {
    const teacher: Teacher = {
      id: '550e8400-e29b-41d4-a716-446655440000',
      email: 'marie.dupont@example.fr',
      display_name: 'Marie Dupont',
      status: 'active',
      created_at: '2026-05-19T08:30:00Z',
      updated_at: '2026-05-19T08:30:00Z',
    }
    expect(teacher.email).toContain('@')
    expect(teacher.status).toBe('active')
  })

  it('ApiError type accepts a structured error', () => {
    const err: ApiError = {
      error: {
        code: 'ACCESS_EXPIRED',
        message: "L'accès a expiré.",
      },
    }
    expect(err.error.code).toBe('ACCESS_EXPIRED')
  })
})
