from odoo import http
from odoo.http import request
from datetime import datetime


class TravelController(http.Controller):

    @http.route('/travels', type='http', auth='public', website=True)
    def travel_list(self, **kwargs):
        products = request.env['product.template'].sudo().search([
            ('prix_par_personne', '>', 0),
        ])
        return request.render('travel_agency.travel_list_page', {
            'products': products,
        })

    @http.route('/travels/<int:product_id>', type='http', auth='public', website=True)
    def travel_detail(self, product_id, **kwargs):
        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists():
            return request.redirect('/travels')
        return request.render('travel_agency.travel_detail_page', {
            'product': product,
        })

    @http.route('/travels/book/<int:product_id>', type='http', auth='public', website=True)
    def travel_book(self, product_id, **kwargs):
        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists():
            return request.redirect('/travels')
        return request.render('travel_agency.travel_booking_page', {
            'product': product,
        })

    @http.route('/travels/book/submit', type='http', auth='public', website=True, methods=['POST'])
    def travel_book_submit(self, **kwargs):
        product_id = int(kwargs.get('product_id', 0))
        client_firstname = kwargs.get('client_firstname', '').strip()
        client_lastname = kwargs.get('client_lastname', '').strip()
        client_email = kwargs.get('client_email', '').strip()
        client_phone = kwargs.get('client_phone', '').strip()
        client_country = kwargs.get('client_country', '').strip()
        date_depart_str = kwargs.get('date_depart', '')
        date_retour_str = kwargs.get('date_retour', '')
        nb_adultes = int(kwargs.get('nb_adultes', 1))
        nb_enfants = int(kwargs.get('nb_enfants', 0))
        notes = kwargs.get('notes', '').strip()

        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists():
            return request.redirect('/travels')

        try:
            date_depart = datetime.strptime(date_depart_str, '%Y-%m-%d').date()
            date_retour = datetime.strptime(date_retour_str, '%Y-%m-%d').date()
        except ValueError:
            return request.render('travel_agency.travel_booking_page', {
                'product': product,
                'error': 'Dates invalides.',
            })

        if date_retour <= date_depart:
            return request.render('travel_agency.travel_booking_page', {
                'product': product,
                'error': 'La date de retour doit être après la date de départ.',
            })

        passenger_count = int(kwargs.get('passenger_count', 0))
        passenger_vals = []
        for i in range(passenger_count):
            prenom = kwargs.get('passenger_prenom_%d' % i, '').strip()
            nom = kwargs.get('passenger_nom_%d' % i, '').strip()
            dob = kwargs.get('passenger_dob_%d' % i, '').strip()
            ptype = kwargs.get('passenger_type_%d' % i, 'adulte')
            if not prenom or not nom:
                continue
            vals = {
                'prenom': prenom,
                'nom': nom,
                'type': ptype,
            }
            if dob:
                try:
                    vals['date_naissance'] = datetime.strptime(dob, '%Y-%m-%d').date()
                except ValueError:
                    pass
            passenger_vals.append((0, 0, vals))

        reservation = request.env['travel.reservation'].sudo().create({
            'client_firstname': client_firstname,
            'client_lastname': client_lastname,
            'client_email': client_email,
            'client_phone': client_phone,
            'client_country': client_country,
            'product_id': product_id,
            'date_depart': date_depart,
            'date_retour': date_retour,
            'nb_adultes': nb_adultes,
            'nb_enfants': nb_enfants,
            'notes': notes,
            'passenger_ids': passenger_vals,
            'state': 'draft',
        })

        return request.render('travel_agency.travel_confirm_page', {
            'reservation': reservation,
        })