Contexte
Tu travailles dans un module Odoo (site e-commerce "Capsule House", pods design sur mesure). La section "Entreprise" (fil d'Ariane "Home / Company") contient 3 pages avec une sous-navigation en pastilles commune : About, The concept, Contact. Mes captures sont en anglais ; le site est multilingue (sélecteur de langue).

Objectif
Mieux aérer ces 3 pages : ajouter des visuels/illustrations et découper le contenu en sections claires avec des sous-titres. Tu changes la structure et les visuels, pas le fond : ne réécris pas mes textes et ne modifie aucun chiffre.

Étape 1 : explorer, sans rien modifier
1. Lis __manifest__.py (version d'Odoo, dépendances, data, assets). Adapte-toi à cette version et vérifie dans le code existant avant d'utiliser une API dont tu n'es pas sûr.
2. Trouve les 3 pages en entier (mes captures ne montrent pas le bas des pages) : templates QWeb, contrôleurs, sous-navigation commune, SCSS/JS associés. Dis-moi si ce sont des templates du module ou des pages du website builder (website.page en base).
3. Liste les images et illustrations déjà utilisées et où elles sont stockées.
4. Propose-moi un plan par page (sections, sous-titres, emplacement et type de chaque visuel). Attends ma validation avant de coder.

Structure à proposer (point de départ à affiner)
ABOUT
- Hero : titre + texte + visuel. Prévois un emplacement pour une vraie photo de pod ; garde l'illustration actuelle en repli.
- Chiffres clés : inchangés.
- Sous-titre "Our values" : 3 cartes, icônes conservées.
- Sous-titre "Our story" : timeline sur deux colonnes en desktop, avec un visuel (photo d'atelier) à côté ; une icône ou miniature par étape si pertinent.
- Bloc facultatif "Behind the scenes" (atelier / équipe) avec emplacement photo.
- Fin de page : appels à l'action "Discover our pods" et "Contact us".
THE CONCEPT
- Intro à gauche + visuel à droite (photo ou rendu d'un pod).
- Ajoute le sous-titre manquant au tableau comparatif : "A pod vs traditional construction" (tableau inchangé).
- "From the workshop to your land" : garde les 4 étapes numérotées, ajoute une icône SVG ou une petite photo à chacune, et un lien vers la page Livraison de l'aide.
- "Technical cross-section" : remplace le schéma abstrait par un schéma technique légendé en SVG, avec repères numérotés (toit isolé, ossature bois, isolation biosourcée, vitrage, plancher) et une légende en liste HTML sous l'image (accessible, lisible sur mobile).
- Fin de page : appels à l'action.
CONTACT
- Garde la mise en page à deux colonnes et le formulaire (ne touche ni à ses champs ni à sa logique).
- Ajoute un petit visuel d'en-tête et un lien "Quick answers" vers la FAQ.
- Pas de carte externe (Google Maps, etc.) sans me demander d'abord : consentement et vie privée.

Règles pour les visuels
- Illustrations : SVG originaux dessinés par toi, dans l'identité existante (formes arrondies en capsule, sphère, terracotta et beige). Réutilise les variables de couleur du projet. Aucune image de banque d'images, aucun logo ou marque tiers, aucune image appelée depuis un site externe.
- Photos réelles : tu ne peux pas en fournir. Crée des emplacements propres (fichiers de remplacement nommés clairement, ratio fixe) et donne-moi la liste des photos à fournir, avec ratio et taille.
- Formats : SVG pour les illustrations, WebP pour les photos.
- Stockage dans static/src/img/ du module, avec les chemins utilisés par le reste du module.
- Performance : attributs width/height, loading="lazy" sauf pour l'image du hero, srcset si utile, environ 200 Ko maximum par photo.
- Accessibilité : alt descriptif pour les images informatives ; alt="" et aria-hidden pour les images décoratives ; le schéma technique a un titre et une description. Respecte prefers-reduced-motion si tu ajoutes une animation.
- Si tu mets du SVG inline dans un template QWeb, il doit être du XML valide.

Conventions Odoo
- Textes dans les templates QWeb pour rester traduisibles. Écris les nouveaux textes dans la même langue source que les textes existants, et ajoute les traductions dans i18n/*.po si le projet en maintient.
- Utilise Bootstrap et le SCSS du module (bundle web.assets_frontend). Aucune nouvelle bibliothèque.
- Factorise les blocs répétés (titre de section, carte, bloc visuel + texte) en sous-templates appelés avec t-call.
- Ne modifie jamais le code d'Odoo ni d'un autre module : utilise l'héritage (inherit_id + xpath) si nécessaire.
- Si les pages sont éditables dans le website builder, utilise de simples balises <img> pour que les images restent remplaçables depuis l'éditeur.
- Responsive : sur mobile, les colonnes s'empilent (visuel après le titre), sans défilement horizontal. Teste desktop, tablette et mobile.
- Ne modifie ni la sous-navigation ni les URLs.

Étape 3 : vérifier
- Donne-moi la commande de mise à jour du module (-u mon_module) et dis-moi si un redémarrage ou une régénération des assets est nécessaire.
- Teste : 3 pages, 3 largeurs d'écran, 2 langues, éditeur de site, textes alternatifs, poids des images.
- Termine par un résumé : fichiers créés/modifiés, photos que je dois fournir, points à vérifier.

À me signaler sans les corriger (hors périmètre)
- Fil d'Ariane incohérent ("Home / Company" sur About et The concept, "Home / Company / Contact" sur Contact).
- Petits textes peu contrastés ou trop petits.
- Affirmations à étayer : "Prior declaration (usually)", "Carbon footprint: Reduced", "6 weeks" sans préciser la France métropolitaine, "€150,000 and up".

Contraintes
- Changements minimaux et propres, sans refactoriser ce qui n'est pas concerné.
- Si une information manque ou si deux choix sont possibles, pose-moi la question au lieu de deviner.