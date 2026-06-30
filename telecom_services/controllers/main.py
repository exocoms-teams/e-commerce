from odoo import http
from odoo.http import request

_UI_STRINGS = {
    'fr_FR': {
        'page_title': 'Solutions Télécom',
        'page_subtitle': 'Voix, mobilité, connectivité, cloud et cybersécurité pour les professionnels.',
        'all_label': 'Tous',
        'order_label': 'Commander',
        'footer_note': '« Commander » redirige vers le portail de commande — aucun paiement sur exocoms.fr',
    },
    'en_US': {
        'page_title': 'Telecom Solutions',
        'page_subtitle': 'Voice, mobility, connectivity, cloud and cybersecurity for professionals.',
        'all_label': 'All',
        'order_label': 'Order',
        'footer_note': "'Order' redirects to the ordering portal — no payment on exocoms.fr",
    },
}

# Catalogue sections used both as filter chips and as card tags.
# (key, FR label, EN label)
_CATEGORIES = [
    ('voix', 'Voix', 'Voice'),
    ('mobile', 'Mobile', 'Mobile'),
    ('internet', 'Internet', 'Internet'),
    ('cloud', 'Cloud', 'Cloud'),
    ('securite', 'Sécurité', 'Security'),
]

# Curated KISSGROUP catalogue shown on /telecom.
_CATALOGUE = {
    'fr_FR': [
        {'cat': 'voix', 'icon': 'fa-phone', 'name': 'Centrex Wazo',
         'description': 'Téléphonie hébergée clé en main : infra, licences, trunk et communications incluses.'},
        {'cat': 'voix', 'icon': 'fa-phone-square', 'name': 'Trunk SIP',
         'description': 'Raccordez tout IPBX existant. Compatible Microsoft Teams, provisionné en live.'},
        {'cat': 'mobile', 'icon': 'fa-mobile', 'name': 'Mobile illimité',
         'description': 'Forfaits illimités sur les réseaux Orange et Bouygues. eSIM, VoLTE, VoWiFi.'},
        {'cat': 'mobile', 'icon': 'fa-wifi', 'name': 'Data Only',
         'description': 'SIM data pour routeurs 4G/5G, tablettes et objets connectés. IP publiques.'},
        {'cat': 'internet', 'icon': 'fa-sitemap', 'name': 'Liens Fibre',
         'description': 'Agrégation neutre de liens fibre, centralisés et pilotés à distance.'},
        {'cat': 'internet', 'icon': 'fa-server', 'name': 'KissBox secours',
         'description': 'Secours 4G illimité et Starlink via boîtiers Mikrotik.'},
        {'cat': 'cloud', 'icon': 'fa-cloud', 'name': 'Sauvegarde MS 365',
         'description': 'Backup facturé à l\'agent, sans limite de stockage, 1 an de rétention.'},
        {'cat': 'cloud', 'icon': 'fa-database', 'name': 'Stockage S3',
         'description': 'Stockage objet S3 hébergé en France, facturé au Go par mois.'},
        {'cat': 'securite', 'icon': 'fa-shield', 'name': 'Cybersécurité',
         'description': 'MPLS et pare-feu managés pour sécuriser l\'ensemble des sites.'},
    ],
    'en_US': [
        {'cat': 'voix', 'icon': 'fa-phone', 'name': 'Centrex Wazo',
         'description': 'Turnkey hosted telephony: infrastructure, licenses, trunk and calls included.'},
        {'cat': 'voix', 'icon': 'fa-phone-square', 'name': 'SIP Trunk',
         'description': 'Connect any existing IPBX. Microsoft Teams compatible, provisioned live.'},
        {'cat': 'mobile', 'icon': 'fa-mobile', 'name': 'Unlimited Mobile',
         'description': 'Unlimited plans on the Orange and Bouygues networks. eSIM, VoLTE, VoWiFi.'},
        {'cat': 'mobile', 'icon': 'fa-wifi', 'name': 'Data Only',
         'description': 'Data SIMs for 4G/5G routers, tablets and connected devices. Public IPs.'},
        {'cat': 'internet', 'icon': 'fa-sitemap', 'name': 'Fiber Links',
         'description': 'Neutral aggregation of fiber links, centralized and managed remotely.'},
        {'cat': 'internet', 'icon': 'fa-server', 'name': 'KissBox Backup',
         'description': '4G unlimited and Starlink failover via Mikrotik boxes.'},
        {'cat': 'cloud', 'icon': 'fa-cloud', 'name': 'MS 365 Backup',
         'description': 'Per-agent backup billing, unlimited storage, 1-year retention.'},
        {'cat': 'cloud', 'icon': 'fa-database', 'name': 'S3 Storage',
         'description': 'S3 object storage hosted in France, billed per GB per month.'},
        {'cat': 'securite', 'icon': 'fa-shield', 'name': 'Cybersecurity',
         'description': 'Managed MPLS and firewalls to secure all your sites.'},
    ],
}


class TelecomController(http.Controller):

    @http.route('/telecom', type='http', auth='public', website=True)
    def telecom_page(self, **kwargs):
        lang = request.env.context.get('lang', 'fr_FR')
        strings = _UI_STRINGS.get(lang, _UI_STRINGS['fr_FR'])
        is_fr = lang == 'fr_FR'

        cat_labels = {key: (fr if is_fr else en) for key, fr, en in _CATEGORIES}
        categories = [{'key': key, 'label': cat_labels[key]} for key, _fr, _en in _CATEGORIES]
        cards = [
            dict(card, cat_label=cat_labels.get(card['cat'], card['cat']))
            for card in _CATALOGUE.get(lang, _CATALOGUE['fr_FR'])
        ]

        order_url = request.env['ir.config_parameter'].sudo().get_param(
            'telecom_services.kissgroup_order_url') or '#'

        return request.render('telecom_services.telecom_page', {
            'categories': categories,
            'cards': cards,
            'order_url': order_url,
            **strings,
        })
