# 📱 PWA Intervenant — Sinistre Services
## Guide complet d'installation et de déploiement

---

## 🏗️ Architecture

```
PWA (front) ──────────────────► Odoo API REST
     │                              /api/sinistre/v1/
     │  Session cookie Odoo
     ▼
Firebase FCM ─────────────────► Notification Push
     │                          (background + foreground)
     ▼
IndexedDB (offline) ──────────► Queue → rejoue à la reconnexion
```

---

## 📁 Structure des fichiers

```
pwa_intervenant/
├── index.html                    # Shell HTML de l'application
├── sw.js                         # Service Worker (cache + push FCM)
├── manifest.json                 # Manifest PWA (icônes, standalone)
├── offline.html                  # Page affichée sans réseau
├── src/
│   ├── styles/main.css           # Design system mobile (Poppins + bleu)
│   ├── services/
│   │   ├── config.js             # ⚙️  Configuration (Firebase, Odoo URL)
│   │   ├── api.js                # Client HTTP → Odoo
│   │   ├── auth.js               # Login / Logout / Session
│   │   ├── fcm.js                # Firebase Cloud Messaging
│   │   └── offline.js            # Queue offline (IndexedDB)
│   ├── components/
│   │   ├── toast.js              # Notifications toast
│   │   ├── photos.js             # Capture, compression, upload
│   │   ├── signature.js          # Canvas tactile signature client
│   │   └── devis.js              # Formulaire devis
│   └── screens/
│       ├── dashboard.js          # Liste des missions
│       └── mission_detail.js     # Détail + workflow complet
├── app.js                        # Orchestrateur (router, init)
├── odoo_api_pwa.py               # Endpoints Odoo à ajouter au module
└── pwa_controller.py             # Route /pwa/ dans Odoo
```

---

## ⚙️ Configuration Firebase

### 1. Créer le projet Firebase

1. Aller sur [console.firebase.google.com](https://console.firebase.google.com)
2. **Créer un projet** → "sinistre-services-pwa"
3. Ajouter une **application Web** (icône `</>`)
4. Copier la config Firebase → `src/services/config.js`

### 2. Activer Cloud Messaging

1. Console Firebase → **Cloud Messaging** → Activer
2. Onglet **Cloud Messaging** → section **Web Push certificates**
3. Générer une paire de clés → copier la **clé VAPID publique** → `CONFIG.FIREBASE_VAPID_KEY`

### 3. Remplir les tokens dans config.js

```javascript
// src/services/config.js
FIREBASE: {
    apiKey:            'AIzaSy...',       // ← depuis Firebase console
    authDomain:        'sinistre-xxx.firebaseapp.com',
    projectId:         'sinistre-xxx',
    storageBucket:     'sinistre-xxx.appspot.com',
    messagingSenderId: '123456789',
    appId:             '1:123...:web:abc...',
},
FIREBASE_VAPID_KEY: 'BNtu...',          // ← clé VAPID publique
```

### 4. Idem dans sw.js

```javascript
// sw.js (lignes ~20-28)
firebase.initializeApp({
    apiKey:            'AIzaSy...',
    // ... copier la même config
});
```

---

## 🏠 Déploiement dans Odoo SH

### Option A — Fichiers dans les assets Odoo (recommandé)

```bash
# Copier les fichiers PWA dans le module sinistre_services
cp -r pwa_intervenant/ sinistre_services/static/pwa/

# Ajouter les controllers dans le module
cp odoo_api_pwa.py sinistre_services/controllers/api_pwa.py
cp pwa_controller.py sinistre_services/controllers/pwa_controller.py

# Mettre à jour controllers/__init__.py
echo "from . import api_pwa" >> sinistre_services/controllers/__init__.py
echo "from . import pwa_controller" >> sinistre_services/controllers/__init__.py
```

### Option B — Serveur statique séparé (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name pwa.sinistre-services.fr;

    root /var/www/pwa;
    index index.html;

    # Service Worker doit avoir le bon Content-Type
    location /sw.js {
        add_header Cache-Control "no-cache";
        add_header Content-Type "application/javascript";
    }

    # PWA : toujours servir index.html (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API vers Odoo
    location /api/ {
        proxy_pass https://votre-instance.odoo.com;
        proxy_set_header Host votre-instance.odoo.com;
    }
}
```

---

## 🔧 Ajouter le champ fcm_token au modèle intervenant

```python
# models/intervenant.py — ajouter ce champ
fcm_token = fields.Char(
    string='Token FCM',
    help="Token Firebase pour les notifications push PWA",
    copy=False,
)
```

---

## 📲 Workflow complet de l'intervenant

```
NOTIFICATION PUSH reçue
         │
         ▼
