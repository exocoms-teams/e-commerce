# -*- coding: utf-8 -*-
"""Catalogue PDF Capsule House — Platypus + FontAwesome (glyphes du site)."""

import glob
import os
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from odoo import http
from odoo.http import request
from odoo.modules.module import get_module_path

from ..data_definition import GAMMES_DATA


# =====================================================================
# FONTAWESOME — vrais glyphes du site, emplacement résilient aux
# montées de version d'Odoo (recherche par glob, jamais de crash).
# =====================================================================

FA_CODEPOINTS = {
    'fa-cubes': 0xF1B3, 'fa-cube': 0xF1B2,
    'fa-industry': 0xF275, 'fa-square-o': 0xF096,
    'fa-shield': 0xF132, 'fa-bath': 0xF2CD,
    'fa-lightbulb-o': 0xF0EB, 'fa-clock-o': 0xF017,
    'fa-bolt': 0xF0E7, 'fa-arrows-alt': 0xF0B2,
    'fa-arrows-v': 0xF07D, 'fa-tint': 0xF043,
    'fa-building-o': 0xF0F7, 'fa-truck': 0xF0D1,
    'fa-refresh': 0xF021, 'fa-thermometer-half': 0xF2C9,
    'fa-tree': 0xF1BB, 'fa-sun-o': 0xF185,
    'fa-plug': 0xF1E6, 'fa-volume-off': 0xF026,
    'fa-compress': 0xF066, 'fa-paint-brush': 0xF1FC,
    'fa-lock': 0xF023, 'fa-check': 0xF00C,
}

_FA_FONT_NAME = 'FA-Catalogue'
_fa_ready = None


def _fa_ttf_path():
    web = get_module_path('web')
    if web:
        for pattern in (
            'static/lib/fontawesome/fonts/fontawesome-webfont.ttf',  # Odoo <= 15
            'static/**/fontawesome*/fonts/*.ttf',
            'static/**/FontAwesome*.ttf',
        ):
            found = glob.glob(os.path.join(web, pattern), recursive=True)
            if found:
                return found[0]
    fa = get_module_path('base_fontawesome')  # OCA, toutes versions
    if fa:
        found = glob.glob(os.path.join(fa, 'static', '**', '*.ttf'),
                          recursive=True)
        for path in found:  # préférer la variante "solid"
            if 'solid' in path.lower():
                return path
        if found:
            return found[0]
    return None


def fa_font_ready():
    """Enregistre la police une fois par worker. Jamais de crash."""
    global _fa_ready
    if _fa_ready is None:
        try:
            path = _fa_ttf_path()
            if path:
                pdfmetrics.registerFont(TTFont(_FA_FONT_NAME, path))
            _fa_ready = bool(path)
        except Exception:
            _fa_ready = False
    return _fa_ready


class Icon(Flowable):
    """Glyphe FontAwesome, dessiné avec la police du site."""

    def __init__(self, name, size=12 * mm, color=None):
        super().__init__()
        self.name = name
        self.size = size
        self.color = color or CapsuleCatalogueController.PRIMARY_COLOR
        self.width = self.height = size

    def draw(self):
        c = self.canv
        c.saveState()
        if fa_font_ready() and self.name in FA_CODEPOINTS:
            c.setFont(_FA_FONT_NAME, self.size * 0.85)
            c.setFillColor(self.color)
            c.drawString(self.size * 0.08, self.size * 0.08,
                         chr(FA_CODEPOINTS[self.name]))
        else:  # fallback : pastille neutre, jamais de PDF cassé
            c.setStrokeColor(self.color)
            c.setLineWidth(1.2)
            c.circle(self.size / 2, self.size / 2, self.size * 0.38,
                     stroke=1, fill=0)
        c.restoreState()


# =====================================================================
# CONTRÔLEUR
# =====================================================================

