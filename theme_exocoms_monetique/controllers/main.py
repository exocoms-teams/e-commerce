# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class MonetiqueContractController(http.Controller):

    @http.route(['/contrat'], type='http', auth="public", website=True)
    def contrat_page(self, **post):
        return request.render("theme_exocoms_monetique.contrat_page_template", {
            'callback_success': post.get('callback_success')
        })

    @http.route(['/contrat/callback'], type='http', auth="public", methods=['POST'], website=True, csrf=True)
    def contrat_callback(self, **post):
        name = post.get('name')
        phone = post.get('phone')
        email = post.get('email')
        company = post.get('company')
        contract_type = post.get('contract_type')

        description = f"Demande de rappel pour Contrat Monétique.\nType de contrat souhaité : {contract_type}\nEntreprise : {company}\nTéléphone : {phone}"

        try:
            Lead = request.env['crm.lead'].sudo()
            if Lead:
                Lead.create({
                    'name': f"Rappel Monétique - {name} ({company or 'Individuel'})",
                    'partner_name': company,
                    'contact_name': name,
                    'phone': phone,
                    'email_from': email,
                    'description': description,
                })
                _logger.info("CRM Lead created successfully via web-callback.")
        except Exception as e:
            _logger.warning(f"Could not create CRM Lead (might be because crm module is not installed): {e}")

        return request.redirect('/contrat?callback_success=1')

    @http.route(['/landing/<string:slug>'], type='http', auth="public", website=True)
    def seo_landing_page(self, slug, **post):
        # Dictionary containing content for the 10 SEO pages
        landings = {
            'terminal-paiement-android': {
                'title': 'Terminal de paiement Android - Monetiques.fr',
                'h1': 'Les Terminaux de Paiement Android de dernière génération',
                'meta_desc': 'Découvrez nos TPE Android tactiles intelligents. Intégrez vos applications métiers et modernisez votre encaissement avec EXOCOMS.',
                'content': 'Le terminal de paiement Android représente une révolution pour le commerce physique. Grâce à un écran tactile intuitif et la possibilité d\'installer des applications de gestion ou de fidélité, il devient un véritable outil de point de vente portable. Les modèles comme le Pax A920 Pro combinent sécurité bancaire et flexibilité technologique.',
                'faq_q': 'Pourquoi choisir un TPE sous Android ?',
                'faq_a': 'Il permet d\'allier l\'encaissement par carte et l\'exécution de vos applications métiers (gestion des stocks, commandes, fidélité) directement sur le même écran tactile.'
            },
            'tpe-restaurant': {
                'title': 'TPE pour Restaurant - Monetiques.fr',
                'h1': 'Solutions d\'encaissement idéales pour la Restauration',
                'meta_desc': 'Optez pour des TPE mobiles et rapides adaptés aux restaurants, bars et cafés. Partage des additions et pourboires facilités.',
                'content': 'Dans la restauration, la rapidité au moment du paiement est cruciale. Nos TPE mobiles 4G et Wifi permettent un encaissement à table ultra-fluide. Ils gèrent nativement les fonctionnalités spécifiques comme le partage d\'addition ou la saisie simplifiée des pourboires pour vos serveurs.',
                'faq_q': 'Le TPE gère-t-il les titres restaurant ?',
                'faq_a': 'Oui, tous nos terminaux acceptent les cartes Titres Restaurant de deuxième génération (Conecs) ainsi que les paiements sans contact classiques.'
            },
            'tpe-pharmacie': {
                'title': 'TPE pour Pharmacie - Monetiques.fr',
                'h1': 'Terminaux Bancaires certifiés pour Officines et Pharmacies',
                'meta_desc': 'Des terminaux de paiement sécurisés et rapides pour les pharmaciens. Intégration SESAM-Vitale et logiciels de santé.',
                'content': 'La gestion d\'une officine requiert une sécurité de premier plan et une intégration parfaite avec le système de santé. Nos terminaux sont compatibles avec les lecteurs de cartes SESAM-Vitale pour un traitement simultané des dossiers de soins et des paiements bancaires.',
                'faq_q': 'Est-il possible de connecter le TPE au logiciel de caisse de la pharmacie ?',
                'faq_a': 'Oui, via les protocoles standards de liaison caisse (comme le protocole Concert), assurant une transmission automatique des montants.'
            },
            'tpe-mobile': {
                'title': 'TPE Mobile 4G & Wifi - Monetiques.fr',
                'h1': 'Terminaux de Paiement Mobiles pour les professionnels en déplacement',
                'meta_desc': 'Restez mobile avec nos terminaux 4G/Wifi. Parfait pour les livraisons, marchés, artisans et professions libérales.',
                'content': 'Que vous soyez artisan, livreur ou gérant d\'un food truck, vous devez pouvoir encaisser partout. Nos solutions mobiles disposent d\'une batterie longue durée et d\'une carte SIM multi-opérateur intégrée pour capter le meilleur réseau 4G.',
                'faq_q': 'La carte SIM 4G est-elle incluse ?',
                'faq_a': 'Oui, une carte SIM multi-opérateur est installée d\'office dans nos modèles mobiles, sans surcoût dans le cadre de nos contrats.'
            },
            'terminal-bancaire': {
                'title': 'Terminal Bancaire Professionnel - Monetiques.fr',
                'h1': 'Votre Terminal Bancaire sécurisé au meilleur tarif',
                'meta_desc': 'Achat et location de terminaux bancaires Ingenico, Pax et Verifone. Matériel certifié conforme aux normes bancaires.',
                'content': 'Monetiques.fr vous accompagne dans le choix de votre terminal bancaire. Nous proposons à l\'achat des modèles neufs ou reconditionnés parmi les leaders du marché mondial comme Ingenico ou Pax Technology, garantissant une compatibilité universelle.',
                'faq_q': 'Le matériel est-il garanti ?',
                'faq_a': 'Tous nos terminaux bénéficient d\'une garantie constructeur de 12 à 24 mois, extensible avec nos contrats de maintenance.'
            },
            'monetique-commerce': {
                'title': 'Monétique pour Commerce - Monetiques.fr',
                'h1': 'Solutions Monétiques complètes pour commerces physiques',
                'meta_desc': 'Optimisez vos ventes en magasin avec des solutions monétiques performantes. Intégration caisse, sans contact rapide.',
                'content': 'Pour les commerces de détail, chaque seconde compte. Nous concevons des environnements d\'encaissement fluides grâce à une liaison rapide entre votre logiciel de caisse et votre lecteur de cartes bancaires.',
                'faq_q': 'Proposez-vous des solutions d\'encaissement rapide ?',
                'faq_a': 'Oui, nos terminaux fixes connectés en Ethernet effectuent l\'autorisation bancaire et l\'impression du ticket en moins de 3 secondes.'
            },
            'solutions-paiement': {
                'title': 'Solutions de Paiement B2B - Monetiques.fr',
                'h1': 'Des solutions de paiement omnicanales pour les entreprises',
                'meta_desc': 'Centralisez vos encaissements physiques et en ligne. Découvrez nos passerelles de paiement sécurisées pour e-commerce et boutiques.',
                'content': 'EXOCOMS propose à travers Monetiques.fr des solutions globales unifiant le paiement physique sur point de vente et le paiement en ligne (e-commerce). Simplifiez votre comptabilité avec un tableau de bord unique.',
                'faq_q': 'Puis-je centraliser mes encaissements ?',
                'faq_a': 'Oui, via notre portail client, vous pouvez suivre les flux de vos TPE physiques et de votre boutique e-commerce.'
            },
            'paiement-sans-contact': {
                'title': 'Paiement Sans Contact - Monetiques.fr',
                'h1': 'Terminaux optimisés pour le Paiement Sans Contact',
                'meta_desc': 'Accélérez le passage en caisse. TPE compatibles NFC, Apple Pay, Google Pay et nouvelles cartes bancaires.',
                'content': 'Le paiement sans contact est devenu le mode d\'encaissement favori des Français. Tous nos lecteurs intègrent la technologie NFC permettant d\'accepter instantanément les cartes et les smartphones (Apple Pay, Google Pay).',
                'faq_q': 'Quelle est la limite du paiement sans contact ?',
                'faq_a': 'La limite par carte sans saisie du code PIN est de 50€ en France. Il n\'y a pas de limite technique spécifique pour les paiements sur smartphone via biométrie.'
            },
            'pin-pad': {
                'title': 'Lecteurs PIN Pad clients - Monetiques.fr',
                'h1': 'Lecteurs de cartes PIN Pad déportés pour comptoirs',
                'meta_desc': 'Facilitez la saisie du code par vos clients. PIN Pad compacts et sécurisés pour terminaux Ingenico et Pax.',
                'content': 'Le PIN Pad déporté évite d\'avoir à manipuler ou déplacer le terminal principal. Placé face au client, il assure la discrétion de la saisie du code secret tout en proposant la lecture sans contact sur un appareil compact.',
                'faq_q': 'Le PIN Pad est-il autonome ?',
                'faq_a': 'Non, le PIN Pad se connecte par câble au terminal de paiement principal qui gère l\'intelligence de la transaction.'
            },
            'caisse-connectee': {
                'title': 'Caisse Connectée & TPE - Monetiques.fr',
                'h1': 'Solutions de Caisse Connectée pour commerce de détail',
                'meta_desc': 'Synchronisez votre TPE et votre système d\'encaissement pour supprimer les erreurs de saisie. Liaison caisse sécurisée.',
                'content': 'Relier votre caisse enregistreuse à votre TPE est la meilleure garantie pour éliminer les erreurs humaines lors de la saisie du montant de la vente. Le montant saisi sur la caisse est envoyé automatiquement vers le lecteur.',
                'faq_q': 'Comment se fait la connexion caisse-TPE ?',
                'faq_a': 'Elle se fait généralement via un câble USB, une liaison série RS232, ou directement en réseau local via Wifi/Ethernet selon vos équipements.'
            }
        }

        landing_data = landings.get(slug)
        if not landing_data:
            return request.render("website.404")

        return request.render("theme_exocoms_monetique.seo_landing_template", {
            'seo_data': landing_data
        })

