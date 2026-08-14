# EXOCOMS RGPD

Module de conformité RGPD / CNIL pour **Odoo 19 uniquement** (Odoo.sh, Enterprise
ou Community). Aucune compatibilité descendante n'est assurée : le code utilise
les API introduites en v19 (`res.groups.privilege`, `group_ids`, `<list>`,
`<chatter/>`, `type="jsonrpc"`, framework Interaction).

---

## Pourquoi

Odoo ne propose pas d'application RGPD. On y trouve un bandeau cookies, la liste
noire de messagerie, les droits d'accès, le nettoyage de données et un DPA
contractuel — mais ni registre des traitements, ni workflow des demandes de
droits, ni preuve de consentement horodatée, ni purge automatique, ni registre
des violations. Ce module comble ces manques.

---

## Contenu

### Registre des traitements — art. 30
Base légale, finalités, catégories de données (avec marquage des données
sensibles de l'art. 9) et de personnes concernées, destinataires et
sous-traitants, transferts hors UE et garanties associées, durée de
conservation, mesures de sécurité (art. 32), AIPD, niveau de risque résiduel,
revue périodique. Workflow `brouillon → revue → actif → suspendu → clôturé`.
Export PDF par fiche.

### Demandes d'exercice des droits — art. 15 à 22
Neuf types de demandes. Vérification d'identité obligatoire avant toute
communication de données (contrainte SQL-level : impossible de clôturer une
demande sans identité vérifiée). Délai légal d'un mois calculé
automatiquement, prorogation de deux mois tracée (art. 12.3), activités et
relances programmées, génération de l'export et du rapport d'effacement,
quatre modèles de courriers.

### Journal des consentements
Chaîne de hachage SHA-256 : chaque entrée scelle le hachage de la précédente.
`write()` et `unlink()` sont bloqués — un consentement se retire, il ne
s'efface pas. Preuve technique complète : IP, user-agent, URL, méthode et
libellé exact affiché au moment du recueil. Bouton de vérification
d'intégrité de la chaîne. Expiration automatique (13 mois par défaut pour les
finalités cookies).

Endpoint JSON-RPC pour les CMP tierces :

```
POST /rgpd/consent/log
Header : X-RGPD-Key: <exocoms_rgpd.consent_api_key>
{"purpose": "analytics", "email": "...", "granted": true,
 "source_url": "...", "consent_text": "..."}
```

### Politique de conservation
Règles par modèle : anonymisation, archivage ou suppression, exécutées par cron
avec traitement par lots. Simulation obligatoire (saisie du mot `APPLIQUER`)
avant toute application manuelle. Neuf stratégies d'anonymisation
(effacement, valeur fixe, hachage salé, masquage e-mail / téléphone / nom /
adresse, réduction à l'année, conservation).

### Cartographie et moteur d'anonymisation
Auto-détection des modèles contenant des données personnelles, avec
pré-remplissage heuristique des champs. Drapeau `legal_hold` : les
enregistrements soumis à une obligation légale de conservation
(comptabilité, paie, garanties) sont exclus de l'effacement et listés dans
le rapport.

### Violations de données — art. 33/34
Compte à rebours de 72 heures, qualification du risque, suivi de la
notification à l'autorité de contrôle et de l'information des personnes,
exemptions de l'art. 34.3.

### Journal d'audit
Journalisation configurable par modèle (création, écriture, suppression,
export) via une surcharge générique de `base`. Garde-fous : liste
`NEVER_AUDIT`, contexte `rgpd_skip_audit`, cache ORM des règles actives,
purge par cron.

### Liste noire de messagerie
Le retrait d'un consentement marketing met immédiatement l'adresse en liste
noire d'Odoo, et inversement une désinscription depuis une campagne (lien
*Se désinscrire*, saisie manuelle, import) est journalisée comme un retrait au
sens de l'article 7.3. Sans cette propagation, un retrait enregistré
n'empêcherait pas l'envoi de la campagne suivante — et le journal ne prouverait
alors qu'une chose : que le responsable de traitement était informé.

`mail.blacklist` est **commune à toutes les sociétés**, contrairement aux
consentements. Une adresse n'est donc bloquée que si **aucune** société ne
dispose d'un consentement marketing accordé pour elle ; un consentement accordé
dans une seule entité suffit à l'en retirer. Ce choix protège la personne dans
le sens qui compte : on ne coupe jamais un envoi qu'elle a accepté ailleurs, et
on ne réactive jamais un envoi sur la seule foi d'une entité tierce.

