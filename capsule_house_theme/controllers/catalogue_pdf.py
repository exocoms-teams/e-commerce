# -*- coding: utf-8 -*-
import io
import os

from odoo import http
from odoo.http import request

from ..data_definition import GAMMES_DATA


# Table des codepoints Unicode FontAwesome 4.7 (même version que celle
# utilisée par le site, voir layout.xml : fontawesome-webfont.woff2 v4.7.0).
# Référence officielle, stable : https://fontawesome.com/v4/cheatsheet/
FA_CODEPOINTS = {
    'fa-square-o': u'\uf096', 'fa-lock': u'\uf023',
    'fa-lightbulb-o': u'\uf0eb', 'fa-bath': u'\uf2cd',
    'fa-sun-o': u'\uf185', 'fa-paint-brush': u'\uf1fc',
    'fa-bolt': u'\uf0e7', 'fa-arrows-v': u'\uf07d',
    'fa-building-o': u'\uf0f7', 'fa-cubes': u'\uf1b3',
    'fa-industry': u'\uf275', 'fa-clock-o': u'\uf017',
    'fa-arrows-alt': u'\uf0b2', 'fa-tint': u'\uf043',
    'fa-refresh': u'\uf021', 'fa-thermometer-half': u'\uf2c9',
    'fa-cube': u'\uf1b2', 'fa-truck': u'\uf0d1',
    'fa-tree': u'\uf1bb', 'fa-shield': u'\uf132',
    'fa-plug': u'\uf1e6', 'fa-volume-off': u'\uf026',
    'fa-compress': u'\uf066', 'fa-check-circle': u'\uf058',
    'fa-th-large': u'\uf009', 'fa-circle-o': u'\uf10c',
    'fa-puzzle-piece': u'\uf12e', 'fa-inbox': u'\uf01c',
    'fa-home': u'\uf015',
}


