# -*- coding: utf-8 -*-
"""WIN-69 : scraper TikTok Creative Center (Top Ads).

Cible le tableau de bord public "Top Ads" du TikTok Creative Center
(ads.tiktok.com/business/creativecenter) : accès gratuit, aucune inscription
requise, contrairement à l'API eBay (collecte_scrapers/ebay_ingestor.py) qui
elle est une vraie API officielle avec identifiants OAuth. Il n'existe pas
d'API publique documentée pour Creative Center : ce module appelle le point
d'entrée JSON interne déjà utilisé par le site lui-même pour peupler son
propre tableau de bord (reverse engineering, pratique courante et
documentée publiquement pour ce site précis).

ATTENTION - à vérifier/ajuster une fois testé en conditions réelles :
les noms de champs exacts de la réponse JSON de Creative Center (BASE_URL,
noms de clés dans _extract_ad_fields) sont basés sur le schéma le plus
largement documenté publiquement pour cet endpoint au moment de l'écriture,
mais TikTok peut le faire évoluer sans préavis (endpoint non officiel, pas
de contrat de stabilité). D'où l'extraction défensive avec plusieurs noms
de clés candidats par champ, plutôt qu'un seul nom supposé garanti.

Choix de modélisation (à confirmer avec l'équipe, cf. le même type de note
dans trend_score_calculator.py pour score_site_x) : Creative Center liste
des publicités (annonceur + créa vidéo), pas des "produits" au sens propre.
Chaque publicité distincte est donc traitée comme SON PROPRE product_ref
(pas de regroupement par annonceur), avec le nom de la publicité/marque
comme product_name - cohérent avec le contrat JSON "ad" existant qui exige
de toute façon un product_ref par ligne trend.ad.

Asynchrone (exigence du ticket) via asyncio + exécution des appels HTTP
synchrones (requests, déjà utilisé par ebay_ingestor.py) dans des threads
(asyncio.to_thread) : évite d'ajouter une dépendance externe (aiohttp) dont
la disponibilité sur l'environnement Odoo.sh n'est pas garantie, tout en
permettant de paralléliser plusieurs pages/requêtes.
"""
import asyncio
import logging

import requests

_logger = logging.getLogger(__name__)

