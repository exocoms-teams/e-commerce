# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cosmetic_type = fields.Char(string="Type de Cosmétique", help="Ex: Lip Colour, Radiance Serum")
    finish = fields.Char(string="Finition / Rendu", help="Ex: Matte Velvet, Satin, High Gloss")
    best_for = fields.Char(string="Idéal pour", help="Ex: Hydratation, Volume & Longueur")
    key_ingredients = fields.Text(string="Ingrédients Clés", help="Ex: Shea Butter, Vitamin E")
    
    # Relation vers un modèle personnalisé pour les nuances/teintes de couleurs
    shade_ids = fields.One2many('lumiere.product.shade', 'product_tmpl_id', string="Teintes disponibles")