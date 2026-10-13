# Capsule House – module Odoo 19 (`capsule_house_theme`)

Thème et module Odoo 19 du site e-commerce Capsule House, déployé sur Odoo.sh.
Branche principale : `capsule_house`.

## Setup dev (Windows, une seule fois)

Ce setup donne l'autocomplétion Odoo dans VS Code (Pylance), un environnement
Python isolé (`venv`) et les dépendances nécessaires (ex. `reportlab` pour le
catalogue PDF). Il ne lance pas Odoo : le site tourne sur Odoo.sh.

### 1. Prérequis

| Outil | Remarque |
|---|---|
| [Git](https://git-scm.com/download/win) | Inclut Git Bash et Git Credential Manager |
| [Python 3.11](https://www.python.org/downloads/) | Cocher **Add Python to PATH** pendant l'installation (3.10 minimum) |
| [VS Code](https://code.visualstudio.com/) | Avec les extensions **Python** et **Pylance** (Microsoft) |

Fermer puis rouvrir tout terminal après l'installation, sinon `git` et `python`
restent introuvables.

### 2. Cloner le projet

Choisir un dossier **court, sans espaces ni accents, hors OneDrive**
(par exemple `C:\Users\<nom>\Documents\Exocoms`).

```bash
git clone --recurse-submodules --branch capsule_house https://github.com/exocoms-teams/e-commerce.git
cd e-commerce
```

Une fenêtre de connexion GitHub s'ouvre : choisir **Sign in with your browser**
et utiliser le compte qui a accès à l'organisation `exocoms-teams`.

> Ne jamais utiliser le mot de passe GitHub dans le terminal : il n'est plus
> accepté pour les opérations Git.

### 3. Lancer le script d'installation

Depuis la racine du dépôt (là où se trouve `setup-dev.ps1`) :

```bash
powershell -ExecutionPolicy Bypass -File setup-dev.ps1
```

Le script :

1. vérifie que Git et Python (3.10+) sont installés ;
2. active les chemins longs Git (`core.longpaths`) ;
3. crée le `venv` et installe `reportlab` ;
4. télécharge le source Odoo 19 dans `odoo-src`, **à côté** du dépôt
   (pas dedans), pour l'autocomplétion ;
5. génère `.vscode/settings.json` avec les bons chemins.

Le téléchargement d'Odoo prend quelques minutes. Le script peut être relancé
sans risque : il saute ce qui existe déjà. Il se termine par `Termine !`.

### 4. Configurer VS Code

```bash
code .
```

1. `Ctrl+Shift+P` → **Python: Select Interpreter** → choisir celui du `venv`
   (normalement pris automatiquement).
2. `Ctrl+Shift+P` → **Python: Restart Language Server**.

### 5. Vérifier

Ouvrir `capsule_house_theme/controllers/catalogue_pdf.py` : il ne doit plus y
avoir de warning sur `odoo` ni sur `reportlab`.

`venv/` et `.vscode/` sont dans le `.gitignore` (chemins propres à chaque
machine) : ne pas les commiter.

## Dépannage

| Problème | Cause / solution |
|---|---|
| `command not found` sur `git`, `cd`… | Le copier-coller depuis Slack ajoute des caractères invisibles. Taper la commande à la main, ou la passer par le Bloc-notes, et coller **une seule ligne à la fois**. |
| `cd Documents\Exocoms` ne marche pas | Dans Git Bash, utiliser `/` et non `\` : `cd Documents/Exocoms`. |
| `destination path 'e-commerce' already exists` | Le dossier existe déjà. Vérifier avec `git status` ; si le clone est cassé (pas de `.git`), le supprimer et recloner. |
| `python` introuvable ou ouvre le Microsoft Store | Python n'est pas dans le PATH : le réinstaller en cochant **Add Python to PATH**. |
| `Password authentication is not supported` au push | Supprimer les identifiants `github.com` dans le **Gestionnaire d'identification Windows**, relancer le push et se connecter via le navigateur. Sinon, utiliser un Personal Access Token (jamais partagé sur Slack ni en capture d'écran). |
| `403` / `repository not found` | Compte sans accès à `exocoms-teams` ou sans droit d'écriture : demander l'accès à Eric. |
| Le script s'arrête avec une erreur rouge | Lire la dernière ligne : le script s'arrête à la première erreur avec un message explicite. |

## Conventions d'équipe

- **Branches perso** : `dev/<initiales ou prénom>-<sujet>`, courtes
  (un nom trop long après `dev/` fait planter silencieusement le build
  Odoo.sh : DNS).
- **1 branche par ticket**, supprimée après le merge.
- **Toujours merger `capsule_house` dans sa branche avant de pousser une PR**,
  pour récupérer le travail des autres :
  ```bash
  git merge capsule_house
  git push -u origin dev/<nom>-<sujet>
  ```
- **Vérifier la syntaxe Python avant de commiter** :
  ```bash
  python -c "import ast,sys; ast.parse(open(sys.argv[1], encoding='utf-8').read())" capsule_house_theme/setup_utils.py
  ```
- **Tester en navigation privée** (visiteur anonyme), jamais connecté en admin :
  cela fausse les résultats de société et de site web.
- **Base partagée (~17 sites)** : toujours filtrer par `website_id` / `company_id`.
- **Chaque branche Odoo.sh a sa propre base de données.** Dans `odoo-bin shell`,
  vérifier le prompt (nom de la base = nom de la branche) avant d'interpréter
  un résultat.
- **La config runtime ne survit pas aux rebuilds** sauf si elle est codée dans
  `setup_utils.py` : un renommage fait à la main en base peut être écrasé.
