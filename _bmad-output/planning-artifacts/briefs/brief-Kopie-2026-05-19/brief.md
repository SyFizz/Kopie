---
title: "Product Brief — Kopie"
status: ready
created: 2026-05-19
updated: 2026-05-19
---

# Product Brief : Kopie

## Executive Summary

Kopie est une plateforme SaaS open-source (AGPL-3.0) qui permet aux enseignants du secondaire français d’envoyer des **évaluations numériques sécurisées à un élève individuel**, à distance, dans des cas ponctuels : rattrapage pour absent, devoir maison encadré, ou évaluation différenciée (PAP, ULIS). Le modèle est **entièrement asynchrone** : l’enseignant génère un lien nominatif, l’élève passe l’évaluation chez lui dans une fenêtre définie, l’enseignant consulte les résultats et le journal de session ensuite.

Ce n’est pas un outil de surveillance de classe en temps réel. Kopie **trace et informe** ; c’est l’enseignant qui interprète le journal et décide de la suite. Zéro installation côté élève, hébergement européen, conformité RGPD native, auto-hébergement Docker en une commande, avec une **instance cloud officielle gratuite** comme canal principal au lancement.

Le moment « aha » visé : en quelques minutes, un prof de lycée envoie un lien à un élève absent (avec aménagements si besoin) et retrouve le lendemain les réponses et un journal de session exploitable pour trancher en confiance.

## The Problem

Un prof de lycée général (ex. anglais) qui doit faire passer une évaluation à **un seul élève** à distance se retrouve souvent sans solution adaptée :

- Les outils grand public (formulaires, LMS) ne offrent ni lien nominatif à usage unique, ni journal d’intégrité, ni aménagements PAP intégrés.
- Les solutions « examens sécurisés » du marché visent la **classe entière** avec webcam, proctoring temps réel ou IA — disproportionné, coûteux en confiance, et mal aligné avec le cadre légal des mineurs.
- L’auto-hébergement ou les alternatives souveraines existent peu pour ce **cas d’usage étroit** ; les enseignants improvisent (mail + PDF, visio surveillée) ou renoncent à encadrer l’évaluation.

**Coût du statu quo** : inéquité pour les absents ou élèves aménagés, charge cognitive pour l’enseignant, flou sur ce qui s’est réellement passé pendant la session, et exposition juridique si des données d’élèves mineurs transitent par des services non conformes.

## The Solution

Kopie fournit un espace enseignant isolé pour **composer des évaluations sur mesure** : une banque de questions réutilisable, des variantes (standard / adaptée PAP), import depuis des formats ouverts (CSV, Markdown), et la liberté de construire des parcours qui reflètent la pratique pédagogique — pas seulement des grilles fermées. Le MVP pose des **formats de base** (choix, réponse courte, production écrite) avec une architecture pensée pour **enrichir et combiner** les types de questions au fil des versions (association, ordre, médias, etc.), afin que chaque matière puisse s’exprimer sans être réduite au QCM.

L’enseignant émet ensuite un **accès individuel** : lien sécurisé, fenêtre temporelle, aménagements (tiers-temps, OpenDyslexic, agrandissement). L’élève passe la session dans le navigateur (plein écran, journalisation des événements suspects, timer, soumission automatique). L’enseignant corrige ce qui s’automatise (ex. choix multiples), traite le reste à la main, consulte un **journal horodaté** exportable, et garde l’historique de ses envois.

L’expérience cible reste légère : pas de compte élève permanent, pas de logiciel à installer, pas de surveillance vidéo.

## What Makes This Different

| Dimension | Kopie | Alternatives typiques (Evalbox, Nexam, Quilgo…) |
|-----------|-------|--------------------------------------------------|
| Granularité | Un élève, un accès, une fenêtre | Classe entière, sessions synchrones |
| Posture | Trace ; l’enseignant décide | Sanction / score anti-triche automatique |
| Souveraineté | UE, RGPD natif, AGPL, Docker self-host | SaaS propriétaire, dépendances cloud US |
| Aménagements | Première classe (variantes, tiers-temps, dyslexie) | Souvent optionnels ou absents |
| Technique élève | APIs navigateur standard uniquement | Webcam, extensions, apps |

