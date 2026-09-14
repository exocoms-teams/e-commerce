# -*- coding: utf-8 -*-
import io
import os

from odoo import http
from odoo.http import request
from odoo.modules.module import get_module_resource

from ..data_definition import GAMMES_DATA


class CapsuleHouseCataloguePdf(http.Controller):
    """Génère un catalogue PDF à la volée pour chaque gamme (CH-35),
    à partir des données réelles de GAMMES_DATA — toujours à jour,
    sans dépendre d'un fichier PDF fourni manuellement par l'équipe
    marketing (option B, décidée avec hamza03 le 2026-09-11).

    Reprend la mise en page de la page web (/nos-gammes/<slug>) :
    section Performances, formats en cartes, specs en 2 blocs empilés,
    équipements avec coche verte, options en pastilles centrées.
    Tente d'utiliser la police FontAwesome déjà livrée avec Odoo (web)
    pour des icônes visuellement identiques au site ; si le fichier
    n'est pas trouvé sur cette instance, se rabat silencieusement sur
    des puces dessinées à la main (jamais d'erreur bloquante pour un
    simple manque d'icône).
    """

    _FA_REGISTERED = None  # cache : None = pas encore tenté, True/False = résultat

    def _register_fontawesome(self):
        """Enregistre la police FontAwesome pour reportlab, une seule
        fois par process. Retourne True si disponible, False sinon.
        """
        if CapsuleHouseCataloguePdf._FA_REGISTERED is not None:
            return CapsuleHouseCataloguePdf._FA_REGISTERED
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            fa_path = get_module_resource(
                'web', 'static', 'src', 'libs', 'fontawesome', 'fonts',
                'fontawesome-webfont.ttf',
            )
            if fa_path and os.path.exists(fa_path):
                pdfmetrics.registerFont(TTFont('FontAwesome', fa_path))
                CapsuleHouseCataloguePdf._FA_REGISTERED = True
            else:
                CapsuleHouseCataloguePdf._FA_REGISTERED = False
        except Exception:
            CapsuleHouseCataloguePdf._FA_REGISTERED = False
        return CapsuleHouseCataloguePdf._FA_REGISTERED

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
        has_fa = self._register_fontawesome()
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        margin = 2 * cm

        # Palette légèrement plus saturée que la version précédente,
        # pour un rendu plus proche de l'éclat des couleurs du site
        # (variables.css : --ch-ink, --ch-terracotta, --ch-panel).
        INK = (0.06, 0.09, 0.08)
        TERRACOTTA = (0.82, 0.35, 0.22)
        PANEL = (0.96, 0.92, 0.87)
        GRAY = (0.42, 0.42, 0.42)
        GREEN = (0.12, 0.52, 0.32)
        WHITE = (1, 1, 1)

        def fa_icon(x, y, codepoint, size=11, color=TERRACOTTA):
            """Dessine une icône FontAwesome si la police est
            disponible, sinon une puce ronde de secours (jamais de
            plantage pour un simple manque d'icône)."""
            if has_fa:
                c.setFillColorRGB(*color)
                c.setFont('FontAwesome', size)
                c.drawString(x, y, codepoint)
            else:
                c.setFillColorRGB(*color)
                c.circle(x + size / 2 / 72 * 2.54, y + size / 3 / 72 * 2.54, 0.15 * cm, fill=1, stroke=0)

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
            # Le trait souligne EXACTEMENT la largeur du texte, jamais
            # une longueur fixe arbitraire (corrige le rendu "mal
            # délimité" signalé).
            c.line(x, y_pos - 0.15 * cm, x + text_w, y_pos - 0.15 * cm)
            return y_pos - 0.9 * cm

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
            y -= 1 * cm

            perfs = gamme['performances']
            col_count = 3
            gap = 0.5 * cm
            card_w = (width - 2 * margin - gap * (col_count - 1)) / col_count
            card_h = 2.6 * cm
            for i in range(0, len(perfs), col_count):
                row = perfs[i:i + col_count]
                y = ensure_space(y, card_h + 0.4 * cm)
                x = margin
                for perf in row:
                    c.setStrokeColorRGB(0.85, 0.85, 0.85)
                    c.setFillColorRGB(*WHITE)
                    c.roundRect(x, y - card_h, card_w, card_h, 4, fill=1, stroke=1)
                    fa_icon(x + 0.3 * cm, y - 0.55 * cm, u'\uf021', size=13)
                    c.setFillColorRGB(*INK)
                    c.setFont('Helvetica-Bold', 10)
                    ptitle = perf['title_fr'] if is_fr else perf['title_en']
                    c.drawString(x + 0.3 * cm, y - 1.1 * cm, ptitle)
                    c.setFillColorRGB(*GRAY)
                    c.setFont('Helvetica', 8)
                    pdesc = perf['desc_fr'] if is_fr else perf['desc_en']
                    # Retour à la ligne simple si la description est longue
                    words = pdesc.split(' ')
                    lines, cur = [], ''
                    for w in words:
                        test = (cur + ' ' + w).strip()
                        if c.stringWidth(test, 'Helvetica', 8) > card_w - 0.6 * cm:
                            lines.append(cur)
                            cur = w
                        else:
                            cur = test
                    lines.append(cur)
                    yy = y - 1.6 * cm
                    for line in lines[:3]:
                        c.drawString(x + 0.3 * cm, yy, line)
                        yy -= 0.4 * cm
                    x += card_w + gap
                y -= card_h + 0.5 * cm
            y -= 0.3 * cm

        # --- Formats : cartes centrées ---
        if gamme.get('formats'):
            y = section_title(y, 'Formats')
            fmts = gamme['formats']
            gap = 0.5 * cm
            card_w = 4.5 * cm
            card_h = 2.4 * cm
            row_w = len(fmts) * card_w + (len(fmts) - 1) * gap
            x = (width - row_w) / 2  # centrage horizontal de la rangée
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
                c.drawCentredString(x + card_w / 2, y - 1.3 * cm, surface)
                c.drawCentredString(x + card_w / 2, y - 1.8 * cm, note)
                x += card_w + gap
            y -= card_h + 0.8 * cm

        # --- Spécifications : EMPILÉES (Extérieur puis Intérieur), pas côte à côte ---
        if gamme.get('specs_ext') or gamme.get('specs_int'):
            y = section_title(y, 'Spécifications techniques' if is_fr else 'Technical specifications')
            full_w = width - 2 * margin

            def draw_spec_block(y_pos, title, rows):
                y_pos = ensure_space(y_pos, 0.8 * cm)
                c.setFillColorRGB(*GRAY)
                c.setFont('Helvetica-Bold', 9)
                c.drawString(margin, y_pos, title.upper())
                y_pos -= 0.55 * cm
                c.setFont('Helvetica', 10)
                for row in rows:
                    y_pos = ensure_space(y_pos, 0.65 * cm)
                    label = row['label_fr'] if is_fr else row['label_en']
                    value = row['value_fr'] if is_fr else row['value_en']
                    c.setFillColorRGB(*GRAY)
                    c.drawString(margin, y_pos, label)
                    c.setFillColorRGB(*INK)
                    c.drawRightString(margin + full_w, y_pos, value)
                    c.setStrokeColorRGB(0.85, 0.85, 0.85)
                    c.line(margin, y_pos - 0.15 * cm, margin + full_w, y_pos - 0.15 * cm)
                    y_pos -= 0.65 * cm
                return y_pos

            if gamme.get('specs_ext'):
                y = draw_spec_block(y, 'Extérieur' if is_fr else 'Exterior', gamme['specs_ext'])
                y -= 0.5 * cm  # retour à la ligne / espace avant Intérieur
            if gamme.get('specs_int'):
                y = draw_spec_block(y, 'Intérieur' if is_fr else 'Interior', gamme['specs_int'])
            y -= 0.4 * cm

        # --- Équipements : coche verte façon site ---
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
                    if has_fa:
                        fa_icon(x, yy - 0.35 * cm, u'\uf058', size=11, color=GREEN)
                    else:
                        c.setFillColorRGB(*GREEN)
                        c.circle(x + 0.15 * cm, yy - 0.28 * cm, 0.15 * cm, fill=1, stroke=0)
                        c.setFillColorRGB(*WHITE)
                        c.setFont('Helvetica-Bold', 7)
                        c.drawCentredString(x + 0.15 * cm, yy - 0.32 * cm, u'\u2713')
                        c.setFont('Helvetica', 10)
                    c.setFillColorRGB(*INK)
                    c.drawString(x + 0.55 * cm, yy, item)
                    yy -= 0.6 * cm
                y_end = min(y_end, yy)
            y = y_end - 0.4 * cm

        # --- Options : pastilles centrées ---
        options = (gamme.get('options_fr') if is_fr else gamme.get('options_en'))
        if options:
            y = section_title(y, 'Options', centered=True)
            c.setFont('Helvetica', 9)
            pill_h = 0.55 * cm
            gap = 0.3 * cm
            # Calcule la largeur totale pour centrer la rangée de pastilles
            widths = [c.stringWidth(opt, 'Helvetica', 9) + 0.6 * cm for opt in options]
            total_w = sum(widths) + gap * (len(options) - 1)
            if total_w > width - 2 * margin:
                # Si ça déborde, on revient à un affichage multi-lignes centré
                x = margin
                y = ensure_space(y, pill_h + 0.3 * cm)
                for opt, pw in zip(options, widths):
                    if x + pw > width - margin:
                        x = margin
                        y -= pill_h + 0.3 * cm
                        y = ensure_space(y, pill_h + 0.3 * cm)
                    c.setFillColorRGB(*PANEL)
                    c.roundRect(x, y - pill_h, pw, pill_h, 8, fill=1, stroke=0)
                    c.setFillColorRGB(*INK)
                    c.drawString(x + 0.3 * cm, y - 0.4 * cm, opt)
                    x += pw + gap
            else:
                x = (width - total_w) / 2
                y = ensure_space(y, pill_h + 0.3 * cm)
                for opt, pw in zip(options, widths):
                    c.setFillColorRGB(*PANEL)
                    c.roundRect(x, y - pill_h, pw, pill_h, 8, fill=1, stroke=0)
                    c.setFillColorRGB(*INK)
                    c.drawString(x + 0.3 * cm, y - 0.4 * cm, opt)
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