class CapsuleCatalogueController(http.Controller):

    # --- gabarit page ---
    M_LEFT = M_RIGHT = 18 * mm
    M_TOP = 22 * mm
    M_BOTTOM = 18 * mm
    CONTENT_W = A4[0] - M_LEFT - M_RIGHT  # 174 mm

    # --- palette (alignée sur le site) ---
    PRIMARY = colors.HexColor('#1d3557')
    ACCENT = colors.HexColor('#c1442e')
    BORDER = colors.HexColor('#d8dee9')
    HEADER_BG = colors.HexColor('#e9eff7')
    MUTED = colors.HexColor('#555555')
    FOOT_MUTED = colors.HexColor('#777777')

    _styles = None

    # -------------------------------------------------------------
    # ROUTES
    # -------------------------------------------------------------

    @http.route('/catalogues', type='http', auth='public', website=True,
                sitemap=True)
    def catalogues_index(self, **kwargs):
        return request.render(
            'capsule_house_theme.catalogues_page',
            {'gammes': GAMMES_DATA},
        )

    @http.route('/catalogue/<string:slug>.pdf', type='http', auth='public',
                website=True, sitemap=False)
    def catalogue_pdf(self, slug, **kwargs):
        gamme = next((g for g in GAMMES_DATA if g.get('slug') == slug), None)
        if not gamme:
            return request.not_found()

        is_fr = request.env.lang != 'en_US'
        pdf = self._build_pdf(gamme, is_fr)
        filename = 'catalogue-%s-%s.pdf' % (slug, 'fr' if is_fr else 'en')
        return request.make_response(pdf, headers=[
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', 'attachment; filename="%s"' % filename),
        ])

    # -------------------------------------------------------------
    # I18N
    # -------------------------------------------------------------

    @staticmethod
    def _t(data, key, is_fr):
        suffix = '_fr' if is_fr else '_en'
        return data.get(key + suffix, data.get(key, ''))

    # -------------------------------------------------------------
    # STYLES (cachés au niveau classe)
    # -------------------------------------------------------------

    @classmethod
    def _get_styles(cls):
        if cls._styles:
            return cls._styles
        base = getSampleStyleSheet()
        cls._styles = {
            'cover_brand': ParagraphStyle(
                'CoverBrand', parent=base['Title'], alignment=TA_CENTER,
                fontSize=26, leading=30, textColor=colors.white),
            'cover_title': ParagraphStyle(
                'CoverTitle', parent=base['Title'], alignment=TA_CENTER,
                fontSize=22, leading=26, textColor=colors.white,
                spaceBefore=4),
            'cover_tag': ParagraphStyle(
                'CoverTag', parent=base['Normal'], alignment=TA_CENTER,
                fontSize=11, leading=15, textColor=colors.white),
            'section': ParagraphStyle(
                'Section', parent=base['Heading2'], fontSize=15, leading=19,
                textColor=cls.PRIMARY, spaceBefore=10, spaceAfter=6),
            'body': ParagraphStyle(
                'Body', parent=base['BodyText'], fontSize=9.5, leading=13),
            'small': ParagraphStyle(
                'Small', parent=base['BodyText'], fontSize=8.5, leading=11),
            'muted_center': ParagraphStyle(
                'MutedCenter', parent=base['BodyText'], alignment=TA_CENTER,
                fontSize=8, textColor=cls.FOOT_MUTED),
        }
        return cls._styles

    # -------------------------------------------------------------
    # GÉNÉRATION
    # -------------------------------------------------------------

    def _build_pdf(self, gamme, is_fr):
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=self.M_LEFT, rightMargin=self.M_RIGHT,
            topMargin=self.M_TOP, bottomMargin=self.M_BOTTOM,
            title='Catalogue %s' % gamme['name'],
            author='Capsule House',
        )
        styles = self._get_styles()
        story = self._cover(gamme, is_fr, styles)
        self._append_performances(story, gamme, is_fr, styles)
        self._append_formats(story, gamme, is_fr, styles)
        self._append_specs(story, gamme, is_fr, styles)
        self._append_list(story, gamme.get('equipements_fr' if is_fr
                                            else 'equipements_en') or [],
                          'Équipements inclus' if is_fr
                          else 'Included equipment', styles)
        self._append_list(story, gamme.get('options_fr' if is_fr
                                           else 'options_en') or [],
                          'Options', styles)
        story.append(Spacer(1, 10 * mm))
        story.append(Paragraph(
            'Document informatif — caractéristiques confirmables '
            'avec notre équipe.' if is_fr else
            'Informational document — specifications can be confirmed '
            'with our team.', styles['small']))
        doc.build(story,
                  onFirstPage=lambda c, d: self._page(c, d, gamme, True),
                  onLaterPages=lambda c, d: self._page(c, d, gamme, False))
        return buffer.getvalue()

    # --- couverture : bandeau pleine largeau via un tableau déguisé ---
    def _cover(self, gamme, is_fr, styles):
        inner = [
            Paragraph('CAPSULE HOUSE', styles['cover_brand']),
            Spacer(1, 2 * mm),
            Paragraph(escape(gamme.get('name', '')),
                      styles['cover_title']),
            Spacer(1, 2 * mm),
            Paragraph(escape(self._t(gamme, 'tagline', is_fr)),
                      styles['cover_tag']),
        ]
        band = Table([[inner]], colWidths=[self.CONTENT_W],
                     rowHeights=[38 * mm])
        band.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.PRIMARY),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return [band, Spacer(1, 10 * mm)]

    # --- sections ---
    def _table(self, rows, widths, header=True):
        t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
        cmds = [
            ('GRID', (0, 0), (-1, -1), 0.4, self.BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]
        if header:
            cmds += [
                ('BACKGROUND', (0, 0), (-1, 0), self.HEADER_BG),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ]
        t.setStyle(TableStyle(cmds))
        return t

    def _append_performances(self, story, gamme, is_fr, styles):
        perfs = gamme.get('performances') or []
        if not perfs:
            return
        story.append(Paragraph(
            'Points forts' if is_fr else 'Highlights', styles['section']))
        rows = [[Icon(p.get('icon', '')),
                 Paragraph('<b>%s</b><br/>%s' % (
                     escape(self._t(p, 'title', is_fr)),
                     escape(self._t(p, 'desc', is_fr))),
                     styles['body'])] for p in perfs]
        story += [self._table(rows, [18 * mm, self.CONTENT_W - 18 * mm],
                              header=False), Spacer(1, 6 * mm)]

    def _append_formats(self, story, gamme, is_fr, styles):
        fmts = gamme.get('formats') or []
        if not fmts:
            return
        story.append(Paragraph(
            'Formats disponibles' if is_fr else 'Available formats',
            styles['section']))
        h = lambda s: Paragraph('<b>%s</b>' % s, styles['small'])
        rows = [[h('Format' if is_fr else 'Format'),
                 h('Surface' if is_fr else 'Area'),
                 h('Note' if is_fr else 'Note')]]
        for f in fmts:
            rows.append([Paragraph(escape(f.get('name', '')), styles['small']),
                         Paragraph(escape(self._t(f, 'surface', is_fr)),
                                   styles['small']),
                         Paragraph(escape(self._t(f, 'note', is_fr)),
                                   styles['small'])])
        story += [self._table(rows, [50 * mm, 50 * mm,
                                     self.CONTENT_W - 100 * mm]),
                  Spacer(1, 6 * mm)]

    def _append_specs(self, story, gamme, is_fr, styles):
        for key, label_fr, label_en in [
                ('specs_ext', 'Spécifications extérieures',
                 'Exterior specifications'),
                ('specs_int', 'Spécifications intérieures',
                 'Interior specifications')]:
            specs = gamme.get(key) or []
            if not specs:
                continue
            story.append(Paragraph(
                label_fr if is_fr else label_en, styles['section']))
            h = lambda s: Paragraph('<b>%s</b>' % s, styles['small'])
            rows = [[h('Caractéristique' if is_fr else 'Characteristic'),
                     h('Valeur' if is_fr else 'Value')]]
            for item in specs:
                rows.append([
                    Paragraph(escape(self._t(item, 'label', is_fr)),
                              styles['small']),
                    Paragraph(escape(self._t(item, 'value', is_fr)),
                              styles['small'])])
            story += [self._table(rows, [self.CONTENT_W * 0.46,
                                         self.CONTENT_W * 0.54]),
                      Spacer(1, 4 * mm)]

    def _append_list(self, story, items, title, styles):
        if not items:
            return
        story.append(Paragraph(title, styles['section']))
        rows = [[Icon('fa-check', size=6 * mm, color=self.ACCENT),
                 Paragraph(escape(str(i)), styles['body'])] for i in items]
        story += [self._table(rows, [8 * mm, self.CONTENT_W - 8 * mm],
                              header=False), Spacer(1, 5 * mm)]

    # -------------------------------------------------------------
    # EN-TÊTE / PIED DE PAGE
    # -------------------------------------------------------------

    def _page(self, c, doc, gamme, first):
        c.saveState()
        if not first:  # rappel discret du nom de gamme en haut des pages 2+
            c.setFillColor(self.PRIMARY)
            c.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont('Helvetica-Bold', 9)
            c.drawString(self.M_LEFT, A4[1] - 8 * mm,
                         'Capsule House — %s' % gamme.get('name', ''))
        # pied de page commun
        c.setStrokeColor(self.BORDER)
        c.setLineWidth(0.5)
        c.line(self.M_LEFT, 14 * mm, A4[0] - self.M_RIGHT, 14 * mm)
        c.setFont('Helvetica', 8)
        c.setFillColor(self.FOOT_MUTED)
        c.drawString(self.M_LEFT, 9 * mm, 'Capsule House')
        c.drawRightString(A4[0] - self.M_RIGHT, 9 * mm,
                          'Page %d' % doc.page)
        c.restoreState()