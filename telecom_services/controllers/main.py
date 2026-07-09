from odoo import http
from odoo.http import request

from .catalogue_data import CATEGORIES, ORDER, PRODUCTS

_UI_STRINGS = {
    'fr_FR': {
        'page_title': 'Solutions Télécom',
        'page_subtitle': 'Voix, mobilité, connectivité, cloud et cybersécurité pour les professionnels.',
        'all_label': 'Tous',
        'order_label': 'Commander',
        'discover_label': 'Découvrir',
        'back_label': 'Retour au catalogue',
        'benefits_title': 'Pourquoi choisir cette offre',
        'faq_title': 'Questions fréquentes',
        'related_title': 'Dans la même catégorie',
        'cta_title': 'Prêt à commander ?',
        'cta_text': 'La commande se fait directement sur le portail KISSGROUP, en toute sécurité.',
        'footer_note': '« Commander » redirige vers le portail de commande — aucun paiement sur exocoms.fr',
    },
    'en_US': {
        'page_title': 'Telecom Solutions',
        'page_subtitle': 'Voice, mobility, connectivity, cloud and cybersecurity for professionals.',
        'all_label': 'All',
        'order_label': 'Order',
        'discover_label': 'Discover',
        'back_label': 'Back to catalogue',
        'benefits_title': 'Why choose this offer',
        'faq_title': 'Frequently asked questions',
        'related_title': 'In the same category',
        'cta_title': 'Ready to order?',
        'cta_text': 'Ordering is done directly on the KISSGROUP portal, securely.',
        'footer_note': "'Order' redirects to the ordering portal — no payment on exocoms.fr",
    },
}


class TelecomController(http.Controller):

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _lang(self):
        return request.env.context.get('lang', 'fr_FR')

    def _lang_prefix(self):
        """URL prefix to preserve the current language on internal links."""
        website = getattr(request, 'website', None)
        cur = getattr(request, 'lang', None)
        if not website or not cur:
            return ''
        default = website.default_lang_id
        if cur and default and cur.id != default.id:
            code = cur.url_code or (cur.code or '').split('_')[0]
            if code:
                return '/' + code
        return ''

    def _order_url(self):
        return request.env['ir.config_parameter'].sudo().get_param(
            'telecom_services.kissgroup_order_url') or '#'

    def _cat_labels(self, is_fr):
        return {key: (fr if is_fr else en) for key, fr, en in CATEGORIES}

    def _card(self, slug, lang, is_fr, prefix, cat_labels):
        meta = PRODUCTS[slug]
        content = meta.get(lang) or meta['fr_FR']
        return {
            'slug': slug,
            'cat': meta['cat'],
            'cat_label': cat_labels.get(meta['cat'], meta['cat']),
            'icon': meta['icon'],
            'image': '/telecom_services/static/src/img/offers/%s.jpg' % slug,
            'name': content['name'],
            'tagline': content.get('tagline', ''),
            'summary': content.get('summary', ''),
            'url': '%s/telecom/%s' % (prefix, slug),
        }

    # ------------------------------------------------------------------
    # Catalogue
    # ------------------------------------------------------------------
    @http.route('/telecom', type='http', auth='public', website=True)
    def telecom_page(self, **kwargs):
        lang = self._lang()
        is_fr = lang == 'fr_FR'
        strings = _UI_STRINGS.get(lang, _UI_STRINGS['fr_FR'])
        prefix = self._lang_prefix()
        cat_labels = self._cat_labels(is_fr)

        categories = [{'key': key, 'label': cat_labels[key]} for key, _fr, _en in CATEGORIES]
        cards = [self._card(slug, lang, is_fr, prefix, cat_labels) for slug in ORDER]

        return request.render('telecom_services.telecom_page', {
            'categories': categories,
            'cards': cards,
            **strings,
        })

    # ------------------------------------------------------------------
    # Fiche produit
    # ------------------------------------------------------------------
    @http.route('/telecom/<string:slug>', type='http', auth='public', website=True)
    def telecom_product(self, slug, **kwargs):
        meta = PRODUCTS.get(slug)
        if not meta:
            return request.redirect(self._lang_prefix() + '/telecom')

        lang = self._lang()
        is_fr = lang == 'fr_FR'
        strings = _UI_STRINGS.get(lang, _UI_STRINGS['fr_FR'])
        prefix = self._lang_prefix()
        cat_labels = self._cat_labels(is_fr)

        content = meta.get(lang) or meta['fr_FR']
        product = {
            'slug': slug,
            'cat': meta['cat'],
            'cat_label': cat_labels.get(meta['cat'], meta['cat']),
            'icon': meta['icon'],
            'image': '/telecom_services/static/src/img/offers/%s.jpg' % slug,
            'name': content['name'],
            'tagline': content.get('tagline', ''),
            'intro': content.get('intro', ''),
            'benefits': content.get('benefits', []),
            'sections': content.get('sections', []),
            'faq': content.get('faq', []),
        }
        related = [
            self._card(s, lang, is_fr, prefix, cat_labels)
            for s in ORDER
            if s != slug and PRODUCTS[s]['cat'] == meta['cat']
        ]

        return request.render('telecom_services.telecom_product', {
            'product': product,
            'related': related,
            'order_url': self._order_url(),
            'catalogue_url': prefix + '/telecom',
            **strings,
        })