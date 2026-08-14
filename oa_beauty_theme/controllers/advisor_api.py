from odoo import http
from odoo.http import request
import uuid

class AdvisorController(http.Controller):

    @http.route('/api/advisor/recommend', type='json', auth='public', website=True, csrf=False)
    def get_recommendation(self, **kw):
        # Extract data from the JSON-RPC params
        skin_type   = kw.get('skin_type', '').lower()
        concern     = kw.get('main_concern', '').lower()
        budget      = kw.get('budget', '').lower()
        # Fragrance fields
        mood        = kw.get('mood', '').lower()
        occasion    = kw.get('occasion', '').lower()
        scent_family = kw.get('scent_family', '').lower()
        advisor_mode = kw.get('mode', 'skincare').lower()  # 'skincare', 'makeup', or 'fragrance'

        Product = request.env['product.template'].sudo()
        recommended_ids = []
        routine_steps = []
        explanation = ''

        # ────────────────────────────────────────────────────
        # MODE: FRAGRANCE
        # ────────────────────────────────────────────────────
        if advisor_mode == 'fragrance':
            fragrances = Product.search([
                ('is_published', '=', True),
                ('oa_fragrance_top_notes', '!=', False),
            ])

            scored = []
            for f in fragrances:
                score = 0
                name_lower = (f.name or '').lower()
                mood_field = (f.oa_mood or '').lower()
                top = (f.oa_fragrance_top_notes or '').lower()
                heart = (f.oa_fragrance_heart_notes or '').lower()
                base = (f.oa_fragrance_base_notes or '').lower()
    
                # Scent family matching
                if scent_family:
                    if scent_family == 'floral' and any(k in heart for k in ['rose', 'jasmine', 'peony', 'lily', 'blossom']):
                        score += 3
                    elif scent_family == 'woody' and any(k in base for k in ['sandalwood', 'cedar', 'oud', 'vetiver']):
                        score += 3
                    elif scent_family == 'oriental' and any(k in base for k in ['amber', 'vanilla', 'musk', 'benzoin']):
                        score += 3
                    elif scent_family == 'fresh' and any(k in top for k in ['bergamot', 'mandarin', 'lemon', 'pear']):
                        score += 3
                    elif scent_family == 'gourmand' and any(k in base for k in ['vanilla', 'praline', 'tonka', 'caramel']):
                        score += 3

                # Mood matching
                if mood and mood in mood_field:
                    score += 2

                # Occasion matching
                if occasion:
                    if occasion in ['evening', 'night', 'soiree'] and any(k in name_lower for k in ['noire', 'noir', 'midnight', 'orchid']):
                        score += 2
                    if occasion in ['day', 'work', 'fresh'] and any(k in name_lower for k in ['lumiere', 'eclat', 'bloom']):
                        score += 2

                scored.append((score, f))

            scored.sort(key=lambda x: x[0], reverse=True)
            top3 = [f for _, f in scored[:3]]

            for i, f in enumerate(top3, 1):
                recommended_ids.append(f.id)
                routine_steps.append({
                    'step': f'Suggestion {i}',
                    'product': f.name,
                    'desc': f.oa_mood or 'Une création olfactive d\'exception.'
                })

            explanation = (
                f"Basé sur votre profil olfactif (Famille: {scent_family or 'polyvalente'}, "
                f"Humeur: {mood or 'équilibrée'}), nous avons sélectionné ces créations de notre "
                f"collection à venir O&A Beauty."
            )

        # ────────────────────────────────────────────────────
        # MODE: SKINCARE (default)
        # ────────────────────────────────────────────────────
        else:
            products = Product.search([
                ('is_published', '=', True),
                ('sale_ok', '=', True),
                ('oa_is_coming_soon', '=', False),
            ])

            # Cleanser
            cleanser = products.filtered(lambda p: 'cleans' in (p.name or '').lower())
            if cleanser:
                recommended_ids.append(cleanser[0].id)
                routine_steps.append({'step': 'Étape 1 — Nettoyer', 'product': cleanser[0].name, 'desc': 'Éliminez les impuretés et préparez la peau.'})

            # Serum / Treatment
            serum = False
            if concern in ['aging', 'anti-age', 'dullness', 'hyperpigmentation', 'taches']:
                serum = products.filtered(lambda p: 'vitamin c' in (p.name or '').lower())
            if not serum:
                serum = products.filtered(lambda p: 'hydrat' in (p.name or '').lower() and 'serum' in (p.name or '').lower())
            if serum:
                recommended_ids.append(serum[0].id)
                routine_steps.append({'step': 'Étape 2 — Traiter', 'product': serum[0].name, 'desc': 'Ciblez vos préoccupations cutanées principales.'})

            # Moisturizer
            moisturizer = products.filtered(lambda p: 'moisturizer' in (p.name or '').lower() or 'cream' in (p.name or '').lower())
            if moisturizer:
                recommended_ids.append(moisturizer[0].id)
                routine_steps.append({'step': 'Étape 3 — Hydrater', 'product': moisturizer[0].name, 'desc': 'Verrouillez l\'hydratation et protégez la barrière cutanée.'})

            explanation = (
                f"Basé sur votre profil (Type de peau: {skin_type}, Préoccupation: {concern}), "
                f"nous avons élaboré une routine pour équilibrer et nourrir votre peau."
            )

        # ────────────────────────────────────────────────────
        # SAVE TO ANALYTICS
        # ────────────────────────────────────────────────────
        session_id = str(uuid.uuid4())
        request.env['oa.advisor.session'].sudo().create({
            'session_id': session_id,
            'skin_type': skin_type or advisor_mode,
            'main_concern': concern or scent_family,
            'budget': budget,
            'recommended_product_ids': [(6, 0, recommended_ids)]
        })

        # ────────────────────────────────────────────────────
        # RETURN
        # ────────────────────────────────────────────────────
        recommended_products_data = []
        for p_id in recommended_ids:
            p = Product.browse(p_id)
            recommended_products_data.append({
                'id': p.id,
                'name': p.name,
                'price': p.list_price,
                'url': p.website_url,
                'image_url': f'/web/image/product.template/{p.id}/image_128',
                'is_coming_soon': p.oa_is_coming_soon,
            })

        return {
            'status': 'success',
            'session_id': session_id,
            'explanation': explanation,
            'routine': routine_steps,
            'products': recommended_products_data,
        }
