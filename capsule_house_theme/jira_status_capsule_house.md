# Statut du projet Capsule House (module Odoo `capsule_house_theme`) — à jour au 05/08/2026

Voici l'état d'avancement du thème Capsule House, pour mise à jour du board Jira.

## Pages livrées

- **Aide** (v19.0.1.0.46) : `/livraison`, `/retours`, `/garantie`, `/faq` — menu latéral partagé, contenu bilingue FR/EN, FAQ en accordéon natif Bootstrap.
- **Entreprise** (v19.0.1.0.47) : `/a-propos`, `/le-concept` — nav en onglets partagée ; À propos = hero + stats + valeurs + historique ; Le concept = comparatif pod vs construction traditionnelle + étapes de fabrication + schéma technique.
- Décision produit : tous les liens "Contact" du site (footer, nav Entreprise, page Retours) pointent vers `/contactus`, la page de contact **native** d'Odoo — aucune page contact custom n'a été construite.

## Corrections livrées

- Live Chat invisible + menu FR affiché en anglais (bug de contexte de traduction) — v19.0.1.0.38.
- Débordement horizontal de la page (halo du hero) — v19.0.1.0.39.
- Pastille "Tous les pods" sans couleur en anglais — v19.0.1.0.40.
- Design boutique "Chips" avec mauvaises classes CSS — v19.0.1.0.41.
- Menu compte natif ("My Account"/"Logout") non traduit + couleurs des pages de connexion natives — v19.0.1.0.42.
- Déconnexion redirigeant vers le mauvais site (conflit `website.sequence` entre sites de la base mutualisée) — v19.0.1.0.43.
- Pagination boutique restée en violet — v19.0.1.0.44.
- Espace excessif avant "Meilleures ventes" — v19.0.1.0.45.

## En attente / bloqué

- Refonte des heros Aide, Entreprise et Avis d'après 3 maquettes fournies par le client — les images envoyées ne sont pas arrivées correctement côté outil, à retransmettre.
- Vérification visuelle live des pages Entreprise une fois le module mis à jour côté client (le travail se fait entièrement en local sur le code, sans accès direct à l'instance Odoo.sh).

Toutes les versions sont documentées dans le `README.md` du module, avec un dossier `migrations/<version>/post-migrate.py` correspondant à chaque changement.
