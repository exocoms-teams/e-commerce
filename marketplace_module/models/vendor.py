from odoo import models, fields, api
from odoo.exceptions import AccessError


class MarketplaceVendor(models.Model):
    """
    Modele representant un vendeur sur la marketplace monetiques.fr.
    Table en base : marketplace_vendor
    """
    _name        = 'marketplace.vendor'
    _description = 'Vendeur Marketplace'
    _order       = 'name asc'          # tri alphabetique par defaut
    _rec_name    = 'name'              # champ affiche dans les listes deroulantes

    # ── Champs d'identification ──────────────────────────────────────────
    name = fields.Char(
        string='Nom du vendeur',
        required=True,
        help='Nom commercial affiche publiquement sur la marketplace'
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact Odoo',
        help='Contact Odoo lie a ce vendeur (optionnel)'
    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Utilisateurs vendeur',
        help='Comptes Odoo autorises a gerer ce vendeur depuis le portail'
    )

    # ── Coordonnees publiques ─────────────────────────────────────────────
    email = fields.Char(
        string='Email de contact',
        help='Email public affiche sur les fiches produit'
    )
    phone = fields.Char(
        string='Telephone',
        help='Telephone public'
    )
    description = fields.Text(
        string='Presentation',
        help='Description publique du vendeur affichee dans la boutique'
    )
    logo = fields.Binary(
        string='Logo',
        attachment=True,
        help='Logo du vendeur affiche dans la boutique et le portail'
    )
    slug = fields.Char(
        string='Identifiant URL',
        help='Utilise dans les URLs ex: /vendor/mon-nom',
        index=True
    )

    # ── Multi-website  ─────────────────────────────────
    website_ids = fields.Many2many(
        comodel_name='website',
        string='Sites actifs',
        help='Sites web sur lesquels ce vendeur est visible'
    )

    # ── Produits associes  ─────────────────────────────
    product_ids = fields.One2many(
        comodel_name='product.template',
        inverse_name='vendor_id',
        string='Produits',
        help='Tous les produits appartenant a ce vendeur'
    )
    product_count = fields.Integer(
        string='Nb produits',
        compute='_compute_product_count',
        store=True
    )

    # ── Etat ─────────────────────────────────────────────────────────────
    active = fields.Boolean(
        default=True,
        help='Desactiver pour archiver le vendeur sans le supprimer'
    )

    # ── Methodes calculees ────────────────────────────────────────────────
    @api.depends('product_ids')
    def _compute_product_count(self):
        """Compte les produits actifs du vendeur."""
        for vendor in self:
            vendor.product_count = len(
                vendor.product_ids.filtered(lambda p: p.active)
            )

    # ── Methodes utilitaires ──────────────────────────────────────────────
    @api.model
    def _get_vendor_for_user(self, user=None):
        """
        Retourne le vendeur associe a l'utilisateur donne.
        Utilise dans le portail pour identifier le vendeur connecte.
        Retourne False si l'utilisateur n'est pas vendeur.
        """
        if user is None:
            user = self.env.user
        return self.search(
            [('user_ids', 'in', user.id), ('active', '=', True)],
            limit=1
        )

    def get_public_products(self, website=None):
        """
        Retourne les produits publics du vendeur pour un site donne.
        Si website est None, retourne tous les produits publis.
        """
        self.ensure_one()
        domain = [
            ('vendor_id', '=', self.id),
            ('website_published', '=', True),
        ]
        if website:
            domain.append(('website_id', '=', website.id))
        return self.env['product.template'].search(domain)
    
    def action_view_products(self):
        """Ouvre la liste des produits du vendeur depuis le back-office."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Produits de %s' % self.name,
            'res_model': 'product.template',
            'view_mode': 'list,form',
            'domain': [('vendor_id', '=', self.id)],
            'context': {'default_vendor_id': self.id},
        }
