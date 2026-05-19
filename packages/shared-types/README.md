# @kopie/shared-types

Types TypeScript partagés entre `web-prof` et `web-eleve`, **générés** depuis `contracts/openapi.yaml`.

> ⚠️ **Ne JAMAIS éditer manuellement.** Toute modification doit passer par le contrat OpenAPI puis `scripts/gen-types.sh` (Story 1.2).

## Génération (Story 1.2)

```bash
pnpm dlx openapi-typescript ../../contracts/openapi.yaml -o src/api.ts
```
