# EXOCOMS Voitures - Marketplace automobile Odoo

Plateforme e-commerce automobile développée pour **EXOCOMS Group** avec Odoo 18.

Le projet permet de présenter, administrer et commercialiser un catalogue de voitures chinoises avec des prix, photos, caractéristiques, disponibilités et parcours clients complets.

## Sommaire

- [Fonctionnalités principales](#fonctionnalités-principales)
- [Accès administrateur](#accès-administrateur)
- [Tableau de bord Automobile](#tableau-de-bord-automobile)
- [Administrer les voitures](#administrer-les-voitures)
- [Administrer les marques](#administrer-les-marques)
- [Rôles et droits d'accès](#rôles-et-droits-daccès)
- [Pages publiques](#pages-publiques)
- [Catalogue livré](#catalogue-livré)
- [Modules Odoo](#modules-odoo)
- [Installation locale avec Docker](#installation-locale-avec-docker)
- [Installation et mise à jour des modules](#installation-et-mise-à-jour-des-modules)
- [Déploiement sur Odoo.sh](#déploiement-sur-odoosh)
- [Base de données et sauvegardes](#base-de-données-et-sauvegardes)
- [Traductions](#traductions)
- [Outils de maintenance du catalogue](#outils-de-maintenance-du-catalogue)
- [Tests et contrôle qualité](#tests-et-contrôle-qualité)
- [Diagnostic des problèmes fréquents](#diagnostic-des-problèmes-fréquents)
- [Documentation complémentaire](#documentation-complémentaire)

## Fonctionnalités principales

- Catalogue public responsive de véhicules.
- Filtres par marque, catégorie, motorisation, disponibilité, année et budget.
- Tri et pagination du catalogue.
- Fiches véhicules avec galerie, prix, caractéristiques, options et disponibilité.
- Accueil premium avec véhicules mis en avant et défilement continu des marques.
- Marques automobiles avec logos et pages dédiées.
- Achat e-commerce via les produits Odoo associés aux véhicules.
- Demandes de devis avec suivi commercial et création d'opportunités CRM.
- Réservations de véhicules et demandes d'essai.
- Demandes de financement.
- Comparateur de véhicules.
- Favoris et espaces portail client.
- Avis clients avec modération.
- Tableau de bord administrateur automobile.
- Site client disponible en **Français**, **English** et **العربي**.

## Accès administrateur

> **Important : l'administration du projet se fait avec le compte administrateur Odoo de la base de données.**

Le compte administrateur est le compte créé lors de la création de la base Odoo, ou le compte utilisé avec le bouton **Connect** dans Odoo.sh.

Le **mot de passe maître** du gestionnaire de bases de données n'est pas le mot de passe du compte administrateur. Il sert uniquement à créer, supprimer, sauvegarder ou restaurer des bases.

### Parcours exact pour accéder à l'administration

1. Ouvrir Odoo :
   - local : `http://localhost:8069/web/login`
   - Odoo.sh : utiliser le bouton **Connect** du build concerné
2. Se connecter avec le **compte administrateur Odoo**.
3. Ouvrir le sélecteur d'applications Odoo.
4. Cliquer sur l'application nommée **Automobile**.
5. Dans le menu **Automobile**, ouvrir **Tableau de bord**.

Le menu principal de cette solution est donc nommé exactement :

```text
Automobile
```

Le tableau de bord se trouve à cet emplacement :

```text
Automobile > Tableau de bord
```

### Si le menu Automobile n'apparaît pas

Vérifier les points suivants :

1. Le module `auto_base` est installé.
2. Le module `auto_dashboard` est installé.
3. L'utilisateur est bien un utilisateur interne Odoo, et non un utilisateur portail.
4. L'utilisateur possède le groupe **Administrateur automobile**.

Pour attribuer le groupe :

1. Se connecter avec un administrateur Odoo.
2. Ouvrir **Paramètres > Utilisateurs et sociétés > Utilisateurs**.
3. Ouvrir l'utilisateur concerné.
4. Dans les droits d'accès, attribuer le groupe **Administrateur automobile**.
5. Enregistrer puis reconnecter l'utilisateur.

Le compte administrateur Odoo standard reçoit automatiquement le groupe **Administrateur automobile** lors de l'installation du module `auto_base`.

## Tableau de bord Automobile

Le tableau de bord moderne est réservé au groupe **Administrateur automobile**.

Il centralise les actions importantes :

- ajouter une voiture ;
- gérer les voitures ;
- ajouter une marque ;
- gérer les marques ;
- ouvrir le catalogue public ;
- suivre les voitures disponibles, réservées et non publiées ;
- suivre le stock total ;
- consulter les demandes de devis ;
- consulter les réservations ;
- consulter les demandes d'essai ;
- consulter les demandes de financement ;
- modérer les avis clients ;
- suivre les commandes confirmées et le chiffre d'affaires ;
- accéder aux catégories, motorisations et options.

Le bouton **Actualiser** recalcule l'affichage des indicateurs pour la période sélectionnée.

## Administrer les voitures

### Ouvrir la liste des voitures

Deux parcours sont disponibles :

```text
Automobile > Tableau de bord > Gérer les voitures
```

ou :

```text
Automobile > Catalogue > Véhicules
```

### Créer une voiture

1. Ouvrir **Automobile > Tableau de bord**.
2. Cliquer sur **Nouvelle voiture** ou **Ajouter une voiture**.
3. Renseigner au minimum :
   - le nom du modèle ;
   - la marque ;
   - le prix de vente ;
   - l'année ;
   - la disponibilité ;
   - le stock ;
   - la catégorie ;
   - la motorisation.
4. Compléter les données utiles :
   - résumé court ;
   - description ;
   - autonomie ;
   - puissance ;
   - capacité de batterie ;
   - temps de charge ;
   - garantie ;
   - couleurs ;
   - options ;
   - spécifications ;
   - informations SEO.
5. Dans l'onglet **Galerie**, ajouter une ou plusieurs photos réelles du véhicule.
6. Marquer une photo comme couverture avec le champ `is_cover`.
7. Activer **Publié sur le site** lorsque la fiche est prête.
8. Enregistrer.
9. Vérifier le rendu sur le catalogue public : `/cars`.

Si aucun produit e-commerce n'est sélectionné, Odoo crée automatiquement un produit lié à la voiture lors de l'enregistrement.

Le prix de vente de la voiture est synchronisé avec le produit e-commerce associé.

### Modifier une voiture

1. Ouvrir **Automobile > Catalogue > Véhicules**.
2. Rechercher le véhicule par nom, marque, catégorie, motorisation ou disponibilité.
3. Ouvrir la fiche.
4. Modifier les informations nécessaires.
5. Enregistrer.
6. Vérifier la fiche publique correspondante.

### Modifier le statut commercial

La fiche véhicule propose des actions rapides :

- **Marquer disponible**
- **Marquer réservé**
- **Marquer vendu**
- **Marquer bientôt disponible**

Ces statuts influencent l'affichage sur le site et les actions disponibles pour le client.

### Retirer une voiture du site sans la supprimer

Pour conserver l'historique tout en retirant une voiture du catalogue public :

1. Ouvrir la fiche véhicule.
2. Désactiver **Publié sur le site**.
3. Enregistrer.

La suppression définitive doit être utilisée avec prudence, surtout si le véhicule est déjà lié à des devis, commandes, réservations ou demandes clients.

## Administrer les marques

### Ouvrir la liste des marques

```text
Automobile > Tableau de bord > Gérer les marques
```

ou :

```text
Automobile > Catalogue > Marques
```

### Créer une marque

1. Cliquer sur **Nouvelle marque**.
2. Renseigner :
   - le nom ;
   - le code court ;
   - la séquence d'affichage ;
   - le logo ;
   - la description.
3. Activer **Publié sur le site**.
4. Enregistrer.

La séquence contrôle l'ordre d'apparition de la marque dans le site public et dans le défilement continu de l'accueil.

Les logos doivent être lisibles, centrés et suffisamment grands dans leur image source.

## Rôles et droits d'accès

Le projet définit trois groupes métier :

| Groupe | Usage |
| --- | --- |
| **Administrateur automobile** | Accès complet au tableau de bord, aux voitures, marques, configurations et suppressions. |
| **Conseiller commercial automobile** | Consultation du catalogue et traitement opérationnel des demandes commerciales. |
| **Gestionnaire de contenu automobile** | Création et modification des marques, voitures, photos, descriptions et contenus sans suppression définitive. |

Les utilisateurs portail n'ont accès qu'à leurs propres données client : favoris, réservations, essais, avis et demandes de financement.

## Pages publiques

| Page | URL |
| --- | --- |
| Accueil automobile | `/cars/home` |
| Catalogue des véhicules | `/cars` |
| Fiche véhicule | `/cars/<id>` |
| Toutes les marques | `/brands` |
| Page d'une marque | `/brands/<id>` |
| Comparateur | `/cars/compare` |
| Favoris client | `/my/favorites` |
| Réservations client | `/my/bookings` |
| Essais client | `/my/test-drives` |
| Avis client | `/my/reviews` |
| Demandes de financement client | `/my/financing-requests` |

Les préfixes de langue sont ajoutés automatiquement :

- Français : `/cars`
- English : `/en/cars`
- العربي : `/ar/cars`

## Catalogue livré

Le catalogue actuel contient :

- **64 véhicules publiés**
- **17 marques partenaires**
- **64 images produits**
- **64 galeries véhicules**

Les voitures utilisent des photos réelles normalisées pour conserver le véhicule entièrement visible sur les cartes et les fiches.

Les prix sont des prix publics TTC indicatifs ou des prix de lancement européens. Ils doivent être revalidés avant une publication commerciale définitive, car les constructeurs peuvent modifier leurs offres.

Sources :

- [`docs/CATALOG_SOURCES.md`](docs/CATALOG_SOURCES.md)
- [`docs/CATALOG_IMAGE_SOURCES.md`](docs/CATALOG_IMAGE_SOURCES.md)
- [`docs/vehicle_image_sources.md`](docs/vehicle_image_sources.md)

## Modules Odoo

| Module technique | Nom dans Odoo | Rôle |
| --- | --- | --- |
| `auto_base` | Automobile - Base | Modèles métier, sécurité, catalogue administrateur, marques, voitures et produits liés. |
| `auto_website` | Automobile - Site web | Accueil, catalogue public, fiches, marques, favoris, identité EXOCOMS et interface responsive. |
| `auto_sale` | Automobile - Ventes | Demandes de devis, intégration vente et opportunités CRM. |
| `auto_booking` | Automobile - Réservations | Réservations, demandes d'essai, créneaux et portail client. |
| `auto_financing` | Automobile - Financement | Demandes de financement et suivi. |
| `auto_reviews` | Automobile - Avis | Avis clients et modération. |
| `auto_compare` | Automobile - Comparateur | Comparaison de véhicules. |
| `auto_dashboard` | Automobile - Tableau de bord | Tableau de bord administrateur et indicateurs commerciaux. |

### Structure du dépôt

```text
custom_addons/
  auto_base/
  auto_website/
  auto_sale/
  auto_booking/
  auto_financing/
  auto_reviews/
  auto_compare/
  auto_dashboard/
config/
docs/
tools/
docker-compose.yml
```

## Installation locale avec Docker

### Prérequis

- Docker Desktop démarré.
- Docker Compose disponible.
- Git.
- Un navigateur moderne.

### Démarrer Odoo et PostgreSQL

Depuis la racine du projet :

```powershell
docker compose up -d
```

Vérifier les conteneurs :

```powershell
docker compose ps
```

Odoo est disponible sur :

```text
http://localhost:8069
```

### Créer la base locale

Lors du premier démarrage, créer une base depuis le gestionnaire de bases Odoo.

Valeurs recommandées :

| Champ | Valeur recommandée |
| --- | --- |
| Database Name | `ecommerce_voitures_dev` |
| Email | Adresse du futur compte administrateur |
| Password | Mot de passe sécurisé du compte administrateur |
| Language | Français |
| Country | France |
| Demo Data | Selon le besoin de test |

Conserver le mot de passe maître choisi. Il sera demandé pour les opérations de sauvegarde, restauration, duplication ou suppression de base.

### Arrêter ou redémarrer les services

```powershell
docker compose stop
docker compose restart odoo
docker compose down
```

`docker compose down` arrête les conteneurs mais conserve les volumes de données tant que l'option `-v` n'est pas utilisée.

## Installation et mise à jour des modules

### Installation depuis l'interface Odoo

1. Se connecter avec le compte administrateur.
2. Activer le mode développeur.
3. Ouvrir **Applications**.
4. Cliquer sur **Mettre à jour la liste des applications**.
5. Rechercher puis installer les modules dans cet ordre :

```text
auto_base
auto_website
auto_sale
auto_booking
auto_financing
auto_reviews
auto_compare
auto_dashboard
```

Les dépendances Odoo standard, comme Vente, Site Web, eCommerce, CRM, Portail et Tableaux de bord, sont installées automatiquement si nécessaire.

### Mise à jour depuis Docker

Après une modification de code, de vues XML, de données ou de traductions :

```powershell
docker exec auto_odoo odoo `
  -c /etc/odoo/odoo.conf `
  -d ecommerce_voitures_dev `
  -u auto_base,auto_website,auto_sale,auto_booking,auto_financing,auto_reviews,auto_compare,auto_dashboard `
  --stop-after-init

docker compose restart odoo
```

### Consulter les logs locaux

```powershell
docker logs --tail 500 auto_odoo
```

Pour rechercher les erreurs importantes :

```powershell
docker logs --tail 1000 auto_odoo 2>&1 |
  Select-String -Pattern "ERROR|CRITICAL|Traceback|ParseError|RPC_ERROR"
```

## Déploiement sur Odoo.sh

Le dépôt GitHub utilisé est :

```text
https://github.com/exocoms/e-commerce
```

La branche de travail automobile est :

```text
Voitures
```

### Fonctionnement

Lorsque la branche `Voitures` est connectée au projet Odoo.sh et configurée avec le comportement **New build**, chaque nouveau commit poussé sur cette branche déclenche un nouveau build Odoo.sh.

La documentation officielle Odoo.sh décrit les builds et leurs statuts :

- [Odoo.sh - Builds](https://www.odoo.com/documentation/18.0/administration/odoo_sh/getting_started/builds.html)
- [Odoo.sh - Branches](https://www.odoo.com/documentation/18.0/administration/odoo_sh/getting_started/branches.html)

### Publier les changements

Avant de pousser :

```powershell
git status
git branch --show-current
```

La branche active doit être `Voitures`.

Puis :

```powershell
git add .
git commit -m "feat(voitures): mise a jour du projet automobile"
git push origin Voitures
```

### Vérifier le build Odoo.sh

1. Ouvrir le projet Odoo.sh.
2. Sélectionner la branche `Voitures`.
3. Attendre la fin du nouveau build.
4. Vérifier que le build est vert.
5. Ouvrir les logs `install.log` et `odoo.log`.
6. Utiliser **Connect** pour accéder à la base du build avec le compte administrateur.
7. Mettre à jour les modules personnalisés si le build ne les met pas à jour automatiquement.

### Ne pas impacter les autres travaux

- Ne pas pousser sur les branches des autres projets EXOCOMS.
- Ne pas fusionner vers `main` sans validation.
- Ne pas utiliser `git push --force` sur une branche partagée.
- Vérifier les logs Odoo.sh avant toute promotion vers une branche de staging ou production.

## Base de données et sauvegardes

> **La base de données Odoo n'est pas stockée dans GitHub.**

GitHub contient le code, les modules, les données déclaratives XML, les traductions et les images statiques. Les éléments suivants restent dans la base Odoo :

- utilisateurs ;
- clients ;
- commandes ;
- devis ;
- réservations ;
- demandes d'essai ;
- demandes de financement ;
- avis ;
- contenus créés depuis l'interface ;
- pièces jointes et filestore.

### En local

Docker conserve PostgreSQL et le filestore dans les volumes :

```text
pgdata
odoo_data
```

### Sur Odoo.sh

Chaque build possède sa propre base. Un push Git ne copie pas automatiquement la base locale vers Odoo.sh.

Pour récupérer des données existantes, utiliser les fonctions de sauvegarde et restauration Odoo/Odoo.sh en respectant les règles de l'entreprise.

La documentation officielle Odoo.sh explique les bases et sauvegardes :

- [Odoo.sh - Databases](https://www.odoo.com/documentation/18.0/administration/odoo_sh/getting_started/settings.html)

Toujours effectuer une sauvegarde avant une mise à jour importante de modules ou de données.

## Traductions

Le site client est traduit en :

- `fr_FR` : Français
- `en_GB` : English
- `ar_001` : العربي

Les fichiers de traduction se trouvent dans les dossiers `i18n/` des modules.

Pour régénérer les traductions après l'ajout de nouveaux textes :

```powershell
python tools\generate_odoo_translations.py
```

Puis recharger les traductions :

```powershell
docker exec auto_odoo odoo `
  -c /etc/odoo/odoo.conf `
  -d ecommerce_voitures_dev `
  -u auto_base,auto_website,auto_booking,auto_sale,auto_financing,auto_reviews,auto_compare `
  --i18n-overwrite `
  --stop-after-init

docker compose restart odoo
```

Les traductions concernent le site client. Le back-office administrateur reste principalement en français.

## Outils de maintenance du catalogue

Le dossier `tools/` contient les outils utilisés pour maintenir les données automobiles :

| Fichier | Usage |
| --- | --- |
| `tools/catalog_expansion.json` | Source structurée des nouveaux véhicules, marques, prix, caractéristiques et sources. |
| `tools/generate_catalog_expansion.py` | Génération du XML Odoo et de la documentation des sources. |
| `tools/fetch_catalog_assets.py` | Téléchargement et normalisation des photos et logos du catalogue. |
| `tools/generate_odoo_translations.py` | Génération des traductions English et العربي. |

Les photos du catalogue doivent conserver la voiture entière visible, avec un cadrage propre et sans recadrage agressif.

## Tests et contrôle qualité

Avant toute livraison, vérifier au minimum :

1. Accueil `/cars/home`.
2. Catalogue `/cars`.
3. Filtres, tri et pagination.
4. Pages des marques `/brands`.
5. Fiches véhicules, photos, prix, caractéristiques et CTA.
6. Achat e-commerce.
7. Demande de devis.
8. Réservation.
9. Demande d'essai.
10. Demande de financement.
11. Comparateur.
12. Favoris.
13. Avis clients et modération.
14. Tableau de bord `Automobile > Tableau de bord`.
15. Rendu responsive sur mobile, tablette et desktop.
16. Traductions Français, English et العربي.
17. Logs Odoo sans erreur critique.

Plan de test détaillé :

- [`docs/test_plan.md`](docs/test_plan.md)
- [`docs/delivery_checklist.md`](docs/delivery_checklist.md)

## Diagnostic des problèmes fréquents

### Docker ne démarre pas

Erreur typique :

```text
failed to connect to the docker API
dockerDesktopLinuxEngine
```

Solution :

1. Démarrer Docker Desktop.
2. Attendre que le moteur Docker soit prêt.
3. Relancer `docker compose up -d`.

### `ERR_CONNECTION_REFUSED` sur `localhost:8069`

Vérifier :

```powershell
docker compose ps
docker logs --tail 200 auto_odoo
```

### Les changements ne sont pas visibles dans Odoo

1. Mettre à jour le module concerné.
2. Redémarrer Odoo.
3. Recharger la page avec `Ctrl + F5`.
4. Vérifier que le bon build et la bonne base sont utilisés.

### Un build Odoo.sh est rouge

1. Ouvrir le build concerné.
2. Consulter `install.log`.
3. Consulter `odoo.log`.
4. Rechercher la première occurrence de `ERROR`, `CRITICAL`, `Traceback` ou `ParseError`.
5. Corriger la première erreur réelle avant de traiter les erreurs suivantes.
6. Pousser un nouveau commit sur `Voitures`.

### Le menu Automobile n'apparaît pas

1. Vérifier que `auto_base` est installé.
2. Vérifier que l'utilisateur est interne.
3. Attribuer le groupe **Administrateur automobile**.
4. Déconnecter puis reconnecter l'utilisateur.

## Sécurité et mise en production

- Ne jamais committer de mot de passe administrateur en clair.
- Utiliser un mot de passe maître de base sécurisé.
- Utiliser des mots de passe forts pour les comptes Odoo.
- Limiter les droits d'administration aux utilisateurs nécessaires.
- Sauvegarder la base avant les mises à jour importantes.
- Revalider les prix avant publication commerciale.
- Vérifier les licences et attributions des images.
- Tester les parcours clients avant une mise en production.
- Vérifier les erreurs et avertissements dans les logs Odoo.sh.

## Informations EXOCOMS Group

```text
EXOCOMS Group
58 rue de Monceau
75008 Paris
+33 (0)1 84 79 37 55
contact@exocoms.fr
https://www.exocoms.fr/
```

## Documentation complémentaire

- [`docs/architecture.md`](docs/architecture.md)
- [`docs/roadmap.md`](docs/roadmap.md)
- [`docs/test_plan.md`](docs/test_plan.md)
- [`docs/git_workflow.md`](docs/git_workflow.md)
- [`docs/delivery_checklist.md`](docs/delivery_checklist.md)
- [`docs/CATALOG_SOURCES.md`](docs/CATALOG_SOURCES.md)
- [`docs/CATALOG_IMAGE_SOURCES.md`](docs/CATALOG_IMAGE_SOURCES.md)
- [`docs/vehicle_image_sources.md`](docs/vehicle_image_sources.md)
