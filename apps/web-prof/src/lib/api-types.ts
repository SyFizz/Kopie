// Ré-export typé du contrat OpenAPI partagé.
// Ne pas éditer @kopie/shared-types directement ; régénérer via `pnpm gen:types`.

import type { components, paths } from '@kopie/shared-types'

export type Teacher = components['schemas']['Teacher']
export type ApiError = components['schemas']['Error']

export type { components, paths }
