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
    # Si un nouvel attribut:
    #  - Doit être impérativement défini avant son enregistrement,
    #  - Ne doit pas être associé à une catégorie de pneus afin
    #    de gérer son affichage,
    # Il faut l'ajouter aux règles définies dans TIRE_FIELD_RULES_MATRIX.

    # Internal
    is_tire = fields.Boolean(
        string="Produit pneu", compute="_compute_is_tire", store=True
    )

    tire_category = fields.Char(
        string="Catégorie pneu",
        related="categ_id.tire_category",
        readonly=True,
    )

    tire_family = fields.Char(
        string="Famille de pneu",
        compute="_compute_tire_family",
        readonly=True,
    )

    tire_field_applicability_map = fields.Json(
        compute="_compute_field_applicability",
        store=True,
    )

    # UI
    tire_brand = fields.Char(
        string="Marque",
        store=True,
    )

    tire_model = fields.Char(
        string="Modèle",
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

    tire_usage_id = fields.Many2one(
        "tire.usage",
        string="Domaine d’utilisation",
        ondelete="restrict",
        store=True,
    )

    tire_tread_pattern_id = fields.Many2one(
        "tire.tread.pattern",
        string="Profil du pneu",
        store=True,
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

    tire_specific_approval = fields.Char(
        string="Homologation spécifique", store=True, default="Non"
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

    # ------------------------------------------------------------
    # ONCHANGE METHODS
    # ------------------------------------------------------------
    @api.onchange("categ_id")
    def _onchange_categ_id(self):
        """Reset champs pneu si changement catégorie"""

        for rec in self:

            is_tire = self._is_tire_category(rec.categ_id)

            # Profil seulement en cas de changement de famille uniquement
            if is_tire:
                old_family = self._get_tire_family(rec._origin.categ_id)
                new_family = self._get_tire_family(rec.categ_id)

                if old_family == new_family:
                    return
                else:
                    rec.tire_tread_pattern_id = False
                    rec.tire_usage_id = False

    # ---------------------------------------------------------
    # COMPUTE METHODS
    # ---------------------------------------------------------
    @api.depends("categ_id", "categ_id.parent_id")
    def _compute_is_tire(self):
        """Définit si le produit est un pneu"""

        for product in self:
            product.is_tire = self._is_tire_category(product.categ_id)

    @api.depends("categ_id", "categ_id.parent_id")
    def _compute_tire_family(self):
        """Définit la famille de pneu"""

        for rec in self:
            rec.tire_family = self._get_tire_family(rec.categ_id)

    @api.depends("categ_id", "categ_id.parent_id")
    def _compute_field_applicability(self):
        """Définit la visibilité des champs pour filtrage XML via la matrice de règles TIRE_FIELD_RULES_MATRIX"""

        for rec in self:

            applicability_map = {}

            is_tire = self._is_tire_category(rec.categ_id)
            tire_family = self._get_tire_family(rec.categ_id)

            for field, rules in TIRE_FIELD_RULES_MATRIX.items():

                if field not in rec._fields:
                    continue

                if not is_tire:
                    applicability_map[field] = False
                    continue

                # Règles
                visible_rules = rules.get("visible")
                hidden_rules = rules.get("hidden")

                # Visibilité (la catégorie parente définie les règles)
                if visible_rules is not None:
                    applicability_map[field] = tire_family in visible_rules
                elif hidden_rules is not None:
                    applicability_map[field] = tire_family not in hidden_rules
                else:
                    applicability_map[field] = True

            rec.tire_field_applicability_map = applicability_map

    # ---------------------------------------------------------
    # ORM METHODS
    # ---------------------------------------------------------
    def write(self, vals):

        if self.env.context.get("skip_tire_reset"):
            return super().write(vals)

        old_categories = {rec.id: rec.categ_id for rec in self}

        res = super().write(vals)

        # IMPORTANT : s'assurer que les computes sont à jour
        self.flush_recordset()
        self.invalidate_recordset(["tire_field_applicability_map"])

        for rec in self:

            old_cat = old_categories.get(rec.id)
            new_cat = rec.categ_id

            if not old_cat or not new_cat:
                continue

            old_family = self._get_tire_family(old_cat)
            new_family = self._get_tire_family(new_cat)

            # CAS 1 : plus un pneu
            if not self._is_tire_category(new_cat):

                fields_to_reset = {
                    name: False
                    for name, field in rec._fields.items()
                    if name.startswith("tire_") and not field.compute
                }

                if fields_to_reset:
                    rec.with_context(skip_tire_reset=True).write(fields_to_reset)

                continue

            # CAS 2 : changement de famille de pneu
            else:
                if self._is_tire_category(old_cat) and old_family != new_family:

                    # Nettoyage des champs non applicables à une catégorie
                    applicability = rec.tire_field_applicability_map or {}

                    fields_to_reset = {
                        name: False
                        for name, field in rec._fields.items()
                        if name.startswith("tire_")
                        and not field.compute
                        and not applicability.get(name, False)
                    }

                    if fields_to_reset:
                        rec.with_context(skip_tire_reset=True).write(fields_to_reset)

                    # Vérification des champs restant
                    rec._check_tire_fields()

        return res

    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            if rec.is_tire:
                rec._check_tire_fields()
        return recs

    # ---------------------------------------------------------
    # BUSINESS METHODS
    # ---------------------------------------------------------
    def _get_tire_root(self):
        """Retourne la catégorie racine 'Pneu'"""

        tire_root = self.env.ref("tire_catalog.tire_category", raise_if_not_found=False)

        if not tire_root:
            _logger.error(
                "[MODULE 'tire_catalog']: XML ID tire_catalog.tire_category introuvable !"
            )

        return tire_root

    def _get_tire_family(self, categ):
        """Retourne la catégorie pneu parente"""

        tire_root = self._get_tire_root()

        if not tire_root or not categ:
            return False

        while categ.parent_id:
            if categ.parent_id == tire_root:
                return categ.tire_category
            categ = categ.parent_id

        return False

    def _is_tire_category(self, categ):
        """Retourne True si la catégorie appartient à l'arbre 'Pneu'"""

        tire_root = self._get_tire_root()

        if not tire_root or not categ:
            return False

        # Le produit est un pneu si sa catégorie appartient à l'arbre "Pneus"
        return categ.parent_path.startswith(tire_root.parent_path)

    def _check_tire_fields(self):
        """Vérifie la saisie des champs obligatoires"""

        for product in self:

            missing = []

            for field_name, applicable in product.tire_field_applicability_map.items():

                if not applicable:
                    continue

                field = product._fields[field_name]
                value = getattr(product, field_name)

                # Integer / Float
                if field.type in ("integer", "float"):
                    if value is None or value <= 0:
                        missing.append(field.string)
                    continue

                # Many2one / Char / etc.
                if not value:
                    missing.append(field.string)

            if missing:
                raise ValidationError(
                    "Les champs suivants sont obligatoires pour cette catégorie de pneu :\n- %s"
                    % "\n- ".join(missing)
                )
