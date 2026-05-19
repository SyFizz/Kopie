---
title: "PRD — Kopie"
status: final
created: 2026-05-19
updated: 2026-05-19
---

# PRD : Kopie

## 0. Objet du document

Ce PRD sert de cahier des charges pour le **MVP** de Kopie : équipe produit/développement, contributeurs open-source et relecteurs institutionnels. Il s’appuie sur le [product brief](../../briefs/brief-Kopie-2026-05-19/brief.md) (statut `ready`) et sur `addendum.md` pour le détail technique, juridique et les options rejetées.

**Structure :** glossaire unique (§3) ; exigences fonctionnelles numérotées globalement (FR-1…FR-N) regroupées par capacité ; parcours utilisateur UJ-1…UJ-N ; hypothèses balisées `[ASSUMPTION: …]` et indexées en §11. Pas de matrice de traçabilité formelle — les SM référencent les FR concernés.

**Public et rigueur :** cadrage **interne / OSS** (~5–8 pages équivalent) ; suffisant pour UX, architecture et découpage en epics, sans lourdeur « lancement commercial ».

---

## 1. Vision

Kopie est une plateforme **open-source (AGPL-3.0)** qui permet aux enseignants du secondaire français d’envoyer des **évaluations numériques sécurisées à un élève individuel**, à distance, dans des cas ponctuels : rattrapage pour absent, devoir maison encadré, ou évaluation différenciée (PAP, ULIS).

Le modèle est **entièrement asynchrone** : l’enseignant compose l’évaluation, génère un **accès individuel** (lien nominatif, fenêtre temporelle, aménagements), l’élève passe la session dans son navigateur, l’enseignant consulte ensuite les **résultats** et le **journal de session**. Ce n’est pas un outil de surveillance de classe en temps réel.

Kopie **trace et informe** ; l’enseignant interprète le journal et décide. Zéro installation côté élève, hébergement européen, conformité RGPD native, **instance cloud officielle gratuite** au lancement et **auto-hébergement Docker** pour la souveraineté.

**Moment « aha » visé :** en quelques minutes, un prof envoie un lien à un élève absent (avec aménagements si besoin) et retrouve le lendemain réponses + journal exploitable pour trancher en confiance.

---

## 2. Utilisateur cible

### 2.1 Persona primaire — Marie, prof de lycée

Marie enseigne l’anglais en lycée général. Un élève est absent le jour du contrôle ; elle doit lui faire passer une évaluation équivalente à la maison, dans un cadre encadré, sans visio ni logiciel à installer. Elle n’est pas admin réseau : elle veut un outil **simple, rapide, conforme** pour les données de mineurs.

### 2.2 Jobs To Be Done

- **Fonctionnel :** créer ou réutiliser une évaluation, l’adapter (variante PAP), envoyer un accès à **un** élève, récupérer réponses + journal, corriger et archiver.
- **Émotionnel :** se sentir **équitable** envers l’absent ou l’élève aménagé ; réduire l’angoisse du « je ne sais pas ce qu’il a fait derrière son écran » sans devenir surveillante.
- **Social :** pouvoir **justifier** sa décision (note, report, oral) face à la direction ou aux parents avec des éléments factuels, pas un score anti-triche opaque.
- **Contextuel :** usage **ponctuel** (quelques fois par trimestre), pas remplacement de l’ENT ni du cours en classe.

### 2.3 Non-utilisateurs (v1)

- Enseignant voulant surveiller **toute une classe en direct** (hors périmètre).
- Établissement exigeant **SSO ENT** dès le jour 1 (roadmap v1).
- Élève ou parent comme utilisateur authentifié permanent (pas de compte élève).

### 2.4 Parcours utilisateur clés

- **UJ-1. Marie envoie un rattrapage à un absent**
  - **Persona + contexte :** Marie, lendemain du contrôle, élève absent justifié.
  - **État d’entrée :** connectée à l’espace enseignant ; évaluation déjà créée ou à créer depuis la banque.
  - **Chemin :** crée ou ouvre une **évaluation** → choisit la variante standard → configure l’**accès individuel** (nom/prénom élève, fenêtre ven–dim 18h–22h) → copie le lien → l’envoie par l’ENT ou mail d’établissement.
  - **Climax :** lien généré en **moins de cinq minutes** depuis une évaluation existante.
  - **Résolution :** accès en statut « en attente » dans l’historique ; elle peut invalider le lien si l’élève ne doit plus passer.
  - **Cas limite :** fenêtre expirée avant passage → statut « expirée », pas de session partielle exposée à un tiers.

