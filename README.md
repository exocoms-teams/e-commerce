# 📋 GUIDE COMPLET — Module `sinistre_services` (Odoo SH v19)

---

## 🗂️ Structure du Module

```
sinistre_services/
├── __manifest__.py              # Déclaration du module
├── __init__.py
├── models/
│   ├── mission.py               # ★ Modèle central — Ordre de Mission
│   ├── intervenant.py           # Artisans / Techniciens
│   ├── assurance.py             # Compagnies d'assurance + clés API
│   ├── devis.py                 # Devis avant intervention
│   ├── commission.py            # Commissions plateforme
│   └── photo_dossier.py         # Photos avant/après
├── controllers/
│   └── api_controller.py        # ★ API REST pour assurances & PWA
├── wizard/
│   └── assigner_mission.py      # Wizard assignation intervenant
├── views/
│   ├── mission_views.xml        # Form + List + Kanban
│   ├── assurance_views.xml
│   ├── intervenant_views.xml
│   ├── devis_views.xml
│   └── menu_views.xml
├── security/
│   ├── security.xml             # Groupes d'accès
│   └── ir.model.access.csv     # Droits CRUD par modèle
├── data/
│   ├── sequence_data.xml        # Séquences MSN-YYYY-XXXXX
│   └── mission_type_data.xml   # Spécialités par défaut
├── report/
│   └── report_mission.xml      # PDF Fiche Mission
└── static/src/
    ├── css/sinistre.css
    └── js/mission_kanban.js
```

---

## 🚀 Installation sur Odoo SH

### 1. Déposer le module

```bash
# Dans votre repo Odoo SH, branche "services"
git checkout services
cp -r sinistre_services/ /path/to/odoo-sh-repo/custom_addons/
git add .
git commit -m "feat: add sinistre_services module v1.0"
git push origin services
```

### 2. Activer dans Odoo SH

- Dashboard Odoo SH → onglet **Branches** → branche `services`
- **Paramètres** → Chemin addons : `custom_addons`
- Redémarrer le serveur
- Apps → Rechercher "Sinistre Services" → **Installer**

---

## 🔑 Modèles Principaux

### `sinistre.mission` — Ordre de Mission

| Champ clé               | Type      | Description                                |
| ----------------------- | --------- | ------------------------------------------ |
| `reference`             | Char      | Auto-généré MSN-2025-00001                 |
| `source`                | Selection | `assurance` / `particulier` / `entreprise` |
| `state`                 | Selection | 11 états (nouveau → clos)                  |
| `assurance_id`          | M2O       | Assurance partenaire                       |
| `client_id`             | M2O       | Client final (res.partner)                 |
| `intervenant_id`        | M2O       | Artisan assigné                            |
| `montant_garanti`       | Monetary  | Part prise en charge assurance             |
| `franchise`             | Monetary  | Franchise du contrat                       |
| `reste_a_charge`        | Monetary  | Calculé auto = devis - garanti + franchise |
| `commission_plateforme` | Monetary  | Calculé auto selon taux intervenant        |

### `sinistre.assurance` — Compagnie d'Assurance

- Clé API générée par Odoo (bouton dans le formulaire)
- Format d'échange : JSON REST / XML SOAP / CSV FTP
- Webhook pour notifier l'assurance des changements de statut

### `sinistre.intervenant` — Artisan

- Taux de commission configurable (défaut 15%)
- Spécialités en Many2Many
- Zone d'intervention
- Compte utilisateur lié (pour accès PWA)

---

## 🌐 API REST — Documentation

### Authentification

Toutes les requêtes assurance nécessitent le header :

```
X-API-KEY: <votre_clé_api>
```

### Endpoints

#### ✅ `GET /api/sinistre/v1/ping`

Test de connectivité.

```json
{ "success": true, "message": "API Sinistre Services opérationnelle" }
```

#### ✅ `POST /api/sinistre/v1/mission` — Créer un ordre (Assurance)

```json
{
  "ref_assurance": "SIN-2025-001234",
  "contrat": "CTR-789456",
  "type_intervention": "serrurerie",
  "urgence": "urgente",
  "description": "Porte fracturée suite à effraction",
  "montant_garanti": 850.0,
  "franchise": 150.0,
  "client": {
    "nom": "Dupont",
    "prenom": "Jean",
    "email": "jean.dupont@email.fr",
    "tel": "0612345678"
  },
  "adresse_intervention": "12 rue de la Paix, 75001 Paris",
  "contact_sur_place": "Mme Dupont",
  "tel_sur_place": "0698765432"
}
```

