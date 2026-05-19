---
stepsCompleted: [1, 2, 3, 4]
status: complete
completedAt: 2026-05-19
revisedAt: 2026-05-19
revisionNote: |
  Clôture des 5 gaps identifiés par bmad-check-implementation-readiness :
  - G-1 : Story 2.7 (Import Markdown) créée
  - Q-1 : Story 4.6 étoffée avec contrat endpoint drafts
  - Q-2 : endpoint drafts documenté dans architecture.md
  - G-2 : Story 6.6 ajoute exigence volume chiffré au repos
  - G-3 : Story 6.5 liste explicite des routes publiques sous rate-limit
  - Bonus : U-1 (jest-axe ajouté à la CI), Q-4 (CSV encodage et séparateurs précisés)
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-Kopie-2026-05-19/prd.md
  - _bmad-output/planning-artifacts/prds/prd-Kopie-2026-05-19/addendum.md
  - _bmad-output/planning-artifacts/prds/prd-Kopie-2026-05-19/.decision-log.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
  - _bmad-output/planning-artifacts/ux-design-directions.html
  - _bmad-output/planning-artifacts/briefs/brief-Kopie-2026-05-19/brief.md
  - _bmad-output/planning-artifacts/briefs/brief-Kopie-2026-05-19/addendum.md
---

# Kopie - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Kopie, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR-1: Un enseignant peut créer un compte avec email et mot de passe (validation email par lien de confirmation au MVP).
FR-2: Un enseignant peut se connecter et maintenir une session authentifiée (JWT) jusqu'à expiration ou déconnexion ; routes non authentifiées renvoient 401 ; déconnexion invalide le jeton côté client.
FR-3: Un enseignant peut consulter et modifier son profil (nom affiché, email, mot de passe).
FR-4: Le système garantit l'isolation stricte des évaluations, accès individuels, sessions et journaux par enseignant ; aucune requête API enseignant ne retourne un identifiant d'un autre enseignant.
FR-5: Un enseignant peut créer une évaluation avec des questions des types : choix (unique ou multiple), réponse courte, texte libre ; chaque question a énoncé, pondération optionnelle et critères de correction pour les choix ; schéma extensible pour nouveaux types.
FR-6: Un enseignant peut activer, par évaluation, la randomisation de l'ordre des questions et/ou des propositions de choix.
FR-7: Un enseignant peut importer des questions depuis un fichier CSV ou Markdown selon un format documenté ; import invalide : message d'erreur lisible, aucune importation partielle silencieuse.
FR-8: Un enseignant peut enregistrer des questions dans sa banque et les réinsérer dans une évaluation.
FR-9: Un enseignant peut créer plusieurs variantes liées à une même évaluation (ex. standard et PAP) partageant titre et métadonnées communes ; règle de synchronisation du titre documentée.
FR-10: Un enseignant peut définir sur l'évaluation : durée nominale, interdiction de retour arrière après validation d'une question (optionnel).
FR-11: Un enseignant peut créer un accès individuel pour un élève (nom, prénom), associé à une variante et à une fenêtre temporelle (début/fin) ; lien non devinable (token signé HMAC ou JWT) ; usage unique pour démarrer une session complète.
FR-12: Un enseignant peut configurer par accès individuel : tiers-temps +33 % ou +50 %, police OpenDyslexic, agrandissement du texte ; durée effective du timer reflète le coefficient.
FR-13: Un enseignant peut invalider un accès individuel non utilisé, ou le réinitialiser avant toute session démarrée ; lien invalidé : HTTP 410 ou équivalent avec message élève explicite ; statut « invalidée » visible dans l'historique.
FR-14: Le système refuse le démarrage ou la poursuite d'une session en dehors de la fenêtre temporelle de l'accès individuel.
FR-15: Un élève peut commencer une session en saisissant nom et prénom, sans créer de compte ; données minimales, pas de tracking publicitaire, conservation limitée.
FR-16: Au démarrage de la session, le système demande le passage en plein écran via Fullscreen API ; si refusé (desktop), l'élève est informé et la session ne démarre pas ; iOS documenté en best-effort.
FR-17: Chaque sortie du plein écran est enregistrée dans le journal de session avec horodatage et durée hors plein écran.
FR-18: Chaque changement d'onglet ou perte de visibilité (Page Visibility API) est journalisé.
FR-19: Les raccourcis copier-coller (Ctrl/Cmd+C/V) sont bloqués pendant la session (hors scope : capture écran, second appareil).
FR-20: L'ouverture des outils de développement est détectée et journalisée comme événement suspect.
FR-21: Un timer visible décompte la durée (après aménagements) ; à expiration, soumission automatique des réponses déjà saisies.
FR-22: À chaque événement suspect, un message visuel non bloquant informe l'élève que l'événement a été enregistré.
FR-23: Si activé sur l'évaluation, l'élève ne peut pas revenir modifier une question déjà validée.
FR-24: L'élève doit confirmer explicitement avant la soumission finale.
FR-25: Le système enregistre horodaté : démarrage, chaque réponse soumise, sorties plein écran, pertes de focus, tentatives copier-coller, DevTools, soumission finale.
FR-26: Seul l'enseignant propriétaire de l'accès individuel peut consulter le journal de session associé.
FR-27: Un enseignant peut exporter le journal en PDF et CSV.
FR-28: Le système affiche un résumé : nombre d'événements suspects, durée totale hors focus, durée totale de la session.
FR-29: Les questions à choix sont corrigées automatiquement à la soumission.
FR-30: Un enseignant voit les réponses courtes et productions écrites pour correction manuelle.
FR-31: Un enseignant peut attribuer un score et/ou une appréciation textuelle par session.
FR-32: Un enseignant peut exporter les résultats d'un élève (PDF, CSV).
FR-33: Un enseignant voit l'historique de tous les accès individuels avec statut : en attente, en cours, terminée, expirée, invalidée.
FR-34: Un déployeur peut configurer l'application via variables d'environnement (.env documenté).
FR-35: Un déployeur peut lancer l'application via Docker Compose incluant application, PostgreSQL et reverse proxy (Caddy ou Traefik).
FR-36: La configuration Docker documentée permet HTTPS via Let's Encrypt.
FR-37: Le déploiement inclut un mécanisme de migration de schéma PostgreSQL versionné.
FR-38: Le dépôt fournit README et guide d'auto-hébergement suffisants pour un déploiement sans support commercial.
FR-39: Le projet maintient une instance cloud officielle gratuite au lancement, fonctionnellement équivalente au MVP self-host (même codebase).
FR-40: Les accès individuels utilisent un token signé non devinable, invalidé après usage ou expiration.
FR-41: Les données d'élève ne sont conservées que pendant la durée configurée par le déployeur ; au-delà, suppression ou anonymisation (défaut proposé : 12 mois).
FR-42: Données chiffrées au repos et en transit (TLS obligatoire en production).
FR-43: Les endpoints d'authentification et d'accès individuel sont protégés contre injection SQL, XSS, CSRF et abus par rate limiting.

