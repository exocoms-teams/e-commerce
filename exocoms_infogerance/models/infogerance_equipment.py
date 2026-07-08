from odoo import api, fields, models, _


class InfogeranceEquipment(models.Model):
    _name = 'exocoms.infogerance.equipment'
    _description = 'Équipement couvert par un contrat d\'infogérance'
    _rec_name = 'equipment_name'
    _order = 'contract_id, equipment_type'

    TYPE_SELECTION = [
        ('workstation', 'Poste de travail'),
        ('server', 'Serveur'),
        ('printer', 'Imprimante'),
        ('network', 'Équipement réseau'),
        ('phone', 'Téléphone'),
        ('tpe', 'TPE'),
        ('caisse', 'Caisse enregistreuse'),
        ('other', 'Autre'),
    ]

    contract_id = fields.Many2one('exocoms.infogerance.contract',
                                  string='Contrat', required=True,
                                  ondelete='cascade')
    equipment_name = fields.Char('Nom de l\'équipement', required=True)
    equipment_type = fields.Selection(TYPE_SELECTION,
                                      string='Type', required=True,
                                      default='workstation')
    serial_number = fields.Char('Numéro de série')
    brand = fields.Char('Marque')
    model = fields.Char('Modèle')
    location = fields.Char('Emplacement')
    ip_address = fields.Char('Adresse IP')
    mac_address = fields.Char('Adresse MAC')
    notes = fields.Text('Notes')
    active = fields.Boolean('Actif', default=True)
    date_installed = fields.Date('Date d\'installation')
    warranty_end = fields.Date('Fin de garantie')
    purchase_value = fields.Monetary('Valeur d\'achat',
                                     currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',
                                  related='contract_id.company_id.currency_id')

    anydesk_id = fields.Char('ID AnyDesk')
    anydesk_password = fields.Char('Mot de passe AnyDesk')

    image = fields.Binary('Photo')