Un cron quotidien réconcilie les deux tables, le journal faisant foi. La
réconciliation est aussi déclenchable à la main depuis les paramètres, utile
après un import massif ou une restauration de sauvegarde. Chaque opération est
tracée dans le chatter de l'entrée de liste noire avec le numéro de l'entrée de
journal correspondante.

Désactivable par société si un autre outil gère déjà les désinscriptions.

### Registre consolidé
**RGPD ‣ Registre ‣ Registre consolidé (PDF)** édite un document unique :
page de garde (responsable de traitement, DPO, nombre de traitements, date
d'arrêté), sommaire, puis une fiche par traitement. C'est ce document qui se
présente en contrôle, l'article 30 attendant un registre et non une collection
de fiches. Seuls les traitements en revue, actifs ou suspendus y figurent — un
brouillon n'est pas mis en œuvre, un traitement clôturé ne relève plus du
registre courant.

### Bandeau cookies (CMP)
`static/src/js/rgpd_cmp_bridge.js` branche Axeptio ou tarteaucitron sur
l'endpoint `/rgpd/consent/log`. Adaptez `CMP_PURPOSE_MAP` à vos codes de
finalité, puis exposez l'adresse via `window.rgpdCurrentEmail` (ou
`rgpdConsent.flush(email)`) une fois la personne identifiée : les
consentements donnés avant sont mis en file d'attente, faute de quoi ils ne
seraient rattachables à personne et n'auraient aucune valeur probante.

La clé `X-RGPD-Key` ne doit pas être utilisée depuis le navigateur, où elle
serait publique : laissez `exocoms_rgpd.consent_api_key` vide pour les appels
front, ou proxifiez l'appel côté serveur.

### Tests
39 tests dans `tests/`, exécutés automatiquement par les builds Odoo.sh :
```bash
odoo -d <base> -i exocoms_rgpd --test-enable --test-tags rgpd --stop-after-init
```
Ils couvrent le scellement et le chaînage par société des consentements
(y compris la détection d'une altération ou d'une suppression faite en SQL),
le cloisonnement des règles de conservation, le `legal hold`, le refus de
clôturer une demande sans vérification d'identité, la résolution des finalités
surchargées, les séquences par société et la propagation vers la liste noire
dans les deux sens.