Réponse :

```json
{
  "success": true,
  "reference": "MSN-2025-00001",
  "token": "abc123...",
  "state": "nouveau",
  "message": "Ordre de mission créé avec succès"
}
```

#### ✅ `GET /api/sinistre/v1/mission/<reference>` — Statut

```json
{
  "success": true,
  "mission": {
    "reference": "MSN-2025-00001",
    "state": "travaux_en_cours",
    "intervenant": "Martin Électricité",
    "date_rdv": "2025-05-15 09:00:00",
    "montant_devis": 650.0,
    "montant_garanti": 500.0,
    "reste_a_charge": 150.0,
    "photos_avant": 3,
    "photos_apres": 0
  }
}
```

#### ✅ `GET /api/sinistre/v1/missions` — Liste missions assurance

Paramètres optionnels : `?state=termine&date_from=2025-01-01`

#### ✅ `POST /api/sinistre/v1/demande` — Demande directe (sans assurance)

```json
{
  "source": "particulier",
  "type_intervention": "plomberie",
  "urgence": "normale",
  "description": "Fuite sous évier cuisine",
  "client": {
    "nom": "Martin",
    "prenom": "Sophie",
    "email": "sophie@email.fr",
    "tel": "0612341234"
  },
  "adresse_intervention": "5 avenue Victor Hugo, 75016 Paris"
}
```

#### ✅ `GET /api/sinistre/v1/intervenant/missions` — Missions PWA (auth requise)

Retourne les missions de l'intervenant connecté pour l'app mobile.

---

## 🔄 Workflow Complet

```
┌─────────────────────────────────────────────────────────┐
│                   SOURCES D'ENTRÉE                       │
├───────────────┬──────────────────┬──────────────────────┤
│  API Assurance│  Formulaire Web  │   Saisie Back-office │
│  (clé API)    │  (particulier/   │   (gestionnaire)     │
│               │   entreprise)    │                       │
└───────┬───────┴────────┬─────────┴──────────┬───────────┘
        │                │                    │
        └────────────────┴────────────────────┘
                         │
                    [NOUVEAU]
                         │
              Gestionnaire assigne intervenant
                         │
                    [ASSIGNÉ]
                         │
              Planification RDV
                         │
                  [RDV PLANIFIÉ]
                         │
        ┌────────────────▼────────────────────┐
        │  INTERVENANT (via PWA)              │
        │  1. Arrive sur place               │
        │  2. Photos AVANT (obligatoires)    │
        │  3. Saisit le devis                │
        │  4. Envoie au client               │
        └────────────────┬────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        [ACCEPTÉ]             [REFUSÉ]
              │
    Travaux démarrent
              │
        Photos APRÈS (obligatoires)
              │
          [TERMINÉ]
              │
    ┌─────────┴──────────┐
    ▼                    ▼
Facture Assurance   Facture Client
(montant garanti)   (reste à charge)
              │
          [FACTURÉ]
              │
    Commission prélevée
    sur l'intervenant
              │
           [CLOS]
```

---

## 👥 Groupes d'Accès

| Groupe                        | Accès                                      |
| ----------------------------- | ------------------------------------------ |
| `group_sinistre_user`         | Consultation uniquement                    |
| `group_sinistre_gestionnaire` | Gestion missions, assignation, facturation |
| `group_sinistre_admin`        | Config assurances, clés API, commissions   |
| `group_sinistre_intervenant`  | Accès PWA : ses missions, devis, photos    |

---

## 🔧 Prochaines Étapes

### Phase 2 — PWA Intervenant

- [ ] App PWA (HTML/JS + Service Worker)
- [ ] Firebase Cloud Messaging (notifications push)
- [ ] Signature électronique client
- [ ] Upload photos géolocalisées

### Phase 3 — Intégrations

- [ ] Webhook sortant vers assurances (changements de statut)
- [ ] Portail client (voir ses missions)
- [ ] Tableau de bord analytics
- [ ] Module commission automatisé (prélèvement)

### Phase 4 — Odoo SH

- [ ] Environments staging / production
- [ ] Cron jobs (relances, alertes urgence)
- [ ] Backups automatiques
- [ ] Monitoring API

---

## 📞 Test rapide de l'API

