# -*- coding: utf-8 -*-
import logging

from . import controllers
from . import models
from .setup_utils import (
    _get_company,
    _grant_company_access,
    _get_website,
    _setup_pricelist,
    _setup_languages,
    _reload_native_translations,
    _set_logo,
    _setup_homepage,
    _setup_domain,
    _setup_website_priority,
    _setup_theme_assets,
    _invalidate_frontend_assets,
    _scope_layout_views,
    _reset_customized_views,
    _setup_livechat,
    _clean_demo_data,
    _setup_shop_categories,
    _setup_shop_display,
    _setup_shop_grid_design,
    _setup_menus,
    _setup_shop_filters,
    _publish_our_products,
    _attach_shop_filters_to_products,
)

_logger = logging.getLogger(__name__)


def run_theme_maintenance(env):
    company = _get_company(env)
    _grant_company_access(env, company)
    website = _get_website(env, company)
    _setup_pricelist(env, website, company)
    _setup_languages(env, website)
    _reload_native_translations(env)
    _set_logo(env, website)
    _setup_homepage(env, website)
    _setup_domain(env, website)
    _setup_website_priority(env, website)
    _setup_theme_assets(env, website)
    _invalidate_frontend_assets(env, website)
    _scope_layout_views(env, website)
    _reset_customized_views(env)
    _setup_livechat(env, website)
    _clean_demo_data(env, website)
    categories = _setup_shop_categories(env, website)
    _setup_shop_display(env, website)
    _setup_shop_grid_design(env, website)
    _setup_menus(env, website, categories)
    _setup_shop_filters(env)
    _publish_our_products(env, website, company)
    _attach_shop_filters_to_products(env, website)
    _logger.info(
        "capsule_house_theme: run_theme_maintenance terminé (website_id=%s, "
        "company_id=%s).", website.id, company.id,
    )
    return website


def post_init_hook(env):
    run_theme_maintenance(env)