### Portail et formulaire public
- `/my/privacy` — consultation, consentements, dépôt de demande, historique
- `/my/privacy/data` — détail des données
- `/my/privacy/download` — export JSON (portabilité, art. 20)
- `/my/privacy/pdf` — export PDF (droit d'accès, art. 15)
- `/rgpd/demande` — formulaire public avec honeypot, limitation de débit et
  vérification par jeton e-mail

---

## Installation

### Odoo.sh
1. Copier le dossier `exocoms_rgpd/` dans le répertoire des addons du dépôt.
2. Commit + push sur la branche cible.
3. Installer le module depuis **Applications** (retirer le filtre « Applications »
   si nécessaire).

### Manuel
```bash
cp -r exocoms_rgpd /chemin/vers/addons/
odoo -u exocoms_rgpd -d <base> --stop-after-init
```

---

## Configuration après installation

1. **RGPD ‣ Configuration ‣ Paramètres**
   - DPO : nom, e-mail, téléphone, adresse postale
   - Autorité de contrôle (CNIL par défaut)
   - Activer le portail et/ou le formulaire public
   - URL de la politique de confidentialité
   - Clé d'API pour l'endpoint de consentement (recommandé si un CMP tiers
     est utilisé)
2. **RGPD ‣ Données ‣ Cartographie** — lancer l'auto-détection, vérifier les
   champs retenus et poser les `legal hold` nécessaires.
3. **RGPD ‣ Registre ‣ Traitements** — créer une fiche par traitement réel.
   Les fiches de démonstration ne valent pas registre.
4. **RGPD ‣ Données ‣ Politique de conservation** — créer les règles, les
   **simuler** avant d'activer `auto_run`.
5. Vérifier les crons dans **Paramètres ‣ Technique ‣ Actions planifiées**.

---

## Droits d'accès

| Groupe | Portée |
|---|---|
| `group_rgpd_user` | Lecture du registre, gestion des demandes qui lui sont assignées |
| `group_rgpd_officer` | Accès complet : cartographie, conservation, audit, configuration, effacement |

Six règles multi-sociétés filtrent les enregistrements par `company_id`.
Le jeton de vérification des demandes est restreint au groupe *officer*.

---

## Crons

| Cron | Fréquence | Rôle |
|---|---|---|
| Politique de conservation | Quotidien | Applique les règles marquées `auto_run` |
| Échéances des demandes | Quotidien | Relance et alerte sur les délais |
| Expiration des consentements | Quotidien | Passe les consentements périmés à l'état expiré |
| Violations 72 h | Horaire | Alerte sur les incidents non notifiés |
| Purge du journal d'audit | Mensuel | Supprime les entrées au-delà de la rétention configurée |

---

## Multi-société

Le module est cloisonné par société. Huit modèles portent un `company_id` avec
une `ir.rule` associée : traitements, demandes, consentements, violations,
journal d'audit, règles de conservation, finalités de consentement et
destinataires.

**Registre, demandes, violations, audit** — chaque société tient son propre
registre. Les modèles de courriels puisent le DPO, l'autorité de contrôle et la
signature dans `company_id`, donc chaque entité écrit avec ses propres
coordonnées.

**Consentements** — chaîne de hachage **distincte par société**. Chaque entité
est un responsable de traitement autonome : un consentement donné à la société A
ne vaut pas pour la société B, et `get_current_state()` ne remonte que les
consentements de la société courante. La vérification d'intégrité contrôle
l'empreinte de chaque entrée *et* la continuité du chaînage, ce qui permet de
détecter une suppression opérée directement en base.

**Finalités et destinataires** — laisser `company_id` vide rend l'enregistrement
partagé par toutes les sociétés. Renseigner une société crée une surcharge : une
finalité propre à une entité prime alors sur la finalité partagée de même code,
ce qui permet d'adapter le libellé de consentement sans dupliquer toute la
configuration.

**Règles de conservation** — une règle rattachée à une société ne traite que les
enregistrements de cette société et ceux qui n'en ont aucune, à condition que le
modèle cible porte un `company_id`. Laissée sans société, elle s'applique
partout. À vérifier avant d'activer `auto_run` : une règle transverse sur un
modèle multi-société purge toutes les entités.

**Crons** — les cinq tâches planifiées s'exécutent en `sudo` afin de couvrir
l'ensemble des sociétés, indépendamment des droits de l'utilisateur qui porte le
cron. Chaque règle de conservation reste néanmoins cloisonnée sur sa propre
société.

**Portail et formulaire public** — la société est résolue à partir du site web
appelant. L'endpoint CMP `/rgpd/consent/log` rattache le consentement à cette
même société.

**Séquences** — partagées par défaut (`company_id` vide) : les références RGPD/,
TRT/ et VIOL/ sont continues sur l'ensemble du groupe. Pour qu'une entité
numérote indépendamment, ouvrir **RGPD ‣ Configuration ‣ Paramètres ‣
Numérotation** et cliquer sur *Créer des séquences propres à cette société*. Les
trois codes sont créés d'un coup et les compteurs repartent de 1 ; les
références déjà attribuées restent inchangées, puisqu'elles ont été
communiquées aux personnes concernées. L'opération est idempotente et
réversible en supprimant les séquences créées, auquel cas la société retombe
sur les séquences partagées.

---

## Points d'attention

- **Le sel de pseudonymisation** (`exocoms_rgpd.hash_salt`) est généré à
  l'installation. Ne le modifiez pas après le premier hachage : les valeurs
  hachées deviendraient incohérentes.
- **L'anonymisation est irréversible.** Utilisez toujours la simulation.
- **La suppression** (`action_type = delete`) peut rompre des liens
  documentaires. Préférez l'anonymisation dans le doute.
- **Ce module ne rend pas conforme à lui seul.** Il fournit l'outillage et la
  traçabilité. La conformité suppose une analyse des traitements, des contrats
  de sous-traitance signés, une politique de confidentialité à jour et des
  procédures internes.

---

## Compatibilité

Écrit pour **Odoo 19.0 exclusivement**. Le code utilise des API introduites en
v19 qui n'existent pas avant : `models.Constraint` en attribut de classe
(`_sql_constraints` est supprimé en v19), `res.groups.privilege` et
`privilege_id`, `group_ids` sur `res.users`, `<list>`, `<chatter/>`,
`type="jsonrpc"` et le framework Interaction côté frontend.

Aucune compatibilité descendante, et aucune garantie de compatibilité ascendante :
Odoo casse des API à chaque version majeure. Le passage en v20 demandera une
passe de migration.

Dépendances : `base`, `base_setup`, `mail`, `portal`, `web`. Aucune dépendance
externe hors bibliothèques standard d'Odoo — le module s'installe tel quel sur
Odoo.sh.

---

Licence LGPL-3 — EXOCOMS Group — [exocoms.fr](https://www.exocoms.fr)
