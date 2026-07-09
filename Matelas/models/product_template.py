# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    """Ajoute les caractéristiques techniques d'un matelas (dimensions,
    matière, épaisseur, fermeté, garantie) directement modifiables par le
    maître de stage depuis la fiche produit Odoo (Ventes > Produits),
    sans toucher au code. Utilisées ensuite pour générer la fiche
    technique imprimable/partageable côté site public.
    """
    _inherit = 'product.template'

    matelas_dimensions = fields.Char(
        string="Dimensions",
        help="Ex : 140 x 190 cm")
    matelas_matiere = fields.Char(
        string="Matière",
        help="Ex : Mousse à mémoire de forme")
    matelas_epaisseur = fields.Char(
        string="Épaisseur",
        help="Ex : 25 cm")
    matelas_fermete = fields.Selection([
        ('souple', 'Souple'),
        ('medium', 'Médium'),
        ('ferme', 'Ferme'),
    ], string="Fermeté")
    matelas_garantie = fields.Char(
        string="Garantie",
        help="Ex : 10 ans")
