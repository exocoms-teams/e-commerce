# -*- coding: utf-8 -*-
import io
import math

from odoo import http
from odoo.http import request

from ..data_definition import GAMMES_DATA


class CapsuleHouseCataloguePdf(http.Controller):
    """Génère un catalogue PDF à la volée pour chaque gamme (CH-35),
    à partir de GAMMES_DATA — toujours à jour (option B, décidée avec
    hamza03 le 2026-09-11).

    Icônes dessinées directement en vectoriel avec reportlab (pas de
    police FontAwesome externe, dont l'API de chargement s'est révélée
    instable selon la version d'Odoo) : résultat visuellement proche
    du site, sans dépendance fragile.
    """

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

        # ------------------------------------------------------------------
        # ICÔNES vectorielles (dessinées, jamais une police externe)
        # ------------------------------------------------------------------
        def icon_cube(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            s = size
            c.line(x, y, x + s * 0.5, y + s * 0.25)
            c.line(x + s * 0.5, y + s * 0.25, x + s, y)
            c.line(x, y, x, y + s * 0.6)
            c.line(x + s, y, x + s, y + s * 0.6)
            c.line(x, y + s * 0.6, x + s * 0.5, y + s * 0.85)
            c.line(x + s, y + s * 0.6, x + s * 0.5, y + s * 0.85)
            c.line(x + s * 0.5, y + s * 0.25, x + s * 0.5, y + s * 0.85)

        def icon_factory(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            s = size
            c.rect(x, y, s, s * 0.55)
            c.line(x, y + s * 0.55, x + s * 0.3, y + s * 0.85)
            c.line(x + s * 0.3, y + s * 0.55, x + s * 0.3, y + s * 0.85)
            c.line(x + s * 0.3, y + s * 0.85, x + s * 0.55, y + s * 0.65)
            c.line(x + s * 0.55, y + s * 0.65, x + s * 0.55, y + s * 0.95)
            c.line(x + s * 0.55, y + s * 0.95, x + s * 0.8, y + s * 0.7)
            c.line(x + s * 0.8, y + s * 0.7, x + s * 0.8, y + s * 0.55)

        def icon_shield(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            s = size
            p = c.beginPath()
            p.moveTo(x + s * 0.5, y + s)
            p.lineTo(x + s, y + s * 0.75)
            p.lineTo(x + s, y + s * 0.25)
            p.lineTo(x + s * 0.5, y)
            p.lineTo(x, y + s * 0.25)
            p.lineTo(x, y + s * 0.75)
            p.close()
            c.drawPath(p, stroke=1, fill=0)

        def icon_bath(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            s = size
            c.roundRect(x, y, s, s * 0.45, s * 0.15, stroke=1, fill=0)
            c.line(x + s * 0.15, y + s * 0.45, x + s * 0.15, y + s * 0.65)
            c.circle(x + s * 0.15, y + s * 0.72, s * 0.07, stroke=1, fill=0)

        def icon_bulb(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.2)
            s = size
            c.circle(x + s * 0.5, y + s * 0.6, s * 0.32, stroke=1, fill=0)
            c.line(x + s * 0.38, y + s * 0.18, x + s * 0.62, y + s * 0.18)
            c.line(x + s * 0.4, y + s * 0.06, x + s * 0.6, y + s * 0.06)
            c.line(x + s * 0.5, y, x + s * 0.5, y + s * 0.06)

        def icon_clock(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            s = size
            c.circle(x + s * 0.5, y + s * 0.5, s * 0.48, stroke=1, fill=0)
            c.line(x + s * 0.5, y + s * 0.5, x + s * 0.5, y + s * 0.78)
            c.line(x + s * 0.5, y + s * 0.5, x + s * 0.72, y + s * 0.5)

        def icon_bolt(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setFillColorRGB(*color)
            s = size
            p = c.beginPath()
            p.moveTo(x + s * 0.55, y + s)
            p.lineTo(x + s * 0.15, y + s * 0.4)
            p.lineTo(x + s * 0.42, y + s * 0.4)
            p.lineTo(x + s * 0.3, y)
            p.lineTo(x + s * 0.75, y + s * 0.62)
            p.lineTo(x + s * 0.48, y + s * 0.62)
            p.close()
            c.drawPath(p, stroke=0, fill=1)

        def icon_expand(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            s = size
            arm = s * 0.3
            for cx, cy, dx, dy in [
                (x, y, 1, 1), (x + s, y, -1, 1),
                (x, y + s, 1, -1), (x + s, y + s, -1, -1),
            ]:
                c.line(cx, cy, cx + arm * dx, cy)
                c.line(cx, cy, cx, cy + arm * dy)

        def icon_droplet(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            s = size
            p = c.beginPath()
            p.moveTo(x + s * 0.5, y + s)
            p.curveTo(x + s * 0.9, y + s * 0.4, x + s * 0.9, y, x + s * 0.5, y)
            p.curveTo(x + s * 0.1, y, x + s * 0.1, y + s * 0.4, x + s * 0.5, y + s)
            p.close()
            c.drawPath(p, stroke=1, fill=0)

        def icon_building(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.1)
            s = size
            c.rect(x + s * 0.15, y, s * 0.7, s, stroke=1, fill=0)
            for row in range(3):
                for col in range(2):
                    wx = x + s * 0.28 + col * s * 0.28
                    wy = y + s * 0.15 + row * s * 0.28
                    c.rect(wx, wy, s * 0.14, s * 0.14, stroke=1, fill=0)

        def icon_truck(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.2)
            s = size
            c.rect(x, y + s * 0.25, s * 0.55, s * 0.4, stroke=1, fill=0)
            c.rect(x + s * 0.55, y + s * 0.35, s * 0.3, s * 0.3, stroke=1, fill=0)
            c.circle(x + s * 0.18, y + s * 0.2, s * 0.1, stroke=1, fill=0)
            c.circle(x + s * 0.68, y + s * 0.2, s * 0.1, stroke=1, fill=0)

        def icon_generic_square(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            c.roundRect(x, y, size, size, size * 0.15, stroke=1, fill=0)

        def icon_tree(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            s = size
            c.circle(x + s * 0.5, y + s * 0.65, s * 0.35, stroke=1, fill=0)
            c.line(x + s * 0.5, y + s * 0.3, x + s * 0.5, y)

        def icon_sun(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.2)
            s = size
            cx, cy, r = x + s * 0.5, y + s * 0.5, s * 0.25
            c.circle(cx, cy, r, stroke=1, fill=0)
            for i in range(8):
                a = i * math.pi / 4
                x1, y1 = cx + r * 1.3 * math.cos(a), cy + r * 1.3 * math.sin(a)
                x2, y2 = cx + r * 1.7 * math.cos(a), cy + r * 1.7 * math.sin(a)
                c.line(x1, y1, x2, y2)

        def icon_plug(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            s = size
            c.roundRect(x + s * 0.2, y + s * 0.3, s * 0.6, s * 0.5, s * 0.1, stroke=1, fill=0)
            c.line(x + s * 0.35, y + s * 0.3, x + s * 0.35, y)
            c.line(x + s * 0.65, y + s * 0.3, x + s * 0.65, y)
            c.line(x + s * 0.5, y + s * 0.8, x + s * 0.5, y + s)

        def icon_volume_off(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            s = size
            p = c.beginPath()
            p.moveTo(x, y + s * 0.35)
            p.lineTo(x + s * 0.3, y + s * 0.35)
            p.lineTo(x + s * 0.55, y + s * 0.1)
            p.lineTo(x + s * 0.55, y + s * 0.9)
            p.lineTo(x + s * 0.3, y + s * 0.65)
            p.lineTo(x, y + s * 0.65)
            p.close()
            c.drawPath(p, stroke=1, fill=0)
            c.line(x + s * 0.7, y + s * 0.35, x + s, y + s * 0.65)
            c.line(x + s, y + s * 0.35, x + s * 0.7, y + s * 0.65)

        def icon_paint(x, y, size, color):
            c.setStrokeColorRGB(*color)
            c.setLineWidth(1.3)
            s = size
            c.roundRect(x + s * 0.1, y + s * 0.5, s * 0.5, s * 0.35, s * 0.08, stroke=1, fill=0)
            c.line(x + s * 0.35, y, x + s * 0.6, y + s * 0.5)
            c.line(x + s * 0.6, y, x + s * 0.85, y + s * 0.5)

        ICON_MAP = {
            'fa-cubes': icon_cube, 'fa-cube': icon_cube,
            'fa-industry': icon_factory,
            'fa-square-o': icon_generic_square,
            'fa-shield': icon_shield,
            'fa-bath': icon_bath,
            'fa-lightbulb-o': icon_bulb,
            'fa-clock-o': icon_clock,
            'fa-bolt': icon_bolt,
            'fa-arrows-alt': icon_expand,
            'fa-tint': icon_droplet,
            'fa-building-o': icon_building,
            'fa-truck': icon_truck,
            'fa-refresh': icon_expand,
            'fa-thermometer-half': icon_generic_square,
            'fa-tree': icon_tree,
            'fa-sun-o': icon_sun,
            'fa-plug': icon_plug,
            'fa-volume-off': icon_volume_off,
            'fa-compress': icon_expand,
            'fa-paint-brush': icon_paint,
            'fa-arrows-v': icon_expand,
        }

        def draw_icon(icon_key, x, y, size, color=TERRACOTTA):
            fn = ICON_MAP.get(icon_key, icon_generic_square)
            fn(x, y, size, color)

        def check_mark(x, y, size, color=GREEN):
            """Coche verte dans un cercle plein, taille et alignement
            calés sur la baseline du texte (identique au rendu du site)."""
            c.setFillColorRGB(*color)
            cy = y + size / 2
            c.circle(x + size / 2, cy, size / 2, stroke=0, fill=1)
            c.setStrokeColorRGB(*WHITE)
            c.setLineWidth(1.1)
            c.setLineCap(1)
            c.line(x + size * 0.28, cy, x + size * 0.44, cy - size * 0.16)
            c.line(x + size * 0.44, cy - size * 0.16, x + size * 0.72, cy + size * 0.18)

        # ------------------------------------------------------------------
        # MISE EN PAGE
        # ------------------------------------------------------------------
        def new_page_header():
            c.setFillColorRGB(*INK)
            c.rect(0, height - 3.5 * cm, width, 3.5 * cm, fill=1, stroke=0)
            c.setFillColorRGB(*WHITE)
            c.setFont('Helvetica-Bold', 20)
            c.drawString(margin, height - 1.6 * cm, 'Capsule House')
            c.setFillColorRGB(*TERRACOTTA)
            c.setFont('Helvetica-Bold', 15)
            c.drawString(margin, height - 2.4 * cm, gamme['name'])
            c.setFillColorRGB(*WHITE)
            c.setFont('Helvetica', 10)
            tagline = gamme['tagline_fr'] if is_fr else gamme['tagline_en']
            c.drawString(margin, height - 3.05 * cm, tagline)
            return height - 4.5 * cm

        def ensure_space(y_pos, needed):
            if y_pos - needed < margin:
                c.showPage()
                return new_page_header()
            return y_pos

        def section_title(y_pos, text, centered=False):
            y_pos = ensure_space(y_pos, 1.2 * cm)
            c.setFillColorRGB(*INK)
            c.setFont('Helvetica-Bold', 14)
            text_w = c.stringWidth(text, 'Helvetica-Bold', 14)
            x = (width - text_w) / 2 if centered else margin
            c.drawString(x, y_pos, text)
            c.setStrokeColorRGB(*TERRACOTTA)
            c.setLineWidth(2)
            c.line(x, y_pos - 0.15 * cm, x + text_w, y_pos - 0.15 * cm)
            return y_pos - 1 * cm

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
            c.setFont('Helvetica-Bold', 9)
            label = 'PERFORMANCES'
            c.drawString((width - c.stringWidth(label, 'Helvetica-Bold', 9)) / 2, y, label)
            y -= 0.6 * cm
            c.setFillColorRGB(*INK)
            c.setFont('Helvetica-Bold', 15)
            c.drawString((width - c.stringWidth(title, 'Helvetica-Bold', 15)) / 2, y, title)
            y -= 1.1 * cm

            perfs = gamme['performances']
            col_count = 2
            gap = 0.6 * cm
            card_w = (width - 2 * margin - gap * (col_count - 1)) / col_count
            card_h = 2.9 * cm
            pad = 0.4 * cm
            icon_size = 0.55 * cm
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
                    c.setFont('Helvetica-Bold', 10.5)
                    ptitle = perf['title_fr'] if is_fr else perf['title_en']
                    c.drawString(x + pad, y - pad - icon_size - 0.55 * cm, ptitle)
                    c.setFillColorRGB(*GRAY)
                    c.setFont('Helvetica', 8.5)
                    pdesc = perf['desc_fr'] if is_fr else perf['desc_en']
                    words = pdesc.split(' ')
                    lines, cur = [], ''
                    max_w = card_w - 2 * pad
                    for w in words:
                        test = (cur + ' ' + w).strip()
                        if c.stringWidth(test, 'Helvetica', 8.5) > max_w:
                            lines.append(cur)
                            cur = w
                        else:
                            cur = test
                    lines.append(cur)
                    yy = y - pad - icon_size - 1.05 * cm
                    for line in lines[:3]:
                        c.drawString(x + pad, yy, line)
                        yy -= 0.38 * cm
                    x += card_w + gap
                y -= card_h + 0.5 * cm
            y -= 0.3 * cm

        # --- Formats ---
        if gamme.get('formats'):
            y = section_title(y, 'Formats')
            fmts = gamme['formats']
            gap = 0.5 * cm
            card_w = 4.6 * cm
            card_h = 2.5 * cm
            row_w = len(fmts) * card_w + (len(fmts) - 1) * gap
            x = (width - row_w) / 2
            y = ensure_space(y, card_h + 0.3 * cm)
            for fmt in fmts:
                c.setFillColorRGB(*PANEL)
                c.roundRect(x, y - card_h, card_w, card_h, 4, fill=1, stroke=0)
                c.setFillColorRGB(*INK)
                c.setFont('Helvetica-Bold', 11)
                c.drawCentredString(x + card_w / 2, y - 0.7 * cm, fmt['name'])
                c.setFillColorRGB(*GRAY)
                c.setFont('Helvetica', 9)
                surface = fmt['surface_fr'] if is_fr else fmt['surface_en']
                note = fmt['note_fr'] if is_fr else fmt['note_en']
                c.drawCentredString(x + card_w / 2, y - 1.35 * cm, surface)
                c.drawCentredString(x + card_w / 2, y - 1.85 * cm, note)
                x += card_w + gap
            y -= card_h + 0.9 * cm

        # --- Spécifications ---
        if gamme.get('specs_ext') or gamme.get('specs_int'):
            y = section_title(y, 'Spécifications techniques' if is_fr else 'Technical specifications')
            full_w = width - 2 * margin

            def draw_spec_block(y_pos, title, rows):
                y_pos = ensure_space(y_pos, 0.9 * cm)
                c.setFillColorRGB(*GRAY)
                c.setFont('Helvetica-Bold', 9)
                c.drawString(margin, y_pos, title.upper())
                y_pos -= 0.6 * cm
                c.setFont('Helvetica', 10)
                for row in rows:
                    y_pos = ensure_space(y_pos, 0.65 * cm)
                    label = row['label_fr'] if is_fr else row['label_en']
                    value = row['value_fr'] if is_fr else row['value_en']
                    c.setFillColorRGB(*GRAY)
                    c.drawString(margin, y_pos, label)
                    c.setFillColorRGB(*INK)
                    c.setFont('Helvetica-Bold', 10)
                    c.drawRightString(margin + full_w, y_pos, value)
                    c.setFont('Helvetica', 10)
                    c.setStrokeColorRGB(*LIGHT_BORDER)
                    c.line(margin, y_pos - 0.18 * cm, margin + full_w, y_pos - 0.18 * cm)
                    y_pos -= 0.68 * cm
                return y_pos

            if gamme.get('specs_ext'):
                y = draw_spec_block(y, 'Extérieur' if is_fr else 'Exterior', gamme['specs_ext'])
                y -= 0.6 * cm
            if gamme.get('specs_int'):
                y = draw_spec_block(y, 'Intérieur' if is_fr else 'Interior', gamme['specs_int'])
            y -= 0.5 * cm

        # --- Équipements ---
        equip = (gamme.get('equipements_fr') if is_fr else gamme.get('equipements_en'))
        if equip:
            y = section_title(y, 'Équipements inclus' if is_fr else 'Included equipment')
            col_gap = 1 * cm
            col_w = (width - 2 * margin - col_gap) / 2
            mid = (len(equip) + 1) // 2
            cols = [equip[:mid], equip[mid:]]
            check_size = 0.3 * cm
            row_h = 0.7 * cm
            y_start = y
            y_end = y
            for i, col in enumerate(cols):
                yy = y_start
                x = margin + i * (col_w + col_gap)
                c.setFont('Helvetica', 10)
                for item in col:
                    check_mark(x, yy - check_size * 0.32, check_size)
                    c.setFillColorRGB(*INK)
                    text_x = x + check_size + 0.3 * cm
                    max_text_w = col_w - check_size - 0.3 * cm
                    if c.stringWidth(item, 'Helvetica', 10) > max_text_w:
                        words = item.split(' ')
                        l1, l2 = '', ''
                        for w in words:
                            test = (l1 + ' ' + w).strip()
                            if c.stringWidth(test, 'Helvetica', 10) <= max_text_w:
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
            y = y_end - 0.3 * cm

        # --- Options : alignées à gauche comme les autres sections ---
        options = (gamme.get('options_fr') if is_fr else gamme.get('options_en'))
        if options:
            y = section_title(y, 'Options')
            c.setFont('Helvetica', 9.5)
            pill_h = 0.7 * cm
            pad_h = 0.45 * cm
            gap = 0.35 * cm
            radius = 0.2 * cm
            x = margin
            y = ensure_space(y, pill_h + 0.3 * cm)
            for opt in options:
                pw = c.stringWidth(opt, 'Helvetica', 9.5) + 2 * pad_h
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