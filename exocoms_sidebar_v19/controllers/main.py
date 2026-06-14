# -*- coding: utf-8 -*-
"""
EXOCOMS — Sidebar Filter
Contrôleur Python pour Odoo 19

Changements v19 vs v17 :
  - La signature de shop() a changé : plus de paramètre `ppg`, nouveau `min_price`/`max_price`
  - website_sale utilise désormais `product.public.category` avec `website_id` lié
  - Les routes sont déclarées via @route avec type='http' uniquement (json retiré du shop)
  - `website_published` a été remplacé par `is_published` sur les catégories en v19
  - Le domaine de recherche produits utilise `is_published` et non `website_published`
"""

from odoo import http
from odoo.http import request

# Odoo 19 : import depuis le bon chemin
try:
    from odoo.addons.website_sale.controllers.main import WebsiteSale
except ImportError:
    from odoo.addons.website_sale.controllers.website_sale import WebsiteSale


class ExoWebsiteSaleV19(WebsiteSale):
    """
    Surcharge du contrôleur website_sale (Odoo 19) pour injecter
    les données du sidebar dans le contexte QWeb de la page /shop.
    """

    @http.route()
    def shop(self, page=0, category=None, search="", **post):
        """
        Appelle le contrôleur parent puis enrichit le qcontext
        avec la structure de catégories pour le sidebar.

        En Odoo 19 la signature ne contient plus `ppg` (géré en interne).
        """
        response = super().shop(
            page=page,
            category=category,
            search=search,
            **post,
        )

        # Récupère les IDs de catégories actifs depuis l'URL (?cat_ids=12,34)
        cat_ids_param = request.params.get("cat_ids", "")
        active_cat_ids = [
            int(x) for x in cat_ids_param.split(",") if x.strip().isdigit()
        ]

        # Construit l'arbre de catégories
        categories = self._build_sidebar_categories(active_cat_ids)

        if hasattr(response, "qcontext"):
            response.qcontext.update(
                {
                    "exo_categories": categories,
                    "exo_active_cat_ids": active_cat_ids,
                }
            )

        return response

    # ─────────────────────────────────────────────────────────────────────────
    # Construction de l'arbre de catégories (3 niveaux)
    # ─────────────────────────────────────────────────────────────────────────

    def _build_sidebar_categories(self, active_cat_ids=None):
        """
        Lit product.public.category et construit l'arbre 3 niveaux.

        Odoo 19 : le champ de publication est `is_published` (bool)
        sur website.published.mixin — les catégories n'héritent pas
        forcément de ce mixin, on filtre donc sur `website_id` uniquement.
        """
        active_cat_ids = active_cat_ids or []
        Cat = request.env["product.public.category"].sudo()
        current_website = request.website

        # Catégories racines visibles pour ce site
        roots = Cat.search(
            [
                ("parent_id", "=", False),
                "|",
                ("website_id", "=", current_website.id),
                ("website_id", "=", False),   # catégories partagées
            ],
            order="sequence, name",
        )

        result = []
        for cat in roots:
            cat_dict = self._cat_to_dict(cat, active_cat_ids, depth=0)
            result.append(cat_dict)

        return result

    def _cat_to_dict(self, cat, active_cat_ids, depth=0):
        """Convertit un record catégorie en dict pour le template QWeb."""
        Product = request.env["product.template"].sudo()
        current_website = request.website

        # Comptage des produits publiés dans cette catégorie
        count = Product.search_count(
            [
                ("public_categ_ids", "child_of", cat.id),
                ("is_published", "=", True),
                ("sale_ok", "=", True),
                "|",
                ("website_id", "=", current_website.id),
                ("website_id", "=", False),
            ]
        )

        data = {
            "id":             cat.id,
            "name":           cat.display_name,
            "icon":           getattr(cat, "x_sidebar_icon", None) or "fa-folder",
            "count":          count,
            "active":         cat.id in active_cat_ids,
            "subcategories":  [],
        }

        # Récursion sur les enfants (limité à 2 niveaux sous la racine)
        if depth < 2:
            for child in cat.child_id:
                data["subcategories"].append(
                    self._cat_to_dict(child, active_cat_ids, depth=depth + 1)
                )

        return data

    # ─────────────────────────────────────────────────────────────────────────
    # Route AJAX : filtrage dynamique sans rechargement de page (optionnel)
    # ─────────────────────────────────────────────────────────────────────────

    @http.route(
        "/shop/sidebar/filter",
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def sidebar_filter_ajax(self, cat_ids=None, page=0, **kwargs):
        """
        Route JSON appelée en AJAX pour mettre à jour la grille de produits
        sans recharger la page entière.

        Retourne : {
            'product_count': int,
            'product_ids':   list[int],
        }
        """
        cat_ids = [int(x) for x in (cat_ids or []) if str(x).isdigit()]
        current_website = request.website
        Product = request.env["product.template"].sudo()

        domain = [
            ("is_published", "=", True),
            ("sale_ok", "=", True),
            "|",
            ("website_id", "=", current_website.id),
            ("website_id", "=", False),
        ]

        if cat_ids:
            domain.append(("public_categ_ids", "child_of", cat_ids))

        products = Product.search(domain, limit=24, offset=page * 24)

        return {
            "product_count": Product.search_count(domain),
            "product_ids":   products.ids,
        }
