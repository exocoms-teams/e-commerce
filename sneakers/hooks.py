# Translation auto-enabler.
#
# Odoo.sh "development" branches create a BRAND-NEW database on every push,
# with only English active. That means the sneakers module's fr.po / ar.po
# translations are never imported into those fresh databases, because French
# and Arabic are not loaded when the module installs. This hook makes the
# module activate fr + ar (on the DB and on the website) and reload its own
# terms at the end of every install/upgrade, so translations are present
# whatever the branch lifecycle.
#
# The hook tolerates both hook signatures used by Odoo (env-only and
# (cr, registry)) and never raises, so it can never block a build.


def post_init_hook(cr, registry=None):
    from odoo import api, SUPERUSER_ID
    import logging

    _logger = logging.getLogger(__name__)

    try:
        if isinstance(cr, api.Environment):
            # Odoo 13+ style: hook called with a single Environment object
            env = cr
        else:
            # Legacy style: hook called with (cr, registry)
            env = api.Environment(cr, SUPERUSER_ID, {})
    except Exception:
        _logger.warning("sneakers: could not obtain environment in post_init_hook")
        return

    lang_codes = ["fr", "ar"]

    # 1) Activate the languages in the DB (res.lang active=True). Prefer the
    #    new method that also updates translations, fall back to plain
    #    activation.
    res_lang = env["res.lang"]
    act = getattr(res_lang, "_activate_and_install_lang", None) or getattr(
        res_lang, "_activate_lang", None
    )
    for base in lang_codes:
        if not act:
            break
        lang = (
            res_lang.with_context(active_test=False)
            .search([("code", "=ilike", base + "%")], limit=1)
        )
        if not lang:
            _logger.warning("sneakers: no res.lang found for %s", base)
            continue
        try:
            act(lang.code)
            _logger.info("sneakers: activated language %s", lang.code)
        except Exception as e:
            _logger.warning("sneakers: activating %s failed: %s", base, e)

    # 2) Make sure the website itself exposes fr + ar (otherwise /fr/ and /ar/
    #    fall back to English even with translations in the DB).
    try:
        site_langs = res_lang.with_context(active_test=False).search(
            [("code", "=ilike", base_code + "%") for base_code in lang_codes]
        )
        for website in env["website"].search([]):
            existing = website.language_ids
            to_add = site_langs - existing
            if to_add:
                website.language_ids = [(4, l.id) for l in to_add]
        _logger.info("sneakers: ensured fr/ar enabled on website")
    except Exception as e:
        _logger.warning("sneakers: website language enable failed: %s", e)

    # 3) Belt-and-suspenders: explicitly (re)load the module's own terms for
    #    the target languages, working regardless of the above.
    try:
        env["ir.translation"]._load_module_terms(["sneakers"], lang_codes)
        _logger.info("sneakers: loaded fr/ar module terms")
    except Exception as e:
        _logger.warning("sneakers: _load_module_terms failed: %s", e)