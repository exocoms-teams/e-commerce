from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.addons.website_sale.controllers.main import WebsiteSale


class LuxuryController(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, options=None):
        """Étend le domain de recherche avec les filtres luxury"""
        domain = super()._get_search_domain(
            search, category, attrib_values, options
        )

        params = request.params

        # Filtre type service
        type_service = params.get('type_service', '')
        if type_service == 'location':
            domain += [('type_service', 'in', ['location', 'les_deux'])]
        elif type_service == 'vente':
            domain += [('type_service', 'in', ['vente', 'les_deux'])]

        # Filtre longueur
        longueur_min = params.get('longueur_min', '')
        longueur_max = params.get('longueur_max', '')
        if longueur_min:
            domain += [('longueur', '>=', float(longueur_min))]
        if longueur_max:
            domain += [('longueur', '<=', float(longueur_max))]

        # Filtre capacité
        capacite_min = params.get('capacite_min', '')
        if capacite_min:
            domain += [('capacite_personnes', '>=', int(capacite_min))]

        # Filtre cabines
        cabines_min = params.get('cabines_min', '')
        if cabines_min:
            domain += [('nb_cabines', '>=', int(cabines_min))]

        # Filtre vitesse
        vitesse_min = params.get('vitesse_min', '')
        if vitesse_min:
            domain += [('vitesse_max', '>=', float(vitesse_min))]

        return domain

    @http.route('/luxury/reserver/<int:product_id>',
                type='http',
                auth='public',
                website=True)
    def reservation_page(self, product_id, **kwargs):
        product = request.env['product.template'].sudo().browse(product_id)

        if not product.exists():
            return request.redirect('/shop')
        if product.type_service not in ('location', 'les_deux'):
            return request.redirect('/shop')
        if not product.disponible:
            return request.redirect('/shop')

        pays = request.env['res.country'].sudo().search([])

        return request.render('luxury_services.luxury_reservation_page', {
            'product': product,
            'pays_list': pays,
        })

    @http.route('/luxury/reserver/recap',
                type='http',
                auth='public',
                website=True,
                methods=['POST'])
    def reservation_recap(self, **kwargs):
        product_id = int(kwargs.get('product_id', 0))
        client_name = kwargs.get('client_name', '').strip()
        client_email = kwargs.get('client_email', '').strip()
        client_phone = kwargs.get('client_phone', '').strip()
        client_adresse = kwargs.get('client_adresse', '').strip()
        client_code_postal = kwargs.get('client_code_postal', '').strip()
        client_pays_id = int(kwargs.get('client_pays_id', 0))
        date_debut_str = kwargs.get('date_debut', '')
        date_fin_str = kwargs.get('date_fin', '')
        notes = kwargs.get('notes', '').strip()

        product = request.env['product.template'].sudo().browse(product_id)
        pays = request.env['res.country'].sudo().browse(client_pays_id)

        if not product.exists():
            return request.redirect('/shop')

        try:
            date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
            date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            pays_list = request.env['res.country'].sudo().search([])
            return request.render('luxury_services.luxury_reservation_page', {
                'product': product,
                'pays_list': pays_list,
                'error': 'Dates invalides.',
            })

        if date_fin <= date_debut:
            pays_list = request.env['res.country'].sudo().search([])
            return request.render('luxury_services.luxury_reservation_page', {
                'product': product,
                'pays_list': pays_list,
                'error': 'La date de fin doit être après la date de début.',
            })

        nb_jours = (date_fin - date_debut).days

        if nb_jours < product.duree_min_location:
            pays_list = request.env['res.country'].sudo().search([])
            return request.render('luxury_services.luxury_reservation_page', {
                'product': product,
                'pays_list': pays_list,
                'error': f'La durée minimum de location est de {product.duree_min_location} jours.',
            })

        if not product.is_available_for_dates(date_debut, date_fin):
            pays_list = request.env['res.country'].sudo().search([])
            return request.render('luxury_services.luxury_reservation_page', {
                'product': product,
                'pays_list': pays_list,
                'error': 'Ce produit n\'est pas disponible pour ces dates.',
            })

        prix_total = nb_jours * product.prix_location_jour

        return request.render('luxury_services.luxury_reservation_recap', {
            'product': product,
            'client_name': client_name,
            'client_email': client_email,
            'client_phone': client_phone,
            'client_adresse': client_adresse,
            'client_code_postal': client_code_postal,
            'client_pays': pays,
            'client_pays_id': client_pays_id,
            'date_debut': date_debut_str,
            'date_fin': date_fin_str,
            'nb_jours': nb_jours,
            'prix_total': prix_total,
            'notes': notes,
        })

    @http.route('/luxury/reserver/submit',
                type='http',
                auth='public',
                website=True,
                methods=['POST'])
    def reservation_submit(self, **kwargs):
        product_id = int(kwargs.get('product_id', 0))
        client_name = kwargs.get('client_name', '').strip()
        client_email = kwargs.get('client_email', '').strip()
        client_phone = kwargs.get('client_phone', '').strip()
        client_adresse = kwargs.get('client_adresse', '').strip()
        client_code_postal = kwargs.get('client_code_postal', '').strip()
        client_pays_id = int(kwargs.get('client_pays_id', 0))
        date_debut_str = kwargs.get('date_debut', '')
        date_fin_str = kwargs.get('date_fin', '')
        notes = kwargs.get('notes', '').strip()

        product = request.env['product.template'].sudo().browse(product_id)

        if not product.exists():
            return request.redirect('/shop')

        try:
            date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
            date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            return request.redirect(f'/luxury/reserver/{product_id}')

        reservation = request.env['luxury.reservation'].sudo().create({
            'product_id': product_id,
            'client_name': client_name,
            'client_email': client_email,
            'client_phone': client_phone,
            'client_adresse': client_adresse,
            'client_code_postal': client_code_postal,
            'client_pays': client_pays_id if client_pays_id else False,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'notes': notes,
            'state': 'en_attente',
        })

        return request.render('luxury_services.luxury_reservation_confirm', {
            'reservation': reservation,
        })

    @http.route('/luxury/paiement/<int:reservation_id>',
                type='http',
                auth='public',
                website=True)
    def paiement_page(self, reservation_id, **kwargs):
        reservation = request.env['luxury.reservation'].sudo().browse(reservation_id)

        if not reservation.exists():
            return request.redirect('/')
        if reservation.state != 'confirmed':
            return request.redirect('/')

        return request.render('luxury_services.luxury_paiement_page', {
            'reservation': reservation,
        })