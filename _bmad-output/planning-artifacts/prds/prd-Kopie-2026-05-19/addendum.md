# Addendum — PRD Kopie

Détail technique, juridique et contexte qui dépasse le PRD principal. Le PRD reste la source des exigences ; ce document alimente architecture et implémentation.

## Stack technique (indicative)

| Couche | Choix indicatif | Note |
|--------|-----------------|------|
| Frontend | React, Vite, TailwindCSS | Enseignant + élève |
| Backend | Node/Fastify **ou** Python/FastAPI | À trancher en architecture |
| Base | PostgreSQL | |
| Auth enseignant | JWT local | OAuth2/SAML2 ENT → v1 |
| Temps réel | Non (MVP async) | |
| Déploiement | Docker Compose, images GHCR | Caddy ou Traefik |
| Licence | AGPL-3.0 | |

## Mécanismes techniques (hors PRD)

- **Lien d’accès :** token signé (HMAC ou JWT) embarquant l’identifiant d’accès, expiration alignée sur la fenêtre ; invalidation côté serveur à l’usage ou action enseignant.
- **Journal :** événements append-only, horodatage serveur (référence) + horodatage client si pertinent ; pas de modification post-soumission.
- **DevTools :** heuristiques navigateur documentées ; faux positifs possibles — posture « informer », pas bloquer.
- **Fullscreen / Visibility :** seules APIs autorisées côté élève ; pas d’extension ni binaire.

## Import CSV / Markdown `[à spécifier]`

**CSV proposé (hypothèse de travail) :**

```csv
type,question,choices,correct,points
single,"Capitale de la France?","Paris|Lyon|Marseille",Paris,1
short,"Définir globalization en une phrase",,,2
text,"Rédiger un paragraphe sur...",,,5
```

- `type` : `single` | `multiple` | `short` | `text`
- `choices` : séparateur `|` pour les choix ; `correct` : valeur(s) ou indices
- Encodage UTF-8 ; séparateur virgule ; guillemets pour champs contenant des virgules

**Markdown :** convention à définir (frontmatter + blocs par question) — story dédiée avant implémentation import.

## Limitations navigateur (session élève)

| Environnement | Attente |
|---------------|---------|
| Chrome / Firefox desktop récents | Support complet FR-16 à FR-20 |
| Safari macOS | Fullscreen et Visibility avec nuances — tester |
| iOS Safari | Fullscreen API limitée ; documenter dans le guide élève/enseignant ; événements partiels possibles |

## Contexte concurrentiel (synthèse Discovery)

Marché dominé par outils **classe entière** et proctoring lourd (Evalbox, Quilgo, Nexam, Exam.net). Kopie exploite : granularité 1 élève, posture trace-sans-sanction, PAP natif, AGPL + self-host, zéro install élève. Risque : ajout d’un mode « accès individuel » par un acteur établi — différenciation durable = cohérence produit + juridique + OSS.

## Décisions reportées à l’architecture

- Choix Node vs Python
- Schéma polymorphe des types de questions
- Stratégie chiffrement au repos (PostgreSQL, volumes)
- CI/CD, scans de vulnérabilités
- Modèle multi-tenant cloud officielle (schéma par enseignant vs instance dédiée établissement)

## Référence dump initial

Le périmètre fonctionnel détaillé provient du dump utilisateur du 2026-05-19 (session product brief). Toutes les capacités listées y sont couvertes par FR-1 à FR-43 du PRD, sauf éléments explicitement hors MVP (§5 et §6.2 du PRD).
