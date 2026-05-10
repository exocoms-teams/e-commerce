from odoo import http
from odoo.http import request
from datetime import datetime


class LuxuryController(http.Controller):

    @http.route('/luxury/reserver/<int:product_id>',
                type='http',
                auth='public',
                website=True)
    def reservation_page(self, product_id, **kwargs):
        """Page de réservation d'un produit"""
        product = request.env['product.template'].sudo().browse(product_id)

        if not product.exists():
            return request.redirect('/shop')

        if product.type_service not in ('location', 'les_deux'):
            return request.redirect('/shop')

        if not product.disponible:
            return request.redirect('/shop')

        return request.render('luxury_services.luxury_reservation_page', {
            'product': product,
        })

    @http.route('/luxury/reserver/submit',
                type='http',
                auth='public',
                website=True,
                methods=['POST'])
    def reservation_submit(self, **kwargs):
        """Traitement du formulaire de réservation"""
        product_id = int(kwargs.get('product_id', 0))
        client_name = kwargs.get('client_name', '').strip()
        client_email = kwargs.get('client_email', '').strip()
        client_phone = kwargs.get('client_phone', '').strip()
        date_debut_str = kwargs.get('date_debut', '')
        date_fin_str = kwargs.get('date_fin', '')
        notes = kwargs.get('notes', '').strip()

        # Récupère le produit
        product = request.env['product.template'].sudo().browse(product_id)

        if not product.exists():
            return request.redirect('/shop')

        # Convertit les dates
        try:
            date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
            date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            return request.redirect(f'/luxury/reserver/{product_id}')

        # Vérifie la disponibilité
        if not product.is_available_for_dates(date_debut, date_fin):
            return request.render('luxury_services.luxury_reservation_page', {
                'product': product,
                'error': 'Ce produit n\'est pas disponible pour ces dates.',
            })

        # Vérifie la durée minimum
        nb_jours = (date_fin - date_debut).days
        if nb_jours < product.duree_min_location:
            return request.render('luxury_services.luxury_reservation_page', {
                'product': product,
                'error': f'La durée minimum de location est de {product.duree_min_location} jours.',
            })

        # Crée la réservation
        reservation = request.env['luxury.reservation'].sudo().create({
            'product_id': product_id,
            'client_name': client_name,
            'client_email': client_email,
            'client_phone': client_phone,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'notes': notes,
            'state': 'confirmed',
        })

        # Marque le produit comme non disponible
        product.sudo().write({'disponible': False})

        return request.render('luxury_services.luxury_reservation_confirm', {
            'reservation': reservation,
        })