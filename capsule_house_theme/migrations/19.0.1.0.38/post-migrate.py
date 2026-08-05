# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.38.

Root cause RÉEL du Live Chat invisible (le point était encore "en
diagnostic" en v.37) : ce n'était PAS un problème de résolution de
domaine multi-site. Inspection live du DOM/console sur une page
confirmée Capsule House (document.title == "Capsule House — Maisons
modulaires") a montré :

  - `.o-livechat-root` est bien présent, visible, z-index correct
    (donc website.channel_id, la règle d'affichage et l'opérateur
    posés par _setup_livechat() sont corrects côté backend) ;
  - mais son innerHTML est vide (0 enfant) ;
  - la console affiche : "ReferenceError: initBurger is not defined"
    levée par @capsule_house_theme/js/main, qui casse le chargement du
    bundle JS de la page ;
  - en cascade, plusieurs templates Owl natifs échouent à
    s'enregistrer : "Missing template: web.PagerIndicator",
    "web.OverlayContainer", "web.BlockUI",
    "html_editor.UploadProgressToast", et surtout **"mail.ChatHub"**
    (le composant qui affiche la fenêtre du live chat) — deux fois.

Cause exacte : static/src/js/main.js appelait encore initBurger() et
initNavActive() dans sa fonction init(), alors que ces deux fonctions
avaient été supprimées lors du passage au header natif Odoo (voir le
commentaire déjà présent en tête du fichier, ajouté à l'époque mais
dont le nettoyage de init() avait été oublié). Résultat : une
ReferenceError à CHAQUE chargement de page, qui empêchait l'app Owl de
finir son démarrage et donc de monter le widget Live Chat — sur
TOUTES les pages, pas seulement celles où on le remarquait.

Fix : suppression des deux appels orphelins dans init(). Le live chat
utilise désormais uniquement initScrollReveal() ; le menu mobile et le
lien actif restent gérés nativement par Odoo (header#top), comme prévu
depuis le passage au header natif.

Deuxième bug trouvé sur la même capture (page confirmée en français,
sélecteur de langue sur "Français") : le menu du haut s'affichait EN
ANGLAIS (Home, All pods, Accessories, Deals, Reviews) alors que le
reste de la page était en français. Cause dans _setup_menus() :
l'écriture du libellé français (existing.write()/Menu.create()) ne
posait aucun contexte de langue, donc héritait de la langue ambiante
de l'environnement du hook/cron (superuser, en_US par défaut) — le
texte français était donc écrit dans la case de traduction "en_US",
que l'écriture EN explicite juste après écrasait avec "Home" etc. La
case "fr_FR" n'était en réalité jamais remplie. Fix : fr_FR est
maintenant posé explicitement (with_context(lang='fr_FR')) à la
création ET à la mise à jour, avant l'écriture en_US.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.38 — correctif JS "
        "(ReferenceError initBurger, empêchait le Live Chat de se "
        "monter sur toutes les pages) + correctif menu fr_FR affiché "
        "en anglais (contexte de langue manquant dans _setup_menus)."
    )
    run_theme_maintenance(env)
