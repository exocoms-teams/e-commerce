from odoo import models, fields
from odoo.exceptions import UserError


class LuxuryListingRefuseWizard(models.TransientModel):
    _name = 'luxury.listing.refuse.wizard'
    _description = 'Wizard Refus Annonce'

    listing_id = fields.Many2one(
        'luxury.listing.request',
        string='Annonce',
        required=True,
    )
    refus_raison = fields.Text(
        string='Raison du refus',
        required=True,
        help='Ce message sera envoyé au propriétaire par email',
    )

    def action_confirm_refuse(self):
        self.ensure_one()
        if not self.refus_raison.strip():
            raise UserError('Veuillez indiquer une raison de refus.')

        # 1. Mettre à jour le statut et la raison
        self.listing_id.write({
            'state': 'refused',
            'refus_raison': self.refus_raison,
        })

        # 2. ✅ Logger la raison dans le chatter pour l'audit
        self.listing_id.message_post(
            body=f"""
                <div style="padding: 1rem; background: #fff3f3; border-left: 4px solid #e74c3c;">
                    <p><strong> Annonce refusée</strong></p>
                    <p><strong>Raison :</strong> {self.refus_raison}</p>
                    <p><strong>Refusée par :</strong> {self.env.user.name}</p>
                </div>
            """,
            subject=f"Refus — {self.listing_id.bien_nom}",
            message_type='comment',
            subtype_xmlid='mail.mt_note',  # Note interne
        )

        # 3. Envoyer l'email au client
        self.listing_id._send_refusal_email()

        return {'type': 'ir.actions.act_window_close'}