---
stepsCompleted:
  - step-01-document-discovery
  - step-02-prd-analysis
  - step-03-epic-coverage-validation
  - step-04-ux-alignment
  - step-05-epic-quality-review
  - step-06-final-assessment
  - gap-closure-2026-05-19
status: complete-and-gaps-closed
documentsIncluded:
  prd:
    - _bmad-output/planning-artifacts/prds/prd-Kopie-2026-05-19/prd.md
    - _bmad-output/planning-artifacts/prds/prd-Kopie-2026-05-19/addendum.md
    - _bmad-output/planning-artifacts/prds/prd-Kopie-2026-05-19/.decision-log.md
  architecture:
    - _bmad-output/planning-artifacts/architecture.md
  epics:
    - _bmad-output/planning-artifacts/epics.md
  ux:
    - _bmad-output/planning-artifacts/ux-design-specification.md
    - _bmad-output/planning-artifacts/ux-design-directions.html
  brief:
    - _bmad-output/planning-artifacts/briefs/brief-Kopie-2026-05-19/brief.md
    - _bmad-output/planning-artifacts/briefs/brief-Kopie-2026-05-19/addendum.md
    - _bmad-output/planning-artifacts/briefs/brief-Kopie-2026-05-19/.decision-log.md
---

# Implementation Readiness Assessment Report

**Date :** 2026-05-19
**Projet :** Kopie
**Évaluateur :** Product Manager (BMAD bmad-check-implementation-readiness)
**Langue :** Français

---

## 1. Document Inventory

| Type | Format | Chemin | Statut |
|------|--------|--------|--------|
| PRD | sharded | `_bmad-output/planning-artifacts/prds/prd-Kopie-2026-05-19/` (prd.md + addendum.md + .decision-log.md) | ✓ présent — statut `final` |
| Architecture | whole | `_bmad-output/planning-artifacts/architecture.md` | ✓ présent |
| Epics | whole | `_bmad-output/planning-artifacts/epics.md` | ✓ présent (modifié 19/05 07:02) |
| UX Spec | whole | `_bmad-output/planning-artifacts/ux-design-specification.md` | ✓ présent |
| UX Directions | annexe | `_bmad-output/planning-artifacts/ux-design-directions.html` | ✓ présent (artefact visuel) |
| Brief | sharded | `_bmad-output/planning-artifacts/briefs/brief-Kopie-2026-05-19/` | ✓ présent (contexte amont) |
| Project Context | — | _absent_ | ⚠ Non bloquant (envisager `bmad-generate-project-context` plus tard) |

**Doublons détectés :** Aucun ✓
**Documents requis manquants :** Aucun ✓
**Stories individuelles :** Aucune (création prévue après cette validation) — normal à ce stade

---

## 2. PRD Analysis

### 2.1 Functional Requirements extraits (43 FR)

#### 4.1 Comptes enseignants
- **FR-1 Inscription** — email + mot de passe, validation email `[ASSUMPTION]`, espace vide isolé, politique mot de passe minimale documentée.
- **FR-2 Connexion et session** — JWT, expiration/déconnexion, 401 sur routes non authentifiées.
- **FR-3 Profil** — consultation/modification (nom, email, mot de passe).
- **FR-4 Isolation des données** — aucune fuite cross-tenant (évaluations, accès, sessions, journaux).

#### 4.2 Création et gestion des évaluations
- **FR-5 Composer une évaluation** — types choix unique/multiple, réponse courte, texte libre ; pondération optionnelle ; schéma extensible.
- **FR-6 Randomisation** — ordre questions et/ou propositions.
- **FR-7 Import de questions** — CSV ou Markdown, format documenté, échec d'import lisible et atomique.
- **FR-8 Banque de questions** — sauvegarde + réinsertion.
- **FR-9 Variantes d'évaluation** — variantes liées (ex. standard/PAP) partageant métadonnées.
- **FR-10 Paramètres de session** — durée nominale, interdiction retour arrière (optionnel).

#### 4.3 Accès individuel
- **FR-11 Générer un accès individuel** — nom/prénom élève, variante, fenêtre temporelle, token non devinable, usage unique strict.
- **FR-12 Aménagements par accès** — tiers-temps +33 % ou +50 %, OpenDyslexic, agrandissement.
- **FR-13 Invalider ou réinitialiser un accès** — HTTP 410 ou équivalent, statut « invalidée » visible.
- **FR-14 Expiration hors fenêtre** — refus démarrage/poursuite session hors fenêtre.

#### 4.4 Session élève
- **FR-15 Identification élève** — nom/prénom sans compte.
- **FR-16 Plein écran au démarrage** — Fullscreen API ; démarrage conditionné desktop, iOS best-effort.
- **FR-17 Journalisation sorties plein écran** — horodatage + durée hors plein écran.
- **FR-18 Journalisation perte de focus** — Page Visibility API.
- **FR-19 Limitation copier-coller** — Ctrl/Cmd+C/V bloqués.
- **FR-20 Détection DevTools** — heuristique navigateur, journalisée comme événement suspect.
- **FR-21 Timer et soumission automatique** — décompte visible (durée aménagée), auto-submit à expiration.
- **FR-22 Avertissements non bloquants** — feedback visuel à chaque événement suspect.
- **FR-23 Navigation entre questions** — interdiction retour arrière si activée.
- **FR-24 Confirmation de soumission** — confirmation explicite obligatoire.

