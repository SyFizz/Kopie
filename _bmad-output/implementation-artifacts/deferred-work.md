## Deferred from: code review of 1-2-contrat-openapi-initial-et-types-partages.md (2026-05-19)

- Chemin `OPENAPI_CONTRACT_PATH` sensible au répertoire de lancement (`../../contracts/openapi.yaml`) : fiabiliser via résolution absolue basée sur le fichier de config ou variable d'environnement obligatoire.
- Preuve d'usage des types front limitée à des smoke tests d'import : renforcer plus tard avec des tests d'intégration qui valident la consommation des types dans des flux métier réels.
