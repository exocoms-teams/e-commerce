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

Après validation du tuteur le 03/09/2026, la solution du champ honeypot invisible a été retenue et implémentée.

Le formulaire contient désormais un champ `website` placé hors de l’écran avec la classe `contact-honeypot`. Il est ignoré par la navigation au clavier et reste invisible pour un utilisateur normal. Le JavaScript transmet sa valeur à la route `/contact/submit`.

Le contrôleur vérifie ce champ avant toute validation complémentaire, création d’un message ou tentative d’envoi d’email. S’il est rempli, la soumission est rejetée avec `success: false`.

### Tests du honeypot

Les tests suivants ont été réalisés le 03/09/2026 :

- un utilisateur normal peut toujours envoyer le formulaire ;
- le formulaire conserve son apparence et son comportement ;
- la route répond avec `success: true` pour une soumission normale ;
- un seul message est enregistré et un seul email est reçu dans Mailpit ;
- une soumission directe avec le champ `website` rempli est rejetée avec `success: false` ;
- la soumission bloquée ne crée aucun message et ne déclenche aucun email ;
- aucune erreur JavaScript liée au formulaire n’apparaît dans la console ;
- aucune erreur serveur liée au formulaire n’apparaît dans les logs Odoo.

Le honeypot constitue une protection anti-spam basique et non intrusive. Une limitation de fréquence ou un CAPTCHA pourra être envisagé ultérieurement uniquement si le niveau de spam le nécessite.

## Alignement de la validation du formulaire d’avis

Date des tests : 04/09/2026
Page testée : `/avis`
Route testée : `/avis/submit`

### Corrections réalisées

Les champs obligatoires affichés dans l’interface ont été comparés aux contrôles de la méthode `avis_submit()`.

Les corrections suivantes ont été appliquées :

- ajout du titre à la validation JavaScript et serveur ;
- nettoyage de `name`, `titre`, `commentaire` et `profession` avec `.strip()` ;
- rejet d’un nom ou d’un titre composé uniquement d’espaces ;
- validation stricte de la note entre 1 et 5 ;
- enregistrement en base des valeurs nettoyées ;
- association des libellés Nom, Profession, Titre et Commentaire avec leurs champs ;
- remplacement du libellé de la note par un texte associé au groupe d’étoiles avec `aria-labelledby`.

### Tests réalisés

- une soumission avec un titre vide est rejetée côté interface ;
- une soumission directe avec un titre vide est rejetée côté serveur ;
- une soumission avec un nom composé uniquement d’espaces est rejetée côté interface ;
- une soumission directe avec un nom composé uniquement d’espaces est rejetée côté serveur ;
- aucun avis invalide n’est enregistré ;
- un avis valide continue d’être enregistré et affiché normalement ;
- les cinq étoiles restent présentes et fonctionnelles ;
- aucun avertissement d’association des libellés n’apparaît après la correction ;
- aucune erreur JavaScript ou serveur n’a été détectée.
