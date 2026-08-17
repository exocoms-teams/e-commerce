import uuid

from odoo import _, http
from odoo.http import request


class AdvisorController(http.Controller):
    _ALLOWED_SKIN_TYPES = {'normal', 'dry', 'oily', 'combination', 'sensitive'}
    _ALLOWED_CONCERNS = {
        'acne', 'hyperpigmentation', 'redness', 'dehydration', 'aging',
        'dullness', 'pores', 'sensitivity',
    }
    _ALLOWED_BUDGETS = {'essential', 'standard', 'premium'}
    _ALLOWED_MAKEUP = {'natural', 'everyday', 'glamorous', 'skip'}
    _ALLOWED_AGE = {'18-25', '25-35', '35-45', '45+', 'skip'}
    _BUDGET_MAX = {
        'essential': 45.0,
        'standard': 80.0,
        'premium': 999999.0,
    }

    def _clean_choice(self, value, allowed, default=''):
        value = (value or '').strip().lower()[:40]
        return value if value in allowed else default

    def _product_domain(self):
        service = request.env['oa.search.service'].sudo()
        domain = service._public_product_domain(website=request.website)
        return service._and_domain([domain, [('sale_ok', '=', True), ('oa_is_coming_soon', '=', False)]])

    def _format_money(self, amount):
        website = request.website
        if website and website.currency_id:
            return request.env['ir.qweb.field.monetary'].value_to_html(
                amount,
                {'display_currency': website.currency_id},
            )
        return "%.2f" % amount

    def _text(self, product):
        values = [
            product.name,
            product.description_sale,
            product.oa_type,
            product.oa_product_type,
            product.oa_finish,
            product.oa_best_for,
            product.oa_ideal_for,
            product.oa_key_ingredients,
            product.oa_skin_type,
            product.oa_concern,
            product.oa_routine_step,
            product.oa_fragrance_family,
            product.oa_occasion,
            product.oa_mood,
            product.oa_fragrance_top_notes,
            product.oa_fragrance_heart_notes,
            product.oa_fragrance_base_notes,
        ]
        values += product.public_categ_ids.mapped('name')
        return ' '.join([v for v in values if v]).lower()

    def _role_score(self, text, role):
        role_terms = {
            'cleanse': ('cleanse', 'cleanser', 'cleansing', 'nettoy', 'mousse'),
            'treat': ('serum', 'sérum', 'vitamin', 'trait', 'repair', 'essence'),
            'hydrate': ('moistur', 'hydrate', 'hydrating', 'crème', 'cream', 'hydra'),
            'protect': ('spf', 'solaire', 'sun', 'protect'),
            'makeup': ('makeup', 'maquillage', 'foundation', 'teint', 'blush', 'lipstick', 'mascara'),
            'fragrance': ('fragrance', 'parfum', 'eau de parfum', 'scent'),
        }
        return sum(10 for term in role_terms.get(role, ()) if term in text)

    def _profile_score(self, product, profile, role):
        text = self._text(product)
        score = 44 + self._role_score(text, role)
        reasons = []

        skin_type = profile.get('skin_type')
        concern = profile.get('main_concern')
        makeup = profile.get('makeup_preference')
        budget = profile.get('budget')
        age_range = profile.get('age_range')
        budget_max = self._BUDGET_MAX.get(budget)

        skin_terms = {
            'dry': ('dry', 'sèche', 'seche', 'dehydrat', 'hydrat'),
            'oily': ('oily', 'grasse', 'mat', 'pores'),
            'combination': ('combination', 'mixte', 'balance', 'équilibr'),
            'normal': ('normal', 'daily', 'quotidien'),
            'sensitive': ('sensitive', 'sensible', 'soothing', 'apais'),
        }
        concern_terms = {
            'acne': ('acne', 'acné', 'imperfection', 'pores', 'purif'),
            'hyperpigmentation': ('pigment', 'tache', 'spot', 'vitamin c', 'glow'),
            'redness': ('redness', 'rougeur', 'soothing', 'apais'),
            'dehydration': ('dehydrat', 'déshydrat', 'hydrat', 'hyaluronic'),
            'aging': ('aging', 'anti-age', 'rides', 'repair', 'peptide'),
            'dullness': ('dull', 'terne', 'glow', 'éclat', 'radiance', 'vitamin c'),
            'pores': ('pores', 'mat', 'smooth', 'lisse'),
        }
        makeup_terms = {
            'natural': ('natural', 'naturel', 'nude', 'bare'),
            'everyday': ('everyday', 'daily', 'quotidien', 'soft'),
            'glamorous': ('glam', 'intense', 'velvet', 'precision', 'highlight'),
        }
        age_terms = {
            '35-45': ('firm', 'repair', 'peptide', 'rides', 'anti-age'),
            '45+': ('firm', 'repair', 'peptide', 'rides', 'anti-age', 'night'),
        }

        if skin_type and any(term in text for term in skin_terms.get(skin_type, ())):
            score += 14
            reasons.append(_("Suitable for your skin type"))
        if concern and any(term in text for term in concern_terms.get(concern, ())):
            score += 16
            reasons.append(_("Targets your main concern"))
        if makeup and any(term in text for term in makeup_terms.get(makeup, ())):
            score += 10
            reasons.append(_("Matches your makeup style"))
        if age_range and any(term in text for term in age_terms.get(age_range, ())):
            score += 8
            reasons.append(_("Adapted to your age range"))
        if budget_max and product.list_price <= budget_max:
            score += 8
            reasons.append(_("Within your selected budget"))
        elif budget == 'essential':
            score -= 8

        if product.oa_key_ingredients:
            score += 4
            reasons.append(_("Key ingredients available"))
        if role != 'fragrance' and product.oa_routine_step:
            score += 5
            reasons.append(_("Fits this routine step"))
        if role == 'fragrance' and (
            product.oa_fragrance_top_notes or product.oa_fragrance_heart_notes or product.oa_fragrance_base_notes
        ):
            score += 10
            reasons.append(_("Fragrance pyramid documented"))

        if not reasons:
            reasons.append(_("Closest catalog match for this step"))

        return max(50, min(98, score)), reasons[:4]

    def _pick_product(self, products, profile, role, used_ids):
        scored = []
        for product in products:
            if product.id in used_ids:
                continue
            match_score, reasons = self._profile_score(product, profile, role)
            role_score = self._role_score(self._text(product), role)
            if role_score <= 0 and role in ('cleanse', 'protect'):
                continue
            scored.append((match_score + role_score, product.list_price, product, match_score, reasons))
        scored.sort(key=lambda item: (-item[0], item[1], item[2].website_sequence or 9999, item[2].name or ''))
        if not scored:
            return False, 0, []
        _, _, product, match_score, reasons = scored[0]
        return product, match_score, reasons

    def _serialize_product(self, product, match_score, reasons, routine_step=''):
        variant = product.product_variant_id
        return {
            'id': product.id,
            'variant_id': variant.id if variant else False,
            'name': product.name,
            'price': product.list_price,
            'price_formatted': self._format_money(product.list_price),
            'url': product.website_url,
            'cart_url': '/shop/cart/update?product_id=%s&add_qty=1' % variant.id if variant else product.website_url,
            'image_url': '/web/image/product.template/%s/image_256' % product.id,
            'is_coming_soon': product.oa_is_coming_soon,
            'match_score': match_score,
            'match_reasons': reasons,
            'routine_step': routine_step,
        }

    @http.route('/api/advisor/recommend', type='jsonrpc', auth='public', website=True, csrf=False, methods=['POST'])
    def get_recommendation(self, **kw):
        skin_type = self._clean_choice(kw.get('skin_type'), self._ALLOWED_SKIN_TYPES)
        concern = self._clean_choice(kw.get('main_concern'), self._ALLOWED_CONCERNS)
        budget = self._clean_choice(kw.get('budget'), self._ALLOWED_BUDGETS, default='standard')
        makeup_preference = self._clean_choice(kw.get('makeup_preference'), self._ALLOWED_MAKEUP)
        age_range = self._clean_choice(kw.get('age_range'), self._ALLOWED_AGE)
        advisor_mode = self._clean_choice(kw.get('mode'), {'skincare', 'makeup', 'fragrance'}, default='skincare')
        profile = {
            'skin_type': skin_type,
            'main_concern': concern,
            'budget': budget,
            'makeup_preference': makeup_preference,
            'age_range': age_range,
        }

        Product = request.env['product.template'].sudo()
        recommended_ids = []
        recommended_products_data = []
        routine_steps = []
        used_ids = set()
        total_price = 0.0
        explanation = _(
            "Your O&A routine is built from published products in the live catalog, "
            "with each match scored against your profile."
        )

        if advisor_mode == 'fragrance':
            fragrances = Product.search(self._product_domain() + [('oa_fragrance_top_notes', '!=', False)])
            for index, product in enumerate(fragrances[:3], 1):
                match_score, reasons = self._profile_score(product, profile, 'fragrance')
                step_label = _("Scent option %s") % index
                recommended_ids.append(product.id)
                total_price += product.list_price
                recommended_products_data.append(self._serialize_product(product, match_score, reasons, step_label))
                routine_steps.append({
                    'step': step_label,
                    'product': product.name,
                    'desc': product.oa_mood or _("A documented fragrance profile from the O&A catalog."),
                    'match_score': match_score,
                })
        else:
            products = Product.search(self._product_domain(), order='website_sequence asc, list_price asc, name asc')
            routine_plan = [
                ('cleanse', _("Step 1 - Cleanse"), _("Remove impurities and prepare the skin.")),
                ('treat', _("Step 2 - Treat"), _("Target the priority concern with an active formula.")),
                ('hydrate', _("Step 3 - Hydrate"), _("Seal hydration and support the skin barrier.")),
                ('protect', _("Step 4 - Protect"), _("Finish the morning routine with daily protection.")),
            ]
            if makeup_preference and makeup_preference != 'skip':
                routine_plan.append(('makeup', _("Optional finish"), _("Complete the ritual with a complexion or color step.")))

            for role, step_label, description in routine_plan:
                product, match_score, reasons = self._pick_product(products, profile, role, used_ids)
                if not product:
                    continue
                used_ids.add(product.id)
                recommended_ids.append(product.id)
                total_price += product.list_price
                routine_steps.append({
                    'step': step_label,
                    'product': product.name,
                    'desc': description,
                    'match_score': match_score,
                })
                recommended_products_data.append(self._serialize_product(product, match_score, reasons, step_label))

        request.env['oa.advisor.session'].sudo().create({
            'session_id': str(uuid.uuid4()),
            'skin_type': skin_type or advisor_mode,
            'main_concern': concern,
            'makeup_preference': makeup_preference,
            'budget': budget,
            'recommended_product_ids': [(6, 0, recommended_ids)],
        })

        if not recommended_products_data:
            explanation = _("No published products currently match this profile. Please explore the catalog or try a broader profile.")

        return {
            'status': 'success',
            'explanation': explanation,
            'routine': routine_steps,
            'products': recommended_products_data,
            'routine_total': total_price,
            'routine_total_formatted': self._format_money(total_price),
            'profile': profile,
        }
