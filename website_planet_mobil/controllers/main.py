# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import json

FAKE_PRODUCTS = {
    1: {'id': 1, 'name': 'iPhone 15 Pro Max', 'category': 'Smartphones', 'description': "Le smartphone le plus puissant d'Apple avec...", 'price': 1299, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/iphone15.jpg', 'badge': False, 'is_top_vente': True, 'is_nouveaute': False, 'is_promotion': True, 'ean': '0194253408222', 'specs': {
        'Processeur': 'Apple A17 Pro',
        'Mémoire': '256 GB',
        'Écran': '6.7" Super Retina XDR',
        'Résolution': '2796 x 1290 pixels',
        'Appareil photo': '48 MP + 12 MP + 12 MP',
        'Batterie': '4422 mAh',
        'Système': 'iOS 17',
        'Connectivité': '5G, WiFi 6E, Bluetooth 5.3',
        'Dimensions': '159.9 x 76.7 x 8.25 mm',
        'Poids': '221 g',
    }},
    2: {'id': 2, 'name': 'Samsung Galaxy S21 Ultra', 'category': 'Smartphones', 'description': 'Le flagship Android ultime avec S Pen intégré', 'price': 1199, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/samsung_s21.jpg', 'badge': False, 'is_top_vente': True, 'is_nouveaute': False, 'is_promotion': False, 'ean': '8806090945182', 'specs': {
        'Processeur': 'Exynos 2100',
        'Mémoire': '256 GB',
        'RAM': '12 GB',
        'Écran': '6.8" Dynamic AMOLED',
        'Résolution': '3200 x 1440 pixels',
        'Appareil photo': '108 MP + 12 MP + 10 MP + 10 MP',
        'Batterie': '5000 mAh',
        'Système': 'Android 11',
        'Connectivité': '5G, WiFi 6, Bluetooth 5.0',
        'Dimensions': '165.1 x 75.6 x 8.9 mm',
        'Poids': '227 g',
    }},
    3: {'id': 3, 'name': 'Apple Watch Series 9', 'category': 'Montres', 'description': 'Montre connectée avec écran toujours actif et...', 'price': 449, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/apple_watch.jpg', 'badge': False, 'is_top_vente': True, 'is_nouveaute': False, 'is_promotion': False, 'ean': '0194253966509', 'specs': {
        'Processeur': 'Apple S9',
        'Écran': 'LTPO OLED 45mm',
        'Résolution': '484 x 396 pixels',
        'Autonomie': "18 heures",
        'Étanchéité': '50 mètres',
        'Capteurs': 'Cardiaque, SpO2, Température',
        'Connectivité': 'WiFi, Bluetooth 5.3, NFC',
        'Compatibilité': 'iPhone XS ou ultérieur',
        'Dimensions': '45 x 38 x 10.7 mm',
        'Poids': '38.7 g',
    }},
    4: {'id': 4, 'name': 'Samsung Galaxy Watch 6', 'category': 'Montres', 'description': 'Suivi santé avancé et autonomie...', 'price': 399, 'rating': 4, 'image_url': '/website_planet_mobil/static/src/img/samsung_watch.jpg', 'badge': False, 'is_top_vente': True, 'is_nouveaute': False, 'is_promotion': True, 'ean': '8806094955627', 'specs': {
        'Processeur': 'Exynos W930',
        'Écran': 'Super AMOLED 44mm',
        'Résolution': '480 x 480 pixels',
        'Autonomie': '40 heures',
        'Étanchéité': '50 mètres',
        'Capteurs': 'Cardiaque, SpO2, Température, ECG',
        'Connectivité': 'WiFi, Bluetooth 5.3, NFC',
        'Compatibilité': 'Android 10 ou ultérieur',
        'Dimensions': '44 x 44 x 9 mm',
        'Poids': '33 g',
    }},
    5: {'id': 5, 'name': 'Google Pixel 8 Pro', 'category': 'Smartphones', 'description': 'Intelligence artificielle au service de la...', 'price': 999, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/pixel8.jpg', 'badge': 'Nouveau', 'is_top_vente': False, 'is_nouveaute': True, 'is_promotion': False, 'ean': '0840244700448', 'specs': {
        'Processeur': 'Google Tensor G3',
        'Mémoire': '128 GB',
        'RAM': '12 GB',
        'Écran': '6.7" LTPO OLED',
        'Résolution': '2992 x 1344 pixels',
        'Appareil photo': '50 MP + 48 MP + 48 MP',
        'Batterie': '5050 mAh',
        'Système': 'Android 14',
        'Connectivité': '5G, WiFi 7, Bluetooth 5.3',
        'Dimensions': '162.6 x 76.5 x 8.8 mm',
        'Poids': '213 g',
    }},
    6: {'id': 6, 'name': 'OnePlus 12', 'category': 'Smartphones', 'description': 'Performance flagship à prix accessible', 'price': 899, 'rating': 4, 'image_url': '/website_planet_mobil/static/src/img/oneplus12.jpg', 'badge': 'Nouveau', 'is_top_vente': False, 'is_nouveaute': True, 'is_promotion': False, 'ean': '6921815624073', 'specs': {
        'Processeur': 'Snapdragon 8 Gen 3',
        'Mémoire': '256 GB',
        'RAM': '12 GB',
        'Écran': '6.82" LTPO AMOLED',
        'Résolution': '3168 x 1440 pixels',
        'Appareil photo': '50 MP + 64 MP + 48 MP',
        'Batterie': '5400 mAh',
        'Système': 'Android 14',
        'Connectivité': '5G, WiFi 7, Bluetooth 5.4',
        'Dimensions': '164.3 x 75.8 x 9.15 mm',
        'Poids': '220 g',
    }},
    7: {'id': 7, 'name': 'Sony WH-1000XM5', 'category': 'Accessoires', 'description': 'Casque à réduction de bruit active premium', 'price': 379, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/sony_wh.jpg', 'badge': 'Nouveau', 'is_top_vente': False, 'is_nouveaute': True, 'is_promotion': True, 'ean': '4548736132504', 'specs': {
        'Type': 'Casque supra-auriculaire',
        'Réduction de bruit': 'Active (ANC)',
        'Autonomie': '30 heures',
        'Charge rapide': '3 min = 3 heures',
        'Connectivité': 'Bluetooth 5.2, Jack 3.5mm',
        'Codecs': 'LDAC, AAC, SBC',
        'Microphones': '8 microphones',
        'Poids': '250 g',
        'Couleurs disponibles': 'Noir, Blanc',
    }},
    8: {'id': 8, 'name': 'LG OLED C3 55"', 'category': 'Televisions', 'description': 'TV OLED 4K 120Hz pour gaming et cinéma', 'price': 1599, 'rating': 5, 'image_url': '/website_planet_mobil/static/src/img/lg_oled.jpg', 'badge': 'Nouveau', 'is_top_vente': False, 'is_nouveaute': True, 'is_promotion': False, 'ean': '8806084076756', 'specs': {
        'Taille': '55 pouces',
        'Technologie': 'OLED evo',
        'Résolution': '4K UHD 3840 x 2160',
        'Taux de rafraîchissement': '120 Hz',
        'HDR': 'Dolby Vision, HDR10, HLG',
        'Processeur': 'α9 Gen6 AI',
        'Son': 'Dolby Atmos 60W',
        'Smart TV': 'webOS 23',
        'Ports': '4x HDMI 2.1, 3x USB',
        'Dimensions': '1228 x 708 x 46 mm',
    }},
}

