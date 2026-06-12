from odoo import http
from odoo.http import request
from datetime import datetime


class TravelController(http.Controller):

    @http.route('/travels', type='http', auth='public', website=True)
    def travel_list(self, **kwargs):
        domain = [('prix_par_personne', '>', 0)]

        destination = kwargs.get('destination', '').strip()
        if destination:
            domain += ['|',
                       ('ville_destination', 'ilike', destination),
                       ('pays_destination', 'ilike', destination)]

        type_voyage = kwargs.get('type_voyage', '').strip()
        if type_voyage:
            domain.append(('type_voyage', '=', type_voyage))

        etoiles = kwargs.get('etoiles', '').strip()
        if etoiles:
            domain.append(('etoiles', '>=', etoiles))

        prix_max = kwargs.get('prix_max', '').strip()
        if prix_max:
            try:
                domain.append(('prix_par_personne', '<=', float(prix_max)))
            except ValueError:
                pass

        products = request.env['product.template'].sudo().search(domain)
        return request.render('travel_agency.travel_list_page', {
            'products': products,
            'filters': kwargs,
        })

    @http.route('/hotels', type='http', auth='public', website=True)
    def hotel_list(self, **kwargs):
        domain = [('disponible', '=', True)]

        destination = kwargs.get('destination', '').strip()
        if destination:
            domain += ['|',
                       ('ville', 'ilike', destination),
                       ('pays', 'ilike', destination)]

        etoiles = kwargs.get('etoiles', '').strip()
        if etoiles:
            domain.append(('etoiles', '>=', etoiles))

        hotels = request.env['travel.hotel'].sudo().search(domain)
        return request.render('travel_agency.hotel_list_page', {
            'hotels': hotels,
            'filters': kwargs,
        })

    @http.route('/hotels/<int:hotel_id>', type='http', auth='public', website=True)
    def hotel_detail(self, hotel_id, **kwargs):
        hotel = request.env['travel.hotel'].sudo().browse(hotel_id)
        if not hotel.exists():
            return request.redirect('/hotels')
        return request.render('travel_agency.hotel_detail_page', {
            'hotel': hotel,
        })

    @http.route('/vols', type='http', auth='public', website=True)
    def vol_list(self, **kwargs):
        domain = [('disponible', '=', True)]

        destination = kwargs.get('destination', '').strip()
        if destination:
            domain += ['|',
                       ('ville_arrivee', 'ilike', destination),
                       ('pays_arrivee', 'ilike', destination)]

        classe = kwargs.get('classe', '').strip()
        if classe:
            domain.append(('classe', '=', classe))

        vols = request.env['travel.vol'].sudo().search(domain)
        return request.render('travel_agency.vol_list_page', {
            'vols': vols,
            'filters': kwargs,
        })

    @http.route('/vols/<int:vol_id>', type='http', auth='public', website=True)
    def vol_detail(self, vol_id, **kwargs):
        vol = request.env['travel.vol'].sudo().browse(vol_id)
        if not vol.exists():
            return request.redirect('/vols')
        return request.render('travel_agency.vol_detail_page', {
            'vol': vol,
        })

    @http.route('/trains', type='http', auth='public', website=True)
    def train_list(self, **kwargs):
        domain = [('disponible', '=', True)]

        destination = kwargs.get('destination', '').strip()
        if destination:
            domain += ['|',
                       ('ville_arrivee', 'ilike', destination),
                       ('pays_arrivee', 'ilike', destination)]

        classe = kwargs.get('classe', '').strip()
        if classe:
            domain.append(('classe', '=', classe))

        trains = request.env['travel.train'].sudo().search(domain)
        return request.render('travel_agency.train_list_page', {
            'trains': trains,
            'filters': kwargs,
        })

    @http.route('/trains/<int:train_id>', type='http', auth='public', website=True)
    def train_detail(self, train_id, **kwargs):
        train = request.env['travel.train'].sudo().browse(train_id)
        if not train.exists():
            return request.redirect('/trains')
        return request.render('travel_agency.train_detail_page', {
            'train': train,
        })

    @http.route('/voitures', type='http', auth='public', website=True)
    def car_list(self, **kwargs):
        domain = [('disponible', '=', True)]

        destination = kwargs.get('destination', '').strip()
        if destination:
            domain += ['|',
                       ('ville_prise_en_charge', 'ilike', destination),
                       ('pays', 'ilike', destination)]

        categorie = kwargs.get('categorie', '').strip()
        if categorie:
            domain.append(('categorie', '=', categorie))

        cars = request.env['travel.car'].sudo().search(domain)
        return request.render('travel_agency.car_list_page', {
            'cars': cars,
            'filters': kwargs,
        })

    @http.route('/voitures/<int:car_id>', type='http', auth='public', website=True)
    def car_detail(self, car_id, **kwargs):
        car = request.env['travel.car'].sudo().browse(car_id)
        if not car.exists():
            return request.redirect('/voitures')
        return request.render('travel_agency.car_detail_page', {
            'car': car,
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