class CapsuleHouseCataloguePdf(http.Controller):
    """Génère un catalogue PDF à la volée pour chaque gamme (CH-35),
    à partir de GAMMES_DATA — toujours à jour (option B, décidée avec
    hamza03 le 2026-09-11).

    Icônes rendues avec le VRAI fichier FontAwebood du module `web`
    (celui déjà utilisé par le site, voir layout.xml), localisé via
    get_module_path (fonction stable, contrairement à
    get_module_resource, retirée dans cette version d'Odoo — voir
    historique de ce fichier). Garantit des icônes pixel-identiques
    entre toutes les gammes. Si le fichier n'est introuvable pour une
    raison quelconque, repli silencieux sur un simple carré (jamais
    d'erreur bloquante pour un manque d'icône).
    """

    _FA_FONT_PATH = None
    _FA_CHECKED = False

    def _get_fa_font_path(self):
        if CapsuleHouseCataloguePdf._FA_CHECKED:
            return CapsuleHouseCataloguePdf._FA_FONT_PATH
        CapsuleHouseCataloguePdf._FA_CHECKED = True
        try:
            from odoo.modules.module import get_module_path
            web_path = get_module_path('web')
            candidate = os.path.join(
                web_path, 'static', 'src', 'libs', 'fontawesome',
                'fonts', 'fontawesome-webfont.ttf',
            )
            if os.path.exists(candidate):
                CapsuleHouseCataloguePdf._FA_FONT_PATH = candidate
        except Exception:
            pass
        return CapsuleHouseCataloguePdf._FA_FONT_PATH

    def _register_fa(self):
        path = self._get_fa_font_path()
        if not path:
            return False
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            if 'FontAwesome' not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont('FontAwesome', path))
            return True
        except Exception:
            return False

    @http.route('/nos-gammes/<string:slug>/catalogue.pdf', type='http',
                auth='public', website=True, sitemap=False)
    def gamme_catalogue_pdf(self, slug, **kw):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.pdfgen import canvas

        gamme = next((g for g in GAMMES_DATA if g['slug'] == slug), None)
        if not gamme:
            return request.not_found()

        is_fr = request.env.lang == 'fr_FR'
        has_fa = self._register_fa()
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        margin = 2 * cm

        INK = (0.06, 0.09, 0.08)
        TERRACOTTA = (0.82, 0.35, 0.22)
        PANEL = (0.96, 0.92, 0.87)
        GRAY = (0.42, 0.42, 0.42)
        GREEN = (0.15, 0.55, 0.35)
        WHITE = (1, 1, 1)
        LIGHT_BORDER = (0.85, 0.85, 0.85)

        def draw_icon(icon_key, x, y, size, color=TERRACOTTA):
            """Dessine l'icône FontAwesome réelle si la police a pu
            être chargée (même fichier que le site, donc identique sur
            toutes les gammes) ; sinon un simple carré de secours."""
            codepoint = FA_CODEPOINTS.get(icon_key)
            if has_fa and codepoint:
                c.setFillColorRGB(*color)
                c.setFont('FontAwesome', size / 0.028 * 0.01)  # taille approx. en pt
                # drawString avec une police d'icônes se centre par la baseline :
                # on ajuste pour aligner visuellement avec le texte à côté.
                fsize = size * 28.35  # cm -> pt approximatif pour la hauteur voulue
                c.setFont('FontAwesome', fsize * 0.85)
                c.drawString(x, y, codepoint)
            else:
                c.setStrokeColorRGB(*color)
                c.setLineWidth(1.2)
                c.roundRect(x, y, size, size, size * 0.15, stroke=1, fill=0)

        def check_mark(x, y, size, color=GREEN):
            """Coche verte — vraie icône fa-check-circle si dispo,
            sinon cercle plein dessiné avec un trait blanc."""
            if has_fa and 'fa-check-circle' in FA_CODEPOINTS:
                c.setFillColorRGB(*color)
                fsize = size * 28.35 * 0.85
                c.setFont('FontAwesome', fsize)
                c.drawString(x, y, FA_CODEPOINTS['fa-check-circle'])
            else:
                c.setFillColorRGB(*color)
                cy = y + size * 0.35
                c.circle(x + size / 2, cy, size / 2, stroke=0, fill=1)
                c.setStrokeColorRGB(*WHITE)
                c.setLineWidth(1.1)
                c.setLineCap(1)
                c.line(x + size * 0.28, cy, x + size * 0.44, cy - size * 0.16)
                c.line(x + size * 0.44, cy - size * 0.16, x + size * 0.72, cy + size * 0.18)

        # ------------------------------------------------------------------
        # MISE EN PAGE — polices légèrement agrandies pour se rapprocher
        # du rendu web (retour utilisateur : "augmente un peu la police")
        # ------------------------------------------------------------------
        def new_page_header():
            c.setFillColorRGB(*INK)
            c.rect(0, height - 3.5 * cm, width, 3.5 * cm, fill=1, stroke=0)
            c.setFillColorRGB(*WHITE)
            c.setFont('Helvetica-Bold', 21)
            c.drawString(margin, height - 1.6 * cm, 'Capsule House')
            c.setFillColorRGB(*TERRACOTTA)
            c.setFont('Helvetica-Bold', 16)
            c.drawString(margin, height - 2.4 * cm, gamme['name'])
            c.setFillColorRGB(*WHITE)
            c.setFont('Helvetica', 10.5)
            tagline = gamme['tagline_fr'] if is_fr else gamme['tagline_en']
            c.drawString(margin, height - 3.05 * cm, tagline)
            return height - 4.5 * cm

        def ensure_space(y_pos, needed):
            if y_pos - needed < margin:
                c.showPage()
                return new_page_header()
            return y_pos

        def section_title(y_pos, text, centered=False):
            y_pos = ensure_space(y_pos, 1.3 * cm)
            c.setFillColorRGB(*INK)
            c.setFont('Helvetica-Bold', 15)
            text_w = c.stringWidth(text, 'Helvetica-Bold', 15)
            x = (width - text_w) / 2 if centered else margin
            c.drawString(x, y_pos, text)
            c.setStrokeColorRGB(*TERRACOTTA)
            c.setLineWidth(2)
            c.line(x, y_pos - 0.15 * cm, x + text_w, y_pos - 0.15 * cm)
            return y_pos - 1.05 * cm

        y = new_page_header()

        # --- Performances ---
        if gamme.get('performances'):
            gender = gamme.get('gender')
            if is_fr:
                article, adj = ('Une', 'pensée') if gender == 'f' else ('Un', 'pensé')
                title = "%s %s %s pour le confort absolu" % (article, gamme['name'].lower(), adj)
            else:
                title = "A %s designed for absolute comfort" % gamme['name'].lower()
            y = ensure_space(y, 2 * cm)
            c.setFillColorRGB(*TERRACOTTA)
            c.setFont('Helvetica-Bold', 9.5)
            label = 'PERFORMANCES'
            c.drawString((width - c.stringWidth(label, 'Helvetica-Bold', 9.5)) / 2, y, label)
            y -= 0.65 * cm
            c.setFillColorRGB(*INK)
            c.setFont('Helvetica-Bold', 16)
            c.drawString((width - c.stringWidth(title, 'Helvetica-Bold', 16)) / 2, y, title)
            y -= 1.15 * cm

            perfs = gamme['performances']
            col_count = 2
            gap = 0.6 * cm
            card_w = (width - 2 * margin - gap * (col_count - 1)) / col_count
            card_h = 3 * cm
            pad = 0.4 * cm
            icon_size = 0.6 * cm
            for i in range(0, len(perfs), col_count):
                row = perfs[i:i + col_count]
                y = ensure_space(y, card_h + 0.4 * cm)
                x = margin
                for perf in row:
                    c.setStrokeColorRGB(*LIGHT_BORDER)
                    c.setFillColorRGB(*WHITE)
                    c.roundRect(x, y - card_h, card_w, card_h, 4, fill=1, stroke=1)
                    draw_icon(perf.get('icon', ''), x + pad, y - pad - icon_size, icon_size)
                    c.setFillColorRGB(*INK)
                    c.setFont('Helvetica-Bold', 11)
                    ptitle = perf['title_fr'] if is_fr else perf['title_en']
                    c.drawString(x + pad, y - pad - icon_size - 0.55 * cm, ptitle)
                    c.setFillColorRGB(*GRAY)
                    c.setFont('Helvetica', 9)
                    pdesc = perf['desc_fr'] if is_fr else perf['desc_en']
                    words = pdesc.split(' ')
                    lines, cur = [], ''
                    max_w = card_w - 2 * pad
                    for w in words:
                        test = (cur + ' ' + w).strip()
                        if c.stringWidth(test, 'Helvetica', 9) > max_w:
                            lines.append(cur)
                            cur = w
                        else:
                            cur = test
                    lines.append(cur)
                    yy = y - pad - icon_size - 1.05 * cm
                    for line in lines[:3]:
                        c.drawString(x + pad, yy, line)
                        yy -= 0.4 * cm
                    x += card_w + gap
                y -= card_h + 0.5 * cm
            y -= 0.3 * cm

        # --- Formats ---
        if gamme.get('formats'):
            y = section_title(y, 'Formats')
            fmts = gamme['formats']
            gap = 0.5 * cm
            card_w = 4.7 * cm
            card_h = 2.6 * cm
            row_w = len(fmts) * card_w + (len(fmts) - 1) * gap
            x = (width - row_w) / 2
            y = ensure_space(y, card_h + 0.3 * cm)
            for fmt in fmts:
                c.setFillColorRGB(*PANEL)
                c.roundRect(x, y - card_h, card_w, card_h, 4, fill=1, stroke=0)
                c.setFillColorRGB(*INK)
                c.setFont('Helvetica-Bold', 11.5)
                c.drawCentredString(x + card_w / 2, y - 0.75 * cm, fmt['name'])
                c.setFillColorRGB(*GRAY)
                c.setFont('Helvetica', 9.5)
                surface = fmt['surface_fr'] if is_fr else fmt['surface_en']
                note = fmt['note_fr'] if is_fr else fmt['note_en']
                c.drawCentredString(x + card_w / 2, y - 1.4 * cm, surface)
                c.drawCentredString(x + card_w / 2, y - 1.9 * cm, note)
                x += card_w + gap
            y -= card_h + 0.9 * cm

        # --- Spécifications : NE JAMAIS COUPER, saut de page complet si besoin ---
        if gamme.get('specs_ext') or gamme.get('specs_int'):
            # Estimation de la hauteur totale nécessaire pour TOUT le bloc
            # (titre + Extérieur + Intérieur) : si ça ne rentre pas
            # intégralement dans l'espace restant, on saute directement à
            # une page neuve plutôt que de couper le contenu au milieu.
            row_h_est = 0.68 * cm
            block_gap = 0.6 * cm
            n_ext = len(gamme.get('specs_ext') or [])
            n_int = len(gamme.get('specs_int') or [])
            total_needed = 1.3 * cm  # titre de section
            if n_ext:
                total_needed += 0.6 * cm + n_ext * row_h_est + block_gap
            if n_int:
                total_needed += 0.6 * cm + n_int * row_h_est
            if y - total_needed < margin:
                c.showPage()
                y = new_page_header()

            y = section_title(y, 'Spécifications techniques' if is_fr else 'Technical specifications')
            full_w = width - 2 * margin

            def draw_spec_block(y_pos, title, rows):
                c.setFillColorRGB(*GRAY)
                c.setFont('Helvetica-Bold', 9.5)
                c.drawString(margin, y_pos, title.upper())
                y_pos -= 0.6 * cm
                c.setFont('Helvetica', 10.5)
                for row in rows:
                    label = row['label_fr'] if is_fr else row['label_en']
                    value = row['value_fr'] if is_fr else row['value_en']
                    c.setFillColorRGB(*GRAY)
                    c.drawString(margin, y_pos, label)
                    c.setFillColorRGB(*INK)
                    c.setFont('Helvetica-Bold', 10.5)
                    c.drawRightString(margin + full_w, y_pos, value)
                    c.setFont('Helvetica', 10.5)
                    c.setStrokeColorRGB(*LIGHT_BORDER)
                    c.line(margin, y_pos - 0.18 * cm, margin + full_w, y_pos - 0.18 * cm)
                    y_pos -= row_h_est
                return y_pos

            if gamme.get('specs_ext'):
                y = draw_spec_block(y, 'Extérieur' if is_fr else 'Exterior', gamme['specs_ext'])
                y -= block_gap
            if gamme.get('specs_int'):
                y = draw_spec_block(y, 'Intérieur' if is_fr else 'Interior', gamme['specs_int'])
            y -= 0.55 * cm

        # --- Équipements ---
        equip = (gamme.get('equipements_fr') if is_fr else gamme.get('equipements_en'))
        if equip:
            y = section_title(y, 'Équipements inclus' if is_fr else 'Included equipment')
            col_gap = 1 * cm
            col_w = (width - 2 * margin - col_gap) / 2
            mid = (len(equip) + 1) // 2
            cols = [equip[:mid], equip[mid:]]
            check_size = 0.32 * cm
            row_h = 0.72 * cm
            y_start = y
            y_end = y
            for i, col in enumerate(cols):
                yy = y_start
                x = margin + i * (col_w + col_gap)
                c.setFont('Helvetica', 10.5)
                for item in col:
                    check_mark(x, yy, check_size)
                    c.setFillColorRGB(*INK)
                    text_x = x + check_size + 0.35 * cm
                    max_text_w = col_w - check_size - 0.35 * cm
                    if c.stringWidth(item, 'Helvetica', 10.5) > max_text_w:
                        words = item.split(' ')
                        l1, l2 = '', ''
                        for w in words:
                            test = (l1 + ' ' + w).strip()
                            if c.stringWidth(test, 'Helvetica', 10.5) <= max_text_w:
                                l1 = test
                            else:
                                l2 = (l2 + ' ' + w).strip()
                        c.drawString(text_x, yy, l1)
                        if l2:
                            c.drawString(text_x, yy - 0.42 * cm, l2)
                            yy -= 0.42 * cm
                    else:
                        c.drawString(text_x, yy, item)
                    yy -= row_h
                y_end = min(y_end, yy)
            # Espace après équipements : ni collé, ni trop loin des options
            y = y_end + 0.1 * cm

        # --- Options ---
        options = (gamme.get('options_fr') if is_fr else gamme.get('options_en'))
        if options:
            y -= 0.5 * cm  # juste milieu entre "trop proche" et "trop loin"
            y = section_title(y, 'Options')
            c.setFont('Helvetica', 10)
            pill_h = 0.72 * cm
            pad_h = 0.45 * cm
            gap = 0.35 * cm
            radius = 0.2 * cm
            x = margin
            y = ensure_space(y, pill_h + 0.3 * cm)
            for opt in options:
                pw = c.stringWidth(opt, 'Helvetica', 10) + 2 * pad_h
                if x + pw > width - margin:
                    x = margin
                    y -= pill_h + gap
                    y = ensure_space(y, pill_h + 0.3 * cm)
                c.setFillColorRGB(*PANEL)
                c.roundRect(x, y - pill_h, pw, pill_h, radius, fill=1, stroke=0)
                c.setFillColorRGB(*INK)
                c.drawCentredString(x + pw / 2, y - pill_h * 0.63, opt)
                x += pw + gap

        c.showPage()
        c.save()
        pdf_data = buffer.getvalue()
        buffer.close()

        filename = 'catalogue-%s-%s.pdf' % (slug, 'fr' if is_fr else 'en')
        return request.make_response(
            pdf_data,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', 'attachment; filename="%s"' % filename),
            ],
        )