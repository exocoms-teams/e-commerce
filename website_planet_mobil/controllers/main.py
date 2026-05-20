# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class WebsitePlanetMobil(http.Controller):

    @http.route(['/', '/accueil'], type='http', auth='public', website=True, sitemap=True)
    def homepage(self, **kwargs):
        top_ventes = request.env['planet.product'].sudo().search([('is_top_vente', '=', True)], limit=4)
        nouveautes = request.env['planet.product'].sudo().search([('is_nouveaute', '=', True)], limit=4)

        if not top_ventes:
            top_ventes = [
                {'name': 'iPhone 15 Pro Max', 'description': "Le smartphone le plus puissant d'Apple avec...", 'price': 1299, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/iphone15.jpg', 'badge': False},
                {'name': 'Samsung Galaxy S21 Ultra', 'description': 'Le flagship Android ultime avec S Pen intÃ©grÃ©', 'price': 1199, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/samsung_s21.jpg', 'badge': False},
                {'name': 'Apple Watch Series 9', 'description': 'Montre connectÃ©e avec Ã©cran toujours actif et...', 'price': 449, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/apple_watch.jpg', 'badge': False},
                {'name': 'Samsung Galaxy Watch 6', 'description': 'Suivi santÃ© avancÃ© et autonomie...', 'price': 399, 'rating': 4, 'image_url': '/website_planet_mobil/static/src/img/samsung_watch.jpg', 'badge': False},
            ]

        if not nouveautes:
            nouveautes = [
                {'name': 'Google Pixel 8 Pro', 'description': 'Intelligence artificielle au service de la...', 'price': 999, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/pixel8.jpg', 'badge': 'Nouveau'},
                {'name': 'OnePlus 12', 'description': 'Performance flagship Ã  prix accessible', 'price': 899, 'rating': 4, 'image_url': '/website_planet_mobil/static/src/img/oneplus12.jpg', 'badge': 'Nouveau'},
                {'name': 'Sony WH-1000XM5', 'description': 'Casque Ã  rÃ©duction de bruit active premium', 'price': 379, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/sony_wh.jpg', 'badge': 'Nouveau'},
                {'name': 'LG OLED C3 55"', 'description': 'TV OLED 4K 120Hz pour gaming et cinÃ©ma', 'price': 1599, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/lg_oled.jpg', 'badge': 'Nouveau'},
            ]

        return request.render('website_planet_mobil.homepage', {
            'top_ventes': top_ventes,
            'nouveautes': nouveautes,
        })


    @http.route('/avis', type='http', auth='public', website=True)
    def avis(self, **kwargs):
        avis_list = [
            {'initiales': 'ML', 'nom': 'Marie L.', 'date': '12 janvier 2026', 'note': 5, 'titre': 'Livraison ultra rapide !', 'commentaire': "Commande passÃ©e le soir, reÃ§ue le lendemain matin. Le produit est exactement comme dÃ©crit, je suis vraiment ravie de mon achat. Je recommande sans hÃ©siter !", 'produit': 'iPhone 15 Pro Max'},
            {'initiales': 'TK', 'nom': 'Thomas K.', 'date': '5 fÃ©vrier 2026', 'note': 5, 'titre': 'Excellent rapport qualitÃ©/prix', 'commentaire': "La montre est magnifique, les fonctionnalitÃ©s sont top. Le service client a Ã©tÃ© trÃ¨s rÃ©actif quand j'ai eu une question. TrÃ¨s bonne expÃ©rience d'achat.", 'produit': 'Apple Watch Series 9'},
            {'initiales': 'SB', 'nom': 'Sophie B.', 'date': '18 fÃ©vrier 2026', 'note': 4, 'titre': 'TrÃ¨s satisfaite de mon casque', 'commentaire': "La rÃ©duction de bruit est impressionnante, idÃ©al pour travailler en open space. Juste dommage que la livraison ait pris 2 jours de plus que prÃ©vu.", 'produit': 'Sony WH-1000XM5'},
            {'initiales': 'AD', 'nom': 'Alexandre D.', 'date': '2 mars 2026', 'note': 5, 'titre': 'Le meilleur smartphone Android', 'commentaire': "Photos Ã©poustouflantes, fluiditÃ© parfaite, autonomie excellente. Le S Pen est un vrai plus pour la productivitÃ©. Un achat que je ne regrette pas du tout !", 'produit': 'Samsung Galaxy S21 Ultra'},
            {'initiales': 'CM', 'nom': 'Clara M.', 'date': '15 mars 2026', 'note': 5, 'titre': 'TV incroyable pour le gaming', 'commentaire': "L'image OLED est Ã  couper le souffle, les noirs sont parfaits. Le mode gaming 120Hz fait vraiment la diffÃ©rence. Installation rapide et livraison soignÃ©e.", 'produit': 'LG OLED C3 55"'},
            {'initiales': 'JP', 'nom': 'Jean-Pierre V.', 'date': '28 mars 2026', 'note': 4, 'titre': 'Bon produit, site agrÃ©able', 'commentaire': "Le site est trÃ¨s bien conÃ§u, la navigation est intuitive. Le Pixel 8 Pro est excellent, l'IA intÃ©grÃ©e est vraiment utile au quotidien. Je reviendrai acheter !", 'produit': 'Google Pixel 8 Pro'},
        ]
        return request.render('website_planet_mobil.avis_page', {'avis_list': avis_list})

    @http.route('/contact', type='http', auth='public', website=True)
    def contact(self, **kwargs):
        return request.render('website_planet_mobil.contact_page', {})

    @http.route('/shop', type='http', auth='public', website=True)
    def shop(self, **kwargs):
        category = kwargs.get('category')  #retourne none si pas de parametre
        
        domain = []
        if category:
            domain = [('category', '=', category)]

        products = request.env['planet.product'].sudo().search(domain, limit=12)

        if not products:    #temporaire pour remplacer bd
            products = [
                {'id': 1, 'name': 'iPhone 15 Pro Max', 'description': "Le smartphone le plus puissant d'Apple", 'price': 1299, 'rating': 5, 'badge': 'Nouveau', 'image_url': '/website_planet_mobil/static/src/img/iphone15.jpg'},
                {'id': 2, 'name': 'Samsung Galaxy S21', 'description': 'Le flagship Android ultime', 'price': 1199, 'rating': 5, 'badge': False, 'image_url': '/website_planet_mobil/static/src/img/samsung_s21.jpg'},
                {'id': 3, 'name': 'Sony WH-1000XM5', 'description': 'Casque Ã  rÃ©duction de bruit', 'price': 379, 'rating': 4, 'badge': False, 'image_url': '/website_planet_mobil/static/src/img/sony_wh.jpg'},
                {'id': 4, 'name': 'Apple Watch Series 9', 'description': 'Montre connectÃ©e Apple', 'price': 449, 'rating': 5, 'badge': False, 'image_url': '/website_planet_mobil/static/src/img/apple_watch.jpg'},               
            ]

        brands = request.env['planet.product'].sudo().search([]).mapped('brand')
        brands = list(set(filter(None, brands)))

        colors = request.env['planet.product'].sudo().search([]).mapped('color')
        colors = list(set(filter(None, colors)))
        return request.render('website_planet_mobil.category_page', {
            'products': products, 
            'category': category,
            'brands' : brands,
            'colors': colors,
        })

    @http.route('/shop/product/<int:product_id>', type='http', auth='public', website=True)
    def product(self, product_id, **kwargs):
        product = request.env['planet.product'].sudo().search([('id', '=', product_id)], limit=1)

        if not product:
            #return request.not_found()     pour linstant pas de base, creer produits fictifs
            fake_products = {
                1:  {'id': 1, 'name': 'iPhone 15 Pro Max', 'description': "Le smartphone le plus puissant d'Apple", 'price': 1299, 'rating': 5, 'badge': 'Nouveau', 'image_url': '/website_planet_mobil/static/src/img/iphone15.jpg'},
                2:  {'id': 2, 'name': 'Samsung Galaxy S21', 'description': 'Le flagship Android ultime', 'price': 1199, 'rating': 5, 'badge': False, 'image_url': '/website_planet_mobil/static/src/img/samsung_s21.jpg'},
                3:  {'id': 3, 'name': 'Sony WH-1000XM5', 'description': 'Casque Ã  rÃ©duction de bruit', 'price': 379, 'rating': 4, 'badge': False, 'image_url': '/website_planet_mobil/static/src/img/sony_wh.jpg'},
                4:  {'id': 4, 'name': 'Apple Watch Series 9', 'description': 'Montre connectÃ©e Apple', 'price': 449, 'rating': 5, 'badge': False, 'image_url': '/website_planet_mobil/static/src/img/apple_watch.jpg'},  
            }
            product = fake_products.get(product_id, fake_products[1])
        return request.render('website_planet_mobil.product_page', {'product': product})

