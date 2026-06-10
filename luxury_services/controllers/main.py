from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.fields import Domain
from odoo.osv.expression import AND
from odoo.addons.website.controllers.main import Website


class LuxuryController(WebsiteSale):


    def _get_vip_website(self):
        return request.env['website'].search(
            [('name', '=', 'VIP')], limit=1
        )

    def _is_vip_website(self):
        vip = self._get_vip_website()
        if not vip:
            return False
        return request.website.id == vip.id


    def _get_additional_shop_values(self, options):
        values = super()._get_additional_shop_values(options)
        
        if self._is_vip_website():
            destinations = request.env['luxury.destination'].sudo().search(
                [('active', '=', True)], 
                order='name asc'
            )
            values['destinations'] = destinations
        
        return values
        

    def _get_shop_domain(self, search, category, attribute_value_dict, search_in_description=True):
        domain = super()._get_shop_domain(
            search, category, attribute_value_dict, search_in_description
        )
        if not self._is_vip_website():
            return domain
        # En Odoo 19, reccuperer les params de GET
        params = request.httprequest.args
    
        extra_domains = []
    
        type_service = params.get('type_service', '')
        if type_service == 'location':
            extra_domains.append([('type_service', 'in', ['location', 'les_deux'])])
        elif type_service == 'vente':
            extra_domains.append([('type_service', 'in', ['vente', 'les_deux'])])
    
        longueur_min = params.get('longueur_min', '')
        longueur_max = params.get('longueur_max', '')
        if longueur_min:
            extra_domains.append([('longueur', '>=', float(longueur_min))])
        if longueur_max:
            extra_domains.append([('longueur', '<=', float(longueur_max))])
    
        capacite_min = params.get('capacite_min', '')
        if capacite_min:
            extra_domains.append([('capacite_personnes', '>=', int(capacite_min))])
    
        cabines_min = params.get('cabines_min', '')
        if cabines_min:
            extra_domains.append([('nb_cabines', '>=', int(cabines_min))])
    
        vitesse_min = params.get('vitesse_min', '')
        if vitesse_min:
            extra_domains.append([('vitesse_croisiere', '>=', float(vitesse_min))])
            
        destination = params.get('destination', '')
        if destination:
            extra_domains.append([('destination_ids', 'in', int(destination))])
    
        import logging
        _logger = logging.getLogger(__name__)
        _logger.warning("LUXURY PARAMS = %s", dict(params))
        _logger.warning("LUXURY EXTRA DOMAINS = %s", extra_domains)
    
        if extra_domains:
            return domain & Domain(AND(extra_domains))
    
        return domain


    def _shop_lookup_products(self, options, post, search, website):
        """Override pour appliquer les filtres luxury après la recherche"""
        fuzzy_search_term, product_count, search_result = super()._shop_lookup_products(
            options, post, search, website
        )


        if not self._is_vip_website():
            return fuzzy_search_term, product_count, search_result
            
        params = request.httprequest.args
    
        # Filtre type service
        type_service = params.get('type_service', '')
        if type_service == 'location':
            search_result = search_result.filtered(
                lambda p: p.type_service in ('location', 'les_deux')
            )
        elif type_service == 'vente':
            search_result = search_result.filtered(
                lambda p: p.type_service in ('vente', 'les_deux')
            )
    
        # Filtre longueur
        longueur_min = params.get('longueur_min', '')
        longueur_max = params.get('longueur_max', '')
        if longueur_min:
            search_result = search_result.filtered(
                lambda p: p.longueur >= float(longueur_min)
            )
        if longueur_max:
            search_result = search_result.filtered(
                lambda p: p.longueur <= float(longueur_max)
            )
    
        # Filtre capacité
        capacite_min = params.get('capacite_min', '')
        if capacite_min:
            search_result = search_result.filtered(
                lambda p: p.capacite_personnes >= int(capacite_min)
            )
    
        # Filtre cabines
        cabines_min = params.get('cabines_min', '')
        if cabines_min:
            search_result = search_result.filtered(
                lambda p: p.nb_cabines >= int(cabines_min)
            )
    
        # Filtre vitesse
        vitesse_min = params.get('vitesse_min', '')
        if vitesse_min:
            search_result = search_result.filtered(
                lambda p: p.vitesse_croisiere >= float(vitesse_min)
            )
        
        destination = params.get('destination', '')
        if destination:
            search_result = search_result.filtered(
                lambda p: int(destination) in p.destination_ids.ids
            )
    
        product_count = len(search_result)
        return fuzzy_search_term, product_count, search_result

    
    
    
    

    @http.route('/luxury/reserver/<int:product_id>',
                type='http',
                auth='public',
                website=True)
    def reservation_page(self, product_id, **kwargs):

        if not self._is_vip_website():
            return request.redirect('/')
            
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
            'destinations': product.destination_ids,
        })

    @http.route('/luxury/reserver/recap',
                type='http',
                auth='public',
                website=True,
                methods=['POST'])
    def reservation_recap(self, **kwargs):

        if not self._is_vip_website():
            return request.redirect('/')
        
        product_id = int(kwargs.get('product_id', 0))
        client_name = kwargs.get('client_name', '').strip()
        client_firstname = kwargs.get('client_firstname', '').strip()
        client_email = kwargs.get('client_email', '').strip()
        client_phone = kwargs.get('client_phone', '').strip()
        client_adresse = kwargs.get('client_adresse', '').strip()
        client_adresse_complement = kwargs.get('client_adresse_complement', '').strip()
        client_code_postal = kwargs.get('client_code_postal', '').strip()
        client_pays_id = int(kwargs.get('client_pays_id', 0))
        date_debut_str = kwargs.get('date_debut', '')
        date_fin_str = kwargs.get('date_fin', '')
        destination_id = int(kwargs.get('destination_id', 0))
        notes = kwargs.get('notes', '').strip()

        product = request.env['product.template'].sudo().browse(product_id)
        pays = request.env['res.country'].sudo().browse(client_pays_id)
        destination = request.env['luxury.destination'].sudo().browse(destination_id) if destination_id else None

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
                'destinations': product.destination_ids,
                'error': 'Ce produit n\'est pas disponible pour ces dates.',
            })

        prix_total = nb_jours * product.prix_location_jour

        return request.render('luxury_services.luxury_reservation_recap', {
            'product': product,
            'client_name': client_name,
            'client_firstname': client_firstname,
            'client_email': client_email,
            'client_phone': client_phone,
            'client_adresse': client_adresse,
            'client_code_postal': client_code_postal,
            'client_adresse_complement': client_adresse_complement,
            'client_pays': pays,
            'client_pays_id': client_pays_id,
            'date_debut': date_debut_str,
            'date_fin': date_fin_str,
            'nb_jours': nb_jours,
            'prix_total': prix_total,
            'notes': notes,
            'destinations': product.destination_ids,
            'destination': destination,
        })

    @http.route('/luxury/reserver/submit',
                type='http',
                auth='public',
                website=True,
                methods=['POST'])
    def reservation_submit(self, **kwargs):

        if not self._is_vip_website():
            return request.redirect('/')
        
        product_id = int(kwargs.get('product_id', 0))
        client_name = kwargs.get('client_name', '').strip()
        client_email = kwargs.get('client_email', '').strip()
        client_phone = kwargs.get('client_phone', '').strip()
        client_adresse = kwargs.get('client_adresse', '').strip()
        client_code_postal = kwargs.get('client_code_postal', '').strip()
        client_pays_id = int(kwargs.get('client_pays_id', 0))
        date_debut_str = kwargs.get('date_debut', '')
        date_fin_str = kwargs.get('date_fin', '')
        destination_id = int(kwargs.get('destination_id', 0))
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
            'client_firstname': client_firstname,
            'client_email': client_email,
            'client_phone': client_phone,
            'client_adresse': client_adresse,
            'client_adresse_complement': client_adresse_complement,
            'client_code_postal': client_code_postal,
            'client_pays': client_pays_id if client_pays_id else False,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'notes': notes,
            'destination_ids': [(4, destination_id)] if destination_id else False,
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

        if not self._is_vip_website():
            return request.redirect('/')
            
        reservation = request.env['luxury.reservation'].sudo().browse(reservation_id)

        if not reservation.exists():
            return request.redirect('/')
        if reservation.state != 'confirmed':
            return request.redirect('/')

        return request.render('luxury_services.luxury_paiement_page', {
            'reservation': reservation,
        })
        
        
        
    #url page maintenance
    @http.route(
        '/maintenance',
        type='http',
        auth='public',
        website=True
    )
    def maintenance_page(self, **kwargs):
        
        if not self._is_vip_website():
            return request.redirect('/shop')
        
        return request.render(
            'luxury_services.luxury_maintenance_page'
        )
        
        
    @http.route('/maintenance/submit',
            type='http',
            auth='public',
            website=True,
            methods=['POST'])
    def maintenance_submit(self, **kwargs):
        if not self._is_vip_website():
            return request.redirect('/shop')

        # Récupération des champs
        client_name = kwargs.get('client_name', '').strip()
        client_email = kwargs.get('client_email', '').strip()
        client_phone = kwargs.get('client_phone', '').strip()
        type_vehicule = kwargs.get('type_vehicule', '').strip()
        annee = kwargs.get('annee', '').strip()
        modele = kwargs.get('modele', '').strip()
        type_intervention = kwargs.get('type_intervention', '').strip()
        localisation = kwargs.get('localisation', '').strip()
        description = kwargs.get('description', '').strip()

        # Validation minimale
        if not client_name or not client_email or not modele:
            return request.render('luxury_services.luxury_maintenance_page', {
                'error': 'Veuillez remplir tous les champs obligatoires.',
            })

        # Création en base
        request.env['luxury.maintenance.request'].sudo().create({
            'client_name': client_name,
            'client_email': client_email,
            'client_phone': client_phone,
            'type_vehicule': type_vehicule or False,
            'annee': int(annee) if annee.isdigit() else False,
            'modele': modele,
            'type_intervention': type_intervention or False,
            'localisation': localisation,
            'description': description,
            'state': 'draft',
        })

        return request.render('luxury_services.luxury_maintenance_confirm', {
            'client_name': client_name,
            'client_email': client_email,
        })
        
        
        
    #pge à propos
    @http.route('/a-propos', type='http', auth='public', website=True)
    def about_page(self, **kwargs):
        if not self._is_vip_website():
            return request.redirect('/shop')
        return request.render('luxury_services.luxury_about_page', {})
    
    
    #page destination
    @http.route('/destinations', type='http', auth='public', website=True)
    def destinations_page(self, **kwargs):
        if not self._is_vip_website():
            return request.redirect('/shop')
        return request.render('luxury_services.luxury_destinations_page', {})
    
    
    
    #page concierge
    @http.route('/concierge', type='http', auth='public', website=True)
    def concierge_page(self, **kwargs):
        if not self._is_vip_website():
            return request.redirect('/shop')
        return request.render('luxury_services.luxury_concierge_page', {})


    @http.route('/concierge/submit', type='http', auth='public',
                website=True, methods=['POST'])
    def concierge_submit(self, **kwargs):
        if not self._is_vip_website():
            return request.redirect('/shop')

        request.env['luxury.concierge.request'].sudo().create({
            'client_name':    kwargs.get('client_name', '').strip(),
            'client_email':   kwargs.get('client_email', '').strip(),
            'client_phone':   kwargs.get('client_phone', '').strip(),
            'type_service':   kwargs.get('type_service', ''),
            'destination':    kwargs.get('destination', '').strip(),
            'date_souhaitee': kwargs.get('date_souhaitee') or False,
            'nb_personnes':   int(kwargs.get('nb_personnes') or 0) or False,
            'description':    kwargs.get('description', '').strip(),
            'budget':         kwargs.get('budget', ''),
            'state':          'draft',
        })

        return request.render('luxury_services.luxury_concierge_confirm', {
            'client_name': kwargs.get('client_name', '').strip(),
        })
        
        
    #page d'accueil
    @http.route('/', type='http', auth='public', website=True)
    def home_page(self, **kwargs):
        if not self._is_vip_website():
            
            return request.render('website.homepage', {})
        return request.render('luxury_services.luxury_home_page', {})
    
    
        """ =========================
            PUBLICATIONS D'ANNONCES
            ========================= 
        """
    @http.route('/vip/demande-annonce', type='http', auth='public', website=True)
    def listing_page(self, **kwargs):
        if not self._is_vip_website():
            return request.redirect('/shop')

        pays = request.env['res.country'].sudo().search([])
        return request.render('luxury_services.luxury_listing_page', {
            'pays_list': pays,
        })


    @http.route('/vip/demande-annonce/submit', type='http', auth='public',
                website=True, methods=['POST'])
    def listing_submit(self, **kwargs):
        if not self._is_vip_website():
            return request.redirect('/shop')

        pays = request.env['res.country'].sudo().search([])

        # Validation
        required = ['owner_name', 'owner_email', 'type_bien',
                    'bien_nom', 'type_service']
        for field in required:
            if not kwargs.get(field, '').strip():
                return request.render('luxury_services.luxury_listing_page', {
                    'pays_list': pays,
                    'error': 'Veuillez remplir tous les champs obligatoires.',
                })

        # Fichiers uploadés
        files = request.httprequest.files
        piece_identite = files.get('piece_identite')
        justif_propriete = files.get('justif_propriete')

        if not piece_identite or not piece_identite.filename:
            return request.render('luxury_services.luxury_listing_page', {
                'pays_list': pays,
                'error': 'La pièce d\'identité est obligatoire.',
            })

        if not justif_propriete or not justif_propriete.filename:
            return request.render('luxury_services.luxury_listing_page', {
                'pays_list': pays,
                'error': 'Le justificatif de propriété est obligatoire.',
            })

        # Lecture des fichiers
        import base64
        piece_identite_data = base64.b64encode(piece_identite.read())
        justif_propriete_data = base64.b64encode(justif_propriete.read())

        # Création de la demande
        vals = {
            'owner_name':               kwargs.get('owner_name', '').strip(),
            'owner_email':              kwargs.get('owner_email', '').strip(),
            'owner_phone':              kwargs.get('owner_phone', '').strip(),
            'owner_country_id':         int(kwargs.get('owner_country_id') or 0) or False,
            'owner_adresse':            kwargs.get('owner_adresse', '').strip(),
            'type_bien':                kwargs.get('type_bien'),
            'type_service':             kwargs.get('type_service'),
            'bien_nom':                 kwargs.get('bien_nom', '').strip(),
            'bien_description':         kwargs.get('bien_description', '').strip(),
            'bien_annee':               int(kwargs.get('bien_annee') or 0) or False,
            'bien_prix_location':       float(kwargs.get('bien_prix_location') or 0),
            'bien_prix_vente':          float(kwargs.get('bien_prix_vente') or 0),
            'piece_identite':           piece_identite_data,
            'piece_identite_filename':  piece_identite.filename,
            'justif_propriete':         justif_propriete_data,
            'justif_propriete_filename': justif_propriete.filename,
            'state':                    'draft',
        }

        # Champs spécifiques par type
        type_bien = kwargs.get('type_bien')
        if type_bien == 'yacht':
            vals.update({
                'longueur':           float(kwargs.get('longueur') or 0),
                'capacite_personnes': int(kwargs.get('capacite_personnes') or 0),
                'nb_cabines':         int(kwargs.get('nb_cabines') or 0),
                'vitesse_croisiere':  float(kwargs.get('vitesse_croisiere') or 0),
                'pavillon':           kwargs.get('pavillon', '').strip(),
                'pays_disponibilite_id': int(kwargs.get('pays_disponibilite_id') or 0) or False,
                'ville_disponibilite':   kwargs.get('ville_disponibilite', '').strip(),
                'zone_navigation':       kwargs.get('zone_navigation', '').strip(),
                'adresse_disponibilite': kwargs.get('adresse_disponibilite', '').strip(),
                'disponible_des':        kwargs.get('disponible_des') or False,
            })
        elif type_bien == 'jet':
            vals.update({
                'constructeur_jet': kwargs.get('constructeur_jet', '').strip(),
                'autonomie_vol':    float(kwargs.get('autonomie_vol') or 0),
                'vitesse_max':      float(kwargs.get('vitesse_max') or 0),
                'nombre_moteurs':   int(kwargs.get('nombre_moteurs') or 0),
                'altitude_max':     float(kwargs.get('altitude_max') or 0),
                'equipage':         int(kwargs.get('equipage') or 0),
                'pays_disponibilite_id': int(kwargs.get('pays_disponibilite_id') or 0) or False,
                'ville_disponibilite':   kwargs.get('ville_disponibilite', '').strip(),
                'zone_navigation':       kwargs.get('zone_navigation', '').strip(),
                'adresse_disponibilite': kwargs.get('adresse_disponibilite', '').strip(),
                'disponible_des':        kwargs.get('disponible_des') or False,
                        })
        elif type_bien == 'hotel':
            vals.update({
                'nb_chambres': int(kwargs.get('nb_chambres') or 0),
                'superficie':  float(kwargs.get('superficie') or 0),
                'localisation': kwargs.get('localisation', '').strip(),
                'equipements': kwargs.get('equipements', '').strip(),
            })
        elif type_bien == 'voiture':
            vals.update({
                'marque':          kwargs.get('marque', '').strip(),
                'modele_voiture':  kwargs.get('modele_voiture', '').strip(),
                'kilometrage':     int(kwargs.get('kilometrage') or 0),
                'couleur':         kwargs.get('couleur', '').strip(),
                'pays_disponibilite_id': int(kwargs.get('pays_disponibilite_id') or 0) or False,
                'ville_disponibilite':   kwargs.get('ville_disponibilite', '').strip(),
                'zone_navigation':       kwargs.get('zone_navigation', '').strip(),
                'adresse_disponibilite': kwargs.get('adresse_disponibilite', '').strip(),
                'disponible_des':        kwargs.get('disponible_des') or False,
            })

        listing = request.env['luxury.listing.request'].sudo().create(vals)

        # Photos multiples
        photos = files.getlist('photos_bien')
        if photos:
            attachments = []
            for photo in photos:
                if photo and photo.filename:
                    photo_data = base64.b64encode(photo.read())
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name':      photo.filename,
                        'datas':     photo_data,
                        'res_model': 'luxury.listing.request',
                        'res_id':    listing.id,
                    })
                    attachments.append(attachment.id)
            if attachments:
                listing.write({'photos_bien': [(6, 0, attachments)]})

        return request.render('luxury_services.luxury_listing_confirm', {
            'owner_name': listing.owner_name,
            'owner_email': listing.owner_email,
            'reference':  listing.name,
        })
    
    
    
    #url vip annonce client
    @http.route('/vip/annonces', type='http', auth='public', website=True)
    def listings_page(self, **kwargs):
        if not self._is_vip_website():
            return request.redirect('/shop')

        # Filtres
        type_bien    = kwargs.get('type_bien', '')
        type_service = kwargs.get('type_service', '')
        pays         = kwargs.get('pays', '')
        prix_max     = kwargs.get('prix_max', '')
        search       = kwargs.get('search', '')
        sort         = kwargs.get('sort', 'recent')

        # Domaine de base — uniquement les annonces publiées
        domain = [('state', '=', 'published')]

        if type_bien:
            domain.append(('type_bien', '=', type_bien))
        if type_service:
            domain.append(('type_service', 'in', [type_service, 'les_deux']))
        if pays:
            domain.append(('pays_disponibilite_id', '=', int(pays)))
        if prix_max:
            domain.append(('bien_prix_location', '<=', float(prix_max)))
        if search:
            domain.append(('bien_nom', 'ilike', search))

        # Tri
        order_map = {
            'recent':    'create_date desc',
            'prix_asc':  'bien_prix_location asc',
            'prix_desc': 'bien_prix_location desc',
        }
        order = order_map.get(sort, 'create_date desc')

        listings = request.env['luxury.listing.request'].sudo().search(
            domain, order=order
        )
        pays_list = request.env['res.country'].sudo().search([])

        return request.render('luxury_services.luxury_listings_page', {
            'listings':  listings,
            'pays_list': pays_list,
            'filters':   kwargs,
        })
        
        
    """
        =========================
        prise de contact annonce
        =========================
    """
    
    @http.route('/vip/annonces/<int:listing_id>',
            type='http', auth='public', website=True)
    def listing_detail(self, listing_id, **kwargs):
        if not self._is_vip_website():
            return request.redirect('/shop')

        listing = request.env['luxury.listing.request'].sudo().browse(listing_id)

        if not listing.exists() or listing.state != 'published':
            return request.redirect('/vip/annonces')

        # Annonces similaires — même type, exclure l'annonce courante
        similar = request.env['luxury.listing.request'].sudo().search([
            ('state', '=', 'published'),
            ('type_bien', '=', listing.type_bien),
            ('id', '!=', listing_id),
        ], limit=3)

        return request.render('luxury_services.luxury_listing_detail', {
            'listing': listing,
            'similar_listings': similar,
        })


    @http.route('/vip/annonces/contact',
                type='http', auth='public', website=True, methods=['POST'])
    def listing_contact(self, **kwargs):
        if not self._is_vip_website():
            return request.redirect('/shop')

        listing_id  = int(kwargs.get('listing_id', 0))
        contact_name    = kwargs.get('contact_name', '').strip()
        contact_email   = kwargs.get('contact_email', '').strip()
        contact_phone   = kwargs.get('contact_phone', '').strip()
        contact_message = kwargs.get('contact_message', '').strip()

        listing = request.env['luxury.listing.request'].sudo().browse(listing_id)

        if listing.exists():
            # Envoyer un email au propriétaire via le chatter
            listing.sudo().message_post(
                body=f"""
                    <p><strong>Nouveau message de :</strong> {contact_name} ({contact_email})</p>
                    <p><strong>Téléphone :</strong> {contact_phone or 'Non renseigné'}</p>
                    <p><strong>Message :</strong></p>
                    <p>{contact_message}</p>
                """,
                subject=f"Demande de contact — {listing.bien_nom}",
                message_type='comment',
            )

        return request.render('luxury_services.luxury_listing_contact_confirm', {
            'listing': listing,
            'contact_name': contact_name,
        })
    """ https://www.youtube.com/watch?v=bF-01uyDXUc"""