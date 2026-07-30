# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    # Champ technique optionnel : permet de choisir une icône Tabler / FontAwesome
    # par catégorie directement depuis le back-office (onglet "Site Web").
    exocoms_icon = fields.Char(
        string="Icône sidebar",
        help="Classe d'icône (ex: 'fa-laptop' ou 'ti ti-device-laptop'). "
             "Affichée dans la sidebar de filtres.",
    )
    exocoms_color = fields.Char(
        string="Couleur d'accent",
        help="Couleur hexadécimale de la pastille (ex: #0F6E56).",
    )

    # ------------------------------------------------------------------
    # API publique consommée par le contrôleur / l'interaction front
    # ------------------------------------------------------------------
    @api.model
    def _exocoms_default_icon(self, category):
        """Icône de repli devinée à partir du nom si aucune n'est définie."""
        if category.exocoms_icon:
            return category.exocoms_icon
        name = (category.name or "").lower()
        mapping = {
            # Catégories réelles de la boutique EXOCOMS
            "monétique": "fa-credit-card",
            "monetique": "fa-credit-card",
            "tpe": "fa-credit-card",
            "point de vente": "fa-desktop",
            "pdv": "fa-desktop",
            "terminaux": "fa-desktop",
            "pos": "fa-desktop",
            "caisse": "fa-calculator",
            "tactile": "fa-calculator",
            "passerelle": "fa-exchange",
            "chèque": "fa-money",
            "cheque": "fa-money",
            "monnaie": "fa-money",
            "logiciel": "fa-window-restore",
            "accessoire": "fa-plug",
            "service": "fa-wrench",
            "santé": "fa-heartbeat",
            "sante": "fa-heartbeat",
            # Lignes métier (si ajoutées plus tard au e-commerce)
            "informatique": "fa-laptop",
            "télécom": "fa-phone",
            "telecom": "fa-phone",
            "wifi": "fa-wifi",
            "réseau": "fa-wifi",
            "reseau": "fa-wifi",
            "vidéo": "fa-video-camera",
            "video": "fa-video-camera",
            "surveillance": "fa-video-camera",
            "affichage": "fa-tv",
            "signal": "fa-tv",
            "écran": "fa-tv",
        }
        for key, icon in mapping.items():
            if key in name:
                return icon
        return "fa-folder-o"

    @api.model
    def _exocoms_category_stats(self, category, website):
        """Retourne (nb_produits, qty_dispo) pour une catégorie ET toute sa
        descendance, en ne comptant que les produits publiés sur le site."""
        all_cats = category | category.search(
            [("id", "child_of", category.id)]
        )
        Product = self.env["product.template"].sudo()
        products = Product.search([
            ("public_categ_ids", "in", all_cats.ids),
            ("is_published", "=", True),
            ("website_id", "in", [False, website.id]),
        ])
        qty = sum(products.mapped("qty_available")) if products else 0.0
        return len(products), int(qty)

    @api.model
    def exocoms_get_tree(self, max_depth=3, website_id=None):
        """Construit l'arbre des catégories du site (jusqu'à 3 niveaux) avec,
        pour chaque nœud : icône, couleur, nombre de produits et quantité
        disponible. Utilisé par le snippet et le contrôleur AJAX."""
        website = self.env["website"].browse(website_id) \
            if website_id else self.env["website"].get_current_website()

        roots = self.sudo().search(
            [("parent_id", "=", False)], order="sequence, name"
        )

        def serialize(cat, depth):
            nb, qty = self._exocoms_category_stats(cat, website)
            if nb == 0 and depth == 1:
                return None
            node = {
                "id": cat.id,
                "name": cat.name,
                "icon": self._exocoms_default_icon(cat),
                "color": cat.exocoms_color or "",
                "depth": depth,
                "product_count": nb,
                "qty_available": qty,
                "children": [],
            }
            if depth < max_depth:
                children = cat.child_id.sorted(lambda c: (c.sequence, c.name))
                node["children"] = [
                    c for c in [serialize(child, depth + 1) for child in children]
                    if c is not None
                ]
            return node

        return [n for n in [serialize(root, 1) for root in roots] if n is not None]
