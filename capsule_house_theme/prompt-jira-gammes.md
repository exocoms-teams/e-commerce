# Prompt Jira — Backlog "Nos Gammes" (Capsule House)

*À coller dans l'assistant IA de Jira (ou dans une description d'Epic) pour générer/organiser le backlog.*

---

## Contexte à donner à l'outil

Nous développons le site e-commerce Capsule House (module Odoo `capsule_house_theme`, v19.0.1.0.83). Le site présente 5 gammes de produits : **Capsule, Cabine, Dôme, Modulaire, Pliable**, chacune avec une page de détail (`/nos-gammes/<slug>`) et une carte dans le filmstrip de l'accueil. Actuellement, **seule la gamme Capsule contient du contenu**, et ce contenu est constitué de **valeurs indicatives reprises d'un concurrent (capsule-home.fr)**, à remplacer par nos vraies données dès qu'elles seront disponibles. Les 4 autres gammes sont vides (statut "à confirmer") et n'affichent qu'un message "informations bientôt disponibles". La boutique (`/shop`) n'a par ailleurs **aucun produit réel publié** sous ces catégories.

Créer un Epic "Nos Gammes" avec les stories/tâches ci-dessous, en respectant les priorités indiquées.

---

## Epic 1 — Contenu réel de la gamme Capsule (remplacer les valeurs indicatives)

**Priorité : Haute** — la page est en ligne avec des données empruntées à un concurrent, à ne pas laisser en l'état trop longtemps.

- [ ] Valider/corriger les formats et surfaces réelles (actuellement en intervalles : Studio 18-20 m², Duo 26-30 m², Panorama 36-40 m²)
- [ ] Fournir les vraies spécifications techniques extérieures (façade, porte d'entrée, vitrage, fenêtres)
- [ ] Fournir les vraies spécifications techniques intérieures (sol, électricité, automatismes)
- [ ] Fournir la vraie liste d'équipements inclus
- [ ] Fournir la vraie liste d'options disponibles
- [ ] Valider ou remplacer les 9 cartes "Performances" (actuellement génériques : vitrage isolant, serrure sécurisée, éclairage LED, etc.)
- [ ] Décider si le statut passe de "Détails disponibles" à un vrai statut commercial une fois des produits publiés en boutique

## Epic 2 — Contenu des 4 gammes manquantes (Cabine, Dôme, Modulaire, Pliable)

**Priorité : Moyenne-Haute** — ces gammes sont annoncées sur le site mais sans aucune donnée.

Pour **chacune** des 4 gammes (créer une story par gamme) :
- [ ] Définir la tagline (FR/EN)
- [ ] Définir les formats/tailles disponibles (en intervalles, pas de valeurs fixes)
- [ ] Définir les spécifications techniques (extérieur + intérieur)
- [ ] Définir les équipements inclus
- [ ] Définir les options disponibles
- [ ] Définir les usages pertinents (logement, bureau, résidence secondaire, location/Airbnb...)
- [ ] Décider si une section "Performances" est pertinente pour cette gamme
- [ ] Passer le statut de "à confirmer" à "détails disponibles" une fois le contenu validé

## Epic 3 — Produits réels en boutique

**Priorité : Haute** — la boutique affiche des catégories (Capsule, Cabine, Dôme, Modulaire, Pliable, Accessoires) sans aucun produit réel dedans.

- [ ] Créer les fiches produits réelles pour au moins la gamme Capsule (par format : Studio/Duo/Panorama)
- [ ] Définir la tarification réelle (aucun prix engageant n'existe actuellement)
- [ ] Publier les produits sous les bonnes catégories (`product.public.category`)
- [ ] Ajouter photos réelles produits (actuellement pas de visuels propres)
- [ ] Revoir le badge de statut des pages gammes une fois des produits publiés (éviter toute ambiguïté "disponible" = achetable)

## Epic 4 — Finitions / décisions en attente

**Priorité : Basse**

- [ ] Décider du format du titre de page pour les gammes (actuellement "Capsule | Capsule House" — redondant, à simplifier ou reformuler, ex. "Gamme Capsule | Capsule House")
- [ ] Revoir si une section usages/application spécifique par gamme est nécessaire (au-delà de la liste générique actuelle sur l'accueil)

---

## Instruction finale pour l'outil

Crée ces 4 epics dans le projet Jira correspondant, avec les tâches ci-dessus en sous-tâches ou stories liées. Étiquette tout avec le label `gammes`. Priorise l'Epic 1 et l'Epic 3 en premier (contenu live actuellement basé sur des données concurrentes, et boutique sans produits réels).
