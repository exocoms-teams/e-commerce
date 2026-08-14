# Analyse pylint-odoo — suivi

Commande utilisée :

```
pip install pylint-odoo --break-system-packages
pylint --load-plugins=pylint_odoo -d all -e odoolint matelas/
```

## Premier passage (9.70/10)

| Fichier | Règle | Détail | Statut |
|---|---|---|---|
| `__manifest__.py:20` | `manifest-required-author` | Aucun auteur "Odoo Community Association (OCA)" listé | **Ignoré** — ce module n'est pas destiné à l'OCA, ajouter cet auteur serait trompeur. Règle non applicable à un module privé. |
| `__manifest__.py:61` | `manifest-superfluous-key` | `installable: True` est déjà la valeur par défaut | Corrigé — clé supprimée |
| `__manifest__.py:63` | `manifest-superfluous-key` | `auto_install: False` est déjà la valeur par défaut | Corrigé — clé supprimée |
| `models/avis.py:14` | `attribute-string-redundant` | `string="Profession"` identique au nom du champ `profession` | Corrigé — `string=` retiré |
| `models/avis.py:17` | `attribute-string-redundant` | `string="Commentaire"` identique au nom du champ `commentaire` | Corrigé — `string=` retiré |
| `models/avis.py:25` | `translation-required` | Message d'erreur `ValidationError` non traduisible | Corrigé — passe par `self.env._(...)` |
| `models/newsletter_wizard.py:7` | `no-wizard-in-models` | Un wizard (`TransientModel`) doit être dans `wizards/`, pas `models/` | Corrigé — fichier déplacé vers `wizards/newsletter_wizard.py`, imports mis à jour |

## Deuxième passage (9.96/10)

Seule règle restante : `manifest-required-author` (voir ci-dessus, volontairement non appliquée).