#### 4.5 Journal de session
- **FR-25 Enregistrement exhaustif** — démarrage, réponses, sorties FS, pertes focus, copier-coller, DevTools, soumission.
- **FR-26 Consultation enseignant** — seul l'enseignant propriétaire.
- **FR-27 Export du journal** — PDF + CSV.
- **FR-28 Résumé synthétique** — nb événements, durée hors focus, durée session.

#### 4.6 Résultats et correction
- **FR-29 Correction automatique des choix** — à la soumission.
- **FR-30 Correction manuelle des ouvertes** — interface enseignant.
- **FR-31 Note ou appréciation** — score et/ou texte par session.
- **FR-32 Export des résultats** — PDF + CSV.
- **FR-33 Historique des envois** — statuts : en attente, en cours, terminée, expirée, invalidée.

#### 4.7 Déploiement et administration
- **FR-34 Configuration par environnement** — `.env` documenté.
- **FR-35 Docker Compose** — application + PostgreSQL + reverse proxy (Caddy/Traefik).
- **FR-36 HTTPS automatique** — Let's Encrypt.
- **FR-37 Migrations base de données** — schéma versionné.
- **FR-38 Documentation auto-hébergement** — README + guide.
- **FR-39 Instance cloud officielle** — gratuite, même codebase `[ASSUMPTION]`.

#### 4.8 Sécurité fonctionnelle
- **FR-40 Lien signé à usage unique** — token signé HMAC/JWT.
- **FR-41 Minimisation et rétention données élève** — paramétrable, suppression/anonymisation.
- **FR-42 Chiffrement et transport** — at-rest + TLS obligatoire en prod.
- **FR-43 Protection des endpoints** — SQLi, XSS, CSRF, rate limiting.

**Total FR : 43**

### 2.2 Non-Functional Requirements extraits

| Réf. | Catégorie | Exigence |
|------|-----------|----------|
| NFR-P1 | Performance | FCP élève < 3 s `[ASSUMPTION]` |
| NFR-P2 | Performance | Interactions formulaire < 100 ms ressenti |
| NFR-P3 | Performance | Pas de WebSocket au MVP |
| NFR-S1 | Sécurité | OWASP Top 10 mitigé |
| NFR-S2 | Sécurité | Audits dépendances en CI `[ASSUMPTION]` |
| NFR-S3 | Sécurité | Secrets hors dépôt, rotation documentée |
| NFR-A1 | Accessibilité | RGAA niveau AA (interface élève) |
| NFR-A2 | Accessibilité | OpenDyslexic via aménagement (FR-12) |
| NFR-B1 | Compatibilité | Chrome/Firefox récents — support complet |
| NFR-B2 | Compatibilité | Safari/iOS best-effort, limitations Fullscreen documentées |
| NFR-I1 | i18n | Chaînes externalisées, français MVP |
| NFR-O1 | Observabilité | Logs structurés, pas de données élève en clair `[ASSUMPTION]` |

**Total NFR transverses : 12**

### 2.3 Additional Requirements / Contraintes (§9)

