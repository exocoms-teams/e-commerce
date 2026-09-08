# -*- coding: utf-8 -*-
"""Moteur de debranding.

Deux modes, pilotés par le paramètre système ``debranding.multi_company`` :

* **mono-société** (défaut) — la marque est écrite en dur dans les héritages
  QWeb. Aucune dépendance au contexte de rendu.
* **multi-société** — les héritages émettent des expressions QWeb qui lisent le
  dictionnaire ``debranding`` injecté par ``ir.qweb._prepare_values``. La marque
  est alors résolue société par société au moment du rendu.

Dans les deux cas les héritages sont créés dans un savepoint : un xpath qui ne
s'applique pas est journalisé, jamais fatal.
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
DEFAULT_LOGO_URL = "/logo.png"

# Modules dont les liens odoo.com sont fonctionnels (IAP, OAuth, achats de
# crédits...) : les réécrire casserait les flux.
DEFAULT_EXCLUDED_MODULES = (
    "iap,iap_mail,iap_extract,iap_crm,partner_autocomplete,mail_plugin,"
    "google_gmail,google_calendar,google_drive,microsoft_outlook,"
    "microsoft_calendar,payment,web_editor,base_setup_iap"
)

# LISTES de xpaths (pas des unions) pour éviter les problèmes d'indexation
ANCHOR_XPATHS = [
    "//a[contains(@href,'odoo.com')]",
    "//a[contains(@t-att-href,'odoo.com')]",
    "//a[contains(@t-attf-href,'odoo.com')]",
]

IMG_XPATHS = [
    "//img[contains(@src,'/web/static/img/odoo')]",
    "//img[contains(@src,'odoo.com')]",
    "//img[contains(@t-att-src,'/web/static/img/odoo')]",
    "//img[contains(@t-attf-src,'/web/static/img/odoo')]",
]

# <link rel="icon"> / apple-touch-icon pointant sur les visuels Odoo.
LINK_XPATHS = [
    "//link[contains(@href,'/web/static/img/odoo')]",
    "//link[contains(@t-att-href,'/web/static/img/odoo')]",
    "//link[contains(@t-attf-href,'/web/static/img/odoo')]",
]

VIEW_SEARCH_DOMAIN = [
    ("type", "=", "qweb"),
    "|",
    ("arch_db", "ilike", "odoo.com"),
    ("arch_db", "ilike", "static/img/odoo"),
]

# Templates dont le <title> doit être rebrandé.
MANUAL_TITLE_TARGETS = ["web.layout", "web.frontend_layout"]

ODOO_ONLINE_CRONS = [
    "base.ir_cron_module_update_notification",
    "mail.ir_cron_mail_notify_odoo",
]


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------
def pre_init_hook(env):
    """Vérifie la version Odoo et nettoie les anciens patches AVANT le chargement des vues."""
    if not release.version.startswith(("19.", "saas~19")):
        raise UserError(
            "exocoms_debranding cible exclusivement Odoo 19. "
            "Version détectée : %s" % release.version
        )

    # 🔥 CRITICAL : Supprimer les anciens patches AVANT que Odoo ne charge les vues
    # Cela évite l'erreur "cannot be located" due aux anciennes XPath avec union
    _clear_patches(env)


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
    # Les patches sont déjà supprimés dans pre_init_hook, mais on le refait pour être sûr
    _clear_patches(env)

    env["ir.config_parameter"].sudo().set_param("web.web_app_name", params["name"])

    count = _apply_manual_patches(env, params)
    count += _apply_view_patches(env, params)

    env.registry.clear_cache()
    env.registry.clear_cache("templates")
    _logger.info(
        "Debranding : %s vue(s) patchée(s) — mode %s.",
        count,
        "multi-société" if params["multi"] else "mono-société",
    )
    return count


# ---------------------------------------------------------------------------
# Paramètres
# ---------------------------------------------------------------------------
def _get_params(env):
    ICP = env["ir.config_parameter"].sudo()
    excluded = ICP.get_param("debranding.excluded_modules") or DEFAULT_EXCLUDED_MODULES
    return {
        "name": ICP.get_param("debranding.name") or DEFAULT_BRAND,
        "url": ICP.get_param("debranding.url") or "",
        "logo": ICP.get_param("debranding.logo_url") or DEFAULT_LOGO_URL,
        "multi": ICP.get_param("debranding.multi_company") in ("True", "true", "1"),
        "excluded": {m.strip() for m in excluded.split(",") if m.strip()},
    }


def _is_enterprise(env):
    """Vrai si au moins un module sous licence Odoo Enterprise est installé."""
    return bool(env["ir.module.module"].sudo().search_count([
        ("state", "=", "installed"),
        ("license", "=like", "OEEL%"),
    ]))


def _toggle_odoo_online(env, active):
    """Active/désactive le cron de notification éditeur.

    La désactivation n'est pratiquée que sur une base Community (LGPL-3).
    Sur Enterprise, ce cron alimente le décompte d'utilisateurs de
    l'abonnement : le neutraliser sortirait du cadre contractuel.
    """
    if not active and _is_enterprise(env):
        _logger.warning(
            "Debranding : modules Enterprise détectés, le cron de notification "
            "éditeur est laissé actif (obligation contractuelle)."
        )
        return
    for xmlid in ODOO_ONLINE_CRONS:
        cron = env.ref(xmlid, raise_if_not_found=False)
        if cron:
            cron.sudo().write({"active": active})


# ---------------------------------------------------------------------------
# Génération des specs d'héritage
# ---------------------------------------------------------------------------
def _literal(value):
    """Littéral Python sûr pour une expression QWeb."""
    return "'%s'" % (value or "").replace("\\", "\\\\").replace("'", "\\'")


def _title_specs(params):
    if params["multi"]:
        expr = "title or debranding['name']"
    else:
        expr = "title or %s" % _literal(params["name"])
    return (
        '<xpath expr="//title" position="replace">'
        '<title t-out="%s"/>'
        "</xpath>" % escape(expr)
    )


def _anchor_specs(tree, params):
    """Réécrit les liens Odoo.com trouvés dans la vue.

    Chaque nœud est traité une seule fois.
    Le premier sélecteur XPath qui trouve le nœud est utilisé.
    """
    matched_nodes = []
    seen_nodes = set()

    for xpath_expr in ANCHOR_XPATHS:
        for node in tree.xpath(xpath_expr):
            node_id = id(node)

            if node_id in seen_nodes:
                continue

            seen_nodes.add(node_id)
            matched_nodes.append((node, xpath_expr))

    if not matched_nodes:
        return ""

    # ------------------------------------------------------------
    # Construction du remplacement
    # ------------------------------------------------------------
    if params["multi"]:
        replacement = (
            "<t t-if=\"debranding['url']\">"
            "<a t-att-href=\"debranding['url']\" "
            "target=\"_blank\" rel=\"noopener\" "
            "t-out=\"debranding['name']\"/>"
            "</t>"
            "<t t-else=\"\">"
            "<span t-out=\"debranding['name']\"/>"
            "</t>"
        )

    elif params["url"]:
        replacement = (
            '<a href="%s" target="_blank" rel="noopener">%s</a>'
            % (
                escape(params["url"]),
                escape(params["name"]),
            )
        )

    else:
        replacement = (
            "<span>%s</span>"
            % escape(params["name"])
        )

    # ------------------------------------------------------------
    # Génération des XPath
    # ------------------------------------------------------------
    specs = []

    for node, matched_xpath in matched_nodes:
        matching_nodes = tree.xpath(matched_xpath)

        try:
            node_index = matching_nodes.index(node) + 1
        except ValueError:
            _logger.warning(
                "Debranding : nœud introuvable lors du calcul "
                "de son index dans %s",
                matched_xpath,
            )
            continue

        indexed_xpath = "(%s)[%d]" % (
            matched_xpath,
            node_index,
        )

        specs.append(
            '<xpath expr="%s" position="replace">%s</xpath>'
            % (
                escape(indexed_xpath),
                replacement,
            )
        )

    return "".join(specs)


def _asset_specs(tree, params):
    """Réécrit les images et liens d'assets Odoo.

    Chaque nœud est traité une seule fois.
    Le premier sélecteur XPath qui trouve le nœud est utilisé.
    """
    specs = []

    for xpaths_list, attr in (
        (IMG_XPATHS, "src"),
        (LINK_XPATHS, "href"),
    ):
        # --------------------------------------------------------
        # Recherche des nœuds sans doublons
        # --------------------------------------------------------
        matched_nodes = []
        seen_nodes = set()

        for xpath_expr in xpaths_list:
            for node in tree.xpath(xpath_expr):
                node_id = id(node)

                if node_id in seen_nodes:
                    continue

                seen_nodes.add(node_id)
                matched_nodes.append((node, xpath_expr))

        if not matched_nodes:
            continue

        # --------------------------------------------------------
        # Construction des attributs
        # --------------------------------------------------------
        if params["multi"]:
            body = (
                '<attribute name="%s"/>'
                '<attribute name="t-attf-%s"/>'
                '<attribute name="t-att-%s">'
                "debranding['logo']"
                "</attribute>"
            ) % (
                attr,
                attr,
                attr,
            )

            if attr == "src":
                body += (
                    '<attribute name="alt"/>'
                    '<attribute name="t-att-alt">'
                    "debranding['name']"
                    "</attribute>"
                )

        else:
            body = (
                '<attribute name="%s">%s</attribute>'
                '<attribute name="t-att-%s"/>'
                '<attribute name="t-attf-%s"/>'
            ) % (
                attr,
                escape(params["logo"]),
                attr,
                attr,
            )

            if attr == "src":
                body += (
                    '<attribute name="alt">%s</attribute>'
                    % escape(params["name"])
                )

        # --------------------------------------------------------
        # Génération des XPath
        # --------------------------------------------------------
        for node, matched_xpath in matched_nodes:
            matching_nodes = tree.xpath(matched_xpath)

            try:
                node_index = matching_nodes.index(node) + 1
            except ValueError:
                _logger.warning(
                    "Debranding : nœud asset introuvable lors "
                    "du calcul de son index dans %s",
                    matched_xpath,
                )
                continue

            indexed_xpath = "(%s)[%d]" % (
                matched_xpath,
                node_index,
            )

            specs.append(
                '<xpath expr="%s" position="attributes">%s</xpath>'
                % (
                    escape(indexed_xpath),
                    body,
                )
            )

    return "".join(specs)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
def _clear_patches(env):
    """Supprime tous les patches existants du module."""
    imd = env["ir.model.data"].sudo().search([
        ("module", "=", MODULE),
        ("model", "=", "ir.ui.view"),
        ("name", "=like", PATCH_PREFIX + "%"),
    ])
    views = env["ir.ui.view"].sudo().browse(imd.mapped("res_id")).exists()
    if imd or views:
        _logger.info("Debranding : suppression de %s anciens patches", len(imd))
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
    except Exception as err:
        # Vérifier si c'est une erreur de localisation XPath
        error_msg = str(err)
        if "cannot be located" in error_msg:
            _logger.info(
                "Debranding : nœud non trouvé dans %s, patch ignoré",
                parent.key or parent.id
            )
        else:
            _logger.warning(
                "Debranding : patch ignoré sur %s (%s)",
                parent.key or parent.id,
                err
            )
        return False


def _apply_manual_patches(env, params):
    count = 0
    specs = _title_specs(params)
    for xmlid in MANUAL_TITLE_TARGETS:
        parent = env.ref(xmlid, raise_if_not_found=False)
        if not parent:
            continue
        name = "%stitle_%s" % (PATCH_PREFIX, xmlid.replace(".", "_"))
        if _create_patch(env, parent, name, specs):
            count += 1
    return count


def _root_view(view):
    while view.inherit_id:
        view = view.inherit_id
    return view


def _apply_view_patches(env, params):
    """Réécrit liens et visuels Odoo dans les templates qui les contiennent.

    Contrairement à l'ancienne stratégie, on ne remonte pas systématiquement
    jusqu'à la vue racine. Cela évite les problèmes liés aux templates
    appelés avec ``t-call`` sur Odoo 19.
    """
    View = env["ir.ui.view"].sudo()
    candidates = View.with_context(active_test=False).search(VIEW_SEARCH_DOMAIN)

    count = 0

    for view in candidates:
        module = (view.key or "").split(".")[0]

        if not module or module == MODULE or module in params["excluded"]:
            continue

        try:
            # Utiliser arch_db directement au lieu de get_combined_arch()
            arch = view.with_context(
                lang=None,
                inherit_branding=False,
            ).arch_db

            tree = etree.fromstring(arch.encode("utf-8"))
        except Exception as e:
            _logger.debug(
                "Debranding : impossible de parser %s (%s)",
                view.key or view.id,
                e
            )
            continue

        specs = _anchor_specs(tree, params) + _asset_specs(tree, params)

        if not specs:
            continue

        name = "%s%s" % (PATCH_PREFIX, view.id)

        if _create_patch(env, view, name, specs):
            count += 1

    return count