# -*- coding: utf-8 -*-
"""Moteur de debranding.

Le patch des templates est appliqué dynamiquement plutôt que via des vues
héritées statiques : chaque héritage est créé dans un savepoint et abandonné
si son xpath ne s'applique pas. Aucun échec d'installation possible si un
template Odoo évolue.
"""
import logging

from lxml import etree
from markupsafe import escape

from odoo import release
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

MODULE = "exocoms_debranding"
PATCH_PREFIX = "debrand_auto_"

DEFAULT_BRAND = "EXOCOMS"

# Modules dont les liens odoo.com sont fonctionnels (IAP, OAuth, achats de
# crédits...) : les réécrire casserait les flux.
DEFAULT_EXCLUDED_MODULES = (
    "iap,iap_mail,iap_extract,iap_crm,partner_autocomplete,mail_plugin,"
    "google_gmail,google_calendar,google_drive,microsoft_outlook,"
    "microsoft_calendar,payment,web_editor,base_setup_iap"
)

ANCHOR_XPATH = (
    "//a[contains(@href,'odoo.com')]"
    " | //a[contains(@t-att-href,'odoo.com')]"
    " | //a[contains(@t-attf-href,'odoo.com')]"
)

IMG_XPATH = (
    "//img[contains(@src,'/web/static/img/odoo')]"
    " | //img[contains(@src,'odoo.com')]"
    " | //img[contains(@t-att-src,'/web/static/img/odoo')]"
    " | //img[contains(@t-attf-src,'/web/static/img/odoo')]"
)

# <link rel="icon"> / apple-touch-icon pointant sur les visuels Odoo.
LINK_XPATH = (
    "//link[contains(@href,'/web/static/img/odoo')]"
    " | //link[contains(@t-att-href,'/web/static/img/odoo')]"
    " | //link[contains(@t-attf-href,'/web/static/img/odoo')]"
)

VIEW_SEARCH_DOMAIN = [
    ("type", "=", "qweb"),
    "|",
    ("arch_db", "ilike", "odoo.com"),
    ("arch_db", "ilike", "static/img/odoo"),
]

# Patchs ciblés (xml_id parent, gabarit de specs). {name} = nom de marque.
MANUAL_PATCHES = [
    (
        "web.layout",
        '<xpath expr="//title" position="replace">'
        "<title t-out=\"title or '{name}'\"/>"
        "</xpath>",
    ),
    (
        "web.frontend_layout",
        '<xpath expr="//title" position="replace">'
        "<title t-out=\"title or '{name}'\"/>"
        "</xpath>",
    ),
]

# Crons / notifications éditeur à neutraliser.
ODOO_ONLINE_CRONS = [
    "base.ir_cron_module_update_notification",
    "mail.ir_cron_mail_notify_odoo",
]


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------
def pre_init_hook(env):
    if not release.version.startswith(("19.", "saas~19")):
        raise UserError(
            "exocoms_debranding cible exclusivement Odoo 19. "
            "Version détectée : %s" % release.version
        )


def post_init_hook(env):
    _toggle_odoo_online(env, False)
    rebrand(env)


def uninstall_hook(env):
    _toggle_odoo_online(env, True)


# ---------------------------------------------------------------------------
# API publique
# ---------------------------------------------------------------------------
def rebrand(env):
    """(Ré)applique l'ensemble des patchs. Idempotent."""
    params = _get_params(env)
    _clear_patches(env)

    ICP = env["ir.config_parameter"].sudo()
    ICP.set_param("web.web_app_name", params["name"])

    count = _apply_manual_patches(env, params)
    count += _apply_view_patches(env, params)

    env.registry.clear_cache()
    env.registry.clear_cache("templates")
    _logger.info("Debranding : %s vue(s) patchée(s) pour « %s ».", count, params["name"])
    return count


# ---------------------------------------------------------------------------
# Interne
# ---------------------------------------------------------------------------
def _get_params(env):
    ICP = env["ir.config_parameter"].sudo()
    excluded = ICP.get_param("debranding.excluded_modules") or DEFAULT_EXCLUDED_MODULES
    return {
        "name": ICP.get_param("debranding.name") or DEFAULT_BRAND,
        "url": ICP.get_param("debranding.url") or "",
        "logo": ICP.get_param("debranding.logo_url") or "/logo.png",
        "excluded": {m.strip() for m in excluded.split(",") if m.strip()},
    }


