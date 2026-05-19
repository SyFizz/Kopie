# Addendum — Kopie (contexte PRD / architecture)

Ce document conserve le détail fourni en Discovery qui dépasse le product brief (1–2 pages). Il alimente le PRD, l’architecture et les specs techniques.

## Philosophie produit (rappel)

- Zéro installation élève — Fullscreen API, Page Visibility API uniquement.
- Kopie trace et informe ; pas de sanction automatique.
- Souveraineté : hébergement UE, RGPD, pas de Big Tech critique.
- Auto-hébergement Docker Compose obligatoire ; instance cloud officielle en parallèle.
- Aménagements PAP/ULIS en première classe.

## Stack technique (indicative, non figée)

- Frontend : React, Vite, TailwindCSS
- Backend : Node/Fastify **ou** Python/FastAPI — à trancher en architecture
- PostgreSQL ; auth JWT local ; OAuth2/SAML2 ENT en roadmap v1
- Pas de temps réel MVP ; Docker Compose + GHCR ; AGPL-3.0

## Périmètre fonctionnel détaillé

Voir le dump initial de session (gestion comptes, création évaluation, accès individuel, session élève, journal, résultats, sécurité, admin/déploiement) — repris intégralement dans les inputs du 2026-05-19. Non dupliqué ici pour éviter la dérive ; le PRD reprendra section par section.

## Contraintes non fonctionnelles

- RGPD : base légale, conservation paramétrable, effacement, pas de transfert hors UE.
- Mineurs : traitement minimal, pas de compte élève permanent, pas de tracking.
- Perf : matériel modeste, ADSL.
- Accessibilité : RGAA AA, OpenDyslexic.
- Navigateurs : Chrome/Firefox récents ; Safari best-effort (doc limitations iOS Fullscreen).

## Décisions Discovery (2026-05-19)

| Sujet | Décision |
|-------|----------|
| Utilisateur MVP | Prof lycée général (réf. anglais) |
| Canal lancement | Instance cloud officielle, gratuite |
| Brief | Interne + open-source + cadrage projet |
| Modèle éco | 100 % free AGPL au début ; premium cloud possible plus tard, gratuit en self-host |
| Succès 6–12 mois | Retours enseignants, signaux intégrité session, feedback institution |
| Risque #1 | Légal |
| Stack | Ouverte — exemples non contraignants |
