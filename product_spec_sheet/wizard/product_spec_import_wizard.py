from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductSpecImportWizard(models.TransientModel):
    """Importe en une fois des lignes de caractéristiques sur un ou plusieurs produits.

    Format attendu, une ligne par caractéristique :
        Catégorie ; Caractéristique ; Valeur

    Exemple :
        Connectivité ; Réseaux ; Wifi, 4G, Bluetooth, Ethernet
        Écran ; Taille ; 5 pouces tactile couleur
    """

    _name = 'product.spec.import.wizard'
    _description = "Import en masse de caractéristiques produit"

    product_tmpl_ids = fields.Many2many(
        'product.template', string="Produits",
        default=lambda self: self.env.context.get('active_ids', []),
        required=True,
    )
    data = fields.Text(
        string="Caractéristiques à appliquer",
        required=True,
        help="Une ligne par caractéristique, au format : Catégorie ; Caractéristique ; Valeur",
    )
    create_missing = fields.Boolean(
        string="Créer les catégories et caractéristiques manquantes",
        default=True,
    )
    update_existing = fields.Boolean(
        string="Mettre à jour la valeur si la caractéristique existe déjà",
        default=True,
    )

    def _get_or_create_category(self, name):
        category = self.env['product.spec.category'].search(
            [('name', '=', name)], limit=1,
        )
        if not category:
            if not self.create_missing:
                raise UserError(_("Catégorie inconnue : %s") % name)
            category = self.env['product.spec.category'].create({'name': name})
        return category

    def _get_or_create_attribute(self, name, category):
        attribute = self.env['product.spec.attribute'].search(
            [('name', '=', name), ('category_id', '=', category.id)], limit=1,
        )
        if not attribute:
            if not self.create_missing:
                raise UserError(_("Caractéristique inconnue : %s (catégorie %s)") % (name, category.name))
            attribute = self.env['product.spec.attribute'].create({
                'name': name,
                'category_id': category.id,
            })
        return attribute

    def action_import(self):
        self.ensure_one()
        if not self.product_tmpl_ids:
            raise UserError(_("Sélectionnez au moins un produit avant de lancer l'import."))

        rows = []
        for raw_line in (self.data or '').splitlines():
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            parts = [p.strip() for p in line.split(';')]
            if len(parts) != 3:
                raise UserError(
                    _("Ligne invalide (3 champs séparés par ';' attendus) : %s") % raw_line
                )
            rows.append(parts)

        if not rows:
            raise UserError(_("Aucune ligne valide trouvée dans le texte fourni."))

        SpecLine = self.env['product.template.spec.line']
        created, updated = 0, 0

        for category_name, attribute_name, value in rows:
            category = self._get_or_create_category(category_name)
            attribute = self._get_or_create_attribute(attribute_name, category)

            for product in self.product_tmpl_ids:
                existing = SpecLine.search([
                    ('product_tmpl_id', '=', product.id),
                    ('attribute_id', '=', attribute.id),
                ], limit=1)
                if existing:
                    if self.update_existing:
                        existing.value = value
                        updated += 1
                else:
                    SpecLine.create({
                        'product_tmpl_id': product.id,
                        'attribute_id': attribute.id,
                        'value': value,
                    })
                    created += 1

        message = _("%(created)d ligne(s) créée(s), %(updated)d mise(s) à jour.") % {
            'created': created, 'updated': updated,
        }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Import terminé"),
                'message': message,
                'type': 'success',
                'sticky': False,
            },
        }