[1] 🔔 Mission assignée → clic notification → ouvre la PWA
         │
         ▼
[2] 👁 Voir le détail de la mission
    • Client, adresse (lien Maps), téléphone, description
    • Type d'intervention, urgence
         │
         ▼
[3] 📸 Photos AVANT (obligatoires)
    • Appui sur "Photo AVANT"
    • Caméra s'ouvre → compression auto → upload Odoo
    • Minimum 1 photo requise pour pouvoir démarrer
         │
         ▼
[4] 💶 Créer le devis
    • Formulaire avec lignes (description, qté, prix HT)
    • TVA 20% calculée automatiquement
    • "Envoyer au client"
         │
         ▼
[5] ✍️ Signature client
    • Canvas tactile
    • Client signe → "Confirmer l'acceptation"
    • OU "Client refuse" → fin
         │
         ▼
[6] 🔧 Démarrer les travaux
         │
         ▼
[7] 📸 Photos APRÈS (obligatoires pour clôturer)
         │
         ▼
[8] 🎉 Terminer & Clôturer la mission
    → Odoo génère les factures automatiquement
```

---

## 🌐 Fonctionnement hors ligne

La PWA fonctionne partiellement sans réseau :

| Action | Offline |
|--------|---------|
| Voir ses missions (cache) | ✅ |
| Prendre des photos | ✅ (stockées en queue) |
| Créer un devis | ✅ (en queue) |
| Signer un devis | ✅ (en queue) |
| Démarrer/Terminer | ✅ (en queue) |

Toutes les actions en queue sont **automatiquement rejouées** dès le retour du réseau via le **Background Sync** du Service Worker.

---

## 🧪 Tests locaux

```bash
# 1. Serveur local simple (Python)
cd pwa_intervenant
python3 -m http.server 8080

# 2. Avec HTTPS (requis pour Service Worker + caméra)
# Installer mkcert : https://github.com/FiloSottile/mkcert
mkcert -install
mkcert localhost
python3 -c "
import ssl, http.server
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain('localhost.pem', 'localhost-key.pem')
server = http.server.HTTPServer(('localhost', 8443), http.server.SimpleHTTPRequestHandler)
server.socket = ctx.wrap_socket(server.socket)
server.serve_forever()
"
# → https://localhost:8443/
```

---

## 📱 Installation sur l'écran d'accueil (prompt)

Sur Android/Chrome : le navigateur propose automatiquement "Ajouter à l'écran d'accueil" si :
- Le site est en HTTPS ✅
- Le manifest.json est valide ✅
- Le Service Worker est actif ✅

Sur iOS/Safari : Menu Partager → "Sur l'écran d'accueil"

---

## 🔔 Envoyer une notification push depuis Odoo

```python
# Dans le modèle sinistre.mission — méthode à ajouter
def _notify_intervenant_push(self, title, body):
    """Envoie une notification push Firebase à l'intervenant."""
    if not self.intervenant_id or not self.intervenant_id.fcm_token:
        return

    import requests
    token = self.intervenant_id.fcm_token
    server_key = self.env['ir.config_parameter'].sudo().get_param('sinistre.firebase_server_key')

    payload = {
        'to': token,
        'notification': {
            'title': title,
            'body': body,
            'icon': '/sinistre_services/static/pwa/icons/icon-192.png',
        },
        'data': {
            'mission_id': str(self.id),
            'reference':  self.reference,
        },
    }

    try:
        response = requests.post(
            'https://fcm.googleapis.com/fcm/send',
            json=payload,
            headers={
                'Authorization': f'key={server_key}',
                'Content-Type': 'application/json',
            },
            timeout=5,
        )
        response.raise_for_status()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"FCM push error: {e}")
```

---

## ✅ Checklist avant mise en production

- [ ] Remplacer `__FIREBASE_*__` dans `config.js` et `sw.js`
- [ ] Remplacer `__ODOO_DB_NAME__` dans `api.js`
- [ ] Remplacer `votre-instance.odoo.com` dans `config.js`
- [ ] Remplacer le numéro `01 XX XX XX XX` dans le layout
- [ ] Générer les icônes PNG 192×192 et 512×512 dans `icons/`
- [ ] Configurer le paramètre système `sinistre.firebase_server_key` dans Odoo
- [ ] Ajouter le champ `fcm_token` au modèle `sinistre.intervenant`
- [ ] Déployer `odoo_api_pwa.py` dans `sinistre_services/controllers/`
- [ ] Tester la capture photo sur mobile réel (iOS + Android)
- [ ] Tester le workflow complet hors ligne + synchronisation