BASE_URL = "https://ads.tiktok.com/creative_radar_api/v1/top_ads/list"
REQUEST_TIMEOUT_SECONDS = 15
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def fetch_trending_ads_page(page=1, period=7, country_code="US", limit=20):
    """Récupère UNE page du tableau "Top Ads" de TikTok Creative Center.

    :param int page: numéro de page (pagination du site, commence à 1).
    :param int period: fenêtre de tendance en jours (7/30/120 sur le site).
    :param str country_code: code pays ISO 2 lettres ("US", "MA", ...).
    :param int limit: nombre de publicités par page.
    :rtype: list[dict] - liste brute des publicités (peut être vide en cas
        d'erreur réseau/HTTP, jamais None, pour simplifier l'appelant).
    """
    params = {
        "page": page,
        "limit": limit,
        "period": period,
        "order_by": "for_you",
        "country_code": country_code,
    }
    try:
        response = requests.get(
            BASE_URL, params=params, headers=DEFAULT_HEADERS,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code != 200:
            _logger.warning(
                "WIN-69: TikTok Creative Center a répondu %s pour la page %s",
                response.status_code, page,
            )
            return []
        payload = response.json()
        return payload.get("data", {}).get("materials", []) or []
    except requests.exceptions.RequestException as exc:
        _logger.warning("WIN-69: erreur réseau TikTok Creative Center: %s", exc)
        return []
    except ValueError:
        # réponse non-JSON (ex: page d'erreur HTML renvoyée par un WAF)
        _logger.warning("WIN-69: réponse non-JSON de TikTok Creative Center")
        return []


def _first_present(item, *keys, default=None):
    """Retourne la première valeur non-vide parmi plusieurs noms de clés
    candidats - voir la note en tête de fichier sur l'incertitude des noms
    de champs exacts de cet endpoint non documenté."""
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return default


def build_ad_payload(item, country_code):
    """Construit le payload JSON du contrat d'ingestion (type="ad") à partir
    d'une publicité brute renvoyée par Creative Center.

    :param dict item: une entrée de la liste renvoyée par
        fetch_trending_ads_page().
    :param str country_code: pays ciblé par ce scan (Creative Center ne
        renvoie pas toujours le pays par publicité individuelle).
    :rtype: dict|None - None si l'entrée n'a pas d'identifiant exploitable
        (pas assez d'info pour construire un ad_ref/product_ref fiable).
    """
    ad_id = _first_present(item, "id", "item_id", "ad_id")
    if not ad_id:
        return None

    ad_title = _first_present(item, "ad_title", "title", default="Publicité TikTok sans titre")
    likes = _first_present(item, "like", "likes", "like_cnt", "like_count", default=0)
    shares = _first_present(item, "share", "shares", "share_cnt", "share_count", default=0)

    return {
        "type": "ad",
        "data": {
            "ad_ref": f"tiktok-{ad_id}",
            # Cf. note en tête de fichier : chaque publicité = son propre
            # product_ref (pas de regroupement par annonceur).
            "product_ref": f"tiktok-product-{ad_id}",
            "product_name": ad_title,
            "country": country_code,
            "social_network": "tiktok",
            "likes_count": int(likes or 0),
            "shares_count": int(shares or 0),
        },
    }


def push_ad_to_odoo(payload, odoo_url, odoo_api_key):
    """Envoie un payload "ad" vers /api/trend/ingest (même contrat que
    ebay_ingestor.push_to_odoo, généralisé au type "ad")."""
    body = dict(payload)
    body["api_key"] = odoo_api_key
    try:
        response = requests.post(odoo_url, json=body, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code != 200:
            _logger.warning(
                "WIN-69: échec ingestion Odoo (%s): %s",
                response.status_code, response.text,
            )
        return response.status_code == 200
    except requests.exceptions.RequestException as exc:
        _logger.warning("WIN-69: erreur de connexion vers Odoo: %s", exc)
        return False


async def run_tiktok_scan(odoo_url, odoo_api_key, pages=1, period=7, country_code="US"):
    """Point d'entrée asynchrone : scanne N pages de Top Ads en parallèle,
    construit les payloads, et les pousse vers Odoo (également en
    parallèle). Les appels HTTP (synchrones, via `requests`) sont délégués
    à des threads via asyncio.to_thread pour un vrai recouvrement I/O sans
    dépendance supplémentaire (cf. note en tête de fichier).

    :rtype: dict {"status": "success", "scanned": int, "inserted": int}
    """
    fetch_tasks = [
        asyncio.to_thread(fetch_trending_ads_page, page, period, country_code)
        for page in range(1, pages + 1)
    ]
    pages_results = await asyncio.gather(*fetch_tasks)

    items = [item for page_items in pages_results for item in page_items]
    payloads = [p for p in (build_ad_payload(item, country_code) for item in items) if p]

    if not payloads:
        return {"status": "success", "scanned": 0, "inserted": 0}

    push_tasks = [
        asyncio.to_thread(push_ad_to_odoo, payload, odoo_url, odoo_api_key)
        for payload in payloads
    ]
    results = await asyncio.gather(*push_tasks)

    return {
        "status": "success",
        "scanned": len(payloads),
        "inserted": sum(1 for ok in results if ok),
    }


def run_tiktok_ingestion(odoo_url, odoo_api_key, pages=1, period=7, country_code="US"):
    """Wrapper synchrone de run_tiktok_scan, pour être appelé depuis un
    contrôleur Odoo (route http classique, non-async) - même rôle que
    run_ingestion_for_keyword() pour l'ingestion eBay."""
    return asyncio.run(
        run_tiktok_scan(odoo_url, odoo_api_key, pages=pages, period=period, country_code=country_code)
    )
