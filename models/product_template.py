from odoo import models, fields, api
from .tire_field_rules import TIRE_FIELD_RULES_MATRIX
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # ---------------------------------------------------------
    # ATTRIBUTES
    # ---------------------------------------------------------
    # Si un nouvel attribut ne doit pas être associé à une catégorie
    # de pneus afin de gérer son affichage, il faut l'ajouter aux règles
    # TIRE_FIELD_RULES_MATRIX.

    is_tire = fields.Boolean(
        string="Produit pneu", compute="_compute_is_tire", store=True
    )

    tire_brand = fields.Char(
        string="Marque",
        store=True,
    )

    tire_model = fields.Char(
        string="Modèle",
        store=True,
    )

    tire_usage_id = fields.Many2one(
        "tire.usage",
        string="Domaine d’utilisation",
        ondelete="restrict",
    )

    tire_width = fields.Integer(
        string="Largeur",
        store=True,
    )

    tire_height = fields.Integer(
        string="Hauteur",
        store=True,
    )

    tire_construction = fields.Selection(
        [
            ("radial", "Radial"),
            ("diagonal", "Diagonal"),
            ("belted", "Belted Bias"),
        ],
        string="Structure",
        default="radial",
        store=True,
    )

    tire_rim = fields.Integer(
        string="Diamètre",
        store=True,
    )

    tire_load_index = fields.Integer(
        string="Indice de charge",
        store=True,
    )

    tire_speed_index = fields.Char(
        string="Indice de vitesse",
        store=True,
    )

    tire_specific_approval = fields.Char(
        string="Homologation spécifique", store=True, default="Non"
    )

    tire_extra_load = fields.Selection(
        [
            ("true", "Oui"),
            ("false", "Non"),
        ],
        string="Renforcé (XL)",
        default="false",
        store=True,
    )

    tire_runflat = fields.Selection(
        [
            ("true", "Oui"),
            ("false", "Non"),
        ],
        string="Runflat",
        default="false",
        store=True,
    )

    tire_seal = fields.Selection(
        [
            ("true", "Oui"),
            ("false", "Non"),
        ],
        string="Self-sealing",
        default="false",
        store=True,
    )

    tire_season = fields.Selection(
        [
            ("all", "4 saisons"),
            ("summer", "Été"),
            ("winter", "Hiver"),
        ],
        string="Saison",
        store=True,
    )

    tire_snow_homologation = fields.Selection(
        [
            ("none", "Aucune"),
            ("m_s", "M+S"),
            ("3pmsf", "3PMSF"),
            ("m_s_3pmsf", "M+S + 3PMSF"),
        ],
        string="Homologation neige",
        default="none",
    )

    tire_new_or_retreaded = fields.Selection(
        [
            ("new", "Pneu neuf"),
            ("retreaded", "Pneu rechapé"),
        ],
        string="Pneu neuf ou rechapé",
        default="new",
        store=True,
    )

    tire_category = fields.Char(
        string="Catégorie pneu",
        related="categ_id.tire_category",
        store=True,
        readonly=True,
    )

    tire_tread_pattern_id = fields.Many2one(
        "tire.tread.pattern",
        string="Profil du pneu",
    )

    tire_sidewall_lettering = fields.Selection(
        [
            ("sbl", "SBL (Lettrage noir standard)"),
            ("owl", "OWL (Lettrage blanc)"),
            ("rwl", "RWL (Lettrage blanc en relief)"),
        ],
        string="Lettrage du pneu",
        default="sbl",
        store=True,
    )

    tire_characteristics = fields.Char(string="Caractéristiques diverses", store=True)

    tire_eprel = fields.Char(
        string="Fiche EPREL",
        store=True,
    )

    tire_label_image = fields.Image(
        string="Étiquette énergétique",
    )

    tire_fuel_efficiency = fields.Selection(
        [
            ("a", "A"),
            ("b", "B"),
            ("c", "C"),
            ("d", "D"),
            ("e", "E"),
            ("f", "F"),
            ("g", "G"),
        ],
        string="Éfficacité en carburant",
        store=True,
    )

    tire_wet_grip = fields.Selection(
        [
            ("a", "A"),
            ("b", "B"),
            ("c", "C"),
            ("d", "D"),
            ("e", "E"),
            ("f", "F"),
            ("g", "G"),
        ],
        string="Freinage sur sol mouillé",
        store=True,
    )

    tire_noise_db = fields.Char(
        string="Bruit de roulement externe",
        store=True,
    )

    tire_field_is_visible_map = fields.Json(
        compute="_compute_field_visibility",
        store=False,
    )

    # ---------------------------------------------------------
    # COMPUTE METHODS
    # ---------------------------------------------------------
    @api.depends("categ_id")
    def _compute_is_tire(self):
        """Recalcule is_tire dès que la catégorie du produit change"""

        # Récupération de la catégorie racine "Pneus" via XML ID
        tire_root = self.env.ref("tire_catalog.tire_category", raise_if_not_found=False)

        if not tire_root:
            _logger.error(
                "[MODULE 'tire_catalog']: /data/product_category.xml => XML ID tire_catalog.tire_category introuvable !"
            )
            for product in self:
                product.is_tire = False
            return

        # Catégories de pneus
        tire_categories_ids = (
            self.env["product.category"]
            .search(
                [
                    (
                        "id",
                        "child_of",
                        self.env.ref(
                            "tire_catalog.tire_category", raise_if_not_found=False
                        ).id,
                    )
                ]
            )
            .ids
        )

        for product in self:
            # Si la catégorie "Pneus" est introuvable ou si le produit n’a pas de catégorie assignée
            if not tire_root or not product.categ_id:
                product.is_tire = False
                continue
            # Le produit est un pneu si sa catégorie fait partie de l'arbre de la catégorie "Pneus"
            product.is_tire = product.categ_id.id in tire_categories_ids

    @api.depends("categ_id")
    def _compute_field_visibility(self):
        """Définit la visibilité des champs pour filtrage XML via la matrice de règles TIRE_FIELD_RULES_MATRIX"""

        for rec in self:

            category = rec.categ_id

            if not category:
                rec.tire_field_is_visible_map = {}
                continue

            while category.parent_id and category.parent_id.parent_id:
                category = category.parent_id

            parent_category = category.tire_category

            visibility_map = {}

            for field, rules in TIRE_FIELD_RULES_MATRIX.items():

                # Règles
                allowed = rules.get("allowed_categories")
                excluded = rules.get("excluded_categories")

                # Visibilité (la catégorie parente définie les règles)
                if allowed is not None:
                    visible = parent_category in allowed
                elif excluded is not None:
                    visible = parent_category not in excluded
                else:
                    visible = True

                visibility_map[field] = visible

            rec.tire_field_is_visible_map = visibility_map
