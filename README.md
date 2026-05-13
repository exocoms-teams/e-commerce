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
Champ clé | Type | Description
---|---|---
`reference` | Char | Auto-généré MSN-2025-00001
`source` | Selection | `assurance` / `particulier` / `entreprise`
`state` | Selection | 11 états (nouveau → clos)
`assurance_id` | M2O | Assurance partenaire
`client_id` | M2O | Client final (res.partner)
`intervenant_id` | M2O | Artisan assigné
`montant_garanti` | Monetary | Part prise en charge assurance
`franchise` | Monetary | Franchise du contrat
`reste_a_charge` | Monetary | Calculé auto = devis - garanti + franchise
`commission_plateforme` | Monetary | Calculé auto selon taux intervenant

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
{"success": true, "message": "API Sinistre Services opérationnelle"}
```

#### ✅ `POST /api/sinistre/v1/mission` — Créer un ordre (Assurance)
```json
{
  "ref_assurance": "SIN-2025-001234",
  "contrat": "CTR-789456",
  "type_intervention": "serrurerie",
  "urgence": "urgente",
  "description": "Porte fracturée suite à effraction",
  "montant_garanti": 850.00,
  "franchise": 150.00,
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
    "montant_devis": 650.00,
    "montant_garanti": 500.00,
    "reste_a_charge": 150.00,
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

Groupe | Accès
---|---
`group_sinistre_user` | Consultation uniquement
`group_sinistre_gestionnaire` | Gestion missions, assignation, facturation
`group_sinistre_admin` | Config assurances, clés API, commissions
`group_sinistre_intervenant` | Accès PWA : ses missions, devis, photos

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
