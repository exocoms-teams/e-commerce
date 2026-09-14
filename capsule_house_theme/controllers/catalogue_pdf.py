# -*- coding: utf-8 -*-
import io

from odoo import http
from odoo.http import request

from ..data_definition import GAMMES_DATA


class CapsuleHouseCataloguePdf(http.Controller):
    """Génère un catalogue PDF à la volée pour chaque gamme (CH-35),
    à partir des données réelles de GAMMES_DATA — toujours à jour,
    sans dépendre d'un fichier PDF fourni manuellement par l'équipe
    marketing (option B, décidée avec hamza03 le 2026-09-11).
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

        # Palette reprise de variables.css
        INK = (0.11, 0.14, 0.13)
        TERRACOTTA = (0.76, 0.41, 0.31)
        PANEL = (0.96, 0.94, 0.91)
        GRAY = (0.45, 0.45, 0.45)
        GREEN = (0.2, 0.55, 0.35)

        def new_page_header():
            """Bandeau titre en haut de chaque page (répété si contenu
            déborde sur plusieurs pages)."""
            c.setFillColorRGB(*INK)
            c.rect(0, height - 3.5 * cm, width, 3.5 * cm, fill=1, stroke=0)
            c.setFillColorRGB(1, 1, 1)
            c.setFont('Helvetica-Bold', 20)
            c.drawString(margin, height - 1.6 * cm, 'Capsule House')
            c.setFillColorRGB(*TERRACOTTA)
            c.setFont('Helvetica-Bold', 15)
            c.drawString(margin, height - 2.4 * cm, gamme['name'])
            c.setFillColorRGB(1, 1, 1)
            c.setFont('Helvetica', 10)
            tagline = gamme['tagline_fr'] if is_fr else gamme['tagline_en']
            c.drawString(margin, height - 3.05 * cm, tagline)
            return height - 4.5 * cm

        def ensure_space(y_pos, needed):
            """Nouvelle page si l'espace restant est insuffisant."""
            if y_pos - needed < margin:
                c.showPage()
                return new_page_header()
            return y_pos

        def section_title(y_pos, text):
            y_pos = ensure_space(y_pos, 1.2 * cm)
            c.setFillColorRGB(*INK)
            c.setFont('Helvetica-Bold', 14)
            c.drawString(margin, y_pos, text)
            c.setStrokeColorRGB(*TERRACOTTA)
            c.setLineWidth(2)
            c.line(margin, y_pos - 0.15 * cm, margin + 2.5 * cm, y_pos - 0.15 * cm)
            return y_pos - 0.9 * cm

        y = new_page_header()

        # --- Formats : 3 cartes côte à côte ---
        if gamme.get('formats'):
            y = section_title(y, 'Formats' if is_fr else 'Formats')
            card_w = (width - 2 * margin - 1 * cm) / 3
            card_h = 2.4 * cm
            y = ensure_space(y, card_h + 0.3 * cm)
            x = margin
            for fmt in gamme['formats']:
                c.setFillColorRGB(*PANEL)
                c.roundRect(x, y - card_h, card_w, card_h, 4, fill=1, stroke=0)
                c.setFillColorRGB(*INK)
                c.setFont('Helvetica-Bold', 11)
                c.drawString(x + 0.3 * cm, y - 0.6 * cm, fmt['name'])
                c.setFillColorRGB(*GRAY)
                c.setFont('Helvetica', 9)
                surface = fmt['surface_fr'] if is_fr else fmt['surface_en']
                note = fmt['note_fr'] if is_fr else fmt['note_en']
                c.drawString(x + 0.3 * cm, y - 1.2 * cm, surface)
                c.drawString(x + 0.3 * cm, y - 1.7 * cm, note)
                x += card_w + 0.5 * cm
            y -= card_h + 0.8 * cm

        # --- Spécifications techniques : 2 colonnes ---
        if gamme.get('specs_ext') or gamme.get('specs_int'):
            y = section_title(y, 'Spécifications techniques' if is_fr else 'Technical specifications')
            col_w = (width - 2 * margin - 1 * cm) / 2
            y_start = y

            def draw_spec_col(x, title, rows):
                yy = y_start
                c.setFillColorRGB(*GRAY)
                c.setFont('Helvetica-Bold', 9)
                c.drawString(x, yy, title.upper())
                yy -= 0.5 * cm
                c.setFont('Helvetica', 10)
                for row in rows:
                    label = row['label_fr'] if is_fr else row['label_en']
                    value = row['value_fr'] if is_fr else row['value_en']
                    c.setFillColorRGB(*GRAY)
                    c.drawString(x, yy, label)
                    c.setFillColorRGB(*INK)
                    c.drawRightString(x + col_w, yy, value)
                    c.setStrokeColorRGB(0.85, 0.85, 0.85)
                    c.line(x, yy - 0.15 * cm, x + col_w, yy - 0.15 * cm)
                    yy -= 0.65 * cm
                return yy

            y_left = draw_spec_col(margin, 'Extérieur' if is_fr else 'Exterior', gamme.get('specs_ext', []))
            y_right = draw_spec_col(margin + col_w + 1 * cm, 'Intérieur' if is_fr else 'Interior', gamme.get('specs_int', []))
            y = min(y_left, y_right) - 0.5 * cm

        # --- Équipements inclus : 2 colonnes avec coche ---
        equip = (gamme.get('equipements_fr') if is_fr else gamme.get('equipements_en'))
        if equip:
            y = section_title(y, 'Équipements inclus' if is_fr else 'Included equipment')
            col_w = (width - 2 * margin - 1 * cm) / 2
            mid = (len(equip) + 1) // 2
            cols = [equip[:mid], equip[mid:]]
            y_start = y
            y_end = y
            for i, col in enumerate(cols):
                yy = y_start
                x = margin + i * (col_w + 1 * cm)
                c.setFont('Helvetica', 10)
                for item in col:
                    c.setFillColorRGB(*GREEN)
                    c.drawString(x, yy, u'\u2713')
                    c.setFillColorRGB(*INK)
                    c.drawString(x + 0.5 * cm, yy, item)
                    yy -= 0.6 * cm
                y_end = min(y_end, yy)
            y = y_end - 0.4 * cm

        # --- Options : puces arrondies ---
        options = (gamme.get('options_fr') if is_fr else gamme.get('options_en'))
        if options:
            y = section_title(y, 'Options')
            x = margin
            c.setFont('Helvetica', 9)
            for opt in options:
                text_width = c.stringWidth(opt, 'Helvetica', 9)
                pill_w = text_width + 0.6 * cm
                if x + pill_w > width - margin:
                    x = margin
                    y -= 0.9 * cm
                    y = ensure_space(y, 0.9 * cm)
                c.setFillColorRGB(*PANEL)
                c.roundRect(x, y - 0.55 * cm, pill_w, 0.55 * cm, 8, fill=1, stroke=0)
                c.setFillColorRGB(*INK)
                c.drawString(x + 0.3 * cm, y - 0.4 * cm, opt)
                x += pill_w + 0.3 * cm

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