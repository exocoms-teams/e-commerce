# -*- coding: utf-8 -*-
import io
import os

from odoo import http
from odoo.http import request

from ..data_definition import GAMMES_DATA


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

    Icônes rendues avec le vrai fichier FontAwesome du module `web`.
    Texte rendu avec Inter (variables.css : --font-head/--font-body),
    fichiers statiques embarqués dans ce module
    (static/src/fonts/Inter/static/) — rendu typographiquement
    identique au site plutôt qu'une approximation avec Helvetica.
    Repli automatique sur Helvetica si les fichiers sont introuvables.
    """

    _FA_FONT_PATH = None
    _FA_CHECKED = False
    _INTER_REGISTERED = None

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

    def _register_inter(self):
        if CapsuleHouseCataloguePdf._INTER_REGISTERED is not None:
            return CapsuleHouseCataloguePdf._INTER_REGISTERED
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            base = os.path.join(
                os.path.dirname(__file__), '..', 'static', 'src',
                'fonts', 'Inter', 'static',
            )
            regular = os.path.join(base, 'Inter_18pt-Regular.ttf')
            bold = os.path.join(base, 'Inter_18pt-Bold.ttf')
            if os.path.exists(regular) and os.path.exists(bold):
                pdfmetrics.registerFont(TTFont('Inter', regular))
                pdfmetrics.registerFont(TTFont('Inter-Bold', bold))
                CapsuleHouseCataloguePdf._INTER_REGISTERED = True
            else:
                CapsuleHouseCataloguePdf._INTER_REGISTERED = False
        except Exception:
            CapsuleHouseCataloguePdf._INTER_REGISTERED = False
        return CapsuleHouseCataloguePdf._INTER_REGISTERED

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
        has_inter = self._register_inter()
        FONT = 'Inter' if has_inter else 'Helvetica'
        FONT_BOLD = 'Inter-Bold' if has_inter else 'Helvetica-Bold'

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        margin = 2 * cm

        INK = (0.04, 0.06, 0.05)
        TERRACOTTA = (0.82, 0.35, 0.22)
        PANEL = (0.96, 0.92, 0.87)
        GRAY = (0.35, 0.35, 0.35)
        GREEN = (0.15, 0.55, 0.35)
        WHITE = (1, 1, 1)
        LIGHT_BORDER = (0.82, 0.82, 0.82)

        DEFAULT_FONT = (FONT, 10.5)

        def wrap_text(text, font, size, max_w):
            words = text.split(' ')
            lines, cur = [], ''
            for w in words:
                test = (cur + ' ' + w).strip()
                if c.stringWidth(test, font, size) > max_w and cur:
                    lines.append(cur)
                    cur = w
                else:
                    cur = test
            if cur:
                lines.append(cur)
            return lines

        def draw_icon(icon_key, x, y, size, color=TERRACOTTA,
                      restore_font=DEFAULT_FONT):
            codepoint = FA_CODEPOINTS.get(icon_key)
            if has_fa and codepoint:
                c.setFillColorRGB(*color)
                c.setFont('FontAwesome', size)
                c.drawString(x, y, codepoint)
            else:
                c.setStrokeColorRGB(*color)
                c.setLineWidth(1.2)
                c.roundRect(x, y, size, size, size * 0.15, stroke=1, fill=0)
            c.setFont(*restore_font)

        def check_mark(x, y, size, color=GREEN, restore_font=DEFAULT_FONT):
            if has_fa and 'fa-check-circle' in FA_CODEPOINTS:
                c.setFillColorRGB(*color)
                c.setFont('FontAwesome', size)
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
            c.setFont(*restore_font)

        # ------------------------------------------------------------------
        # MISE EN PAGE
        # ------------------------------------------------------------------
        def new_page_header():
            c.setFillColorRGB(*INK)
            c.rect(0, height - 3.5 * cm, width, 3.5 * cm, fill=1, stroke=0)
            c.setFillColorRGB(*WHITE)
            c.setFont(FONT_BOLD, 21)
            c.drawString(margin, height - 1.6 * cm, 'Capsule House')
            c.setFillColorRGB(*TERRACOTTA)
            c.setFont(FONT_BOLD, 16)
            c.drawString(margin, height - 2.4 * cm, gamme['name'])
            c.setFillColorRGB(*WHITE)
            c.setFont(FONT, 10.5)
            tagline = gamme['tagline_fr'] if is_fr else gamme['tagline_en']
            c.drawString(margin, height - 3.05 * cm, tagline)
            return height - 4.5 * cm

        def ensure_space(y_pos, needed):
            if y_pos - needed < margin:
                c.showPage()
                return new_page_header()
            return y_pos

        def ensure_block(y_pos, needed_height):
            if y_pos - needed_height < margin:
                c.showPage()
                return new_page_header()
            return y_pos

        def section_title(y_pos, text, centered=False):
            c.setFillColorRGB(*INK)
            c.setFont(FONT_BOLD, 15)
            text_w = c.stringWidth(text, FONT_BOLD, 15)
            x = (width - text_w) / 2 if centered else margin
            c.drawString(x, y_pos, text)
            c.setStrokeColorRGB(*TERRACOTTA)
            c.setLineWidth(2)
            c.line(x, y_pos - 0.15 * cm, x + text_w, y_pos - 0.15 * cm)
            c.setFont(*DEFAULT_FONT)
            return y_pos - 1.05 * cm

        y = new_page_header()

        # --- Performances ---
        if gamme.get('performances'):
            perfs = gamme['performances']
            col_count = 2
            gap = 0.6 * cm
            card_w = (width - 2 * margin - gap * (col_count - 1)) / col_count
            card_h = 3 * cm
            pad = 0.4 * cm
            icon_size = 0.6 * cm

            header_block_h = 2 * cm
            y = ensure_block(y, header_block_h + card_h + 0.4 * cm)

            gender = gamme.get('gender')
            if is_fr:
                article, adj = ('Une', 'pensée') if gender == 'f' else ('Un', 'pensé')
                title = "%s %s %s pour le confort absolu" % (article, gamme['name'].lower(), adj)
            else:
                title = "A %s designed for absolute comfort" % gamme['name'].lower()
            c.setFillColorRGB(*TERRACOTTA)
            c.setFont(FONT_BOLD, 9.5)
            label = 'PERFORMANCES'
            c.drawString((width - c.stringWidth(label, FONT_BOLD, 9.5)) / 2, y, label)
            y -= 0.65 * cm
            c.setFillColorRGB(*INK)
            c.setFont(FONT_BOLD, 16)
            c.drawString((width - c.stringWidth(title, FONT_BOLD, 16)) / 2, y, title)
            y -= 1.15 * cm
            c.setFont(*DEFAULT_FONT)

            for i in range(0, len(perfs), col_count):
                row = perfs[i:i + col_count]
                y = ensure_space(y, card_h + 0.4 * cm)
                x = margin
                for perf in row:
                    c.setStrokeColorRGB(*LIGHT_BORDER)
                    c.setFillColorRGB(*WHITE)
                    c.roundRect(x, y - card_h, card_w, card_h, 4, fill=1, stroke=1)
                    draw_icon(perf.get('icon', ''), x + pad, y - pad - icon_size, icon_size,
                              restore_font=(FONT_BOLD, 11))
                    c.setFillColorRGB(*INK)
                    ptitle = perf['title_fr'] if is_fr else perf['title_en']
                    c.drawString(x + pad, y - pad - icon_size - 0.55 * cm, ptitle)
                    c.setFillColorRGB(*GRAY)
                    c.setFont(FONT, 9)
                    pdesc = perf['desc_fr'] if is_fr else perf['desc_en']
                    lines = wrap_text(pdesc, FONT, 9, card_w - 2 * pad)
                    yy = y - pad - icon_size - 1.05 * cm
                    for line in lines[:3]:
                        c.drawString(x + pad, yy, line)
                        yy -= 0.4 * cm
                    c.setFont(*DEFAULT_FONT)
                    x += card_w + gap
                y -= card_h + 0.5 * cm
            y -= 0.3 * cm

        # --- Formats ---
        if gamme.get('formats'):
            fmts = gamme['formats']
            gap = 0.5 * cm
            card_w = 4.7 * cm
            note_max_w = card_w - 0.5 * cm
            card_h = 2.9 * cm
            title_block_h = 1.3 * cm
            y = ensure_block(y, title_block_h + card_h + 0.9 * cm)

            y = section_title(y, 'Formats')
            row_w = len(fmts) * card_w + (len(fmts) - 1) * gap
            x = (width - row_w) / 2
            for fmt in fmts:
                c.setFillColorRGB(*PANEL)
                c.roundRect(x, y - card_h, card_w, card_h, 4, fill=1, stroke=0)
                c.setFillColorRGB(*INK)
                c.setFont(FONT_BOLD, 11.5)
                c.drawCentredString(x + card_w / 2, y - 0.75 * cm, fmt['name'])
                c.setFillColorRGB(*GRAY)
                c.setFont(FONT, 9.5)
                surface = fmt['surface_fr'] if is_fr else fmt['surface_en']
                note = fmt['note_fr'] if is_fr else fmt['note_en']
                c.drawCentredString(x + card_w / 2, y - 1.4 * cm, surface)
                note_lines = wrap_text(note, FONT, 9.5, note_max_w)
                ny = y - 1.9 * cm
                for line in note_lines[:2]:
                    c.drawCentredString(x + card_w / 2, ny, line)
                    ny -= 0.38 * cm
                x += card_w + gap
            c.setFont(*DEFAULT_FONT)
            y -= card_h + 0.9 * cm

        # --- Spécifications ---
        if gamme.get('specs_ext') or gamme.get('specs_int'):
            row_h_est = 0.68 * cm
            block_gap = 0.6 * cm
            n_ext = len(gamme.get('specs_ext') or [])
            n_int = len(gamme.get('specs_int') or [])
            total_needed = 1.3 * cm
            if n_ext:
                total_needed += 0.6 * cm + n_ext * row_h_est + block_gap
            if n_int:
                total_needed += 0.6 * cm + n_int * row_h_est
            y = ensure_block(y, total_needed)

            y = section_title(y, 'Spécifications techniques' if is_fr else 'Technical specifications')
            full_w = width - 2 * margin

            def draw_spec_block(y_pos, title, rows):
                c.setFillColorRGB(*GRAY)
                c.setFont(FONT_BOLD, 9.5)
                c.drawString(margin, y_pos, title.upper())
                y_pos -= 0.6 * cm
                c.setFont(FONT, 10.5)
                for row in rows:
                    label = row['label_fr'] if is_fr else row['label_en']
                    value = row['value_fr'] if is_fr else row['value_en']
                    c.setFillColorRGB(*GRAY)
                    c.drawString(margin, y_pos, label)
                    c.setFillColorRGB(*INK)
                    c.setFont(FONT_BOLD, 10.5)
                    c.drawRightString(margin + full_w, y_pos, value)
                    c.setFont(FONT, 10.5)
                    c.setStrokeColorRGB(*LIGHT_BORDER)
                    c.line(margin, y_pos - 0.18 * cm, margin + full_w, y_pos - 0.18 * cm)
                    y_pos -= row_h_est
                return y_pos

            if gamme.get('specs_ext'):
                y = draw_spec_block(y, 'Extérieur' if is_fr else 'Exterior', gamme['specs_ext'])
                y -= block_gap
            if gamme.get('specs_int'):
                y = draw_spec_block(y, 'Intérieur' if is_fr else 'Interior', gamme['specs_int'])
            c.setFont(*DEFAULT_FONT)
            y -= 0.55 * cm

        # --- Équipements ---
        equip = (gamme.get('equipements_fr') if is_fr else gamme.get('equipements_en'))
        if equip:
            col_gap = 1 * cm
            col_w = (width - 2 * margin - col_gap) / 2
            mid = (len(equip) + 1) // 2
            cols = [equip[:mid], equip[mid:]]
            check_size = 0.32 * cm
            row_h = 0.72 * cm

            title_block_h = 1.3 * cm
            rows_in_longest_col = max(len(cols[0]), len(cols[1]))
            y = ensure_block(y, title_block_h + rows_in_longest_col * row_h)

            y = section_title(y, 'Équipements inclus' if is_fr else 'Included equipment')
            y_start = y
            y_end = y
            for i, col in enumerate(cols):
                yy = y_start
                x = margin + i * (col_w + col_gap)
                for item in col:
                    check_mark(x, yy, check_size, restore_font=DEFAULT_FONT)
                    c.setFillColorRGB(*INK)
                    c.setFont(*DEFAULT_FONT)
                    text_x = x + check_size + 0.35 * cm
                    max_text_w = col_w - check_size - 0.35 * cm
                    item_lines = wrap_text(item, FONT, 10.5, max_text_w)
                    for idx, line in enumerate(item_lines[:2]):
                        c.drawString(text_x, yy - idx * 0.42 * cm, line)
                    if len(item_lines) > 1:
                        yy -= 0.42 * cm
                    yy -= row_h
                y_end = min(y_end, yy)
            y = y_end + 0.1 * cm

        # --- Options ---
        options = (gamme.get('options_fr') if is_fr else gamme.get('options_en'))
        if options:
            y -= 0.5 * cm
            y = ensure_block(y, 1.3 * cm + 0.72 * cm)
            y = section_title(y, 'Options')
            pill_h = 0.72 * cm
            pad_h = 0.45 * cm
            gap = 0.35 * cm
            radius = 0.2 * cm
            x = margin
            c.setFont(FONT, 10)
            for opt in options:
                pw = c.stringWidth(opt, FONT, 10) + 2 * pad_h
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