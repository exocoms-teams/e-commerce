from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.fields import Domain
from odoo.osv.expression import AND


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
            'client_email': client_email,
            'client_phone': client_phone,
            'client_adresse': client_adresse,
            'client_code_postal': client_code_postal,
            'client_pays': client_pays_id if client_pays_id else False,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'notes': notes,
            'destination_ids': destination_id if destination_id else False,
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