- **UJ-2. Lucas passe l’évaluation avec aménagements PAP**
  - **Persona + contexte :** Lucas, 16 ans, tiers-temps et police OpenDyslexic.
  - **État d’entrée :** reçoit le lien ; pas de compte.
  - **Chemin :** saisit nom/prénom → écran d’instructions → plein écran automatique → répond aux questions (timer visible, +50 % temps) → avertissements non bloquants si perte de focus → confirmation → soumission.
  - **Climax :** soumission avant expiration du timer ; session enregistrée.
  - **Résolution :** message de fin clair ; pas d’accès aux résultats côté élève `[ASSUMPTION: pas de consultation note par l’élève au MVP]`.
  - **Cas limite :** sortie plein écran sur iPad Safari → événement journalisé + avertissement ; passage possible si l’élève revient `[ASSUMPTION: pas de blocage dur au MVP, conformément à la posture « tracer »]`.

- **UJ-3. Marie analyse résultats et journal le lendemain**
  - **Persona + contexte :** Marie, lendemain matin, avant de saisir la note.
  - **État d’entrée :** connectée ; accès en statut « terminée ».
  - **Chemin :** ouvre l’accès → consulte réponses (QCM auto-corrigés, ouvertes à corriger) → attribue note/appréciation → ouvre le **journal** (résumé + détail) → exporte PDF si besoin pour le dossier.
  - **Climax :** décision de note fondée sur **copie + journal**, pas sur un score anti-triche automatique.
  - **Résolution :** résultat exporté ; historique à jour.

---

## 3. Glossaire

| Terme | Définition |
|-------|------------|
| **Enseignant** | Utilisateur authentifié propriétaire de ses **évaluations** et **accès individuels**. |
| **Élève** | Personne passant une **session** via un **accès individuel**, identifiée par nom/prénom sans compte permanent. |
| **Évaluation** | Unité pédagogique composée de **questions**, métadonnées (titre, consignes, durée nominale) et paramètres (randomisation, etc.). |
| **Variante** | Version d’une **évaluation** liée (ex. standard / PAP) partageant les métadonnées, contenu distinct. |
| **Banque de questions** | Répertoire personnel de **questions** réutilisables par l’enseignant. |
| **Accès individuel** | Lien sécurisé nominatif, fenêtre temporelle, aménagements et **variante** associée ; statut : en attente, en cours, terminée, expirée, invalidée. |
| **Session** | Instance unique du passage d’une **évaluation** par un **élève** via un **accès individuel**. |
| **Journal de session** | Chronologie horodatée d’événements (démarrage, réponses, sorties plein écran, pertes de focus, etc.). |
| **Événement suspect** | Événement journalisé pouvant indiquer un manquement à l’intégrité (ex. sortie plein écran, perte de focus, DevTools) — **sans score automatique de triche**. |
| **Aménagement** | Réglage par **accès individuel** : tiers-temps, OpenDyslexic, agrandissement texte. |
| **Instance cloud officielle** | Déploiement hébergé par l’éditeur du projet, gratuit au lancement. |
| **Auto-hébergement** | Déploiement Docker Compose par l’établissement ou un tiers. |

---

## 4. Fonctionnalités

### 4.1 Comptes enseignants

**Description :** Espace personnel isolé ; aucun enseignant n’accède aux données d’un autre. Réalise UJ-1, UJ-3.

#### FR-1 : Inscription

Un **enseignant** peut créer un compte avec email et mot de passe `[ASSUMPTION: validation email au MVP — lien de confirmation]`.

**Conséquences (testables) :**
- Après inscription validée, un espace vide est créé, sans données d’un autre enseignant.
- Les mots de passe respectent une politique minimale documentée (longueur, complexité).

#### FR-2 : Connexion et session

