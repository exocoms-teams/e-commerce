# -*- coding: utf-8 -*-
"""Nettoyage / remplacement des mentions Odoo dans le HTML rendu.

Deux modes :

* ``remove``  : la mention est purement supprimée ;
* ``replace`` : le premier bloc promotionnel rencontré est remplacé par le
  bloc de marque fourni (``snippet``), en conservant la balise conteneur
  d'origine — donc son style, sa position et son alignement. Les éventuelles
  occurrences suivantes sont supprimées.

Passes appliquées :

1. balise ``<meta name="generator" content="Odoo">`` ;
2. plus petit conteneur (span/p/div/...) contenant un lien odoo.com ;
3. liens ``<a href="...odoo.com...">`` résiduels ;
4. formules textuelles restantes (FR/EN).
"""

import re

from markupsafe import Markup

# Taille maximale (en caractères) du contenu d'un bloc traité.
MAX_BLOCK = 900

# Marqueur interne : le bloc de marque est injecté en toute fin de traitement
# afin qu'aucune passe ultérieure ne puisse le dégrader.
SENTINEL = "\x00EXOCOMS_BRAND\x00"

# Déclencheurs bon marché : si aucun n'est présent, on ne lance aucune regex.
_TRIGGERS = (
    "odoo.com",
    "powered by",
    "propuls",
    "sent by",
    "envoy",
    "generator",
    "openerp",
)


def _block_regex(tags):
    """Regex capturant le plus petit élément ``tags`` contenant un lien odoo.com."""
    inner = r"(?:(?!</?(?P=tag)\b).){0,%d}?" % MAX_BLOCK
    return re.compile(
        r"(?P<open><(?P<tag>%s)\b[^>]*>)%sodoo\.com%s</(?P=tag)\s*>" % (tags, inner, inner),
        re.IGNORECASE | re.DOTALL,
    )


# Ordre important : on traite d'abord les conteneurs les plus fins.
BLOCK_RES = (
    _block_regex(r"span|small|em|strong|b|i"),
    _block_regex(r"p|li|center"),
    _block_regex(r"div"),
)

# <meta name="generator" content="Odoo"> (ordre des attributs indifférent)
META_GENERATOR_RE = re.compile(
    r"<meta\b(?=[^>]*\bgenerator\b)(?=[^>]*odoo)[^>]*/?>", re.IGNORECASE
)

# Liens vers odoo.com
ANCHOR_RE = re.compile(
    r"<a\b[^>]*href\s*=\s*(\"|')[^\"']*odoo\.com[^\"']*\1[^>]*>.*?</a>",
    re.IGNORECASE | re.DOTALL,
)

# --- Formules textuelles résiduelles ---------------------------------------
# Deux garde-fous pour ne jamais toucher un texte légitime :
#   * soit la formule est suivie du mot Odoo/OpenERP (_BRAND) ;
#   * soit elle est « orpheline » (_DANGLING) parce que le lien odoo.com vient
#     d'être supprimé : plus rien derrière, hormis une balise fermante.
_NO_BLOCK = r"(?:(?!</?(?:div|table|tr|td|p|body|html)\b).)"
_BRAND = r"(?:<[^>]{0,200}>\s*){0,2}(?:odoo|openerp)\b(?:\s*</[^>]{0,60}>){0,2}"
_DANGLING = r"(?=\s*(?:&nbsp;|\s)*(?:[.!,;]|</|\Z))"
_TAIL = r"\s*(?:%s|%s)" % (_BRAND, _DANGLING)

_INTROS = (
    r"powered\s*by",
    r"propuls[ée]{1,2}\s*par",
    r"g[ée]n[ée]r[ée]{1,2}\s*(?:par|avec)",
    r"generated\s*(?:by|with)",
    r"create\s+a\s+free\s+website\s+with",
    r"cr[ée]{1,2}(?:z|er)?\s+un\s+site\s+(?:web\s+)?gratuit(?:ement)?\s+avec",
)

PHRASE_RES = tuple(
    re.compile(r"\b(?:%s)%s" % (intro, _TAIL), re.IGNORECASE | re.DOTALL)
    for intro in _INTROS
) + (
    # "Sent by <Société> using Odoo"
    re.compile(
        r"\bsent\s+by\b%s{0,300}?\busing\b%s" % (_NO_BLOCK, _TAIL),
        re.IGNORECASE | re.DOTALL,
    ),
    # "Envoyé par <Société> avec Odoo"
    re.compile(
        r"\benvoy[ée]{1,2}\s+par\b%s{0,300}?\b(?:avec|via)\b%s" % (_NO_BLOCK, _TAIL),
        re.IGNORECASE | re.DOTALL,
    ),
)


def needs_debranding(html):
    """Test rapide (substring) avant de dérouler les expressions régulières."""
    if not html:
        return False
    low = str(html).lower()
    return any(trigger in low for trigger in _TRIGGERS)


def debrand_html(html, snippet=None, generator=None):
    """Retourne ``html`` débrandé, en préservant le type (str / Markup).

    :param snippet: HTML de marque à injecter à la place de la première
        mention rencontrée. ``None`` => simple suppression.
    :param generator: valeur de remplacement de la balise meta generator.
        ``None`` => la balise est supprimée.
    """
    if not html or not needs_debranding(html):
        return html

    original = str(html)
    state = {"injected": False}

    def _replace_block(match):
        if snippet is None or state["injected"]:
            return ""
        state["injected"] = True
        return "%s%s</%s>" % (match.group("open"), SENTINEL, match.group("tag"))

    text = META_GENERATOR_RE.sub(
        ('<meta name="generator" content="%s"/>' % generator) if generator else "",
        original,
    )
    for regex in BLOCK_RES:
        text = regex.sub(_replace_block, text)
    text = ANCHOR_RE.sub("", text)
    for regex in PHRASE_RES:
        text = regex.sub("", text)

    if snippet is not None:
        text = text.replace(SENTINEL, str(snippet))

    if text == original:
        return html
    return Markup(text) if isinstance(html, Markup) else text
