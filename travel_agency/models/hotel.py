from odoo import models, fields


class Hotel(models.Model):
    _name = 'travel.hotel'
    _description = 'Hôtel' #afficher sur odoo

    name = fields.Char(string='Nom de l\'hôtel', required=True) 
    description = fields.Html(string='Description')
    image_1920 = fields.Image(string='Image', max_width=1920, max_height=1920) #stocke image

    pays = fields.Char(string='Pays')
    ville = fields.Char(string='Ville')
    adresse = fields.Char(string='Adresse')
    latitude = fields.Float(string='Latitude', digits=(10, 6))
    longitude = fields.Float(string='Longitude', digits=(10, 6))

    etoiles = fields.Selection([ #liste déroulante
        ('1', '1 étoile'),
        ('2', '2 étoiles'),
        ('3', '3 étoiles'),
        ('4', '4 étoiles'),
        ('5', '5 étoiles'),
    ], string='Étoiles')

    type_chambre = fields.Selection([
        ('simple', 'Simple'),
        ('double', 'Double'),
        ('twin', 'Twin'),
        ('suite', 'Suite'),
        ('familiale', 'Familiale'),
    ], string='Type de chambre', default='double')

    pension = fields.Selection([
        ('sans', 'Sans repas'),
        ('petit_dejeuner', 'Petit-déjeuner'),
        ('demi_pension', 'Demi-pension'),
        ('pension_complete', 'Pension complète'),
        ('tout_inclus', 'Tout inclus'),
    ], string='Formule repas', default='petit_dejeuner')

    nombre_chambres = fields.Integer(string='Chambres disponibles', default=1)
    prix_par_nuit = fields.Float(string='Prix par nuit (€)')
    disponible = fields.Boolean(string='Disponible', default=True) #case à cocher qui est vrai par défaut

    points_forts = fields.Text(string='Les plus') # texte d'avantages