```bash
# Ping
curl https://votre-odoo.sh/api/sinistre/v1/ping

# Créer une mission (assurance)
curl -X POST https://votre-odoo.sh/api/sinistre/v1/mission \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: VOTRE_CLE_API" \
  -d '{
    "type_intervention": "serrurerie",
    "urgence": "urgente",
    "description": "Serrure forcée, porte ne ferme plus",
    "client": {"nom": "Test", "email": "test@test.fr", "tel": "0600000000"},
    "adresse_intervention": "1 rue Test, 75001 Paris"
  }'

# Demande directe sans assurance
curl -X POST https://votre-odoo.sh/api/sinistre/v1/demande \
  -H "Content-Type: application/json" \
  -d '{
    "source": "particulier",
    "type_intervention": "plomberie",
    "description": "Fuite sous évier",
    "client": {"nom": "Dupont", "email": "dupont@email.fr", "tel": "0612345678"},
    "adresse_intervention": "5 rue de la Paix, 75001 Paris"
  }'
```

# Sinistres — Récapitulatif des évolutions apportées

**Module :** `custom_addons/sinistre_services` (Odoo 19, Odoo.sh)
**Dépôt :** `exocoms-teams/e-commerce`
**Auteure :** Cécilia Elkrieff
**Période :** octobre 2026

---

## 1. Vue d'ensemble

Le module `sinistre_services` gère des interventions après sinistre (plomberie, serrurerie, vitrerie…) entre trois acteurs :

- les **clients** (particuliers, entreprises, assurances), qui font une demande sur le site ;
- les **artisans** (« intervenants »), qui reçoivent et traitent les missions dans une application mobile (PWA, `/pwa/`) ;
- la **plateforme**, qui gère les missions dans le back-office Odoo.

Ce document récapitule les fonctionnalités ajoutées, les bugs corrigés et le nettoyage effectué.

