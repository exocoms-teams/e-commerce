# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.101.

CORRECTIF DE FOND (pas un simple correctif de contenu) — retour client :
"c est parce qu il sont toujour sur all au lieu de capsule house alors
que il doivent gardé permanament le fais qu il sont sur capsule house".

Cause réelle : _publish_our_products() (setup_utils.py), censée
rescoper automatiquement nos 24 vrais produits (data/products.xml) sur
website_id=notre site à CHAQUE (ré)installation du module, filtrait par
('company_id', '=', company.id) — or data/products.xml ne pose jamais
company_id sur ses <record> product.template (reste False, "toutes les
sociétés"), et un domaine Odoo ('company_id', '=', X) ne matche jamais
un enregistrement à False. Nos 24 produits étaient donc invisibles pour
cette fonction depuis le début : à chaque nouvelle base (les builds de
développement Odoo.sh recréent TOUJOURS une base neuve à partir des
data files du module à chaque push, voir doc Odoo.sh "Branches"), ils
repartaient avec website_id=False ("Tous les sites") sans jamais être
corrigés automatiquement. Une session précédente avait corrigé ça À LA
MAIN dans le backend d'un build donné — mais une édition manuelle ne
vit que dans CETTE base précise, jamais rejouée, donc reperdue au
prochain build/push.

Fix : _publish_our_products() identifie maintenant nos produits par
leurs external ids fixes (product_template_1 à _24, voir
data/products.xml) plutôt que par company_id — robuste sur la base
mutualisée (~17 sites), et réellement auto-réparateur : rejoué à chaque
post_init_hook (nouvelle base) et à chaque migration future, donc plus
jamais besoin d'édition manuelle en backend pour ce problème précis.

Fichier modifié : setup_utils.py (_publish_our_products).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.101 — "
        "_publish_our_products() identifie désormais nos 24 produits par "
        "leurs external ids fixes (au lieu de company_id, qui les "
        "excluait silencieusement) : website_id + is_published "
        "recorrigés, et corrigés automatiquement à chaque future "
        "(ré)installation de la base."
    )
    run_theme_maintenance(env)
