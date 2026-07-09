# -*- coding: utf-8 -*-
import json
import logging
import urllib.parse
import urllib.request

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# Codes Odoo (fr_FR/en_US) <-> codes courts attendus par l'API de
# traduction (fr/en), et langue "opposée" pour savoir vers quoi
# traduire automatiquement un avis déposé dans une langue donnée.
_LANG_TO_SHORT = {'fr_FR': 'fr', 'en_US': 'en'}
_OTHER_LANG = {'fr_FR': 'en_US', 'en_US': 'fr_FR'}


def _translate_text(text, target_short_lang):
    """Traduit `text` vers `target_short_lang` ('fr' ou 'en') via
    l'endpoint PUBLIC et GRATUIT de Google Translate (celui utilisé par
    la page translate.google.com elle-même, sans clé API ni compte à
    créer). Aucune dépendance pip supplémentaire : urllib/json sont
    dans la bibliothèque standard Python.

    Ce n'est PAS l'API officielle Google Cloud Translation (payante) —
    c'est un usage non documenté, donc à surveiller si le volume
    d'avis devient important (peut être bridé ou bloqué sans préavis).
    En cas d'échec (réseau, timeout, blocage), retourne None plutôt que
    de faire planter la soumission de l'avis : l'avis reste alors
    visible uniquement dans sa langue d'origine jusqu'à une nouvelle
    tentative (bouton "Traduire" côté backend, ou prochaine sauvegarde).
    """
    if not text:
        return text
    try:
        params = {
            'client': 'gtx',
            'sl': 'auto',
            'tl': target_short_lang,
            'dt': 't',
            'q': text,
        }
        url = 'https://translate.googleapis.com/translate_a/single?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return ''.join(segment[0] for segment in data[0] if segment and segment[0])
    except Exception:
        _logger.warning(
            "Traduction automatique indisponible (vers '%s') — "
            "l'avis reste affiché uniquement dans sa langue d'origine.",
            target_short_lang,
        )
        return None


class ExocomsAvis(models.Model):
    """Avis client déposés depuis le formulaire public /avis.
    Scopé par website_id — OBLIGATOIRE sur cette base partagée à
    plusieurs sites (même logique que product.public.category,
    website.menu, etc. dans __init__.py) : sans ce champ, les avis
    d'un site s'afficheraient sur tous les autres.

    `comment` est traduisible (translate=True) : Odoo stocke une
    valeur distincte par langue active, et `avis.comment` retourne
    automatiquement la bonne version selon la langue de la page en
    cours — aucune logique de template supplémentaire nécessaire."""
    _name = 'exocoms.avis'
    _description = "Avis client (Exocoms)"
    _order = 'date desc, id desc'

    name = fields.Char(string="Nom", required=True)
    rating = fields.Integer(string="Note (1 à 5)", required=True, default=5)
    comment = fields.Text(string="Commentaire", required=True, translate=True)
    product = fields.Char(string="Produit acheté")
    date = fields.Date(string="Date", default=lambda self: fields.Date.context_today(self))
    state = fields.Selection([
        ('pending', "En attente de validation"),
        ('published', "Publié"),
    ], string="Statut", default='pending', required=True)
    website_id = fields.Many2one(
        'website', string="Site", required=True,
        default=lambda self: self.env['website'].get_current_website(),
    )

    @api.constrains('rating')
    def _check_rating(self):
        for rec in self:
            if rec.rating < 1 or rec.rating > 5:
                raise ValidationError("La note doit être comprise entre 1 et 5.")

    def action_translate_missing(self):
        """Traduit `comment` vers l'AUTRE langue (fr<->en) à partir de
        la langue dans laquelle l'enregistrement vient d'être écrit
        (déduite du contexte courant, cf. appelants). Rejouable sans
        risque (bouton backend "Traduire") si l'appel automatique à la
        soumission a échoué faute de réseau."""
        for rec in self:
            source_lang = rec.env.context.get('lang') or 'fr_FR'
            target_lang = _OTHER_LANG.get(source_lang)
            target_short = _LANG_TO_SHORT.get(target_lang)
            if not target_lang or not target_short:
                continue
            source_text = rec.with_context(lang=source_lang).comment
            translated = _translate_text(source_text, target_short)
            if translated:
                rec.with_context(lang=target_lang).write({'comment': translated})
