from odoo import http
from odoo.http import request
from datetime import datetime


class TravelController(http.Controller):

    # ============================================
    # PAGES STATIQUES
    # ============================================
    
    @http.route('/conditions-utilisation', type='http', auth='public', website=True)
    def terms_page(self, **kwargs):
        return request.render('travel_agency.terms_page', {})

    @http.route('/a-propos', type='http', auth='public', website=True)
    def about_page(self, **kwargs):
        return request.render('travel_agency.about_page', {})

    @http.route('/faq', type='http', auth='public', website=True)
    def faq_page(self, **kwargs):
        return request.render('travel_agency.faq_page', {})

    # ============================================
    # ROUTES EXISTANTES - VOYAGES (PRODUCTS)
    # ============================================
    
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
        providers = request.env['travel.payment.provider'].sudo().search([('active', '=', True)])
        return request.render('travel_agency.travel_booking_page', {
            'product': product,
            'providers': providers,
        })
    @http.route('/travels/payment/<int:transaction_id>', type='http', auth='public', website=True)
    def travel_payment_page(self, transaction_id, **kwargs):
        transaction = request.env['travel.payment.transaction'].sudo().browse(transaction_id)
        if not transaction.exists() or transaction.state != 'pending':
            return request.redirect('/travels')
        return request.render('travel_agency.travel_payment_page', {
            'transaction': transaction,
        })

    @http.route('/travels/payment/submit', type='http', auth='public', website=True, methods=['POST'])
    def travel_payment_submit(self, **kwargs):
        transaction_id = int(kwargs.get('transaction_id', 0))
        transaction = request.env['travel.payment.transaction'].sudo().browse(transaction_id)
        if not transaction.exists():
            return request.redirect('/travels')

        card_number = kwargs.get('card_number', '').strip()
        card_last_4 = card_number[-4:] if len(card_number) >= 4 else ''

        # Simulateur : on valide juste que le numéro de carte a bien 16 chiffres
        if len(card_number.replace(' ', '')) == 16:
            transaction.write({
                'state': 'done',
                'card_last_4': card_last_4,
            })
            transaction.action_done()
            transaction.reservation_id.action_confirm()
        else:
            transaction.action_failed()
            return request.render('travel_agency.travel_payment_page', {
                'transaction': transaction,
                'error': 'Numéro de carte invalide (simulateur : 16 chiffres requis).',
            })

        return request.render('travel_agency.travel_confirm_page', {
            'reservation': transaction.reservation_id,
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

        payment_provider_id = int(kwargs.get('payment_provider_id', 0) or 0)
        if not payment_provider_id:
            return request.render('travel_agency.travel_booking_page', {
                'product': product,
                'providers': request.env['travel.payment.provider'].sudo().search([('active', '=', True)]),
                'error': 'Veuillez choisir un prestataire de paiement.',
            })

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
            'payment_provider_id': payment_provider_id,
            'state': 'en_attente',
        })

