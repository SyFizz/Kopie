#!/usr/bin/env bash
# =========================================================================
# Kopie — Génération des types TypeScript depuis contracts/openapi.yaml
# Source de vérité unique : contracts/openapi.yaml
# Cible générée : packages/shared-types/src/api.ts
# =========================================================================
#
# Équivalent cross-platform : `pnpm gen:types` (script npm racine).
# Préférer `pnpm gen:types` sous Windows (PowerShell, cmd).
# Ce script reste compatible Unix/macOS/CI Linux.
#
# ⚠️ Anti-pattern à éviter (cf. Dev Notes story 1.2) :
#   Ne PAS utiliser `pnpm dlx openapi-typescript "$CONTRACT" -o "$OUTPUT"`.
#   `pnpm dlx` télécharge la *latest* (version non figée) à chaque exécution
#   et casse le contrat de reproductibilité (CI <-> local).
#   On utilise `pnpm exec` qui résout via le binaire installé en
#   `devDependencies` racine (version figée dans pnpm-lock.yaml).
# =========================================================================

set -euo pipefail

# Résolution du chemin racine du monorepo (parent de scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CONTRACT="$REPO_ROOT/contracts/openapi.yaml"
OUTPUT="$REPO_ROOT/packages/shared-types/src/api.ts"

if [[ ! -f "$CONTRACT" ]]; then
  echo "[gen-types] ERREUR : $CONTRACT introuvable" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"

echo "[gen-types] Génération depuis $CONTRACT"
# Version figée via devDependency racine (cf. en-tête : ne pas remplacer par `pnpm dlx`).
pnpm --silent --dir "$REPO_ROOT" exec openapi-typescript "$CONTRACT" -o "$OUTPUT"

echo "[gen-types] OK → $OUTPUT"
