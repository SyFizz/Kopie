#!/usr/bin/env bash
# =========================================================================
# Kopie — Génération des types TypeScript depuis contracts/openapi.yaml
# PLACEHOLDER (Story 1.2 : Contrat OpenAPI initial et types partagés)
#
# Implémentation cible (Story 1.2) :
#   pnpm dlx openapi-typescript contracts/openapi.yaml \
#     -o packages/shared-types/src/api.ts
#   pnpm --filter @kopie/shared-types build
#
# ⚠️ Ne PAS éditer packages/shared-types/ manuellement — c'est un artefact
# généré, qui doit rester en synchro avec contracts/openapi.yaml.
# =========================================================================

set -euo pipefail

echo "[gen-types] Placeholder — implémentation prévue en Story 1.2"
exit 0