Un **enseignant** peut se connecter et maintenir une session authentifiée (JWT) jusqu’à expiration ou déconnexion.

**Conséquences :**
- Toute route enseignant non authentifiée renvoie une erreur 401.
- Déconnexion invalide le jeton côté client.

#### FR-3 : Profil

Un **enseignant** peut consulter et modifier son profil (nom affiché, email, mot de passe).

#### FR-4 : Isolation des données

Le système garantit l’isolation stricte des **évaluations**, **accès individuels**, **sessions** et **journaux** par enseignant.

**Conséquences :**
- Aucune requête API enseignant ne retourne un identifiant appartenant à un autre enseignant.

---

### 4.2 Création et gestion des évaluations

**Description :** Composition sur mesure, banque, import, variantes. Formats MVP : choix unique/multiple, réponse courte, production écrite ; modèle extensible pour types futurs (association, ordre, médias). Réalise UJ-1.

#### FR-5 : Composer une évaluation

Un **enseignant** peut créer une **évaluation** avec des **questions** des types : choix (unique ou multiple), réponse courte, texte libre.

**Conséquences :**
- Chaque question a un énoncé, une pondération optionnelle et des critères de correction pour les choix.
- L’architecture de données permet d’ajouter de nouveaux types sans migration destructive `[ASSUMPTION: schéma polymorphe ou JSON typé documenté en architecture]`.

#### FR-6 : Randomisation

Un **enseignant** peut activer, par **évaluation**, la randomisation de l’ordre des **questions** et/ou des propositions de choix.

#### FR-7 : Import de questions

Un **enseignant** peut importer des **questions** depuis un fichier CSV ou Markdown selon un format documenté (voir addendum).

**Conséquences :**
- Import invalide : message d’erreur lisible, aucune importation partielle silencieuse.

#### FR-8 : Banque de questions

Un **enseignant** peut enregistrer des **questions** dans sa **banque** et les réinsérer dans une **évaluation**.

#### FR-9 : Variantes d’évaluation

Un **enseignant** peut créer plusieurs **variantes** liées à une même **évaluation** (ex. standard et PAP) partageant titre et métadonnées communes.

**Conséquences :**
- Modifier le titre sur la variante mère se propage ou est explicitement synchronisé selon règle documentée.

#### FR-10 : Paramètres de session sur l’évaluation

Un **enseignant** peut définir sur l’**évaluation** : durée nominale, interdiction de retour arrière après validation d’une question (optionnel).

---

### 4.3 Accès individuel

**Description :** Pont entre enseignant et élève ; un élève, un lien, une fenêtre. Réalise UJ-1, UJ-2.

#### FR-11 : Générer un accès individuel

Un **enseignant** peut créer un **accès individuel** pour un **élève** (nom, prénom), associé à une **variante** et à une fenêtre temporelle (début/fin).

**Conséquences :**
- Le lien est **non devinable** (token signé HMAC ou JWT à usage unique).
- Un accès ne peut être utilisé qu’**une fois** pour démarrer une **session** complète `[ASSUMPTION: réouverture interdite après soumission ; avant soumission, comportement défini en FR-14]`.

#### FR-12 : Aménagements par accès

Un **enseignant** peut configurer par **accès individuel** : tiers-temps +33 % ou +50 % sur la durée, police OpenDyslexic, agrandissement du texte.

**Conséquences :**
- La durée effective du timer reflète le coefficient choisi.

#### FR-13 : Invalider ou réinitialiser un accès

Un **enseignant** peut invalider un **accès individuel** non utilisé, ou le réinitialiser avant toute **session** démarrée.

**Conséquences :**
- Lien invalidé : HTTP 410 ou équivalent avec message élève explicite.
- Accès en statut « invalidée » visible dans l’historique.

#### FR-14 : Expiration hors fenêtre

Le système refuse le démarrage ou la poursuite d’une **session** en dehors de la fenêtre temporelle de l’**accès individuel**.

---

### 4.4 Session élève

**Description :** Interface élève minimale, APIs navigateur standard uniquement (Fullscreen, Page Visibility). Réalise UJ-2.

#### FR-15 : Identification élève

