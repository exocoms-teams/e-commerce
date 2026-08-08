# EXOCOMS – Marque blanche (Debranding Odoo)

Module Odoo 19 qui **remplace par votre marque** — ou supprime — les mentions
promotionnelles Odoo dans le portail, les e-mails, les devis et tous les
rapports PDF.

Paramétrage **par société** : sur une instance multi-société, chaque client
hébergé peut afficher sa propre marque, son propre logo et son propre lien.

## Principe

Plutôt que de surcharger une dizaine de templates XML (dont les identifiants
changent à chaque version majeure), le module intercepte **le moteur de rendu
QWeb lui-même** (`ir.qweb._render`). Tout ce qui est rendu par Odoo passe par ce
point unique :

| Canal | Couvert |
|---|---|
| Pages portail (`/my`, `/my/quotes`, `/my/invoices`…) | ✅ |
| Site web / page de login / page de signup | ✅ |
| E-mails de notification (`mail.mail_notification_layout`, `_light`…) | ✅ |
| Templates de mail (devis envoyé, facture envoyée, relances…) | ✅ |
| Rapports QWeb-HTML et PDF (devis, BC, factures, BL, en-têtes/pieds) | ✅ |
| Back-office : titre de l'onglet + menu utilisateur | ✅ (option) |

Aucune surcharge de vue standard : le module survit aux mises à jour Odoo.sh et
aux migrations de version.

## Configuration

**Paramètres > Technique > Marque blanche** (administrateur), puis choisir la
société.

| Champ | Rôle |
|---|---|
| **Mentions Odoo** | `Remplacer par notre marque` ou `Supprimer sans rien afficher` |
| **Texte d'accroche** | Ex. `Propulsé par`. Vide = seulement le logo / le nom |
| **Nom de marque** | Vide = nom de la société |
| **Lien de la marque** | Vide = site web de la société ; vide aussi = non cliquable |
| **Afficher le logo** | Affiche le logo à la place du nom |
| **Logo de marque** | PNG à fond transparent, ~200×50 px conseillé |
| **Hauteur du logo (px)** | 16 par défaut ; 20–24 pour un logo plus lisible |
| **Débrander le back-office** | Titre d'onglet + retrait des entrées Odoo du menu utilisateur |

Interrupteur général (désactive tout le module sans le désinstaller) :
paramètre système `exocoms_debranding.enabled` = `True` / `False`.

### Rendu en mode « Remplacer »

Le bloc d'origine est **conservé** — sa balise, ses classes, son style inline,
donc sa position et son alignement — et seul son contenu est remplacé. Le pied
de page du devis PDF passe ainsi de `Powered by Odoo` à
`Propulsé par [logo] EXOCOMS`, au même endroit, avec la même taille de police.

Le logo est servi par une route publique `/exocoms_brand/logo?company=<id>`
en URL **absolue** : indispensable pour qu'il s'affiche dans les e-mails et les
PDF, consultés hors session.

## Ce qui est traité

* `Powered by Odoo` / `Propulsé par Odoo` / `Généré par Odoo`
* `Sent by <Société> using Odoo` / `Envoyé par <Société> avec Odoo`
* `Create a free website with Odoo` / `Créez un site web gratuitement avec Odoo`
* tous les liens `<a href="…odoo.com…">`
* la balise `<meta name="generator">` (renommée avec votre marque)
* back-office : entrées *Documentation*, *Support*, *Compte Odoo* du menu
  utilisateur, et `Odoo` dans le titre de l'onglet

Deux garde-fous évitent les faux positifs : la suppression d'un bloc est
plafonnée à 900 caractères de contenu, et une formule (« Powered by … ») n'est
traitée que si elle est suivie du mot *Odoo* ou si elle est devenue orpheline.
« Powered by Stripe » ou « Envoyé par Radia avec accusé de réception » restent
intacts. Une seule injection de marque par document, quel que soit le nombre de
mentions rencontrées.

## Installation

> **Important** : ce module contient du code Python. Il ne peut donc **pas**
> être installé via *Apps > Importer un module (.zip)* : ce mécanisme ne charge
> que les fichiers de données, jamais le Python. Sur Odoo.sh, le déploiement
> passe obligatoirement par Git.

### Odoo.sh

```bash
git checkout -b feature/debranding
unzip exocoms_debranding.zip -d .
git add exocoms_debranding
git commit -m "feat(debranding): marque blanche configurable"
git push origin feature/debranding
```

Après le build : **Apps > Mettre à jour la liste des applications** > rechercher
*EXOCOMS - Marque blanche* > **Installer**.

### Local / VPS

```bash
unzip exocoms_debranding.zip -d /chemin/vers/addons/
sudo systemctl restart odoo
odoo -d <base> -i exocoms_debranding --stop-after-init
```

## Déploiement chez un client

1. Installer le module sur l'instance du client.
2. *Paramètres > Technique > Marque blanche* > sélectionner sa société.
3. Renseigner son nom, son URL, téléverser son logo.
4. Vérifier sur trois supports : `/my/quotes` (portail), l'impression PDF d'un
   devis, et un e-mail de devis envoyé à une adresse de test.

Aucune donnée métier n'est modifiée : à la désinstallation, tout revient à
l'état d'origine.

## Désactivation ponctuelle (débogage)

```python
html = self.env["ir.qweb"].with_context(exocoms_skip_debrand=True)._render(tid, values)
```

## Tests

```bash
odoo -d <base> -i exocoms_debranding --test-enable --test-tags /exocoms_debranding --stop-after-init
```

## Limites connues

* Le **gestionnaire de bases de données** (`/web/database/manager`) est rendu
  hors ORM : il ne peut pas être débrandé par un module. Non exposé sur Odoo.sh.
* Le **favicon** reste celui d'Odoo tant qu'il n'est pas remplacé dans
  *Paramètres > Sociétés > … > Favicon*.
* Les **métadonnées PDF** (producteur du fichier) sont écrites par le moteur de
  rendu PDF et ne dépendent pas du HTML.

## Rappel juridique

L'AGPL/LGPL n'impose pas de conserver la mention « Powered by Odoo » dans les
pages rendues. En revanche, si vous distribuez du code AGPL modifié, vous devez
en publier les sources. Vérifiez également les clauses de votre contrat Odoo
Enterprise, qui encadre l'usage de la marque et peut restreindre la revente
sous marque blanche : à valider avant tout déploiement client.