<<<<<<< HEAD
        return request.render('travel_agency.travel_confirm_page', {
            'reservation': reservation,
        })

    # ============================================
    # ROUTES EXISTANTES - HÔTELS
    # ============================================
    
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

    # ============================================
    # ROUTES EXISTANTES - VOLS
    # ============================================
    
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

    # ============================================
    # ROUTES EXISTANTES - TRAINS
    # ============================================
    
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

    # ============================================
    # ROUTES EXISTANTES - VOITURES
    # ============================================
    
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

    # ============================================
    # NOUVELLES ROUTES - TRAVEL GUIDE (Guides touristiques)
    # ============================================
    
    @http.route('/guides', type='http', auth='public', website=True)
    def guide_list(self, **kwargs):
        """
        Liste des guides touristiques
        URL: /guides
        """
        domain = [('active', '=', True)]

        # Filtrage par catégorie
        category_id = kwargs.get('category_id', '').strip()
        if category_id:
            try:
                domain.append(('category_id', '=', int(category_id)))
            except ValueError:
                pass

        # Recherche par nom ou description
        search = kwargs.get('search', '').strip()
        if search:
            domain += ['|',
                       ('name', 'ilike', search),
                       ('description', 'ilike', search)]

        # Filtrer par prix max
        price_max = kwargs.get('price_max', '').strip()
        if price_max:
            try:
                domain.append(('price', '<=', float(price_max)))
            except ValueError:
                pass

        guides = request.env['travel.guide'].sudo().search(domain)
        
        # Récupérer les catégories pour le filtre
        categories = request.env['product.category'].sudo().search([])
        
        return request.render('travel_agency.website_guide_list', {
            'guides': guides,
            'categories': categories,
            'filters': kwargs,
        })

    @http.route('/guides/<int:guide_id>', type='http', auth='public', website=True)
    def guide_detail(self, guide_id, **kwargs):
        """
        Détail d'un guide touristique
        URL: /guides/1
        """
        guide = request.env['travel.guide'].sudo().browse(guide_id)
        if not guide.exists():
            return request.redirect('/guides')
        if not guide.active:
            return request.redirect('/guides')
        
        # Guides similaires (même catégorie)
        similar_guides = request.env['travel.guide'].sudo().search([
            ('active', '=', True),
            ('category_id', '=', guide.category_id.id),
            ('id', '!=', guide.id)
        ], limit=4)
        
        return request.render('travel_agency.website_guide_detail', {
            'guide': guide,
            'similar_guides': similar_guides,
        })

    # ============================================
    # NOUVELLES ROUTES - TRAVEL LEISURE (Sorties & Loisirs)
    # ============================================
    
    @http.route('/loisirs', type='http', auth='public', website=True)
    def leisure_list(self, **kwargs):
        """
        Liste des sorties et loisirs
        URL: /loisirs
        """
        domain = [('active', '=', True)]

        # Filtrage par catégorie
        category_id = kwargs.get('category_id', '').strip()
        if category_id:
            try:
                domain.append(('category_id', '=', int(category_id)))
            except ValueError:
                pass

        # Recherche par nom ou description
        search = kwargs.get('search', '').strip()
        if search:
            domain += ['|',
                       ('name', 'ilike', search),
                       ('description', 'ilike', search)]

        # Filtrer par âge minimum
        min_age = kwargs.get('min_age', '').strip()
        if min_age:
            try:
                domain.append(('min_age', '>=', int(min_age)))
            except ValueError:
                pass

        # Filtrer par prix max
        price_max = kwargs.get('price_max', '').strip()
        if price_max:
            try:
                domain.append(('price', '<=', float(price_max)))
            except ValueError:
                pass

        leisures = request.env['travel.leisure'].sudo().search(domain)
        
        # Récupérer les catégories pour le filtre
        categories = request.env['product.category'].sudo().search([])
        
        return request.render('travel_agency.website_leisure_list', {
            'leisures': leisures,
            'categories': categories,
            'filters': kwargs,
        })

    @http.route('/loisirs/<int:leisure_id>', type='http', auth='public', website=True)
    def leisure_detail(self, leisure_id, **kwargs):
        """
        Détail d'une sortie ou loisir
        URL: /loisirs/1
        """
        leisure = request.env['travel.leisure'].sudo().browse(leisure_id)
        if not leisure.exists():
            return request.redirect('/loisirs')
        if not leisure.active:
            return request.redirect('/loisirs')
        
        # Loisirs similaires (même catégorie)
        similar_leisures = request.env['travel.leisure'].sudo().search([
            ('active', '=', True),
            ('category_id', '=', leisure.category_id.id),
            ('id', '!=', leisure.id)
        ], limit=4)
        
        return request.render('travel_agency.website_leisure_detail', {
            'leisure': leisure,
            'similar_leisures': similar_leisures,
        })

    # ============================================
    # NOUVELLES ROUTES - TRAVEL RENTAL (Locations de maison)
    # ============================================
    
    @http.route('/locations', type='http', auth='public', website=True)
    def rental_list(self, **kwargs):
        """
        Liste des locations de maison
        URL: /locations
        """
        domain = [('active', '=', True)]

        # Filtrage par localisation
        location = kwargs.get('location', '').strip()
        if location:
            domain.append(('location', 'ilike', location))

        # Recherche par nom ou description
        search = kwargs.get('search', '').strip()
        if search:
            domain += ['|',
                       ('name', 'ilike', search),
                       ('description', 'ilike', search)]

        # Filtrer par capacité minimum
        capacity_min = kwargs.get('capacity_min', '').strip()
        if capacity_min:
            try:
                domain.append(('capacity', '>=', int(capacity_min)))
            except ValueError:
                pass

        # Filtrer par nombre de chambres
        bedrooms = kwargs.get('bedrooms', '').strip()
        if bedrooms:
            try:
                domain.append(('bedrooms', '>=', int(bedrooms)))
            except ValueError:
                pass

        # Filtrer par prix max
        price_max = kwargs.get('price_max', '').strip()
        if price_max:
            try:
                domain.append(('price', '<=', float(price_max)))
            except ValueError:
                pass

        rentals = request.env['travel.rental'].sudo().search(domain)
        
        return request.render('travel_agency.website_rental_list', {
            'rentals': rentals,
            'filters': kwargs,
        })

    @http.route('/locations/<int:rental_id>', type='http', auth='public', website=True)
    def rental_detail(self, rental_id, **kwargs):
        """
        Détail d'une location de maison
        URL: /locations/1
        """
        rental = request.env['travel.rental'].sudo().browse(rental_id)
        if not rental.exists():
            return request.redirect('/locations')
        if not rental.active:
            return request.redirect('/locations')
        
        # Locations similaires (même localisation)
        similar_rentals = request.env['travel.rental'].sudo().search([
            ('active', '=', True),
            ('location', '=', rental.location),
            ('id', '!=', rental.id)
        ], limit=4)
        
        return request.render('travel_agency.website_rental_detail', {
            'rental': rental,
            'similar_rentals': similar_rentals,
        })

    # ============================================
    # ROUTES API (JSON) pour chargement asynchrone
    # ============================================
    
    @http.route('/api/guides', type='json', auth='public', methods=['GET'], website=True)
    def api_guides_list(self, **kwargs):
        """
        API JSON pour la liste des guides
        Utilisé pour le chargement asynchrone (AJAX)
        """
        guides = request.env['travel.guide'].sudo().search([('active', '=', True)])
        return {
            'status': 'success',
            'data': [{
                'id': guide.id,
                'name': guide.name,
                'description': guide.description,
                'price': guide.price,
                'image_url': guide.image_1920 and f'/web/image/{guide._name}/{guide.id}/image_1920' or None,
            } for guide in guides]
        }

    @http.route('/api/leisures', type='json', auth='public', methods=['GET'], website=True)
    def api_leisures_list(self, **kwargs):
        """
        API JSON pour la liste des loisirs
        """
        leisures = request.env['travel.leisure'].sudo().search([('active', '=', True)])
        return {
            'status': 'success',
            'data': [{
                'id': leisure.id,
                'name': leisure.name,
                'description': leisure.description,
                'price': leisure.price,
                'min_age': leisure.min_age,
                'image_url': leisure.image_1920 and f'/web/image/{leisure._name}/{leisure.id}/image_1920' or None,
            } for leisure in leisures]
        }

    @http.route('/api/rentals', type='json', auth='public', methods=['GET'], website=True)
    def api_rentals_list(self, **kwargs):
        """
        API JSON pour la liste des locations
        """
        rentals = request.env['travel.rental'].sudo().search([('active', '=', True)])
        return {
            'status': 'success',
            'data': [{
                'id': rental.id,
                'name': rental.name,
                'description': rental.description,
                'price': rental.price,
                'location': rental.location,
                'capacity': rental.capacity,
                'bedrooms': rental.bedrooms,
                'image_url': rental.image_1920 and f'/web/image/{rental._name}/{rental.id}/image_1920' or None,
            } for rental in rentals]
        }

    # ============================================
    # ROUTES DE RECHERCHE GLOBALE
    # ============================================
    
    @http.route('/recherche', type='http', auth='public', website=True)
    def global_search(self, **kwargs):
        """
        Recherche globale sur tous les services
        URL: /recherche?q=paris
        """
        query = kwargs.get('q', '').strip()
        results = {
            'guides': [],
            'leisures': [],
            'rentals': [],
            'hotels': [],
            'vols': [],
            'trains': [],
            'cars': [],
        }
        
        if query:
            # Recherche dans les guides
            results['guides'] = request.env['travel.guide'].sudo().search([
                ('active', '=', True),
                '|',
                ('name', 'ilike', query),
                ('description', 'ilike', query)
            ])
            
            # Recherche dans les loisirs
            results['leisures'] = request.env['travel.leisure'].sudo().search([
                ('active', '=', True),
                '|',
                ('name', 'ilike', query),
                ('description', 'ilike', query)
            ])
            
            # Recherche dans les locations
            results['rentals'] = request.env['travel.rental'].sudo().search([
                ('active', '=', True),
                '|',
                ('name', 'ilike', query),
                ('description', 'ilike', query),
                ('location', 'ilike', query)
            ])
            
            # Recherche dans les hôtels
            results['hotels'] = request.env['travel.hotel'].sudo().search([
                ('disponible', '=', True),
                '|',
                ('name', 'ilike', query),
                ('ville', 'ilike', query),
                ('pays', 'ilike', query)
            ])
            
            # Recherche dans les vols
            results['vols'] = request.env['travel.vol'].sudo().search([
                ('disponible', '=', True),
                '|',
                ('ville_arrivee', 'ilike', query),
                ('pays_arrivee', 'ilike', query)
            ])
            
            # Recherche dans les trains
            results['trains'] = request.env['travel.train'].sudo().search([
                ('disponible', '=', True),
                '|',
                ('ville_arrivee', 'ilike', query),
                ('pays_arrivee', 'ilike', query)
            ])
            
            # Recherche dans les voitures
            results['cars'] = request.env['travel.car'].sudo().search([
                ('disponible', '=', True),
                '|',
                ('ville_prise_en_charge', 'ilike', query),
                ('pays', 'ilike', query)
            ])
        
        return request.render('travel_agency.global_search_results', {
            'query': query,
            'results': results,
            'total_count': sum(len(results[key]) for key in results)
=======
        transaction = request.env['travel.payment.transaction'].sudo().create({
            'reservation_id': reservation.id,
            'provider_id': payment_provider_id,
            'state': 'pending',
            'first_name': client_firstname,
            'last_name': client_lastname,
            'email': client_email,
            'phone': client_phone,
        })

        return request.redirect('/travels/payment/%d' % transaction.id)
    
    
    @http.route('/recommandation', type='http', auth='public', website=True)
    def recommandation_form(self, **kwargs):
        return request.render('travel_agency.recommandation_form_page', {'error': False})

    @http.route('/recommandation/resultats', type='http', auth='public', website=True, methods=['POST'])
    def recommandation_resultats(self, **kwargs):
        budget_max = float(kwargs.get('budget_max', 0) or 0)
        nb_personnes = int(kwargs.get('nb_personnes', 1) or 1)
        etoiles_min = kwargs.get('etoiles_min') or None
        pays = kwargs.get('pays', '').strip() or None
        type_voyage = kwargs.get('type_voyage') or None

        engine = request.env['travel.recommendation.engine']
        recommendations = engine.get_recommendations(
            budget_max=budget_max,
            nb_personnes=nb_personnes,
            etoiles_min=etoiles_min,
            pays=pays,
            type_voyage=type_voyage,
        )
        return request.render('travel_agency.recommandation_results_page', {
            'recommendations': recommendations,
>>>>>>> ef5e29ef157ea4354f0c7d9cddede872353beb71
        })