# -*- coding: utf-8 -*-
import io

from odoo import http
from odoo.http import request

from ..data_definition import GAMMES_DATA


class CapsuleHouseCataloguePdf(http.Controller):
    """Génère un catalogue PDF à la volée pour chaque gamme (CH-35),
    à partir des données réelles de GAMMES_DATA — toujours à jour,
    sans dépendre d'un fichier PDF fourni manuellement par l'équipe
    marketing (option B, décidée avec hamza03 le 2026-09-11 : accès
    Jira/équipe marketing non disponible pour fournir les PDF finaux).
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

        # Bandeau titre
        c.setFillColorRGB(0.11, 0.14, 0.13)
        c.rect(0, height - 4 * cm, width, 4 * cm, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont('Helvetica-Bold', 24)
        c.drawString(2 * cm, height - 2.5 * cm, 'Capsule House')
        c.setFillColorRGB(0.76, 0.41, 0.31)
        c.setFont('Helvetica-Bold', 18)
        c.drawString(2 * cm, height - 3.3 * cm, gamme['name'])

        y = height - 5.5 * cm
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont('Helvetica', 12)
        tagline = gamme['tagline_fr'] if is_fr else gamme['tagline_en']
        c.drawString(2 * cm, y, tagline)
        y -= 1 * cm

        def check_page_break(y_pos):
            if y_pos < 3 * cm:
                c.showPage()
                c.setFont('Helvetica', 11)
                return height - 3 * cm
            return y_pos

        if gamme.get('formats'):
            c.setFont('Helvetica-Bold', 13)
            c.drawString(2 * cm, y, 'Formats')
            y -= 0.7 * cm
            c.setFont('Helvetica', 11)
            for fmt in gamme['formats']:
                surface = fmt['surface_fr'] if is_fr else fmt['surface_en']
                note = fmt['note_fr'] if is_fr else fmt['note_en']
                c.drawString(2.3 * cm, y, "- %s : %s (%s)" % (fmt['name'], surface, note))
                y -= 0.55 * cm
                y = check_page_break(y)
            y -= 0.5 * cm

        if gamme.get('equipements_fr'):
            items = gamme['equipements_fr'] if is_fr else gamme['equipements_en']
            c.setFont('Helvetica-Bold', 13)
            c.drawString(2 * cm, y, 'Équipements inclus' if is_fr else 'Included equipment')
            y -= 0.7 * cm
            c.setFont('Helvetica', 11)
            for item in items:
                c.drawString(2.3 * cm, y, "- %s" % item)
                y -= 0.55 * cm
                y = check_page_break(y)

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