Un **élève** peut commencer une **session** en saisissant nom et prénom, sans créer de compte.

**Conséquences :**
- Données minimales ; pas de tracking publicitaire ; conservation limitée (voir §4.8 et NFR).

#### FR-16 : Plein écran au démarrage

Au démarrage de la **session**, le système demande le passage en plein écran via Fullscreen API.

**Conséquences :**
- Si le plein écran est refusé, l’élève est informé et la **session** ne démarre pas `[ASSUMPTION: démarrage conditionné au plein écran sur desktop ; iOS documenté en best-effort]`.

#### FR-17 : Journalisation sorties plein écran

Chaque sortie du plein écran est enregistrée dans le **journal de session** avec horodatage et durée hors plein écran.

#### FR-18 : Journalisation perte de focus

Chaque changement d’onglet ou perte de visibilité (Page Visibility API) est journalisé.

#### FR-19 : Limitation copier-coller

Les raccourcis copier-coller (Ctrl/Cmd+C/V) sont bloqués pendant la **session**.

**Out of scope :** empêcher toute exfiltration (capture écran, second appareil).

#### FR-20 : Détection DevTools

L’ouverture des outils de développement est détectée et journalisée comme **événement suspect**.

#### FR-21 : Timer et soumission automatique

Un timer visible décompte la durée (après aménagements) ; à expiration, soumission automatique des réponses déjà saisies.

#### FR-22 : Avertissements non bloquants

À chaque **événement suspect**, un message visuel non bloquant informe l’élève que l’événement a été enregistré.

#### FR-23 : Navigation entre questions

Si activé sur l’**évaluation**, l’élève ne peut pas revenir modifier une question déjà validée.

#### FR-24 : Confirmation de soumission

L’élève doit confirmer explicitement avant la soumission finale.

---

### 4.5 Journal de session

**Description :** Artefact central de la posture « tracer, pas sanctionner ». Réalise UJ-3.

#### FR-25 : Enregistrement exhaustif

Le système enregistre horodaté : démarrage, chaque réponse soumise, sorties plein écran, pertes de focus, tentatives copier-coller, DevTools, soumission finale.

#### FR-26 : Consultation enseignant

Seul l’**enseignant** propriétaire de l’**accès individuel** peut consulter le **journal de session** associé.

#### FR-27 : Export du journal

Un **enseignant** peut exporter le **journal** en PDF et CSV.

#### FR-28 : Résumé synthétique

Le système affiche un résumé : nombre d’**événements suspects**, durée totale hors focus, durée totale de la **session**.

---

### 4.6 Résultats et correction

**Description :** Correction hybride auto + manuelle. Réalise UJ-3.

#### FR-29 : Correction automatique des choix

Les questions à choix sont corrigées automatiquement à la soumission.

#### FR-30 : Correction manuelle des ouvertes

Un **enseignant** voit les réponses courtes et productions écrites pour correction manuelle.

#### FR-31 : Note ou appréciation

Un **enseignant** peut attribuer un score et/ou une appréciation textuelle par **session**.

#### FR-32 : Export des résultats

Un **enseignant** peut exporter les résultats d’un **élève** (PDF, CSV).

#### FR-33 : Historique des envois

Un **enseignant** voit l’historique de tous les **accès individuels** avec statut : en attente, en cours, terminée, expirée, invalidée.

---

### 4.7 Déploiement et administration

**Description :** Double canal cloud + self-host. Hors interface enseignant standard.

#### FR-34 : Configuration par environnement

Un déployeur peut configurer l’application via variables d’environnement (`.env` documenté).

#### FR-35 : Docker Compose

Un déployeur peut lancer l’application via Docker Compose incluant application, PostgreSQL et reverse proxy (Caddy ou Traefik).

#### FR-36 : HTTPS automatique

La configuration Docker documentée permet HTTPS via Let’s Encrypt.

#### FR-37 : Migrations base de données

Le déploiement inclut un mécanisme de migration de schéma PostgreSQL versionné.

#### FR-38 : Documentation auto-hébergement

Le dépôt fournit README et guide d’auto-hébergement suffisants pour un déploiement sans support commercial.

#### FR-39 : Instance cloud officielle