### NonFunctional Requirements

NFR-1: La session élève reste utilisable sur matériel modeste et connexion ADSL (FCP élève < 3 s ; interactions formulaire < 100 ms ressenti).
NFR-2: Pas de WebSocket requis au MVP.
NFR-3: OWASP Top 10 mitigé ; audits de dépendances dans CI.
NFR-4: Secrets hors dépôt ; rotation documentée pour self-hosters.
NFR-5: Interface élève conforme RGAA niveau AA ; OpenDyslexic disponible via aménagement (FR-12).
NFR-6: Chrome et Firefox récents : support complet ; Safari/iOS : best-effort avec limitations Fullscreen documentées.
NFR-7: Chaînes externalisées (i18n) ; français livré au MVP.
NFR-8: Logs techniques structurés côté serveur ; pas de données élève en clair dans les logs.
NFR-9: Hébergement et traitement Union européenne uniquement ; pas de transfert hors UE ; pas de sous-traitant US critique dans la chaîne MVP.
NFR-10: Durée de conservation paramétrable par le déployeur (défaut proposé : 12 mois) ; base légale et documentation RGPD pour cloud et self-host.
NFR-11: Traitement minimal des mineurs ; pas de compte élève ; pas de profilage ni tracking publicitaire.
NFR-12: Code AGPL-3.0 ; self-host gratuit sans restriction fonctionnelle MVP.
NFR-13: Web responsive (enseignant + élève) ; pas d'app native MVP.
NFR-14: Bundle élève optimisé (code-splitting, dépendances minimales) pour FCP < 3 s.
NFR-15: Cibles tactiles session élève ≥ 44×44 px ; focus visible ; statuts = icône + texte (pas couleur seule) ; `prefers-reduced-motion` respecté.

### Additional Requirements