def _toggle_odoo_online(env, active):
    for xmlid in ODOO_ONLINE_CRONS:
        cron = env.ref(xmlid, raise_if_not_found=False)
        if cron:
            cron.sudo().write({"active": active})


def _clear_patches(env):
    imd = env["ir.model.data"].sudo().search([
        ("module", "=", MODULE),
        ("model", "=", "ir.ui.view"),
        ("name", "=like", PATCH_PREFIX + "%"),
    ])
    views = env["ir.ui.view"].sudo().browse(imd.mapped("res_id")).exists()
    imd.unlink()
    views.unlink()


def _create_patch(env, parent, name, specs):
    """Crée une vue d'extension. Renvoie False si le xpath ne s'applique pas."""
    View = env["ir.ui.view"].sudo()
    try:
        with env.cr.savepoint():
            view = View.create({
                "name": "Debranding: %s" % (parent.key or parent.name),
                "type": "qweb",
                "mode": "extension",
                "inherit_id": parent.id,
                "key": "%s.%s" % (MODULE, name),
                "priority": 99,
                "arch": "<data>%s</data>" % specs,
            })
            env["ir.model.data"].sudo().create({
                "module": MODULE,
                "name": name,
                "model": "ir.ui.view",
                "res_id": view.id,
                "noupdate": True,
            })
            View.flush_model()
        return view
    except Exception as err:  # noqa: BLE001 - dégradation volontaire
        _logger.warning(
            "Debranding : patch ignoré sur %s (%s)", parent.key or parent.id, err
        )
        return False


def _apply_manual_patches(env, params):
    count = 0
    for xmlid, template in MANUAL_PATCHES:
        parent = env.ref(xmlid, raise_if_not_found=False)
        if not parent:
            continue
        specs = template.format(name=escape(params["name"]))
        name = "%smanual_%s" % (PATCH_PREFIX, xmlid.replace(".", "_"))
        if _create_patch(env, parent, name, specs):
            count += 1
    return count


def _asset_specs(tree, params):
    """Specs pour les visuels Odoo (img / link icon) : réécriture de la source."""
    specs = ""
    logo = escape(params["logo"])
    name = escape(params["name"])

    for xpath, attr in ((IMG_XPATH, "src"), (LINK_XPATH, "href")):
        for _i in range(len(tree.xpath(xpath))):
            specs += (
                '<xpath expr="(%s)[1]" position="attributes">'
                '<attribute name="%s">%s</attribute>'
                '<attribute name="t-att-%s"/>'
                '<attribute name="t-attf-%s"/>'
                "%s"
                "</xpath>"
            ) % (
                xpath,
                attr,
                logo,
                attr,
                attr,
                '<attribute name="alt">%s</attribute>' % name if attr == "src" else "",
            )
    return specs


def _anchor_specs(tree, params):
    """Specs pour les liens odoo.com : remplacement complet du noeud."""
    nb = len(tree.xpath(ANCHOR_XPATH))
    if not nb:
        return ""
    if params["url"]:
        replacement = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (
            escape(params["url"]),
            escape(params["name"]),
        )
    else:
        replacement = "<span>%s</span>" % escape(params["name"])
    # Chaque spec est appliquée séquentiellement sur l'arbre muté :
    # n specs identiques traitent les n occurrences.
    return (
        '<xpath expr="(%s)[1]" position="replace">%s</xpath>'
        % (ANCHOR_XPATH, replacement)
    ) * nb


def _root_view(view):
    while view.inherit_id:
        view = view.inherit_id
    return view


def _apply_view_patches(env, params):
    """Réécrit liens et visuels Odoo dans tous les templates QWeb.

    On patche la vue racine avec l'arch combinée : les contenus introduits par
    des vues d'extension tierces sont donc couverts eux aussi.
    """
    View = env["ir.ui.view"].sudo()
    candidates = View.with_context(active_test=False).search(VIEW_SEARCH_DOMAIN)

    roots = View.browse()
    for view in candidates:
        roots |= _root_view(view)

    count = 0
    for root in roots:
        module = (root.key or "").split(".")[0]
        if not module or module == MODULE or module in params["excluded"]:
            continue
        try:
            arch = root.with_context(lang=None, inherit_branding=False).get_combined_arch()
            tree = etree.fromstring(arch.encode("utf-8"))
        except Exception:  # noqa: BLE001
            continue

        specs = _anchor_specs(tree, params) + _asset_specs(tree, params)
        if not specs:
            continue
        if _create_patch(env, root, "%s%s" % (PATCH_PREFIX, root.id), specs):
            count += 1
    return count