class WebsitePlanetMobil(WebsiteSale):  #herite du websitesale

    def _get_products_with_price(self, products):
        result = []
        for product in products:
            list_price = product.list_price
            # Cherche une règle de remise sur ce produit dans n'importe quelle pricelist
            rule = request.env['product.pricelist.item'].sudo().search([
                ('product_tmpl_id', '=', product.id),
                ('compute_price', '=', 'discount'),
            ], limit=1)
            if rule:
                promo_price = list_price * (1 - rule.price_discount / 100)
            else:
                promo_price = None
            result.append({
                'product': product,
                'list_price': list_price,
                'promo_price': promo_price,
            })
        return result

    @http.route(['/', '/accueil'], type='http', auth='public', website=True, sitemap=True)
    def homepage(self, **kwargs):
        use_fake = not bool(request.env['product.template'].sudo().search(
            [('is_published', '=', True)], limit=1
        ))

        if use_fake:
            top_ventes = [p for p in FAKE_PRODUCTS.values() if p['is_top_vente']]
            nouveautes = [p for p in FAKE_PRODUCTS.values() if p['is_nouveaute']]
        else:
            tv = request.env['product.template'].sudo().search(
                [('x_is_top_vente', '=', True), ('is_published', '=', True)], limit=4)
            nv = request.env['product.template'].sudo().search(
                [('x_is_nouveaute', '=', True), ('is_published', '=', True)], limit=4)
            top_ventes = self._get_products_with_price(tv)
            nouveautes = self._get_products_with_price(nv)

        return request.render('website_planet_mobil.homepage', {
            'top_ventes': top_ventes,
            'nouveautes': nouveautes,
            'use_fake': use_fake,
        })

    @http.route('/catalogue', type='http', auth='public', website=True, sitemap=True)
    def catalogue(self, category=None, **kwargs):
        all_products = request.env['product.template'].sudo().search([])
        brands = sorted(set(filter(None, all_products.mapped('x_brand'))))
        colors = sorted(set(filter(None, all_products.mapped('color'))))
        if not brands:
            brands = ['Apple', 'Samsung', 'Sony', 'LG', 'Google', 'OnePlus']
        if not colors:
            colors = ['Noir', 'Blanc', 'Bleu', 'Rouge', 'Rose', 'Or']

        domain = [('is_published', '=', True)]
        if category == 'Nouveautes':
            domain.append(('x_is_nouveaute', '=', True))
        elif category == 'Promotions':
            domain.append(('x_is_promotion', '=', True))
        elif category:
            domain.append(('public_categ_ids.name', '=', category))

        use_fake = not bool(request.env['product.template'].sudo().search(
            [('is_published', '=', True)], limit=1
        ))

        if use_fake:
            fake = list(FAKE_PRODUCTS.values())
            if category == 'Nouveautes':
                fake = [p for p in fake if p['is_nouveaute']]
            elif category == 'Promotions':
                fake = [p for p in fake if p.get('is_promotion')]
            elif category:
                fake = [p for p in fake if p.get('category') == category]
            products = fake
        else:
            raw_products = request.env['product.template'].sudo().search(domain, limit=20)
            products = self._get_products_with_price(raw_products)

        return request.render('website_planet_mobil.category_page', {
            'products': products,
            'category': category,
            'brands': brands,
            'colors': colors,
            'use_fake': use_fake,
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

    
    #@http.route('/shop/product/<int:product_id>', type='http', auth='public', website=True)
    #def product(self, product_id, **kwargs):
    #    product = request.env['product.template'].sudo().search([('id', '=', product_id)], limit=1)

    #    if not product:
            #return request.not_found()     pour linstant pas de base, creer produits fictifs
    #        product =  FAKE_PRODUCTS.get(product_id, FAKE_PRODUCTS[1])

    #    if isinstance(product, dict):
    #        specs = product.get('specs', {})
    #    else:
    #        specs = json.loads(product.x_specs) if product.x_specs else {}

    #    return request.render('website_planet_mobil.product_page', {
    #        'product': product,
    #        'specs': specs,
    #    })

