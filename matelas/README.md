# e-commerce

## Tests du formulaire de contact

Date des tests : 02/09/2026
Page testée : `/contact`
Route testée : `/contact/submit`

### Environnement

- Odoo 19
- Base de données : `matelas_dev`
- Navigateur avec console et onglet Réseau ouverts
- Mailpit utilisé comme serveur SMTP local
- SMTP Mailpit : `127.0.0.1:1025`
- Interface Mailpit : `http://localhost:8025`

### Résultats des tests

| Test | Résultat attendu | Résultat obtenu |
|---|---|---|
| Soumission avec des données valides | Réponse `success: true`, formulaire vidé et message de confirmation affiché | Conforme |
| Champ obligatoire manquant | Alerte côté navigateur et aucune requête envoyée | Conforme |
| Champ obligatoire manquant envoyé directement à la route | Réponse `success: false` avec un message explicite | Conforme |
| Adresse email invalide | Alerte côté navigateur et aucune requête envoyée | Conforme |
| Email invalide envoyé directement à la route | Réponse `success: false` avec un message explicite | Conforme |
| Double clic rapide | Une seule requête, un seul enregistrement et un seul email | Conforme |
| Échec du serveur SMTP | Réponse `success: false`, formulaire conservé et bouton réactivé | Conforme |
| Vérification de la console JavaScript | Aucune erreur liée au formulaire | Conforme |
| Vérification des logs Odoo après configuration SMTP | Aucune erreur liée au formulaire | Conforme |

### Gestion des réponses de la route

La route `/contact/submit` renvoie un objet contenant :

- `success: true` lorsque le message est enregistré et que l’email est envoyé ;
- `success: false` accompagné d’un message explicite en cas de données invalides, de configuration email absente ou d’échec pendant l’envoi.

Les validations des champs obligatoires et de l’adresse email sont réalisées côté JavaScript et côté serveur. La validation serveur a également été testée directement depuis la console du navigateur afin de contourner volontairement les contrôles JavaScript.

Le bouton d’envoi est désactivé avant l’appel réseau, puis réactivé dans le bloc `finally`. Un double clic rapide ne génère donc qu’une seule soumission.

### Configuration SMTP locale

Le premier test a signalé l’absence d’adresse email sur la société. Après correction, l’envoi a échoué avec une erreur de connexion SMTP, car aucun serveur sortant n’était configuré.

Mailpit a été installé et configuré comme serveur SMTP local. Après cette configuration :

- le test de connexion Odoo a réussi ;
- la route a renvoyé `success: true` ;
- l’email de contact est apparu dans Mailpit ;
- un seul message a été produit par soumission.

Les erreurs périodiques concernant la base inexistante `matelas_devwith` sont indépendantes du formulaire de contact.

### Évaluation de la protection anti-spam

Solutions évaluées :

- **Honeypot caché** : simple, invisible pour les utilisateurs et adapté à une première protection.
- **Limitation par adresse IP** : plus complexe et susceptible de poser des problèmes avec les proxys ou une exécution multi-processus.
- **Délai minimal de soumission** : simple, mais peut provoquer des faux positifs avec le remplissage automatique.
- **CAPTCHA** : protection plus forte, mais considérée comme intrusive pour ce besoin.

### Décision anti-spam

La solution recommandée est un champ honeypot caché, contrôlé côté serveur.

Conformément à la consigne de ne pas ajouter de mécanisme sans validation préalable, aucune protection anti-spam n’a été implémentée à ce stade. La proposition doit d’abord être validée par le tuteur.