Le projet maintient une **instance cloud officielle** gratuite au lancement, fonctionnellement équivalente au MVP self-host `[ASSUMPTION: même codebase, configuration managée par l’équipe projet]`.

---

### 4.8 Sécurité et confidentialité (fonctionnel)

**Description :** Exigences sécurité visibles côté produit ; détail technique en addendum.

#### FR-40 : Lien signé à usage unique

Les **accès individuels** utilisent un token signé non devinable, invalidé après usage ou expiration.

#### FR-41 : Minimisation et rétention données élève

Les données d’**élève** ne sont conservées que pendant la durée configurée par le déployeur ; au-delà, suppression ou anonymisation.

#### FR-42 : Chiffrement et transport

Données chiffrées au repos et en transit (TLS obligatoire en production).

#### FR-43 : Protection des endpoints

Les endpoints d’authentification et d’**accès individuel** sont protégés contre injection SQL, XSS, CSRF et abus par rate limiting.

---

## 5. Non-objectifs (explicites)

- Surveillance **classe entière** en temps réel.
- Webcam, micro, proctoring vidéo ou IA anti-triche.
- Correction automatique des réponses ouvertes par IA.
- Carnet de notes ou intégration ENT (MVP).
- Application mobile native (responsive web suffit).
- SSO / OAuth ENT (roadmap v1).
- Compte **élève** permanent ou espace élève historique.
- Score ou sanction automatique de « triche ».
- Fonctionnalités payantes sur le self-host `[NON-GOAL for MVP: monétisation self-host]`.

---

## 6. Périmètre MVP

### 6.1 Dans le périmètre

- Comptes **enseignants** isolés (FR-1 à FR-4).
- **Évaluations** : types de base, banque, import, variantes, randomisation (FR-5 à FR-10).
- **Accès individuels** avec aménagements (FR-11 à FR-14).
- **Session élève** complète (FR-15 à FR-24).
- **Journal** + exports (FR-25 à FR-28).
- **Résultats** + historique (FR-29 à FR-33).
- Sécurité fonctionnelle (FR-40 à FR-43).
- Docker Compose + cloud officielle gratuite (FR-34 à FR-39).
- UI en français ; architecture i18n prête.
- Accessibilité élève RGAA AA ; OpenDyslexic.

### 6.2 Hors MVP

| Élément | Raison |
|---------|--------|
| SSO ENT | Complexité institutionnelle — v1 |
| Types de questions avancés (association, médias…) | Extensibilité prévue, pas requis jour 1 |
| Premium cloud | Modèle futur ; MVP 100 % gratuit |
| Temps réel / WebSocket | Architecture async suffit |

---

## 7. Métriques de succès

**Primaire**

- **SM-1 : Activation enseignant** — % de comptes ayant créé ≥1 **évaluation** et émis ≥1 **accès individuel** dans les 14 jours. Cible : `[ASSUMPTION: ≥ 40 %]` sur cohorte bêta. Valide FR-5, FR-11.
- **SM-2 : Time-to-link** — médiane du temps entre connexion et première génération de lien sur un parcours « évaluation existante ». Cible : **< 5 minutes**. Valide UJ-1, FR-11.

**Secondaire**

- **SM-3 : Sessions complétées** — ratio **sessions** « terminée » / accès « en attente ou en cours ». Valide UJ-2, FR-21, FR-24.
- **SM-4 : Rétention d’usage** — % d’enseignants actifs mois M ayant réémis un **accès** en M+1. Cible : `[ASSUMPTION: ≥ 25 %]` à 6 mois. Valide valeur récurrente du cas d’usage.
- **SM-5 : Signaux d’intégrité exploitables** — % de **sessions** avec ≥1 **événement suspect** ; corrélation qualitative avec décisions enseignants (enquête bêta). Valide FR-25, FR-28. `[ASSUMPTION: seuil N et protocole d’enquête définis en bêta]`.
- **SM-6 : Feedback institutionnel** — nombre de retours positifs documentés (RGPD, PAP, charte) de directions ou référents numériques. Valide positionnement conformité.

**Contre-métriques (ne pas optimiser)**