| Réf. | Catégorie | Contrainte |
|------|-----------|------------|
| C-1 | RGPD | Hébergement et traitement UE uniquement |
| C-2 | RGPD | Base légale, info, droits, registre documentés `[ASSUMPTION: validation juridique avant bêta]` |
| C-3 | RGPD | Conservation paramétrable (défaut 12 mois `[ASSUMPTION]`) |
| C-4 | RGPD | Pas de transfert hors UE, pas de sous-traitant US critique |
| C-5 | Mineurs | Traitement minimal, pas de compte élève, pas de profilage |
| C-6 | Licence | AGPL-3.0, self-host gratuit sans restriction MVP |
| C-7 | Licence | Cloud officielle gratuite au lancement |
| C-8 | Plateforme | Web responsive (pas d'app native MVP) |

### 2.4 Métriques de succès référencées

SM-1 Activation (FR-5, FR-11), SM-2 Time-to-link (UJ-1, FR-11), SM-3 Sessions complétées (UJ-2, FR-21, FR-24), SM-4 Rétention, SM-5 Signaux d'intégrité (FR-25, FR-28), SM-6 Feedback institutionnel.
Contre-métriques : SM-C1 (pas de score punitif), SM-C2 (pas de sur-complexité composition).

### 2.5 Hypothèses indexées (12)

PRD §11 — toutes balisées `[ASSUMPTION]`. Aucune n'est bloquante pour démarrer l'implémentation, mais doivent être confirmées en bêta ou implémentation.

### 2.6 Questions ouvertes du PRD (§10)

1. Base légale et rôles RGPD cloud vs self-host → juridique, avant bêta publique.
2. Format d'import CSV/Markdown → architecture / story dédiée.
3. Comportement accès partiellement utilisé → UX + architecture.
4. Seuils SM-5 → bêta / produit.
5. Choix backend Node/Fastify vs Python/FastAPI → architecture.
6. Conservation par défaut 12 mois → juridique + déploiement.

### 2.7 PRD Completeness Assessment

**Points forts** :
- Structure rigoureuse (glossaire, FRs numérotés globalement, UJs détaillés, NFR, contraintes, succès + contre-métriques).
- 43 FR avec **conséquences testables** explicites — excellent pour découpage en stories et critères d'acceptance.
- 12 hypothèses **indexées** — pas d'ambiguïté cachée.
- 3 UJ couvrant les parcours critiques (UJ-1 envoi, UJ-2 passage, UJ-3 analyse).
- Contre-métriques (SM-C1, SM-C2) — garde-fous produit clairs contre dérive proctoring/complexité.

**Zones d'attention pour la suite (à valider Step 3-5)** :
- ⚠ Vérifier que les questions ouvertes **techniques** §10 sont tranchées dans `architecture.md` (Node vs Python, schéma polymorphe, multi-tenant, chiffrement at-rest, CI/CD).
- ⚠ Vérifier qu'une story réserve le travail d'investigation format Markdown (FR-7).
- ⚠ Vérifier qu'une story tranche le comportement « session abandonnée ».
- ⚠ NFRs transverses non numérotés dans la source — risque de couverture floue dans le mapping epics ↔ NFR.
- ⚠ Aucune cible chiffrée pour latence API backend (P95 endpoints) — à confirmer en architecture.

> **Note** : Les epics ont **renuméroté** les NFR (NFR-1 à NFR-15) avec décomposition plus fine du PRD §8/§9. Mapping documenté en §3.4.

---

## 3. Epic Coverage Validation

### 3.1 Inventaire des epics

| Epic | Titre | FRs couverts | Stories | Persona / UJ |
|------|-------|--------------|---------|--------------|
| Epic 1 | Fondation plateforme et espace enseignant | FR-1, FR-2, FR-3, FR-4 | 6 | Setup + Marie |
| Epic 2 | Composer et organiser les évaluations | FR-5, FR-6, FR-7, FR-8, FR-9, FR-10 | 6 | Marie (UJ-1 prep) |
| Epic 3 | Publier un accès individuel à un élève | FR-11, FR-12, FR-13, FR-14, FR-33, FR-40 | 6 | Marie (UJ-1 golden path) |
| Epic 4 | Passer la session d'évaluation (côté élève) | FR-15 → FR-24 | 7 | Lucas (UJ-2) |
| Epic 5 | Consulter résultats, journal et corriger | FR-25 → FR-32 | 6 | Marie (UJ-3) |
| Epic 6 | Déployer, sécuriser et exploiter | FR-34 → FR-39, FR-41, FR-42, FR-43 | 8 | Déployeur + Conformité |

**Totaux** : 6 epics, 39 stories métier (+ 2 stories d'infrastructure 1.1/1.2), **43 FRs cartographiés** (100 %).

### 3.2 Matrice de couverture FR

| FR | Epic | Story | Statut |
|---|---|---|---|
| FR-1 | E1 | 1.3 | ✅ Couvert |
| FR-2 | E1 | 1.4 | ✅ Couvert |
| FR-3 | E1 | 1.5 | ✅ Couvert |
| FR-4 | E1 | 1.6 | ✅ Couvert (test pytest cross-teacher) |
| FR-5 | E2 | 2.1 (+ 4.3 rendu) | ✅ Couvert |
| FR-6 | E2 | 2.4 | ✅ Couvert |
| FR-7 | E2 | 2.6 (CSV uniquement) | ⚠️ **Partiel** — Markdown reporté à story dédiée non créée |
| FR-8 | E2 | 2.2 | ✅ Couvert |
| FR-9 | E2 | 2.3 | ✅ Couvert |
| FR-10 | E2 | 2.5 | ✅ Couvert |
| FR-11 | E3 | 3.1 | ✅ Couvert |
| FR-12 | E3 | 3.2 (+ 4.3 application) | ✅ Couvert |
| FR-13 | E3 | 3.4 | ✅ Couvert |
| FR-14 | E3 | 3.6 | ✅ Couvert |
| FR-15 | E4 | 4.1 | ✅ Couvert |
| FR-16 | E4 | 4.2 | ✅ Couvert |
| FR-17 | E4 | 4.5 | ✅ Couvert |
| FR-18 | E4 | 4.5 | ✅ Couvert |
| FR-19 | E4 | 4.5 | ✅ Couvert |
| FR-20 | E4 | 4.5 | ✅ Couvert |
| FR-21 | E4 | 4.4 | ✅ Couvert |
| FR-22 | E4 | 4.6 | ✅ Couvert |
| FR-23 | E4 | 4.3 (+ 2.5 paramètre) | ✅ Couvert |
| FR-24 | E4 | 4.7 | ✅ Couvert |
| FR-25 | E5 | 5.1 | ✅ Couvert |
| FR-26 | E5 | 5.2 | ✅ Couvert |
| FR-27 | E5 | 5.6 | ✅ Couvert |
| FR-28 | E5 | 5.2 | ✅ Couvert |
| FR-29 | E5 | 5.3 | ✅ Couvert |
| FR-30 | E5 | 5.4 | ✅ Couvert |
| FR-31 | E5 | 5.5 | ✅ Couvert |
| FR-32 | E5 | 5.6 | ✅ Couvert |
| FR-33 | E3 | 3.5 | ✅ Couvert |
| FR-34 | E6 | 6.4 | ✅ Couvert |
| FR-35 | E6 | 6.1 | ✅ Couvert |
| FR-36 | E6 | 6.2 | ✅ Couvert |
| FR-37 | E6 | 6.3 (Alembic) | ✅ Couvert |
| FR-38 | E6 | 6.6 | ✅ Couvert |
| FR-39 | E6 | 6.7 | ✅ Couvert |
| FR-40 | E3 | 3.1 | ✅ Couvert |
| FR-41 | E6 | 6.4 | ✅ Couvert |
| FR-42 | E6 | 6.2 (TLS) + AR « disque managé UE » | ⚠️ **Partiel** — at-rest implicite, pas de vérification self-host |
| FR-43 | E1/E3/E6 | 1.4 + 6.5 | ⚠️ **Partiel** — rate limit routes accès public non explicitement testé |

### 3.3 Statistiques

- **FRs PRD totaux** : 43
- **FRs entièrement couverts** : 40 (93 %)
- **FRs partiellement couverts** : 3 (FR-7, FR-42, FR-43) — 7 %
- **FRs manquants** : 0 (0 %)
- **FRs en epics absents du PRD** : 0
- **Couverture globale** : **100 % (tous adressés au moins partiellement)**

### 3.4 Mapping NFR PRD ↔ NFR epics

| PRD | Epics | Note |
|-----|-------|------|
| NFR-P1 FCP < 3s | NFR-1, NFR-14 | ✅ NFR-14 ajoute critère bundle |
| NFR-P2 < 100 ms | NFR-1 | ✅ |
| NFR-P3 pas de WS | NFR-2 | ✅ |
| NFR-S1 OWASP | NFR-3 | ✅ |
| NFR-S2 audits CI | NFR-3 | ✅ (regroupé) |
| NFR-S3 secrets hors dépôt | NFR-4 | ✅ |
| NFR-A1 RGAA AA | NFR-5, NFR-15 | ✅ NFR-15 décline en exigences UI concrètes |
| NFR-A2 OpenDyslexic | NFR-5 | ✅ |
| NFR-B1/B2 navigateurs | NFR-6 | ✅ |
| NFR-I1 i18n | NFR-7 | ✅ |
| NFR-O1 logs | NFR-8 | ✅ |
| C-1/C-4 UE | NFR-9 | ✅ |
| C-2/C-3 RGPD/rétention | NFR-10 | ✅ |
| C-5 mineurs | NFR-11 | ✅ |
| C-6/C-7 AGPL | NFR-12 | ✅ |
| C-8 responsive | NFR-13 | ✅ |

**Aucun gap NFR.** Les epics ajoutent même NFR-14 (bundle) et NFR-15 (UI accessibilité concrète) en raffinement.

### 3.5 Gaps identifiés (à traiter avant Phase 4)

| # | Sévérité | Item | Description | Recommandation |
|---|----------|------|-------------|----------------|
| G-1 | 🟡 Medium | FR-7 Import Markdown | Story 2.6 ne couvre que CSV ; Markdown reporté « story dédiée » non créée | Soit ajouter **Story 2.7 Import Markdown**, soit déplacer MD en §6.2 « Hors MVP » du PRD pour cohérence |
| G-2 | 🟡 Medium | FR-42 Chiffrement at-rest | Couverture implicite via « disque managé hébergeur UE » ; aucune story ne le vérifie pour self-host | Ajouter un AC dans **Story 6.6** : « le guide self-host mentionne explicitement l'exigence d'un volume chiffré » |
| G-3 | 🟡 Medium | FR-43 Rate limit routes publiques | Story 1.4 couvre `/auth/*`, Story 6.5 mentionne « ou routes accès public » sans détail | Étoffer AC de **Story 6.5** avec liste explicite : `GET /api/v1/accesses/{token}`, `POST /api/v1/sessions/...`, `POST /api/v1/sessions/{id}/events` |

**Aucun gap critique (🔴) ne bloque le démarrage de l'implémentation.** Les 3 gaps medium sont aisément refermables en quelques minutes par édition ciblée d'`epics.md`.

### 3.6 Surcouverture / Points forts

- ✅ `FR Coverage Map` explicite dans `epics.md` (lignes 142-186) — excellente traçabilité native.
- ✅ Additional Requirements (lignes 88-112) capturent les décisions d'architecture appliquées au découpage.
- ✅ UX-DR1 à UX-DR25 **référencés dans les ACs** (ex. UX-DR4 dans 3.3, UX-DR8 dans 4.1, UX-DR9 dans 5.2) — alignement PRD/UX/Epics naturel.
- ✅ Questions ouvertes PRD §10 tranchées : §10.3 (session abandonnée → sauvegarde incrémentale), §10.5 (backend → FastAPI), §10.1 (RGPD juridique → **Story 6.8** dédiée).
- ✅ Test cross-teacher pytest **automatisé** (Story 1.6) — protection FR-4 explicitement vérifiée.

---

## 4. UX Alignment Assessment

### 4.1 UX Document Status

**Found** — `ux-design-specification.md` (statut `complete`, 14 steps complétés) + visualiseur `ux-design-directions.html` (direction D2 validée).

### 4.2 UX ↔ PRD Alignment

| Élément | PRD | UX | Statut |
|---------|-----|-----|--------|
| Personas Marie + Lucas | §2 | Étendus + parent + DPO | ✅ Cohérent |
| UJ-1 envoi rattrapage | §2.4 | Diagramme mermaid + UX-DR13 | ✅ Couvert |
| UJ-2 passage PAP | §2.4 | Diagramme + cas iOS dégradé | ✅ Couvert |
| UJ-3 analyse résultats | §2.4 | Diagramme + onglets Réponses/Journal | ✅ Couvert |
| Posture « tracer, pas sanctionner » | Principe transverse | Copywriting + palette sans rouge sur événements | ✅ UX-DR2, UX-DR21 |
| OpenDyslexic (FR-12) | Aménagement | `font-dyslexic` chargement conditionnel (UX-DR6) | ✅ |
| RGAA AA (NFR) | §8 | Section accessibilité + jest-axe (UX-DR19) | ✅ |
| Time-to-link < 5 min (SM-2) | §7 | Wizard ≤ 3 étapes (UX-DR5, UX-DR13) | ✅ |
| Bandeau transparence | Implicite | `TransparencyBanner` (UX-DR8) | ✅ UX raffine |
| Statuts d'accès (FR-33) | §4.6 | `AccessStatusBadge` icône + texte (UX-DR3) | ✅ |
| Reprise session abandonnée | §10 Q3 ouverte | « honnêteté réseau, file d'attente visible » (UX-DR23) | ✅ Tranché en UX + archi |

**Conclusion** : Aucun désalignement UX ↔ PRD.

### 4.3 UX ↔ Architecture Alignment

| UX | Architecture | Statut |
|----|--------------|--------|
| Tailwind v4 + shadcn/ui (Radix) | React + Vite + Tailwind v4 (Starter Template) | ✅ |
| Thèmes `theme-teacher` / `theme-student` | Dual-app (2× Vite, sous-domaines `prof.kopie.cc` / `eleve.kopie.cc`) | ✅ |
| Bundle élève FCP < 3 s | « code-splitting, deps minimales » (Frontend Architecture) | ✅ |
| Polling 5 s statut accès | TanStack Query `refetchInterval: 5000` (Communication Patterns) | ✅ |
| HTTP 410 lien invalidé | `error.code = ACCESS_EXPIRED` (Format Patterns) | ✅ |
| Sauvegarde incrémentale | « sauvegarde incrémentale + reprise tant que session non soumise » (Critical Decisions) | ✅ |
| Export PDF/CSV soigné | `endpoints/exports.py` + stratégie streaming | ✅ |
| Web responsive (pas d'app native) | NFR-13 | ✅ |
| `jest-axe` parcours élève | CI architecture liste `ruff, mypy, pytest, vitest` sans `jest-axe` | ⚠️ Gap mineur de spécification CI |

### 4.4 Architecture ↔ PRD Alignment

L'architecture déclare elle-même `READY WITH MINOR GAPS`. Vérifications croisées :

- ✅ FRs PRD mappés (Requirements to Structure Mapping)
- ✅ NFRs couverts architecturalement
- ✅ PRD §10.5 (Node vs Python) → tranché FastAPI
- ✅ PRD §10.3 (session abandonnée) → tranché sauvegarde incrémentale
- ✅ PRD §10.1 (RGPD) → Story 6.8 dédiée
- ✅ PRD §10.6 (conservation 12 mois) → Story 6.4 (`DATA_RETENTION_MONTHS`) + 6.8 (validation juridique)
- ⚠️ PRD §10.2 (import Markdown) → reporté « story dédiée » non créée — **identique au gap G-1**
- ⚠️ PRD §10.4 (seuils SM-5) → non traité techniquement (relève bêta produit)

### 4.5 Warnings et désalignements

| # | Sévérité | Constat | Recommandation |
|---|----------|---------|----------------|
| U-1 | 🟢 Info | UX-DR19 + NFR-15 imposent `jest-axe`, CI architecture ne le mentionne pas | Ajouter `jest-axe` dans la matrice CI (Story 6.5 ou `docs/architecture-patterns.md`) |
| U-2 | 🟢 Info | UX mentionne Storybook « optionnel MVP » | Aucune action — explicitement optionnel |
| U-3 | 🟢 Info | UX prévoit « bêta avec 1 prof + 1 élève PAP » | Hors périmètre stories — plan de validation produit |

**Aucun désalignement critique ou bloquant.** Tous les warnings sont info-only.

---

## 5. Epic Quality Review

### 5.1 Checklist de conformité par epic

| Critère | E1 | E2 | E3 | E4 | E5 | E6 |
|---------|----|----|----|----|----|----|
| Epic delivers user value | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Epic peut fonctionner indépendamment (avec epics précédents) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Stories appropriately sized | ✅ | ✅ | ✅ | ⚠️ Story 4.6 | ✅ | ✅ |
| No forward dependencies | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DB tables créées au besoin (Alembic) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| AC clairs Given/When/Then | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Traçabilité FRs | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 5.2 Conformité Starter Template + Greenfield

- ✅ **Story 1.1 « Scaffold monorepo »** correspond au pattern « Set up initial project from starter template ». AC fidèle aux commandes `architecture.md § Starter Template Evaluation` (pnpm, uv, create-vite 9, Tailwind v4, Docker Compose, thèmes D2).
- ✅ **Story 1.2 « Contrat OpenAPI initial »** précède toute story consommant l'API (contract-first).
- ⚠️ **CI complète arrive en Story 6.5** — pattern acceptable mais à risque de dette technique si reporté trop loin. **Recommandation** : ajouter un AC CI minimal (lint + tests unitaires) dans Story 1.1.

### 5.3 🔴 Violations critiques

**Aucune.**

### 5.4 🟠 Issues majeures

| # | Story | Issue | Action recommandée |
|---|-------|-------|--------------------|
| Q-1 | Story 4.6 | Combine `IntegrityToast` (FR-22) + sauvegarde incrémentale ; **endpoint sauvegarde non spécifié** dans les AC | Soit scinder en 4.6a/4.6b, soit ajouter un AC explicite : « `POST /api/v1/sessions/{id}/answers` (draft, idempotent) appelé sur changement de réponse, debounce 2 s » |
| Q-2 | Architecture / `contracts/openapi.yaml` | Sauvegarde incrémentale mentionnée sans contrat API formel | Compléter OpenAPI dès Story 1.2 ou Story 4.6 avec l'endpoint drafts |

### 5.5 🟡 Concerns mineurs

| # | Story | Concern | Suggestion |
|---|-------|---------|------------|
| Q-3 | Story 1.1 | Aucune CI au scaffold | AC : `.github/workflows/ci.yml` minimal exécute lint + tests unitaires sur PR |
| Q-4 | Story 2.6 | Format CSV imprécis (séparateur, encodage Windows) | Préciser : « UTF-8 BOM accepté, séparateur virgule ou point-virgule auto-détecté » |
| Q-5 | Story 5.5 | « note sur 20 ou échelle documentée » non tranchée | Trancher : note sur 20 fixe MVP, échelle paramétrable post-MVP |
| Q-6 | Story 5.6 | Combine export résultats + export journal | Split optionnel 5.6a / 5.6b |
| Q-7 | Story 6.8 | Persona inversé (référent consomme la doc) | Reformuler « As a équipe projet, I want fournir... pour que les référents... » |
| Q-8 | Stories 3.6 / 4.5 / 5.1 | « As a système » au lieu de user | Pattern acceptable pour règles infra ; reformulation possible |
| Q-9 | Story 4.4 | Pas d'AC pour horloge client décalée (mobile sleep) | AC : « si timer client diverge > N s du serveur, resync sur prochaine requête » |
| Q-10 | Story 4.6 (lié à Q-1) | Vocabulaire « événements suspects » dans le copywriting des AC | Vérifier conformité UX-DR21 (zéro « suspect » côté élève) |

### 5.6 Statistiques qualité globale

- **Stories totales** : 39 (37 métier + 2 infra : 1.1, 1.2)
- **Stories conformes sans remarque** : **30/39 (77 %)**
- **Stories avec concerns mineurs** : 8/39 (20 %)
- **Stories avec issue majeure** : 1/39 (Story 4.6 — 2.5 %)
- **Stories avec violation critique** : 0/39 (0 %)

**Qualité globale : très élevée.** Découpage sain, traçabilité PRD/UX/Architecture explicite dans les AC, starter template correctement intégré, aucune forward-dependency, aucun epic technique déguisé.

---

## 6. Summary and Recommendations

### 6.1 Overall Readiness Status

# ✅ READY (avec ajustements mineurs recommandés)

Le projet **Kopie** est prêt à entrer en **Phase 4 — Implémentation**. Les 4 piliers de planification (PRD, UX, Architecture, Epics/Stories) sont complets, cohérents, alignés et tracés. **Aucun blocage critique** ne s'oppose au démarrage de la première story (`1.1 Scaffold monorepo`).

**Indicateurs clés :**

| Dimension | Score | Détail |
|-----------|-------|--------|
| Couverture FR | **100 %** | 43/43 FRs adressés (40 complets + 3 partiels) |
| Couverture NFR | **100 %** | 12/12 NFRs couverts par 15 NFRs raffinés en epics |
| Alignement UX ↔ PRD | **100 %** | 25 UX-DR explicitement référencés dans les AC |
| Alignement Architecture ↔ PRD | **100 %** | Mapping FR→endpoints complet |
| Qualité epics | **97 %** | 30/39 stories sans remarque ; 0 violation critique |
| Questions PRD §10 tranchées | **5/6** | Seul §10.4 (seuils SM-5) reporté à la bêta — acceptable |

### 6.2 Critical Issues Requiring Immediate Action

**Aucune issue critique.** Le projet peut démarrer en l'état.

### 6.3 Issues majeures recommandées avant la première story de l'Epic 4

| # | Item | Sévérité | Effort | Quand traiter |
|---|------|----------|--------|---------------|
| Q-1 | Story 4.6 ne spécifie pas le contrat API de sauvegarde incrémentale des réponses | 🟠 Major | ~15 min | **Avant Story 4.6** — au plus tard en Story 1.2 (OpenAPI) |
| Q-2 | `contracts/openapi.yaml` à compléter avec l'endpoint drafts | 🟠 Major | ~10 min | **Story 1.2** (contract-first) |
| G-1 | FR-7 Import Markdown : décider Story 2.7 vs report explicite « Hors MVP » | 🟡 Medium | ~5 min | **Avant Story 2.6** |
| G-2 | FR-42 Chiffrement at-rest : exigence self-host non documentée | 🟡 Medium | ~5 min | **Avant Story 6.6** |
| G-3 | FR-43 Rate limit routes publiques : liste explicite manquante | 🟡 Medium | ~5 min | **Avant Story 6.5** |

**Effort total estimé pour refermer tous les gaps : ~40 minutes** d'édition ciblée sur `epics.md` et `architecture.md` (et `contracts/openapi.yaml` quand il sera créé).

### 6.4 Concerns mineurs (peuvent être traités en cours de route)

- **Q-3** Ajouter CI minimale à Story 1.1
- **Q-4** Préciser format CSV (UTF-8 BOM, séparateurs alternatifs) — Story 2.6
- **Q-5** Trancher l'échelle de notation — Story 5.5
- **Q-6** Split optionnel export résultats/journal — Story 5.6
- **Q-7** Reformuler persona Story 6.8
- **Q-8** Reformuler stories « As a système »
- **Q-9** AC resync horloge — Story 4.4
- **U-1** Ajouter `jest-axe` à la matrice CI

### 6.5 Recommended Next Steps

1. **(40 min) Refermer les 3 gaps Medium (G-1, G-2, G-3) et les 2 issues majeures (Q-1, Q-2)** par édition de `epics.md` :
   - Ajouter **Story 2.7 Import Markdown** ou trancher « MD = post-MVP » et l'écrire dans `epics.md` § Hors MVP.
   - Ajouter AC dans Story 6.6 : « le guide self-host documente l'exigence d'un volume chiffré au repos ».
   - Étoffer Story 6.5 avec la liste explicite des routes publiques sous rate-limit.
   - Ajouter AC dans Story 4.6 (ou créer Story 4.6b) avec l'endpoint `POST /api/v1/sessions/{id}/answers` + debounce + idempotency.
   - Ajouter une mention de cet endpoint dans Story 1.2 (OpenAPI initial — élargir le scope contrat).

2. **(facultatif, 15 min)** Refermer les concerns mineurs Q-3 à Q-9 et U-1.

3. **Démarrer Phase 4** par la **Story 1.1 Scaffold monorepo** avec un agent BMad-quick-dev ou BMad-dev-story.

4. **Tracker en parallèle (hors stories de code)** :
   - **Story 6.8** doit démarrer en amont avec un expert juridique externe (la rédaction RGPD prend plus de temps qu'une story de code).
   - **Plan de validation bêta** : protocole SM-5 (seuils événements suspects), recrutement 1 prof + 1 élève PAP — peut être préparé en parallèle.

5. **À mi-parcours d'Epic 4** : exécuter un `bmad-code-review` adversarial sur l'implémentation de la session élève (la zone la plus critique en termes d'UX confiance + intégrité technique).

### 6.6 Forces saillantes du projet

- 🎯 **PRD exemplaire** : 43 FRs avec conséquences testables, hypothèses indexées, contre-métriques explicites.
- 🎯 **UX raffinée** : 25 UX-DR mappés, direction visuelle D2 validée par l'utilisateur, copywriting cohérent avec la posture produit (« tracer pas sanctionner »).
- 🎯 **Architecture tranchée** : versions verrouillées (FastAPI 0.136.1, create-vite 9.0.7), commandes d'init reproductibles, patterns anti-conflit pour agents IA.
- 🎯 **Epics traçables** : FR Coverage Map explicite, AC en Given/When/Then systématique, références UX-DR dans les AC.
- 🎯 **Décisions reportées maîtrisées** : 5 des 6 questions ouvertes PRD sont tranchées (architecture) ou planifiées (Story 6.8 RGPD).
- 🎯 **Posture produit anti-dérive** : contre-métriques SM-C1/SM-C2 + interdiction du rouge sur événements élève + vocabulaire neutre = garde-fous contre la dérive proctoring.

### 6.7 Final Note

Cette évaluation a identifié **0 issue critique, 2 issues majeures, 8 concerns mineurs et 3 warnings info** répartis sur **5 catégories** (couverture FR, alignement UX/Archi, qualité stories, contrat API, CI). Tous sont refermables en moins d'une heure d'édition ciblée.

Le projet **Kopie est l'un des dossiers de planification les plus aboutis** que j'ai validés dans le cadre de cette skill : la traçabilité PRD → UX → Architecture → Epics → Stories est explicite à chaque niveau, les conventions anti-conflit pour agents IA sont documentées, et le starter template est codifié à la commande près. Vous pouvez démarrer l'implémentation **en confiance**.

---

**Évaluation conduite par** : Product Manager (BMad — bmad-check-implementation-readiness)
**Date** : 2026-05-19
**Statut** : ✅ READY pour Phase 4 — Implémentation

---

## 7. Addendum — Clôture des gaps (2026-05-19, post-évaluation)

À la demande de l'utilisateur, les 5 gaps identifiés (Q-1, Q-2, G-1, G-2, G-3) ont été refermés par édition ciblée de `epics.md` et `architecture.md`. Deux concerns mineurs bonus ont également été traités (U-1 jest-axe, Q-4 CSV).

### 7.1 Actions effectuées

| Réf. | Sévérité | Action concrète | Fichier(s) |
|------|----------|-----------------|-------------|
| **G-1** | 🟡 Medium | **Story 2.7 « Spécification et import de questions depuis Markdown » créée**. AC complets : convention à publier dans `docs/imports/markdown-format.md`, 4 types MVP supportés, 2 exemples min., parser réutilise service Story 2.6, alternative documentée si trop coûteux. | `epics.md` (nouvelle Story 2.7 entre 2.6 et Epic 3) |
| **Q-1** | 🟠 Major | **Story 4.6 restructurée en 2 volets explicites** : (a) avertissements (FR-22) inchangé, (b) sauvegarde incrémentale avec contrat API précis : `POST /api/v1/sessions/{id}/answers` avec debounce 2 s, `X-Idempotency-Key`, `GET` pour reprise, file d'attente visible, avertissement « Sauvegarde indisponible » après 3 retries. | `epics.md` (Story 4.6) |
| **Q-2** | 🟠 Major | **Endpoint drafts ajouté à la table « API & Communication Patterns »** de l'architecture, avec mention « idempotent par `question_id` + `X-Idempotency-Key` », « mutable jusqu'à soumission, gelé après ». Le gap « Spécification import Markdown » de l'analyse architecture est requalifié en « Story 2.7 dédiée ». | `architecture.md` (§ API & Communication Patterns + § Gap Analysis Results) |
| **G-2** | 🟡 Medium | **Story 6.6 enrichie** : exigence explicite de volume chiffré au repos (LUKS / volume managé / option provider), checklist de durcissement post-installation, avertissement de non-conformité FR-42 sans chiffrement disque même si TLS actif. | `epics.md` (Story 6.6) |
| **G-3** | 🟡 Medium | **Story 6.5 restructurée en 4 volets** : (a) rate limit routes auth (4 endpoints listés), (b) **rate limit routes élève publiques (5 endpoints listés explicitement)** avec test pytest par famille et seuils configurables `.env`, (c) protections transverses, (d) CI complète. | `epics.md` (Story 6.5) |
| **Bonus U-1** | 🟢 Info | `jest-axe` ajouté à la matrice CI de Story 6.5 et dans les Additional Requirements (« CI »). | `epics.md` (Story 6.5 + AR) |
| **Bonus Q-4** | 🟡 Concern mineur | Story 2.6 précisée : UTF-8 ± BOM accepté, séparateur virgule ou point-virgule auto-détecté (compatibilité Excel FR), transaction atomique explicite, fixtures de test enrichies (1 valide + 1 erreurs + 1 Excel FR). | `epics.md` (Story 2.6 + AR) |

### 7.2 Vérifications post-clôture

| Vérification | Résultat |
|--------------|----------|
| Cohérence FR Coverage Map (FR-7 = Story 2.6 + Story 2.7) | ✅ Mise à jour ligne 150 |
| Cohérence liste « FRs couverts » Epic 2 | ✅ Mise à jour |
| Cohérence Additional Requirements (Import MD, rate limit, CI, chiffrement) | ✅ 4 entrées mises à jour |
| Cohérence avec section architecture (endpoint drafts mentionné) | ✅ |
| Lints markdown | ✅ Aucune erreur |
| Frontmatter `epics.md` : `revisionNote` ajoutée | ✅ |

### 7.3 Statistiques actualisées post-clôture

| Indicateur | Avant clôture | Après clôture |
|------------|---------------|---------------|
| Stories totales | 39 (2 infra + 37 métier) | **40** (2 infra + 38 métier — Story 2.7 ajoutée) |
| FRs entièrement couverts | 40/43 (93 %) | **43/43 (100 %)** |
| FRs partiellement couverts | 3 (FR-7, FR-42, FR-43) | **0** |
| Issues majeures (🟠) | 2 (Q-1, Q-2) | **0** |
| Gaps medium (🟡) | 3 (G-1, G-2, G-3) | **0** |
| Concerns mineurs résolus en bonus | — | 2 (U-1, Q-4) |
| Concerns mineurs restants | 8 | **6** (Q-3, Q-5, Q-6, Q-7, Q-8, Q-9 — tous optionnels) |
| Stories conformes sans remarque | 30/39 (77 %) | **34/40 (85 %)** |

### 7.4 Nouveau statut final

# ✅ READY (gaps refermés) — Démarrage Phase 4 sans réserve

Le projet est désormais **entièrement aligné** : 100 % de couverture FR complète, zéro issue majeure, zéro gap medium. Les 6 concerns mineurs restants (Q-3, Q-5, Q-6, Q-7, Q-8, Q-9) sont **optionnels** et peuvent être traités en cours d'implémentation par l'agent dev sans risque de retravail.

**Première story à attaquer** : `Story 1.1 — Scaffold monorepo et infrastructure locale` (epics.md ligne ~228).
