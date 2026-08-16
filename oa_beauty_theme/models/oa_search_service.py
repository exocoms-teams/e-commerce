import re
import unicodedata
from difflib import get_close_matches
from urllib.parse import quote_plus

from odoo import api, models
from odoo.osv import expression
from odoo.tools import html2plaintext


class OASearchService(models.AbstractModel):
    _name = 'oa.search.service'
    _description = 'O&A Intelligent Product Search Service'

    _TOKEN_RE = re.compile(r"[\w\u0600-\u06ff]+", re.UNICODE)
    _STOP_WORDS = {
        'a', 'an', 'and', 'avec', 'de', 'des', 'du', 'en', 'et', 'for', 'la', 'le',
        'les', 'of', 'pour', 'the', 'un', 'une', 'with', 'بشرة', 'للبشرة', 'من',
    }

    @api.model
    def _synonym_groups(self):
        return [
            ('hydratant', 'hydratation', 'hydration', 'hydrating', 'moisturizer', 'moisturising', 'moisturizing', 'مرطب', 'ترطيب'),
            ('anti age', 'anti-age', 'anti âge', 'anti-âge', 'antiaging', 'anti aging', 'age defying', 'rides'),
            ('parfum', 'perfume', 'fragrance', 'scent', 'عطر'),
            ('serum', 'sérum', 'سيروم'),
            ('rouge a levres', 'rouge à lèvres', 'lipstick', 'nude lipstick', 'احمر شفاه'),
            ('fond de teint', 'foundation', 'teint'),
            ('peau seche', 'peau sèche', 'dry skin', 'skin dryness', 'جافة', 'البشرة الجافة'),
            ('peau grasse', 'oily skin', 'البشرة الدهنية', 'دهنية'),
            ('peau sensible', 'sensitive skin', 'حساسة', 'البشرة الحساسة'),
            ('maquillage', 'makeup', 'make up', 'مكياج'),
            ('naturel', 'natural', 'clean', 'طبيعي'),
            ('floral', 'florale', 'زهري'),
            ('vitamine c', 'vitamin c', 'vit c'),
            ('eclat', 'glow', 'radiance', 'lumineux'),
            ('creme', 'crème', 'cream', 'كريم'),
        ]

    @api.model
    def normalize_query(self, query):
        query = (query or '')[:120].strip().lower()
        query = unicodedata.normalize('NFKD', query)
        query = ''.join(ch for ch in query if not unicodedata.combining(ch))
        query = re.sub(r"[^\w\u0600-\u06ff\s-]+", " ", query, flags=re.UNICODE)
        query = re.sub(r"\s+", " ", query).strip()
        return query

    @api.model
    def tokenize(self, query):
        normalized = self.normalize_query(query)
        tokens = self._TOKEN_RE.findall(normalized)
        return [token for token in tokens if len(token) > 1 and token not in self._STOP_WORDS]

    @api.model
    def expand_terms(self, query):
        normalized = self.normalize_query(query)
        terms = set(self.tokenize(normalized))
        if normalized:
            terms.add(normalized)

        groups = [[self.normalize_query(item) for item in group] for group in self._synonym_groups()]
        vocabulary = {item for group in groups for item in group}
        for token in list(terms):
            for match in get_close_matches(token, vocabulary, n=2, cutoff=0.84):
                terms.add(match)
            for group in groups:
                if token in group or any(token in phrase.split() for phrase in group):
                    terms.update(group)
        return [term for term in terms if term]

    @api.model
    def _available_text_fields(self):
        product_model = self.env['product.template']
        candidates = [
            'name',
            'default_code',
            'description',
            'description_sale',
            'website_meta_keywords',
            'website_meta_description',
            'oa_type',
            'oa_finish',
            'oa_best_for',
            'oa_key_ingredients',
            'oa_benefits',
            'oa_how_to_use',
            'oa_seo_keywords',
            'oa_fragrance_top_notes',
            'oa_fragrance_heart_notes',
            'oa_fragrance_base_notes',
            'oa_mood',
        ]
        optional = ['product_brand_id', 'brand_id']
        fields = [field for field in candidates if field in product_model._fields]
        brand_fields = [field for field in optional if field in product_model._fields]
        return fields, brand_fields

    @api.model
    def _public_product_domain(self, website=None):
        website = website or self.env['website'].get_current_website()
        domain = [('sale_ok', '=', True), ('is_published', '=', True)]
        if 'website_id' in self.env['product.template']._fields and website:
            domain = expression.AND([domain, ['|', ('website_id', '=', False), ('website_id', '=', website.id)]])
        return domain

    @api.model
    def _candidate_domain(self, terms, website=None):
        fields, brand_fields = self._available_text_fields()
        search_parts = []
        for term in terms[:18]:
            for field in fields:
                search_parts.append((field, 'ilike', term))
            search_parts.extend([
                ('categ_id.name', 'ilike', term),
                ('public_categ_ids.name', 'ilike', term),
            ])
            for field in brand_fields:
                search_parts.append((field + '.name', 'ilike', term))
        if not search_parts:
            return self._public_product_domain(website)
        return expression.AND([self._public_product_domain(website), expression.OR(search_parts)])

    @api.model
    def _field_text(self, product, field):
        value = product[field]
        if not value:
            return ''
        if product._fields[field].type == 'html':
            return html2plaintext(value or '')
        return str(value)

    @api.model
    def _score_product(self, product, query, terms):
        normalized_query = self.normalize_query(query)
        tokens = self.tokenize(query)
        fields, brand_fields = self._available_text_fields()
        weighted_fields = [
            ('name', 100, 60),
            ('default_code', 80, 45),
            ('public_categ_ids', 70, 42),
            ('categ_id', 60, 36),
            ('oa_type', 56, 32),
            ('oa_key_ingredients', 50, 28),
            ('oa_benefits', 44, 24),
            ('oa_best_for', 44, 24),
            ('oa_fragrance_top_notes', 38, 20),
            ('oa_fragrance_heart_notes', 38, 20),
            ('oa_fragrance_base_notes', 38, 20),
            ('oa_mood', 34, 18),
            ('oa_finish', 30, 16),
            ('description_sale', 24, 12),
            ('description', 18, 8),
            ('website_meta_keywords', 14, 7),
            ('oa_seo_keywords', 14, 7),
            ('website_meta_description', 10, 5),
        ]
        for field in brand_fields:
            weighted_fields.append((field, 42, 20))

        score = 0
        for field, phrase_weight, token_weight in weighted_fields:
            if field in ('public_categ_ids',):
                haystack = ' '.join(product.public_categ_ids.mapped('name'))
            elif field == 'categ_id':
                haystack = product.categ_id.name or ''
            elif field in brand_fields:
                haystack = product[field].name if product[field] else ''
            elif field in fields:
                haystack = self._field_text(product, field)
            else:
                continue
            normalized_text = self.normalize_query(haystack)
            if normalized_query and normalized_query in normalized_text:
                score += phrase_weight
            score += sum(token_weight for token in tokens if token in normalized_text)
            score += sum(max(2, token_weight // 3) for term in terms if len(term) > 2 and term in normalized_text)

        if product.is_published:
            score += 2
        return score

    @api.model
    def _serialize_product(self, product, score):
        website = self.env['website'].get_current_website()
        return {
            'id': product.id,
            'name': product.name,
            'url': product.website_url or '/shop/product/%s' % product.id,
            'image': '/web/image/product.template/%s/image_256' % product.id,
            'price': product.list_price,
            'price_formatted': self.env['ir.qweb.field.monetary'].value_to_html(
                product.list_price,
                {'display_currency': website.currency_id},
            ) if website and website.currency_id else product.list_price,
            'category': product.public_categ_ids[:1].name or product.categ_id.name or '',
            'relevance': min(round(score / 180.0, 2), 1.0),
        }

    @api.model
    def search_products(self, query, limit=8, offset=0, website=None):
        normalized = self.normalize_query(query)
        if len(normalized) < 2:
            return {'query': query or '', 'normalized_query': normalized, 'results': [], 'count': 0, 'suggestions': []}

        terms = self.expand_terms(normalized)
        candidate_limit = max(min((limit + offset) * 8, 160), 40)
        candidates = self.env['product.template'].sudo().search(
            self._candidate_domain(terms, website=website),
            limit=candidate_limit,
        )
        scored = []
        for product in candidates:
            score = self._score_product(product, normalized, terms)
            if score > 0:
                scored.append((score, product))
        scored.sort(key=lambda item: (-item[0], item[1].name or ''))
        sliced = scored[offset:offset + limit]
        results = [self._serialize_product(product, score) for score, product in sliced]
        return {
            'query': query or '',
            'normalized_query': normalized,
            'results': results,
            'count': len(scored),
            'suggestions': self.suggestions(query, terms=terms, limit=5),
        }

    @api.model
    def suggestions(self, query, terms=None, limit=5):
        normalized = self.normalize_query(query)
        terms = terms or self.expand_terms(query)
        suggestions = []
        category_domain = expression.OR([('name', 'ilike', term) for term in terms[:8]]) if terms else [('id', '=', 0)]
        categories = self.env['product.public.category'].sudo().search(category_domain, limit=3)
        for category in categories:
            suggestions.append({
                'type': 'category',
                'label': category.name,
                'url': '/shop/category/%s' % category.id,
                'id': category.id,
            })
        if normalized:
            suggestions.append({'type': 'search', 'label': 'Search for "%s"' % query[:60], 'url': '/shop?search=%s' % quote_plus(query[:80])})
        fallback = ['serum peau sèche', 'crème hydratante', 'floral perfume', 'vitamin C', 'مكياج طبيعي']
        for item in fallback:
            if len(suggestions) >= limit:
                break
            if self.normalize_query(item) != normalized:
                suggestions.append({'type': 'popular', 'label': item, 'url': '/shop?search=%s' % quote_plus(item)})
        return suggestions[:limit]