- **SM-C1 : Taux de « triche détectée » automatique** — Kopie ne doit pas introduire de score punitif automatique. Contrebalance toute dérive produit vers le proctoring.
- **SM-C2 : Durée moyenne de configuration d’une évaluation** — une hausse continue signale une sur-complexité de composition ; ne pas « réussir » en alourdissant FR-5 à FR-9.

---

## 8. Exigences non fonctionnelles transverses

### Performance

- La **session élève** reste utilisable sur matériel modeste et connexion ADSL (First Contentful Paint élève < 3 s `[ASSUMPTION]` ; interactions formulaire < 100 ms ressenti).
- Pas de WebSocket requis au MVP.

### Sécurité

- OWASP Top 10 mitigé ; audits de dépendances dans CI `[ASSUMPTION: CI à définir en architecture]`.
- Secrets hors dépôt ; rotation documentée pour self-hosters.

### Accessibilité

- Interface **élève** conforme **RGAA niveau AA**.
- OpenDyslexic disponible via **aménagement** (FR-12).

### Compatibilité navigateur

- Chrome et Firefox récents : support complet.
- Safari / iOS : best-effort ; limitations Fullscreen documentées (addendum).

### Internationalisation

- Chaînes externalisées ; français livré au MVP.

### Observabilité

- Logs techniques structurés côté serveur ; pas de données élève en clair dans les logs `[ASSUMPTION]`.

---

## 9. Contraintes et garde-fous

### Confidentialité et RGPD

- Hébergement et traitement **Union européenne** uniquement.
- Base légale, information des personnes, droits (accès, rectification, effacement), registre : documentés pour le self-host et la cloud officielle `[ASSUMPTION: base légale mission d’intérêt public / contrat selon déploiement — validation juridique requise avant bêta publique]`.
- Durée de conservation **paramétrable** par le déployeur (défaut proposé : 12 mois `[ASSUMPTION]`).
- Pas de transfert hors UE ; pas de sous-traitant US critique dans la chaîne MVP.

### Données des mineurs

- Traitement minimal ; pas de compte élève ; pas de profilage ni tracking publicitaire.
- Responsable de traitement : établissement ou enseignant selon déploiement — clarifier dans la documentation légale.

### Coût et modèle open source

- Code **AGPL-3.0** ; self-host **gratuit** sans restriction fonctionnelle MVP.
- Cloud officielle gratuite au lancement ; premium cloud possible plus tard sans briser l’équité self-host.

### Plateforme

- Web responsive (enseignant + élève) ; pas d’app native MVP.

---

## 10. Questions ouvertes

1. **Base légale et rôles RGPD** — Qui est responsable de traitement sur la cloud officielle vs self-host ? DPA type établissement ?
2. **Format d’import CSV/Markdown** — Spécification finale et exemples de fichiers.
3. **Comportement accès partiellement utilisé** — Session abandonnée en cours : réémission d’un nouvel accès ou reprise ?
4. **Seuils SM-5** — Valeur de N pour « événements suspects » et protocole bêta.
5. **Choix backend** Node/Fastify vs Python/FastAPI — tranché en architecture.
6. **Conservation par défaut** — 12 mois adapté au contexte scolaire français ?

---

## 11. Index des hypothèses

| Réf. | Description |
|------|-------------|
| §2.4 UJ-2 | Pas de consultation note par l’élève au MVP |
| §2.4 UJ-2 | Pas de blocage dur après événement suspect au MVP |
| FR-1 | Validation email à l’inscription |
| FR-5 | Schéma extensible pour types de questions |
| FR-11 | Usage unique strict ; pas de reprise après soumission |
| FR-16 | Démarrage conditionné au plein écran (desktop) |
| FR-39 | Cloud et self-host partagent la même codebase |
| SM-1 | Cible 40 % activation bêta |
| SM-4 | Cible 25 % rétention M+1 |
| SM-5 | Seuil N et protocole en bêta |
| §9 RGPD | Conservation défaut 12 mois ; base légale à valider juridiquement |
| NFR perf | FCP < 3 s, CI audits à définir |
| NFR logs | Pas de données élève en clair dans les logs |

---

*Stack technique, formats d’import, digest concurrentiel et limites navigateur : `addendum.md`.*