- **Starter template (Epic 1 Story 1)** : Scaffold monorepo pnpm + create-vite@9.0.7 ×2 (web-prof, web-eleve) + uv + FastAPI 0.136.1 + Tailwind v4 + Docker Compose (postgres, api, web-prof, web-eleve) + Caddy (TLS Let's Encrypt) — voir commandes d'init dans architecture.md § Starter Template Evaluation.
- **Stack tranchée** : Backend Python FastAPI ≥3.12 + uv ; front React/Vite/TypeScript ; PostgreSQL + SQLAlchemy 2.x async + Alembic ; monorepo pnpm workspaces.
- **Dual-surface** : Deux apps distinctes — `prof.kopie.cc` (enseignant), `eleve.kopie.cc/s/{token}` (élève), `api.kopie.cc` (API REST) ; CORS origines explicites uniquement.
- **Auth enseignant** : JWT access (court) + refresh cookie httpOnly Secure SameSite=Strict sur prof.kopie.cc ; bcrypt (passlib) pour mots de passe.
- **Auth élève** : JWT signé embarqué dans le lien ; validation à chaque requête ; pas de header Authorization.
- **Multi-tenant** : `teacher_id` UUID FK sur toutes tables métier ; filtre obligatoire au repository ; tests d'isolation cross-teacher automatisés.
- **Questions** : JSONB `content` + colonnes `type`, `schema_version` pour extensibilité FR-5.
- **Machine à états accès** : en attente → en cours → terminée / expirée / invalidée ; distinction accès (token) vs session (passage).
- **Journal** : POST batch `POST /api/v1/sessions/{id}/events` + header `X-Idempotency-Key` obligatoire ; horodatage serveur authoritative ; catalogue `event_types.py`.
- **Drafts réponses élève** : `POST /api/v1/sessions/{id}/answers` (idempotent par `question_id` + `X-Idempotency-Key`) appelé en debounce 2 s ou perte de focus ; `GET /api/v1/sessions/{id}/answers` pour la reprise ; distinct du journal (mutable jusqu'à soumission, gelé après) — Story 4.6.
- **Session abandonnée** : sauvegarde incrémentale via endpoint drafts ci-dessus + reprise tant que session non soumise ; pas de nouveau lien requis.
- **Polling enseignant** : `GET /api/v1/accesses/{id}` avec refetchInterval 5s si statut pending/in_progress (pas de WebSocket).
- **OpenAPI** : `contracts/openapi.yaml` versionné dès story 1 ; types front générés via openapi-typescript → `packages/shared-types` (régénération obligatoire après changement API).
- **Formats API** : JSON snake_case ; dates ISO 8601 UTC ; erreurs `{ "error": { "code", "message", "details" } }` ; HTTP 410 pour accès invalidé.
- **Rate limiting** : slowapi sur `/api/v1/auth/*` (Story 1.4) ET routes élève publiques (Story 6.5) — `accesses/by-token`, `sessions`, `answers`, `events`, `submit` — seuils par route documentés et ajustables via `.env`.
- **Logs** : structlog JSON ; jamais nom/prénom élève en clair ; corrélation request_id / session_id.
- **Rétention** : job planifié purge ; défaut 12 mois via `.env`.
- **CI** : GitHub Actions — ruff, mypy, pytest, vitest, **jest-axe (parcours élève — UX-DR19, NFR-15)**, build, scan deps ; images GHCR.
- **Chiffrement repos** : disque managé hébergeur UE au MVP (pas de chiffrement applicatif par champ) ; **exigence rendue explicite dans le guide self-host (Story 6.6) pour conformité FR-42**.
- **Import CSV** : format hypothèse documenté (type, question, choices, correct, points) ; UTF-8 ± BOM ; séparateur virgule ou point-virgule auto-détecté (compatibilité Excel FR) — voir PRD addendum + Story 2.6.
- **Import Markdown** : **Story 2.7 dédiée** — spécification + implémentation ; convention publiée dans `docs/imports/markdown-format.md`.
- **Documentation légale RGPD** : `docs/legal/` — story avant bêta publique.
- **SMTP** : validation email compte enseignant (async).
- **Pas de Redis, SSO ENT, WebSocket, e2e** au MVP (reportés post-MVP).

### UX Design Requirements

UX-DR1: Implémenter le design system Tailwind CSS v4 + shadcn/ui (Radix) avec thèmes `theme-teacher` (dense, pro) et `theme-student` (minimal, apaisant) selon direction visuelle **D2 — Calme professionnel** (primary `#2563eb`, fonds slate clair).
UX-DR2: Définir tokens CSS sémantiques (couleurs HSL, typo, espacements 4px base) — `--primary`, `--success`, `--warning`, `--info`, `--destructive` réservé aux actions irréversibles enseignant uniquement, jamais pour événements d'intégrité élève.
UX-DR3: Composant `AccessStatusBadge` — statuts en attente, en cours, terminée, expirée, invalidée avec icône + texte ; couleurs D2 (pas de rouge « triche »).
UX-DR4: Composant `CopyLinkButton` — CTA primaire post-création accès avec états default/copied/error ; annonce accessibilité « Lien copié ».
UX-DR5: Composant `AccessWizard` — wizard linéaire ≤ 3 étapes (élève → fenêtre/variante → aménagements) avec progression « Étape X/3 », défauts intelligents (dernière fenêtre, preset PAP).
UX-DR6: Composant `StudentSessionShell` — layout plein écran session élève, chrome minimal ; variants `font-dyslexic` (OpenDyslexic chargement conditionnel) et `--text-scale` 125 %/150 %.
UX-DR7: Composant `IntegrityToast` — toast bleu informatif non bloquant (4–6 s, dismissible) pour événements journalisés ; vocabulaire « enregistré », pas « triche/fraude/suspect » côté élève.
UX-DR8: Composant `TransparencyBanner` — écran « Ce qui est enregistré » avant démarrage session (confiance avant contrôle).
UX-DR9: Composant `JournalSummary` + `JournalTimeline` — résumé synthétique (événements suspects, durées) avant chronologie détaillée ; vocabulaire neutre (« événements », pas « infractions »).
UX-DR10: Composant `QuestionRenderer` — rendu types MVP : choix unique/multiple, réponse courte, texte libre ; option une question à la fois selon paramètre évaluation.
UX-DR11: Navigation enseignant — sidebar fixe 240px (Évaluations · Accès · Banque · Profil) + fil d'Ariane sur fiches profondes ; responsive drawer < 768px.
UX-DR12: Navigation élève — parcours linéaire sans menu global ; pas de hamburger.
UX-DR13: Golden path UJ-1 — bouton primaire « Envoyer à un élève » / « Créer un accès » sur fiche évaluation ; time-to-link < 5 min (SM-2).
UX-DR14: Écran de fin session élève — message apaisant « Votre copie a bien été envoyée » ; pas d'accès à la note au MVP.
UX-DR15: Empty states guidés — première utilisation « un élève, un lien » avec CTA vers création évaluation ou accès.
UX-DR16: Fiche accès terminé UJ-3 — onglets Réponses / Journal sur même fiche ; correction hybride visible ; export PDF/CSV pour dossier.
UX-DR17: Messages d'échec actionnables — fenêtre expirée, plein écran refusé, session déjà soumise, navigateur limité (Safari/iOS dégradation explicite, pas de promesse verrouillage total).
UX-DR18: Hiérarchie boutons — max 1 primaire par écran ; destructif (invalider accès) uniquement pour actions irréversibles enseignant.
UX-DR19: Contraste RGAA AA ≥ 4,5:1 sur texte session élève ; texte 16px min ; eslint-plugin-jsx-a11y + tests jest-axe sur parcours élève.
UX-DR20: Responsive — session élève mobile-first (colonne unique max-w-2xl) ; enseignant desktop-first (sidebar + max-w-6xl) ; breakpoints Tailwind sm/md/lg.
UX-DR21: Copywriting — vouvoiement ; zéro libellé « triche / fraude / suspect » côté élève ; toasts et bandeaux informatifs, pas accusateurs.
UX-DR22: Iconographie Lucide React ; mode clair uniquement au MVP (dark mode v2).
UX-DR23: Chargement — skeleton listes enseignant ; spinner sur bouton ; saisie non bloquée en session ; honnêteté réseau (retry, file d'attente visible pour réponses longues).
UX-DR24: Modales — confirmation soumission (irréversible) et invalider accès (destructif) avec focus trap.
UX-DR25: Prévisualisation élève optionnelle post-création accès (aménagements PAP visibles avant envoi).

### FR Coverage Map

FR-1: Epic 1 — Inscription enseignant avec validation email
FR-2: Epic 1 — Connexion et session JWT
FR-3: Epic 1 — Gestion du profil enseignant
FR-4: Epic 1 — Isolation stricte des données par enseignant
FR-5: Epic 2 — Composer une évaluation (types de questions MVP)
FR-6: Epic 2 — Randomisation questions et choix
FR-7: Epic 2 — Import de questions CSV (Story 2.6) + Markdown (Story 2.7)
FR-8: Epic 2 — Banque de questions réutilisable
FR-9: Epic 2 — Variantes d'évaluation (standard / PAP)
FR-10: Epic 2 — Paramètres de session sur l'évaluation
FR-11: Epic 3 — Générer un accès individuel signé
FR-12: Epic 3 — Aménagements par accès (tiers-temps, dyslexie, agrandissement)
FR-13: Epic 3 — Invalider ou réinitialiser un accès
FR-14: Epic 3 — Expiration hors fenêtre temporelle
FR-15: Epic 4 — Identification élève sans compte
FR-16: Epic 4 — Plein écran au démarrage
FR-17: Epic 4 — Journalisation sorties plein écran
FR-18: Epic 4 — Journalisation perte de focus
FR-19: Epic 4 — Blocage copier-coller
FR-20: Epic 4 — Détection DevTools journalisée
FR-21: Epic 4 — Timer et soumission automatique
FR-22: Epic 4 — Avertissements non bloquants
FR-23: Epic 4 — Navigation sans retour arrière (optionnel)
FR-24: Epic 4 — Confirmation de soumission
FR-25: Epic 5 — Enregistrement exhaustif du journal
FR-26: Epic 5 — Consultation journal réservée à l'enseignant propriétaire
FR-27: Epic 5 — Export du journal PDF et CSV
FR-28: Epic 5 — Résumé synthétique du journal
FR-29: Epic 5 — Correction automatique des choix
FR-30: Epic 5 — Correction manuelle des questions ouvertes
FR-31: Epic 5 — Note ou appréciation par session
FR-32: Epic 5 — Export des résultats élève PDF et CSV
FR-33: Epic 3 — Historique des accès individuels avec statuts
FR-34: Epic 6 — Configuration par variables d'environnement
FR-35: Epic 6 — Docker Compose (app, PostgreSQL, reverse proxy)
FR-36: Epic 6 — HTTPS automatique Let's Encrypt
FR-37: Epic 6 — Migrations PostgreSQL versionnées
FR-38: Epic 6 — Documentation auto-hébergement
FR-39: Epic 6 — Instance cloud officielle gratuite
FR-40: Epic 3 — Token signé à usage contrôlé
FR-41: Epic 6 — Minimisation et rétention données élève
FR-42: Epic 6 — Chiffrement au repos et en transit
FR-43: Epic 1/3/6 — Protection endpoints (rate limiting, OWASP)

## Epic List

### Epic 1: Fondation plateforme et espace enseignant
Un enseignant peut s'inscrire, se connecter, gérer son profil et disposer d'un espace isolé sur une base technique déployable.
**FRs couverts:** FR-1, FR-2, FR-3, FR-4

### Epic 2: Composer et organiser les évaluations
Marie peut créer des évaluations sur mesure, gérer sa banque, importer des questions (CSV et Markdown) et définir des variantes (standard / PAP).
**FRs couverts:** FR-5, FR-6, FR-7 (Story 2.6 CSV + Story 2.7 Markdown), FR-8, FR-9, FR-10

### Epic 3: Publier un accès individuel à un élève
Marie envoie un lien nominatif à un élève en moins de 5 minutes, avec fenêtre, aménagements et suivi des statuts (golden path UJ-1).
**FRs couverts:** FR-11, FR-12, FR-13, FR-14, FR-33, FR-40

### Epic 4: Passer la session d'évaluation (côté élève)
Lucas peut passer sa session de bout en bout avec intégrité tracée et soumission fiable (UJ-2).
**FRs couverts:** FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21, FR-22, FR-23, FR-24

### Epic 5: Consulter résultats, journal et corriger
Marie consulte réponses et journal, corrige, attribue note/appréciation et exporte pour justifier sa décision (UJ-3).
**FRs couverts:** FR-25, FR-26, FR-27, FR-28, FR-29, FR-30, FR-31, FR-32

### Epic 6: Déployer, sécuriser et exploiter Kopie
Un déployeur peut installer, configurer, sécuriser et maintenir Kopie en conformité RGPD (self-host + cloud officielle).
**FRs couverts:** FR-34, FR-35, FR-36, FR-37, FR-38, FR-39, FR-41, FR-42, FR-43

## Epic 1: Fondation plateforme et espace enseignant

Un enseignant peut s'inscrire, se connecter, gérer son profil et disposer d'un espace isolé sur une base technique déployable (monorepo, API, front prof, isolation multi-tenant).

### Story 1.1: Scaffold monorepo et infrastructure locale

As a **développeur / équipe projet**,
I want **initialiser le monorepo pnpm avec les apps web-prof, web-eleve, l'API FastAPI et PostgreSQL via Docker Compose**,
So that **l'équipe dispose d'une base exécutable pour livrer les fonctionnalités enseignant et élève**.

**Acceptance Criteria:**

**Given** un dépôt vide
**When** les commandes d'initialisation documentées dans architecture.md sont exécutées
**Then** la structure `apps/web-prof`, `apps/web-eleve`, `apps/api`, `packages/shared-types` et `docker-compose.yml` existent
**And** `docker compose up` démarre PostgreSQL et l'API en mode développement
**And** `pnpm --filter web-prof dev` et `pnpm --filter web-eleve dev` lancent les deux frontends
**And** Tailwind CSS v4 est configuré sur les deux apps avec thèmes `theme-teacher` et `theme-student` (direction D2)

### Story 1.2: Contrat OpenAPI initial et types partagés

As a **développeur**,
I want **un fichier `contracts/openapi.yaml` versionné et la génération automatique de `packages/shared-types`**,
So that **les fronts et l'API partagent un contrat stable dès la première story métier**.

**Acceptance Criteria:**

**Given** le monorepo scaffoldé (Story 1.1)
**When** le contrat OpenAPI définit au minimum les schémas `Teacher`, `Error` et les routes `/api/v1/health`
**Then** le script `scripts/gen-types.sh` régénère `packages/shared-types` sans erreur
**And** les deux apps front importent les types générés
**And** l'API FastAPI expose `/docs` aligné sur le même contrat

### Story 1.3: Inscription enseignant avec validation email

As an **enseignant**,
I want **créer un compte avec email et mot de passe puis valider mon email via un lien**,
So that **j'accède à mon espace personnel sécurisé**.

**Acceptance Criteria:**

**Given** je ne possède pas encore de compte
**When** je soumets un email valide et un mot de passe respectant la politique documentée (longueur, complexité)
**Then** un compte enseignant est créé en statut « non confirmé »
**And** un email de confirmation est envoyé de façon asynchrone (SMTP configurable)
**When** je clique sur le lien de confirmation
**Then** mon compte passe en statut « actif » et un espace vide m'est attribué (FR-1)
**And** aucune donnée d'un autre enseignant n'est visible

### Story 1.4: Connexion enseignant et gestion de session JWT

As an **enseignant**,
I want **me connecter et rester authentifié jusqu'à expiration ou déconnexion**,
So that **j'accède à mon espace sans me reconnecter à chaque action**.

**Acceptance Criteria:**

**Given** un compte enseignant actif
**When** je saisis email et mot de passe corrects
**Then** je reçois un JWT access (court) et un refresh token en cookie httpOnly `Secure` `SameSite=Strict` sur le domaine prof (FR-2)
**When** j'appelle une route enseignant sans token valide
**Then** l'API renvoie HTTP 401
**When** je me déconnecte
**Then** le jeton côté client est invalidé et le cookie refresh est supprimé
**And** slowapi applique un rate limiting sur `/api/v1/auth/*` (FR-43 partiel)

### Story 1.5: Gestion du profil enseignant

As an **enseignant**,
I want **consulter et modifier mon nom affiché, email et mot de passe**,
So that **mes informations de compte restent à jour**.

**Acceptance Criteria:**

**Given** je suis connecté
**When** j'ouvre la page Profil
**Then** je vois mon nom affiché, email et options de modification (FR-3, UX-DR11)
**When** je modifie mon mot de passe avec l'ancien mot de passe correct
**Then** le changement est enregistré et je dois me reconnecter si configuré
**When** je modifie mon email
**Then** une nouvelle validation email est requise avant activation

### Story 1.6: Isolation des données enseignant

As an **enseignant**,
I want **la garantie que seules mes évaluations, accès, sessions et journaux me sont accessibles**,
So that **la confidentialité de mes élèves et de ma pratique est assurée**.

**Acceptance Criteria:**

**Given** deux enseignants A et B avec chacun des données métier
**When** l'enseignant A appelle toute route API authentifiée avec son JWT
**Then** aucun identifiant ou enregistrement appartenant à B n'est retourné (FR-4)
**And** chaque repository filtre systématiquement par `teacher_id`
**And** un test automatisé pytest tente un accès cross-teacher et échoue (403 ou 404)
**And** structlog n'inclut jamais de nom/prénom élève en clair (NFR-8)

## Epic 2: Composer et organiser les évaluations

Marie peut créer des évaluations sur mesure, gérer sa banque, importer des questions et définir des variantes (standard / PAP).

### Story 2.1: Créer une évaluation avec questions de base

As an **enseignant**,
I want **créer une évaluation avec des questions à choix unique, choix multiple, réponse courte et texte libre**,
So that **je prépare un sujet adapté à ma matière**.

**Acceptance Criteria:**

**Given** je suis connecté
**When** je crée une nouvelle évaluation avec titre, consignes et durée nominale
**Then** je peux ajouter des questions des types : choix unique, choix multiple, réponse courte, texte libre (FR-5)
**And** chaque question a un énoncé, une pondération optionnelle et des critères de correction pour les choix
**And** le modèle de données utilise JSONB + `type` + `schema_version` pour extensibilité future
**And** l'UI enseignant affiche un empty state guidé si aucune évaluation n'existe (UX-DR15)

### Story 2.2: Banque de questions personnelle

As an **enseignant**,
I want **enregistrer des questions dans ma banque et les réinsérer dans une évaluation**,
So that **je réutilise mon travail sans tout recréer**.

**Acceptance Criteria:**

**Given** une question existante dans une évaluation
**When** je choisis « Ajouter à la banque »
**Then** la question est copiée dans ma banque personnelle (FR-8)
**When** j'édite une évaluation et ouvre la banque
**Then** je peux insérer une question de la banque dans l'évaluation courante
**And** seules mes questions de banque sont listées (isolation teacher_id)

### Story 2.3: Variantes d'évaluation (standard et PAP)

As an **enseignant**,
I want **créer plusieurs variantes liées à une même évaluation (ex. standard et PAP)**,
So that **j'adapte le même sujet aux besoins de mes élèves**.

**Acceptance Criteria:**

**Given** une évaluation mère avec titre et métadonnées communes
**When** je crée une variante « PAP »
**Then** elle partage le titre et métadonnées selon la règle documentée (propagation ou synchronisation explicite) (FR-9)
**And** le contenu des questions peut différer de la variante standard
**When** je génère un accès individuel
**Then** je peux choisir la variante associée

### Story 2.4: Randomisation des questions et choix

As an **enseignant**,
I want **activer la randomisation de l'ordre des questions et/ou des propositions de choix**,
So that **je réduis la facilité de copie entre élèves**.

**Acceptance Criteria:**

**Given** une évaluation avec au moins deux questions ou choix multiples
**When** j'active la randomisation des questions et/ou des propositions
**Then** le paramètre est persisté sur l'évaluation (FR-6)
**When** un élève démarre une session
**Then** l'ordre présenté reflète la randomisation (seed stable par session)

### Story 2.5: Paramètres de session sur l'évaluation

As an **enseignant**,
I want **définir la durée nominale et l'interdiction de retour arrière après validation d'une question**,
So that **je cadre le passage de l'élève selon mes règles pédagogiques**.

**Acceptance Criteria:**

**Given** une évaluation en édition
**When** je définis la durée nominale en minutes
**Then** la valeur est enregistrée (FR-10)
**When** j'active « pas de retour arrière après validation »
**Then** le paramètre est persisté et transmis à la session élève (FR-23)
**And** la durée nominale sert de base au calcul du timer (avant aménagements accès)

### Story 2.6: Import de questions depuis CSV

As an **enseignant**,
I want **importer des questions depuis un fichier CSV au format documenté**,
So that **je gagne du temps sur la composition de grands sujets**.

**Acceptance Criteria:**

**Given** un fichier CSV conforme au format hypothèse (type, question, choices, correct, points) du PRD addendum
**When** je lance l'import sur une évaluation ou la banque
**Then** les questions valides sont créées (FR-7 partiel — volet CSV)
**And** l'encodage UTF-8 (avec ou sans BOM) est accepté
**And** le séparateur est auto-détecté entre virgule et point-virgule (compatibilité Excel FR)
**When** le fichier contient des erreurs (type invalide, ligne mal formée, encodage incompatible)
**Then** un message d'erreur lisible liste les problèmes avec numéro de ligne
**And** aucune importation partielle silencieuse n'est effectuée (transaction atomique : tout ou rien)
**And** des fixtures CSV réalistes (1 valide, 1 avec erreurs, 1 Excel FR) sont incluses dans les tests

### Story 2.7: Spécification et import de questions depuis Markdown

As an **enseignant**,
I want **importer des questions depuis un fichier Markdown selon une convention documentée**,
So that **je réutilise mes contenus rédigés en Markdown sans conversion intermédiaire**.

**Acceptance Criteria:**

**Given** la convention Markdown documentée (à spécifier dans cette story : frontmatter YAML par fichier + blocs `## Question N` avec syntaxe pour type, énoncé, choix, bonne réponse, points)
**When** la spécification est validée et publiée dans `docs/imports/markdown-format.md`
**Then** elle couvre les 4 types MVP : `single`, `multiple`, `short`, `text`
**And** elle fournit au moins 2 exemples complets (sujet simple + sujet avec aménagements)
**Given** un fichier Markdown conforme à la spécification
**When** je lance l'import sur une évaluation ou la banque
**Then** les questions valides sont créées (FR-7 complet — volet Markdown)
**When** le fichier ne respecte pas la convention (frontmatter manquant, syntaxe bloc invalide)
**Then** un message d'erreur lisible liste les problèmes avec numéro de ligne
**And** aucune importation partielle silencieuse n'est effectuée
**And** des fixtures Markdown réalistes sont incluses dans les tests
**And** le parser réutilise le même service d'ingestion que le CSV (Story 2.6) pour valider les questions

**Notes d'implémentation :**
- Story de **spécification + implémentation** : la moitié du travail est la définition de la convention.
- Décision PRD §10.2 tranchée par cette story.
- Si la convention s'avère trop coûteuse, alternative documentée dans la story : reporter post-MVP et mettre à jour `epics.md § Hors MVP`.

## Epic 3: Publier un accès individuel à un élève

Marie envoie un lien nominatif à un élève en moins de 5 minutes, avec fenêtre, aménagements et suivi des statuts.

### Story 3.1: Générer un accès individuel avec lien signé

As an **enseignant**,
I want **créer un accès pour un élève (nom, prénom) avec variante et fenêtre temporelle**,
So that **il puisse passer l'évaluation via un lien sécurisé**.

**Acceptance Criteria:**

**Given** une évaluation avec au moins une variante
**When** je complète le wizard : nom, prénom, dates début/fin, variante
**Then** un accès individuel est créé avec statut « en attente » (FR-11, FR-40)
**And** le lien contient un JWT signé non devinable avec expiration alignée sur la fenêtre
**And** un seul démarrage de session complète est autorisé par accès
**And** le wizard comporte au maximum 3 étapes (UX-DR5, UX-DR13)

### Story 3.2: Configurer les aménagements par accès

As an **enseignant**,
I want **appliquer tiers-temps (+33 % ou +50 %), police OpenDyslexic et agrandissement du texte sur un accès**,
So that **l'élève bénéficie de ses aménagements PAP pendant la session**.

**Acceptance Criteria:**

**Given** un accès en cours de création (étape 3 du wizard)
**When** je sélectionne tiers-temps +50 %, OpenDyslexic et agrandissement 125 %
**Then** les aménagements sont figés sur l'accès (FR-12)
**And** la durée effective du timer sera calculée avec le coefficient choisi
**And** un preset PAP est proposé par défaut si la variante est PAP

### Story 3.3: Copier le lien et confirmer l'envoi

As an **enseignant**,
I want **copier le lien généré en un clic avec retour visuel clair**,
So that **j'envoie rapidement l'accès à l'élève via l'ENT ou un mail**.

**Acceptance Criteria:**

**Given** un accès vient d'être créé
**When** la page de confirmation s'affiche
**Then** le bouton « Copier le lien » est le CTA primaire unique (UX-DR4, UX-DR18)
**When** je clique sur Copier
**Then** l'URL est dans le presse-papiers et un toast vert confirme « Lien copié »
**And** l'annonce accessibilité « Lien copié » est émise (screen reader)
**And** un texte d'aide suggère l'envoi via ENT ou mail (sans intégration MVP)

### Story 3.4: Invalider ou réinitialiser un accès

As an **enseignant**,
I want **invalider un accès non utilisé ou le réinitialiser avant toute session démarrée**,
So that **je garde le contrôle si l'élève ne doit plus passer**.

**Acceptance Criteria:**

**Given** un accès en statut « en attente » sans session démarrée
**When** je choisis « Invalider l'accès » et confirme dans une modale destructive (UX-DR24)
**Then** le statut passe à « invalidée » (FR-13)
**And** le lien renvoie HTTP 410 avec un message élève explicite
**Given** un accès non utilisé
**When** je choisis « Réinitialiser »
**Then** un nouveau token est généré et l'ancien est invalidé

### Story 3.5: Historique des accès avec statuts

As an **enseignant**,
I want **voir la liste de tous mes accès individuels avec leur statut**,
So that **je suis l'avancement de chaque envoi**.

**Acceptance Criteria:**

**Given** je suis connecté
**When** j'ouvre la section Accès
**Then** je vois tous mes accès avec statuts : en attente, en cours, terminée, expirée, invalidée (FR-33)
**And** chaque ligne affiche un `AccessStatusBadge` avec icône + texte (UX-DR3)
**And** le polling rafraîchit les statuts toutes les 5 s pour les accès pending/in_progress
**And** un empty state guide vers « Envoyer à un élève » si la liste est vide

### Story 3.6: Enforcement de la fenêtre temporelle

As a **système**,
I want **refuser le démarrage ou la poursuite d'une session hors fenêtre**,
So that **l'évaluation reste encadrée dans le créneau défini par l'enseignant**.

**Acceptance Criteria:**

**Given** un accès dont la fenêtre est expirée
**When** l'élève ouvre le lien
**Then** un écran « Fenêtre expirée » s'affiche avec message actionnable (FR-14, UX-DR17)
**And** le statut de l'accès est « expirée »
**And** aucune session partielle n'est exposée à un tiers
**Given** une session en cours dont la fenêtre se termine
**When** l'heure de fin est atteinte
**Then** la poursuite est refusée et la soumission auto s'applique si des réponses existent

## Epic 4: Passer la session d'évaluation (côté élève)

Lucas peut passer sa session de bout en bout avec intégrité tracée et soumission fiable.

### Story 4.1: Identification élève et bandeau de transparence

As an **élève**,
I want **saisir mon nom et prénom puis lire ce qui sera enregistré pendant la session**,
So that **je comprends le cadre avant de commencer**.

**Acceptance Criteria:**

**Given** un lien d'accès valide dans la fenêtre temporelle
**When** j'ouvre `eleve.kopie.cc/s/{token}`
**Then** je saisis nom et prénom sans créer de compte (FR-15)
**And** l'écran `TransparencyBanner` liste clairement ce qui est enregistré (durée, événements, pas de webcam) (UX-DR8, UX-DR21)
**And** aucun tracking publicitaire n'est activé
**And** le vouvoiement est utilisé dans tous les libellés

### Story 4.2: Démarrage en plein écran

As an **élève**,
I want **passer en plein écran pour démarrer la session**,
So that **je suis dans les conditions d'examen définies par mon enseignant**.

**Acceptance Criteria:**

**Given** j'ai validé l'écran de transparence
**When** je clique « Commencer » sur Chrome/Firefox desktop
**Then** le navigateur demande le plein écran via Fullscreen API (FR-16)
**When** je refuse le plein écran
**Then** la session ne démarre pas et un message clair explique la marche à suivre
**Given** iOS Safari
**Then** un mode dégradé documenté s'affiche (bannière best-effort, pas de promesse de verrouillage total) (UX-DR17, NFR-6)

### Story 4.3: Répondre aux questions avec navigation conditionnelle

As an **élève**,
I want **répondre aux questions de l'évaluation avec une interface claire et accessible**,
So that **je me concentre sur mes réponses**.

**Acceptance Criteria:**

**Given** une session démarrée dans `StudentSessionShell` (UX-DR6)
**When** les questions s'affichent via `QuestionRenderer` (choix, courte, texte libre) (UX-DR10, FR-5)
**Then** la police OpenDyslexic et l'agrandissement s'appliquent si configurés sur l'accès (FR-12)
**When** l'évaluation interdit le retour arrière
**Then** je ne peux pas modifier une question déjà validée (FR-23)
**And** le layout est mobile-first, colonne unique max-w-2xl (UX-DR20)
**And** les cibles tactiles font au minimum 44×44 px (NFR-15)

### Story 4.4: Timer visible et soumission automatique

As an **élève**,
I want **voir le temps restant et être soumis automatiquement à expiration**,
So that **je respecte la durée de l'évaluation**.

**Acceptance Criteria:**

**Given** une session avec durée nominale et aménagements (ex. +50 %)
**When** la session démarre
**Then** un timer visible décompte la durée effective (FR-21)
**When** le timer atteint zéro
**Then** les réponses déjà saisies sont soumises automatiquement
**And** un message informe que le temps est écoulé

### Story 4.5: Surveillance d'intégrité et journalisation

As a **système**,
I want **journaliser les sorties plein écran, pertes de focus, copier-coller et DevTools**,
So that **l'enseignant dispose d'un contexte factuel pour sa décision**.

**Acceptance Criteria:**

**Given** une session active
**When** l'élève sort du plein écran
**Then** l'événement est enregistré avec horodatage et durée hors plein écran (FR-17)
**When** l'élève change d'onglet (Page Visibility)
**Then** l'événement est journalisé (FR-18)
**When** l'élève tente Ctrl/Cmd+C/V
**Then** l'action est bloquée et journalisée (FR-19)
**When** les DevTools sont détectés
**Then** un événement suspect est journalisé sans bloquer la session (FR-20)
**And** les événements sont envoyés en batch via `POST /api/v1/sessions/{id}/events` avec `X-Idempotency-Key`

### Story 4.6: Avertissements non bloquants et sauvegarde incrémentale

As an **élève**,
I want **être informé calmement des événements enregistrés et ne pas perdre mes réponses**,
So that **je termine ma session sereinement**.

**Acceptance Criteria:**

*Volet avertissements (FR-22)*

**Given** un événement d'intégrité survient
**When** l'événement est journalisé
**Then** un `IntegrityToast` bleu informatif s'affiche 4–6 s, dismissible (FR-22, UX-DR7, UX-DR21)
**And** aucun libellé « triche », « fraude » ou « suspect » n'est affiché côté élève (vocabulaire neutre : « enregistré », « événement »)

*Volet sauvegarde incrémentale (décision archi — endpoint drafts)*

**Given** une session démarrée et au moins une réponse saisie
**When** l'élève modifie ou complète une réponse
**Then** le front appelle `POST /api/v1/sessions/{id}/answers` avec le payload `{ "question_id", "value", "client_timestamp" }` après un **debounce de 2 s** (ou à la perte de focus du champ, événement le plus précoce)
**And** la requête inclut un header `X-Idempotency-Key` pour éviter les doublons en cas de retry
**And** le serveur persiste la réponse en mode draft (la session reste en statut « en cours »)
**Given** je perds la connexion ou ferme l'onglet avant soumission
**When** je rouvre le lien dans la fenêtre temporelle et avant soumission finale
**Then** mes réponses sauvegardées sont restaurées via `GET /api/v1/sessions/{id}/answers` (récupération de l'état draft)
**And** une file d'attente de sync est visible en cas de réseau instable (UX-DR23) : compteur des écritures en attente + retry exponentiel
**And** aucune perte silencieuse : si une écriture draft échoue 3 fois, un avertissement explicite « Sauvegarde indisponible — vérifiez votre connexion » s'affiche
**And** le contrat OpenAPI (`contracts/openapi.yaml`) documente l'endpoint drafts avant l'implémentation backend

**Notes d'implémentation :**
- Distinct du journal d'intégrité (`POST /api/v1/sessions/{id}/events`) qui reste append-only.
- L'endpoint drafts est **idempotent** par clé (`session_id`, `question_id`, `X-Idempotency-Key`) — un même payload répété ne crée pas de doublon.
- Après soumission finale (Story 4.7), les drafts sont gelés et lus comme réponses définitives.

### Story 4.7: Confirmation et écran de fin de session

As an **élève**,
I want **confirmer ma soumission et voir un message de fin clair**,
So that **je sais que ma copie est bien envoyée**.

**Acceptance Criteria:**

**Given** j'ai répondu aux questions
**When** je clique « Terminer »
**Then** une modale de confirmation irréversible s'affiche avec focus trap (FR-24, UX-DR24)
**When** je confirme la soumission
**Then** la session passe à « terminée » et les réponses sont figées
**And** l'écran de fin affiche « Votre copie a bien été envoyée » (UX-DR14)
**And** aucune note n'est affichée à l'élève au MVP
**And** le token d'accès ne permet plus de redémarrer une session

## Epic 5: Consulter résultats, journal et corriger

Marie consulte réponses et journal, corrige, attribue note/appréciation et exporte pour justifier sa décision.

### Story 5.1: Ingestion et stockage du journal de session

As a **système**,
I want **enregistrer de façon exhaustive et horodatée tous les événements de session**,
So that **l'enseignant dispose d'un artefact fiable pour interpréter le passage**.

**Acceptance Criteria:**

**Given** des événements client envoyés en batch avec `X-Idempotency-Key`
**When** l'API reçoit `POST /api/v1/sessions/{id}/events`
**Then** les événements sont stockés en append-only avec horodatage serveur authoritative (FR-25)
**And** les doublons (même idempotency key) sont ignorés sans double enregistrement
**And** le catalogue `event_types.py` documente les types en snake_case
**And** démarrage, réponses, sorties plein écran, focus, copier-coller, DevTools et soumission sont couverts

### Story 5.2: Consulter le journal (résumé et timeline)

As an **enseignant**,
I want **voir un résumé synthétique puis le détail chronologique du journal**,
So that **je comprends rapidement le contexte avant de noter**.

**Acceptance Criteria:**

**Given** un accès en statut « terminée » dont je suis propriétaire
**When** j'ouvre l'onglet Journal sur la fiche élève
**Then** `JournalSummary` affiche : nombre d'événements, durée hors focus, durée totale session (FR-28, UX-DR9)
**When** je développe le détail
**Then** `JournalTimeline` affiche la chronologie horodatée (FR-26)
**And** le vocabulaire est neutre (« événements », pas « infractions »)
**And** un autre enseignant ne peut pas accéder à ce journal (FR-26, isolation)

### Story 5.3: Correction automatique des questions à choix

As an **enseignant**,
I want **voir les QCM auto-corrigés dès la soumission**,
So that **je gagne du temps sur la partie fermée**.

**Acceptance Criteria:**

**Given** une session terminée avec des questions à choix
**When** l'élève a soumis
**Then** les réponses à choix sont corrigées automatiquement (FR-29)
**And** le score partiel ou les bonnes/mauvaises réponses sont visibles dans l'onglet Réponses (UX-DR16)

### Story 5.4: Correction manuelle des questions ouvertes

As an **enseignant**,
I want **lire et corriger les réponses courtes et productions écrites**,
So that **j'attribue une note juste sur la partie ouverte**.

**Acceptance Criteria:**

**Given** une session avec réponses courtes ou texte libre
**When** j'ouvre l'onglet Réponses
**Then** je vois le texte intégral de chaque réponse ouverte (FR-30)
**And** je peux parcourir toutes les questions sans quitter la fiche

### Story 5.5: Attribuer note et appréciation

As an **enseignant**,
I want **saisir un score et/ou une appréciation textuelle pour la session**,
So that **je formalise ma décision pédagogique**.

**Acceptance Criteria:**

**Given** une session terminée
**When** je saisis une note sur 20 (ou échelle documentée) et une appréciation
**Then** les valeurs sont enregistrées sur la session (FR-31)
**And** elles sont visibles sur la fiche élève et dans l'historique des accès

### Story 5.6: Exporter résultats et journal

As an **enseignant**,
I want **exporter les résultats et le journal en PDF et CSV**,
So that **je constitue un dossier pour la direction ou les parents**.

**Acceptance Criteria:**

**Given** une session terminée avec réponses et journal
**When** je clique « Exporter PDF » ou « Exporter CSV »
**Then** un fichier téléchargeable contient les résultats de l'élève (FR-32)
**When** j'exporte le journal
**Then** le PDF et CSV contiennent résumé et événements horodatés (FR-27)
**And** les exports respectent l'isolation enseignant
**And** la mise en page est adaptée à un dossier institutionnel (UX-DR16)

## Epic 6: Déployer, sécuriser et exploiter Kopie

Un déployeur peut installer, configurer, sécuriser et maintenir Kopie en conformité RGPD.

### Story 6.1: Docker Compose production complet

As a **déployeur**,
I want **lancer l'application complète via Docker Compose**,
So that **je déploie Kopie sans assembler manuellement chaque service**.

**Acceptance Criteria:**

**Given** le fichier `docker-compose.prod.yml` et `.env.example`
**When** je exécute `docker compose -f docker-compose.prod.yml up -d`
**Then** les services postgres, api, web-prof, web-eleve et reverse proxy démarrent (FR-35)
**And** les images sont publiées sur GHCR selon la documentation
**And** un healthcheck API répond sur `/api/v1/health`

### Story 6.2: HTTPS automatique avec Caddy

As a **déployeur**,
I want **obtenir des certificats TLS automatiques via Let's Encrypt**,
So that **toutes les communications sont chiffrées en transit**.

**Acceptance Criteria:**

**Given** un `Caddyfile` configuré avec les domaines `prof`, `eleve` et `api`
**When** le reverse proxy démarre avec les DNS pointant vers le serveur
**Then** HTTPS est actif avec certificats Let's Encrypt (FR-36, FR-42)
**And** HTTP redirige vers HTTPS
**And** les origines CORS correspondent aux sous-domaines configurés

### Story 6.3: Migrations de base de données versionnées

As a **déployeur**,
I want **exécuter les migrations Alembic de façon fiable au déploiement**,
So that **le schéma PostgreSQL est toujours à jour**.

**Acceptance Criteria:**

**Given** une base PostgreSQL vide ou existante
**When** j'exécute `scripts/migrate.sh` ou le service `migrate` dans Compose
**Then** toutes les migrations Alembic s'appliquent dans l'ordre (FR-37)
**And** les migrations sont versionnées dans le dépôt
**And** un échec de migration bloque le déploiement avec logs explicites

### Story 6.4: Configuration environnement et purge des données

As a **déployeur**,
I want **configurer l'application via `.env` et une politique de rétention des données élève**,
So that **je respecte les exigences RGPD de mon établissement**.

**Acceptance Criteria:**

**Given** un fichier `.env` documenté (FR-34)
**When** je définis `DATA_RETENTION_MONTHS` (défaut 12)
**Then** un job planifié purge ou anonymise les données élève au-delà de la durée (FR-41, NFR-10)
**And** la documentation explique chaque variable critique (SMTP, secrets, rétention)
**And** les secrets ne sont jamais commités dans le dépôt (NFR-4)

### Story 6.5: Durcissement sécurité et observabilité

As a **déployeur**,
I want **une API protégée contre les abus et des logs sans données sensibles**,
So that **l'instance respecte les bonnes pratiques OWASP**.

**Acceptance Criteria:**

*Rate limiting — routes auth (déjà partiellement couvert par Story 1.4)*

**Given** l'API en production
**When** des requêtes excessives ciblent `/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/register`, `/api/v1/auth/forgot-password`
**Then** slowapi renvoie HTTP 429 selon la politique documentée (ex. 10 req/min/IP) (FR-43)

*Rate limiting — routes d'accès public élève (gap G-3 fermé)*

**Given** l'API en production
**When** des requêtes excessives ciblent les routes élève publiques sans authentification enseignant :
  - `GET /api/v1/accesses/by-token/{token}` — résolution du lien d'accès
  - `POST /api/v1/sessions` — démarrage d'une session
  - `POST /api/v1/sessions/{id}/answers` — drafts de réponses (Story 4.6)
  - `POST /api/v1/sessions/{id}/events` — journal d'intégrité (Story 5.1)
  - `POST /api/v1/sessions/{id}/submit` — soumission finale (Story 4.7)
**Then** slowapi renvoie HTTP 429 selon une politique documentée par route (ex. 60 req/min/IP pour les drafts, 30 req/min/IP pour les events, 5 req/min/IP pour `submit`)
**And** un test pytest vérifie le seuil pour au moins **une** route publique de chaque famille (accesses, sessions, answers, events, submit)
**And** la documentation `.env` permet d'ajuster les seuils par environnement (`RATE_LIMIT_*`)

*Protections transverses*

**And** les protections CSRF, XSS et injection SQL sont en place sur les mutations prof (FR-43)
**And** structlog émet des logs JSON avec `request_id` sans nom/prénom élève (NFR-8)

*CI complète*

**And** la CI GitHub Actions exécute : `ruff`, `mypy`, `pytest` (avec couverture isolation tenant), `vitest`, `jest-axe` sur les parcours élève critiques (UX-DR19, NFR-15), build des images Docker, scan de dépendances (NFR-3, NFR-S2)

### Story 6.6: Documentation auto-hébergement

As a **déployeur**,
I want **un README et un guide d'auto-hébergement complets**,
So that **je déploie Kopie sans support commercial en restant conforme RGPD et FR-42**.

**Acceptance Criteria:**

**Given** le dépôt public
**When** je lis `README.md` et `docs/self-hosting.md`
**Then** je trouve les prérequis, étapes d'installation, configuration `.env` et dépannage (FR-38)
**And** les limitations Safari/iOS pour la session élève sont documentées
**And** le guide mentionne l'hébergement UE uniquement (NFR-9)
**And** le guide **exige explicitement un volume chiffré au repos** pour le service `postgres` (FR-42) avec exemples : LUKS sur disque physique, volume chiffré OVH/Scaleway/Hetzner managé, ou option `encrypted: true` du provider cloud
**And** le guide fournit une checklist de durcissement post-installation : variables secrètes générées (`openssl rand -hex 32`), pare-feu activé, sauvegardes chiffrées hors-site, rotation des secrets documentée (NFR-S3)
**And** un avertissement explicite mentionne que **sans volume chiffré, le déploiement n'est pas conforme à FR-42** même si TLS est actif

### Story 6.7: Instance cloud officielle

As a **utilisateur**,
I want **accéder à une instance cloud officielle gratuite fonctionnellement équivalente au self-host**,
So that **je commence sans déployer moi-même**.

**Acceptance Criteria:**

**Given** l'infrastructure cloud de l'équipe projet (UE)
**When** l'instance officielle est déployée avec la même codebase que le self-host
**Then** les parcours enseignant et élève sont fonctionnellement équivalents au MVP (FR-39)
**And** la configuration est gérée par l'équipe (secrets, TLS, rétention)
**And** la documentation indique l'URL d'inscription et les conditions d'usage

### Story 6.8: Documentation juridique RGPD

As a **référent conformité / direction**,
I want **une documentation légale sur les rôles, bases légales et droits des personnes**,
So that **l'établissement peut valider le déploiement avant la bêta publique**.

**Acceptance Criteria:**

**Given** le dossier `docs/legal/` à créer
**When** un DPO consulte la documentation
**Then** elle couvre : responsable de traitement (cloud vs self-host), base légale, durée de conservation, droits (accès, rectification, effacement), hébergement UE (NFR-9, NFR-10)
**And** les questions ouvertes PRD §10.1 et §10.6 sont traitées ou explicitement marquées « à valider juridiquement »
**And** aucun transfert hors UE n'est requis pour le MVP