**Avantage honnête** : exécution focalisée sur un cas d’usage réel et sous-servi, plus open-source et auto-hébergeable que les suites « examen » généralistes — pas une barrière technique infranchissable si un acteur majeur copiait le positionnement.

**Limites assumées** : un journal navigateur ne prouve pas l’absence de triche (second appareil, contournement DevTools). Kopie documente et informe ; il ne remplace pas le jugement professionnel ni un cadre légal solide.

## Who This Serves

**Primaire (MVP)** : enseignant de **lycée général** (toutes matières ; persona de référence : prof d’anglais) qui gère seul ses évaluations ponctuelles à distance. Succès = envoyer un accès en moins de cinq minutes, recevoir des résultats et un journal lisibles sans formation lourde.

**Secondaire** : élève mineur sans compte — identification légère (nom, prénom), session unique, données minimales et durée de conservation paramétrable.

**Tertiaire (post-MVP)** : référent numérique ou direction d’établissement pour avis institutionnel ; contributeurs open-source et auto-hébergeurs (instance cloud = porte d’entrée, self-host = souveraineté).

## Success Criteria

À **6–12 mois**, le produit réussit si :

1. **Retours enseignants** — usage récurrent pour les cas cibles, recommandations pairs, faible friction signalée (création d’éval, envoi de lien, lecture du journal).
2. **Signaux d’intégrité de session** — pas un « taux de triche » objectif (Kopie ne tranche pas), mais des indicateurs exploitables : volume d’événements suspects dans les journaux, corrélation avec les décisions enseignants, sentiment de confiance accrue vs. solutions improvisées. `[ASSUMPTION : métriques détaillées à définir au PRD — ex. % de sessions avec ≥ N sorties plein écran]`
3. **Feedback institutionnel** — retours positifs de directions ou référents sur conformité RGPD, charte numérique, et pertinence pour aménagements (PAP/ULIS), ouvrant la voie à des déploiements établissement.

**Risque n°1 assumé** : **légal** (données de mineurs, base légale, conservation, hébergement UE). Le MVP doit traiter la conformité comme exigence bloquante, pas comme documentation tardive.

## Scope

**Dans le MVP**

- Comptes enseignants isolés ; création d’évaluations et variantes ; accès individuel (lien signé, fenêtre, aménagements, invalidation).
- Session élève navigateur (plein écran, visibilité, timer, journal) ; **formats de questions de base** au MVP, modèle extensible pour la suite.
- Journal exportable ; résultats et correction manuelle ; historique des envois.
- Sécurité applicative de base ; déploiement Docker Compose + instance **cloud officielle gratuite**.
- i18n prête, UI en français ; accessibilité RGAA AA côté élève ; stack technique **ouverte** (exemples React/Vite, Node ou Python, PostgreSQL — choix final en architecture).

**Hors MVP (explicitement)**

- Surveillance classe temps réel, webcam/micro, correction IA des ouvertes.
- Carnet de notes, intégration ENT, SSO (roadmap v1).
- App mobile native.
- Fonctionnalités payantes cloud (possibles plus tard ; **toujours gratuites en self-hosted**).

## Vision

À **2–3 ans**, Kopie devient la référence open-source francophone pour l’**évaluation individuelle encadrée à distance** : adoptée par des enseignants via le cloud, déployée en établissement en self-host quand la souveraineté l’exige, avec SSO ENT et écosystème de contributeurs. Le modèle économique peut évoluer (features premium sur le cloud) sans rompre la promesse AGPL ni l’équité self-host. La posture « tracer, pas sanctionner » et les aménagements PAP/ULIS restent le cœur de la différenciation face aux suites de proctoring de masse.

---

*Détail fonctionnel, stack et contraintes non fonctionnelles : voir `addendum.md` dans ce dossier.*
