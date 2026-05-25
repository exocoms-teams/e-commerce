# Methode Git recommandee

## Branches
- `main`: version stable
- `develop`: integration continue
- `feature/*`: une fonctionnalite par branche
- `fix/*`: correctifs ponctuels

## Sequence de travail
1. pull de `develop`
2. creer branche `feature/<module-or-feature>`
3. commits petits et explicites
4. ouvrir PR vers `develop`
5. review rapide + tests manuels
6. merge vers `develop`
7. release vers `main`

## Messages de commit
- `feat(auto_base): add vehicle data model and admin views`
- `feat(auto_booking): add reservation and test drive forms`
- `fix(auto_sale): map order line product to vehicle`