| Branche                   | Contenu                                                          | Statut                               |
| ------------------------- | ---------------------------------------------------------------- | ------------------------------------ |
| `sinistres-cecilia`       | Propositions 15 min, compte client, correctifs `monetique_theme` | Fusionnée dans `Sinistres` (PR #166) |
| `sinistres-suivi-artisan` | Suivi de l'artisan en route, frais de déplacement                | Pull Request vers `Sinistres`        |

---

## 2. Fonctionnalités

### 2.1 Propositions aux artisans avec délai de 15 minutes

**Besoin :** l'artisan a 15 minutes pour répondre à une mission.

**Fonctionnement retenu :**

- À la création d'une demande, la mission est proposée **en même temps à tous les artisans disponibles du secteur**, avec la bonne spécialité.
- **Le premier qui accepte la prend** ; elle disparaît chez les autres.
- Si personne n'accepte en 15 minutes, ou si tout le monde refuse, la mission passe **« Sans réponse »** et un message l'indique dans l'historique.
- Bouton **« Reproposer aux artisans »** pour relancer un tour de 15 minutes.
- Onglet **« Propositions »** sur la mission : qui l'a reçue, quand, la date limite et la réponse.

**Technique :**

- Nouveau modèle `sinistre.proposition` (mission, artisan, état, date d'envoi, date limite, date de réponse).
- Tâche automatique (`data/cron_data.xml`) toutes les minutes : fait expirer les propositions dépassées.
- Constantes dans `models/mission.py` :
  - `DELAI_REPONSE_MINUTES = 15`
  - `TAILLE_VAGUE = 0` (0 = tous les artisans ; un nombre > 0 permet de passer à des vagues, par exemple 3).
- Côté PWA, un artisan ne voit que les missions qui lui sont proposées, et ne peut répondre que dans le délai.

> Les missions créées avant cette évolution n'ont pas de proposition : utiliser « Reproposer aux artisans ».

### 2.2 Compte client automatique

**Besoin :** création d'un compte client sur le site.

**Fonctionnement :**

- À la demande d'intervention, un **compte portail** est créé avec l'email du client, et il reçoit un email pour **choisir son mot de passe**.
- Pas de doublon : un client qui refait une demande retrouve toutes ses demandes dans le même compte.
- Pas de compte pour les demandes venant d'une **assurance** (l'email du formulaire est alors celui du gestionnaire).
- Une erreur lors de la création du compte ne bloque jamais la demande (elle est écrite dans les logs).
- Espace client **« Mes interventions »** (`/my/interventions`) : liste des demandes, état, bouton « Suivre ».

**Technique :**

- `controllers/website_controller.py` : `_creer_compte_client()` utilise la méthode d'inscription d'Odoo (`_create_user_from_template` + `action_reset_password`), prévue pour fonctionner sans utilisateur connecté.
- `controllers/portal.py` et `views/portal_templates.xml` : carte « Mes interventions » sur `/my` et page de liste.

### 2.3 Suivi de l'artisan en route (façon Uber)

**Besoin :** le client voit l'artisan se déplacer sur une carte jusqu'à chez lui.

**Fonctionnement :**

- PWA : bouton **« 🚗 Je suis en route »** sur une mission assignée. L'appli envoie la position GPS toutes les 10 secondes.
- Le suivi s'arrête quand l'artisan **pointe son arrivée** (« Démarrer l'intervention »). La position est alors **effacée** (RGPD : on ne suit l'artisan que pendant son trajet, et sur action volontaire).
- Page de suivi client (`/suivi/<token>`) : encadré « Suivi de votre artisan » avec une carte (🚗 artisan, 🏠 adresse d'intervention), mise à jour toutes les 10 secondes, recadrage automatique quand l'artisan sort de la vue, zoom limité.

**Technique :**

- Nouveaux champs sur la mission : `en_route`, `date_depart`, `artisan_lat`, `artisan_lng`, `artisan_position_date`, `dest_lat`, `dest_lng`, `adresse_geocodee`.
- Nouvelles routes :
  - `POST /api/sinistre/v1/intervenant/mission/<id>/en-route`
  - `POST /api/sinistre/v1/intervenant/mission/<id>/position`
  - `GET /suivi/<token>/position` (JSON pour la carte client)
- PWA : nouveau fichier `static/pwa/src/services/tracking.js` ; bouton dans `mission_detail.js`.
- Page client : nouveau fichier `static/src/js/suivi_map.js`.
- Carte : Google Maps (clé de la PWA, surchargeable par le paramètre système `sinistre_services.google_maps_key`).
- Position de l'adresse : **OpenStreetMap (Nominatim)**, calculée une seule fois par adresse (`_geocoder_adresse()`), car la clé Google n'a pas la facturation activée.

### 2.4 Frais de déplacement automatiques

**Besoin :** si le client annule pendant que l'artisan est en chemin, l'assurance règle les frais de déplacement.

**Fonctionnement :**

- Si une mission est annulée alors que l'artisan est **en route**, les frais de déplacement sont facturés automatiquement : **à l'assurance** si la mission en a une, sinon **au client**.
- Montant : celui saisi sur la mission, ou **80 € par défaut** (`FRAIS_DEPLACEMENT_DEFAUT`).
- La facture est créée en **brouillon**.

---

## 3. Bugs corrigés

| Problème                                                                                   | Cause                                                                              | Correction                                                                                     |
| ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Lien « Suivre ma mission » des emails en **404 pour tous les clients**                     | `monetique_theme` redéclarait `/suivi/` et cherchait des templates renommés depuis | Route retirée de `monetique_theme`                                                             |
| Formulaire de demande qui **plantait** et créait un **contact en double** à chaque demande | `monetique_theme` redéclarait `/demande-intervention/send` avec du code ancien     | Route retirée de `monetique_theme` (même approche que `/rejoindre-le-reseau`, commit 270d7b12) |
| Email de notification d'une nouvelle demande jamais envoyé                                 | `request.website.email` n'existe plus en Odoo 19                                   | Remplacé par `request.website.company_id.email`                                                |
| Erreur 500 sur « Mes interventions »                                                       | `t-field` interdit sur une cellule `<td>` en Odoo 19                               | Champ enveloppé dans un `<span>`                                                               |
| Erreur sur le profil de l'artisan dans la PWA                                              | Champ `mobile` des contacts supprimé en Odoo 19                                    | Utilisation de `phone` uniquement                                                              |

---

## 4. Nettoyage

- **Deux copies de `monetique_theme`** existaient : à la racine et dans `custom_addons`. Odoo.sh utilise celle de la **racine** (elle passe en premier dans l'addons path) : toute modification dans `custom_addons/monetique_theme` était ignorée.
- Les styles du formulaire **« Rejoindre le réseau »** (commit du 29 juin) avaient été faits dans la copie ignorée : ils ont été **reportés dans la bonne copie**.
- La copie `custom_addons/monetique_theme` a ensuite été **supprimée** (avec l'accord d'Eric).

---

## 5. Tester

### Préparation (base de test Odoo.sh)

1. Créer un utilisateur artisan (Settings > Users), avec un mot de passe.
2. **Connecter l'artisan à la PWA** (`/pwa/`) dans une fenêtre privée : c'est la première connexion qui crée sa fiche intervenant.
3. **Ensuite seulement**, faire une demande sur `/demande-intervention` avec un email neuf et une vraie adresse.

> L'ordre compte : une mission n'est proposée qu'aux artisans qui existent au moment de la demande.

### Propositions et compte client

- Mission > onglet Propositions : ligne « En attente », limite à +15 min ; la mission apparaît dans la PWA.
- Accepter dans la PWA → mission « Assigné ».
- Onglet **Mails** d'Odoo.sh : email de confirmation + email d'invitation. Ouvrir l'invitation **dans un nouvel onglet**, choisir un mot de passe → `/my` → Mes interventions.

### Suivi de l'artisan

1. Fenêtre de l'artisan : DevTools (`Cmd+Option+I`) > `Cmd+Shift+P` > « Show Sensors » > Location = `47.4784` / `-0.5632`, **avant** de cliquer.
2. « Je suis en route » → le bouton est remplacé par un bandeau bleu.
3. Ouvrir le lien de suivi de l'email client **dans un nouvel onglet** → carte avec 🚗 et 🏠.
4. Changer la position dans Sensors → le 🚗 se déplace.

### Frais de déplacement

- Annuler dans le back-office une mission en route → message « frais de déplacement facturés » dans l'historique, facture brouillon dans Facturation.

---

## 6. Limites et points à signaler

- **Suivi GPS :** ne fonctionne que si l'artisan **garde l'appli ouverte** pendant le trajet (le navigateur coupe le GPS en arrière-plan). Un suivi en arrière-plan demanderait une application native.
- **Clé Google Maps :** la facturation n'est pas activée sur le projet Google Cloud ; le géocodage Google est refusé (contourné avec OpenStreetMap).
- **Dépendance cachée :** `sinistre_services` charge le CSS et une image de `monetique_theme` sans le déclarer dans `depends`.
- **Affichage :** dans la liste des intervenants, la commission s'affiche « 2000% » au lieu de 20 %.
- **Message de facture :** l'historique affiche « Facture frais déplacement créée : False » (facture en brouillon, sans numéro) — à améliorer.
- **Annulation :** les champs « Annulé par » et « Motif » ne sont pas demandés au moment du clic sur Annuler.

---

## 7. Questions en attente

- Mission **sans assurance** annulée pendant le trajet : facturer le déplacement au client ?
- **Validation du devis :** sous le seuil de garantie, le site valide seul et au-dessus l'assureur, ou les deux valident toujours ?
- **API assurance :** documentation disponible pour récupérer les seuils de garantie ?
- **Module Vente :** remplacer les devis du module par les devis Odoo, ou générer un devis Odoo en plus ?

---

## 8. Prochaines étapes

1. **Prise de rendez-vous** par l'artisan dans la PWA, visible côté client (page de suivi et Mes interventions).
2. **Désistement de l'artisan** avec message d'explication obligatoire, et reproposition automatique de la mission aux autres artisans.
3. **Messages artisan** : préciser à qui ils sont destinés (plateforme et/ou client).
4. **Validation du devis** et seuil de garantie de l'assurance (selon les réponses ci-dessus).
5. Possible : proposer les missions à **l'artisan le plus proche**, en s'appuyant sur la géolocalisation ajoutée.

---

## 9. Notes pratiques (environnement)

- **Odoo.sh recrée une base neuve à chaque push** sur une branche de développement : il faut recréer les données de test (artisan, demandes).
- Le numéro à la fin de l'adresse de l'instance change à chaque build : reprendre l'adresse depuis le bouton **Connect**.
- Les emails ne partent pas réellement sur une branche de dev : ils sont visibles dans l'onglet **Mails** d'Odoo.sh. Ouvrir les liens **dans un nouvel onglet** (l'aperçu bloque les pages Odoo et les scripts).
- Les logs utiles sont dans **Logs > odoo.log** (pas install.log).
- **VS Code :** fermer les onglets restés ouverts sur un fichier avant d'appliquer un patch ; avec l'enregistrement automatique, une ancienne version peut être réécrite par-dessus (arrivé deux fois sur `mission.py`).
- Pour créer une Pull Request vers `Sinistres`, utiliser l'adresse `…/compare/Sinistres...<branche>` : le bouton « Compare & pull request » propose `main` par défaut.
