#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
product_spec_sheet/scripts/fetch_specs_shipping.py
====================================================
Récupère les caractéristiques complètes (poids, dimensions, specs techniques)
des produits sur internet, puis calcule les frais de port par transporteur.

DÉPENDANCES :
    pip install requests beautifulsoup4 lxml anthropic

UTILISATION :
    # Un seul produit
    python3 fetch_specs_shipping.py --product "Ingenico Desk/5000"

    # Fichier liste (un produit par ligne)
    python3 fetch_specs_shipping.py --file produits.txt

    # Mode silencieux + export CSV
    python3 fetch_specs_shipping.py --file produits.txt --csv resultats.csv

    # Forcer la mise à jour Odoo via shell (depuis racine Odoo)
    python3 fetch_specs_shipping.py --file produits.txt --odoo-output odoo_import.txt
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import quote_plus

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Erreur : pip install requests beautifulsoup4 lxml")

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# ═══════════════════════════════════════════════════════════════════
#  CONFIGURATION TRANSPORTEURS — tarifs 2025 France métropolitaine
#  (indicatifs, à mettre à jour depuis les grilles tarifaires)
# ═══════════════════════════════════════════════════════════════════

CARRIERS = {
    "Colissimo": {
        "zones": {
            "France": [
                (250,   5.45), (500,   5.65), (750,   6.10), (1000,  6.35),
                (2000,  7.10), (3000,  8.30), (5000, 10.15), (10000, 13.15),
                (15000, 16.40), (30000, 22.75),
            ],
            "Europe zone 1": [
                (500,   8.95), (1000, 10.10), (2000, 12.50), (5000, 17.80),
                (10000, 26.40), (30000, 42.00),
            ],
            "Europe zone 2": [
                (500,  11.20), (1000, 13.00), (2000, 16.50), (5000, 23.00),
                (10000, 34.00), (30000, 56.00),
            ],
        },
        "volumetric_divisor": 5000,
        "max_weight_kg": 30,
        "max_size_cm": 150,
    },
    "Chronopost": {
        "zones": {
            "France 13h": [
                (500,   9.50), (1000, 10.50), (2000, 12.00), (3000, 13.50),
                (5000, 15.00), (10000, 20.00), (30000, 35.00),
            ],
            "France 18h": [
                (500,   8.50), (1000,  9.50), (2000, 11.00), (3000, 12.50),
                (5000, 14.00), (10000, 18.50), (30000, 30.00),
            ],
            "Europe J+1": [
                (500,  15.00), (1000, 17.50), (2000, 22.00), (5000, 30.00),
                (10000, 42.00), (30000, 70.00),
            ],
        },
        "volumetric_divisor": 5000,
        "max_weight_kg": 30,
        "max_size_cm": 150,
    },
    "DHL Express": {
        "zones": {
            "France J+1": [
                (500,  11.00), (1000, 12.50), (2000, 14.50), (3000, 16.50),
                (5000, 19.00), (10000, 27.00), (30000, 48.00),
            ],
            "Europe J+1": [
                (500,  18.00), (1000, 21.00), (2000, 26.00), (5000, 36.00),
                (10000, 52.00), (30000, 90.00),
            ],
        },
        "volumetric_divisor": 5000,
        "max_weight_kg": 70,
        "max_size_cm": 300,
    },
    "UPS": {
        "zones": {
            "Standard France": [
                (500,   8.50), (1000,  9.50), (2000, 11.00), (3000, 13.00),
                (5000, 15.50), (10000, 21.00), (30000, 34.00),
            ],
            "Express France": [
                (500,  13.00), (1000, 15.00), (2000, 18.00), (3000, 21.00),
                (5000, 26.00), (10000, 37.00), (30000, 60.00),
            ],
            "Standard Europe": [
                (500,  12.00), (1000, 14.00), (2000, 17.00), (5000, 24.00),
                (10000, 34.00), (30000, 56.00),
            ],
        },
        "volumetric_divisor": 5000,
        "max_weight_kg": 70,
        "max_size_cm": 274,
    },
    "GLS": {
        "zones": {
            "France": [
                (500,   6.50), (1000,  7.50), (2000,  9.00), (3000, 10.50),
                (5000, 12.50), (10000, 17.50), (30000, 27.00),
            ],
            "Europe": [
                (500,  10.00), (1000, 12.00), (2000, 15.00), (5000, 21.00),
                (10000, 30.00), (30000, 50.00),
            ],
        },
        "volumetric_divisor": 5000,
        "max_weight_kg": 40,
        "max_size_cm": 200,
    },
}

# Sites fabricants prioritaires pour les produits EXOCOMS
MANUFACTURER_DOMAINS = {
    "ingenico": "ingenico.com",
    "pax": "paxtechnology.com",
    "sunmi": "sunmi.com",
    "panini": "panini.com",
    "verifone": "verifone.com",
    "castles": "castlestechnology.com",
    "bbpos": "bbpos.com",
    "newland": "newlandnpd.com",
    "honeywell": "sps.honeywell.com",
    "zebra": "zebra.com",
    "epson": "epson.fr",
    "star": "starmicronics.com",
}

# Patterns regex pour extraire poids et dimensions
PATTERNS = {
    "weight_kg": [
        r"(?:poids|weight|masse|grammes?|kg)\s*[:\-]?\s*([0-9]+[.,][0-9]*)\s*kg",
        r"(?:poids|weight|masse)\s*[:\-]?\s*([0-9]+[.,][0-9]*)\s*g(?:ramme)?s?\b",
        r"\b([0-9]+[.,][0-9]*)\s*kg\b",
    ],
    "weight_g": [
        r"\b([0-9]{2,4})\s*g(?:ramme)?s?\b",
        r"(?:poids|weight|masse)\s*[:\-]?\s*([0-9]+)\s*g\b",
    ],
    "dimensions_mm": [
        r"([0-9]+[.,]?[0-9]*)\s*[×xX]\s*([0-9]+[.,]?[0-9]*)\s*[×xX]\s*([0-9]+[.,]?[0-9]*)\s*mm",
        r"(?:dim|lxlxh|l\s*[×x]\s*l\s*[×x]\s*h)\s*[:\-]?\s*([0-9]+[.,]?[0-9]*)\s*[×xX]\s*([0-9]+[.,]?[0-9]*)\s*[×xX]\s*([0-9]+[.,]?[0-9]*)",
    ],
    "dimensions_cm": [
        r"([0-9]+[.,]?[0-9]*)\s*[×xX]\s*([0-9]+[.,]?[0-9]*)\s*[×xX]\s*([0-9]+[.,]?[0-9]*)\s*cm",
    ],
}

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ═══════════════════════════════════════════════════════════════════
#  DATACLASSES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ProductSpecs:
    name: str
    ref: str = ""
    weight_kg: Optional[float] = None
    length_mm: Optional[float] = None
    width_mm: Optional[float] = None
    height_mm: Optional[float] = None
    os: str = ""
    cpu: str = ""
    memory: str = ""
    screen: str = ""
    connectivity: str = ""
    card_reader: str = ""
    ports: str = ""
    battery: str = ""
    certification: str = ""
    extra: dict = field(default_factory=dict)
    source_url: str = ""
    confidence: str = "low"   # low | medium | high

    @property
    def volume_cm3(self) -> Optional[float]:
        if all([self.length_mm, self.width_mm, self.height_mm]):
            return (self.length_mm / 10) * (self.width_mm / 10) * (self.height_mm / 10)
        return None

    @property
    def dims_str(self) -> str:
        if all([self.length_mm, self.width_mm, self.height_mm]):
            return f"{self.length_mm:.0f} × {self.width_mm:.0f} × {self.height_mm:.0f} mm"
        return ""


@dataclass
class ShippingQuote:
    carrier: str
    zone: str
    billed_weight_kg: float
    price_eur: float
    is_volumetric: bool = False
    note: str = ""


# ═══════════════════════════════════════════════════════════════════
#  RECHERCHE WEB
# ═══════════════════════════════════════════════════════════════════

def _get(url: str, timeout: int = 10) -> Optional[requests.Response]:
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception as e:
        print(f"  [WARN] GET {url[:60]}… → {e}")
        return None


def search_duckduckgo(query: str, max_results: int = 8) -> list[str]:
    """Recherche DuckDuckGo HTML — renvoie les URLs des premiers résultats."""
    url = "https://html.duckduckgo.com/html/"
    try:
        resp = requests.post(
            url,
            data={"q": query},
            headers={**HTTP_HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
            timeout=12,
        )
        soup = BeautifulSoup(resp.text, "lxml")
        links = []
        for a in soup.select("a.result__url"):
            href = a.get("href", "")
            if href.startswith("http") and "duckduckgo" not in href:
                links.append(href)
                if len(links) >= max_results:
                    break
        return links
    except Exception as e:
        print(f"  [WARN] DuckDuckGo search → {e}")
        return []


def fetch_text(url: str) -> str:
    """Télécharge une page et renvoie son texte brut (nettoyé)."""
    resp = _get(url)
    if not resp:
        return ""
    soup = BeautifulSoup(resp.text, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s{2,}", " ", text)
    return text[:12000]


def get_candidate_urls(product_name: str) -> list[str]:
    """
    Construit la liste d'URLs à inspecter pour un produit :
    1. URLs directes fabricant si le nom est reconnu
    2. Résultats DuckDuckGo
    """
    urls = []
    name_lower = product_name.lower()

    # Tentative URL fabricant directe
    for brand, domain in MANUFACTURER_DOMAINS.items():
        if brand in name_lower:
            slug = re.sub(r"[^a-z0-9]+", "-", name_lower).strip("-")
            urls.append(f"https://www.{domain}/search?q={quote_plus(product_name)}")
            urls.append(f"https://www.{domain}/fr/products/{slug}")
            break

    # DuckDuckGo
    time.sleep(0.5)
    queries = [
        f'{product_name} fiche technique spécifications poids dimensions',
        f'{product_name} datasheet specifications weight dimensions',
        f'{product_name} technical specifications filetype:pdf',
    ]
    for q in queries[:2]:
        urls += search_duckduckgo(q, max_results=5)
        time.sleep(0.8)

    # Déduplication en conservant l'ordre
    seen = set()
    result = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            result.append(u)
    return result[:12]


# ═══════════════════════════════════════════════════════════════════
#  EXTRACTION PAR REGEX
# ═══════════════════════════════════════════════════════════════════

def _float(s: str) -> float:
    return float(s.replace(",", "."))


def extract_weight(text: str) -> Optional[float]:
    """Renvoie le poids en kg (float) ou None."""
    for pat in PATTERNS["weight_kg"]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return _float(m.group(1))
    for pat in PATTERNS["weight_g"]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = _float(m.group(1))
            if 10 < val < 50000:       # filtre valeurs aberrantes
                return val / 1000
    return None


def extract_dimensions(text: str) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """Renvoie (L, l, H) en mm ou (None, None, None)."""
    for pat in PATTERNS["dimensions_mm"]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return _float(m.group(1)), _float(m.group(2)), _float(m.group(3))
    for pat in PATTERNS["dimensions_cm"]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return _float(m.group(1)) * 10, _float(m.group(2)) * 10, _float(m.group(3)) * 10
    return None, None, None


def extract_field(text: str, *keywords: str) -> str:
    """Extrait la valeur suivant un mot-clé sur la même ligne."""
    for kw in keywords:
        pattern = rf"{re.escape(kw)}\s*[:\-]?\s*([^\n\r\|;]{{3,80}})"
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip().rstrip(".,;")
            if len(val) > 3:
                return val
    return ""


def regex_extract(text: str, product_name: str) -> ProductSpecs:
    """Extraction rapide par expressions régulières."""
    specs = ProductSpecs(name=product_name)
    specs.weight_kg = extract_weight(text)
    specs.length_mm, specs.width_mm, specs.height_mm = extract_dimensions(text)

    specs.os = extract_field(text, "système d'exploitation", "operating system", "OS")
    specs.cpu = extract_field(text, "processeur", "processor", "CPU", "SoC")
    specs.memory = extract_field(text, "mémoire", "memory", "RAM", "stockage", "flash")
    specs.screen = extract_field(text, "écran", "display", "screen", "résolution")
    specs.connectivity = extract_field(text, "connectivité", "connectivity", "réseau", "network", "WiFi")
    specs.card_reader = extract_field(text, "lecteur", "card reader", "piste", "NFC", "sans contact")
    specs.ports = extract_field(text, "port", "interface", "USB", "ethernet", "RS232")
    specs.battery = extract_field(text, "batterie", "battery", "autonomie", "mAh")
    specs.certification = extract_field(text, "certification", "norme", "PCI", "EMV", "CE")

    return specs


# ═══════════════════════════════════════════════════════════════════
#  EXTRACTION IA (ANTHROPIC) — optionnelle
# ═══════════════════════════════════════════════════════════════════

def ai_extract(text: str, product_name: str, api_key: Optional[str] = None) -> Optional[ProductSpecs]:
    """Extraction via l'API Anthropic — plus précise sur les textes complexes."""
    if not HAS_ANTHROPIC:
        return None
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None

    client = anthropic.Anthropic(api_key=key)
    prompt = f"""Tu es un expert en fiches techniques produit. Extrais les caractéristiques de ce produit : "{product_name}".

Réponds UNIQUEMENT en JSON valide, sans markdown, sans explication :
{{
  "weight_kg": null,
  "length_mm": null,
  "width_mm": null,
  "height_mm": null,
  "os": "",
  "cpu": "",
  "memory": "",
  "screen": "",
  "connectivity": "",
  "card_reader": "",
  "ports": "",
  "battery": "",
  "certification": "",
  "extra": {{}}
}}

Texte source :
{text[:6000]}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        data = json.loads(raw)
        specs = ProductSpecs(name=product_name, confidence="high")
        for k, v in data.items():
            if hasattr(specs, k) and v not in (None, "", {}):
                setattr(specs, k, v)
        return specs
    except Exception as e:
        print(f"  [WARN] API Anthropic → {e}")
        return None


# ═══════════════════════════════════════════════════════════════════
#  ORCHESTRATION : récupérer les specs d'un produit
# ═══════════════════════════════════════════════════════════════════

def fetch_product_specs(product_name: str, api_key: Optional[str] = None) -> ProductSpecs:
    print(f"\n{'═'*60}")
    print(f"Produit : {product_name}")
    print(f"{'─'*60}")

    best: Optional[ProductSpecs] = None
    urls = get_candidate_urls(product_name)
    print(f"  {len(urls)} URL(s) candidates trouvées")

    for url in urls:
        print(f"  → {url[:70]}…")
        text = fetch_text(url)
        if not text or len(text) < 200:
            continue

        # Tentative IA d'abord
        specs = ai_extract(text, product_name, api_key)
        if specs is None:
            specs = regex_extract(text, product_name)
            specs.confidence = "medium" if (specs.weight_kg or specs.length_mm) else "low"

        specs.source_url = url

        # Choisir le meilleur résultat : priorité au poids + dimensions
        score = sum([
            specs.weight_kg is not None,
            specs.length_mm is not None,
            bool(specs.os),
            bool(specs.cpu),
            bool(specs.screen),
        ])

        best_score = sum([
            best.weight_kg is not None if best else False,
            best.length_mm is not None if best else False,
            bool(best.os) if best else False,
            bool(best.cpu) if best else False,
            bool(best.screen) if best else False,
        ]) if best else -1

        if score > best_score:
            best = specs
            print(f"     ✓ meilleur résultat (score={score}/5, confiance={specs.confidence})")

        if best and best.weight_kg and best.length_mm:
            print(f"     → Données suffisantes, arrêt de la recherche")
            break

        time.sleep(0.5)

    if best is None:
        best = ProductSpecs(name=product_name, confidence="low")

    print(f"  Poids      : {best.weight_kg:.3f} kg" if best.weight_kg else "  Poids      : NON TROUVÉ")
    print(f"  Dimensions : {best.dims_str}" if best.dims_str else "  Dimensions : NON TROUVÉES")
    return best


# ═══════════════════════════════════════════════════════════════════
#  CALCUL FRAIS DE PORT
# ═══════════════════════════════════════════════════════════════════

def volumetric_weight(length_mm: float, width_mm: float, height_mm: float, divisor: int = 5000) -> float:
    """Poids volumétrique en kg = (L × l × H cm³) / diviseur."""
    return (length_mm / 10) * (width_mm / 10) * (height_mm / 10) / divisor


def carrier_price(weight_g: float, grid: list[tuple]) -> Optional[float]:
    """Interpolation linéaire dans la grille tarifaire."""
    for max_g, price in grid:
        if weight_g <= max_g:
            return price
    return None   # hors gabarit


def calculate_shipping(specs: ProductSpecs) -> list[ShippingQuote]:
    quotes = []
    if not specs.weight_kg:
        return quotes

    weight_g = specs.weight_kg * 1000

    for carrier_name, carrier_cfg in CARRIERS.items():
        divisor = carrier_cfg["volumetric_divisor"]
        max_kg = carrier_cfg["max_weight_kg"]

        # Poids volumétrique si on a les dimensions
        vol_weight_g = 0.0
        is_vol = False
        if all([specs.length_mm, specs.width_mm, specs.height_mm]):
            vol_weight_g = volumetric_weight(
                specs.length_mm, specs.width_mm, specs.height_mm, divisor
            ) * 1000
            is_vol = vol_weight_g > weight_g

        billed_g = max(weight_g, vol_weight_g)
        billed_kg = billed_g / 1000

        if billed_kg > max_kg:
            for zone_name in carrier_cfg["zones"]:
                quotes.append(ShippingQuote(
                    carrier=carrier_name, zone=zone_name,
                    billed_weight_kg=billed_kg, price_eur=0.0,
                    note=f"Hors gabarit (max {max_kg} kg)",
                ))
            continue

        for zone_name, grid in carrier_cfg["zones"].items():
            price = carrier_price(billed_g, grid)
            if price:
                quotes.append(ShippingQuote(
                    carrier=carrier_name, zone=zone_name,
                    billed_weight_kg=round(billed_kg, 3),
                    price_eur=price, is_volumetric=is_vol,
                    note="poids volumétrique" if is_vol else "",
                ))

    return quotes


# ═══════════════════════════════════════════════════════════════════
#  FORMATAGE CONSOLE
# ═══════════════════════════════════════════════════════════════════

def print_report(specs: ProductSpecs, quotes: list[ShippingQuote]):
    print(f"\n{'━'*60}")
    print(f"  RAPPORT : {specs.name}")
    print(f"{'━'*60}")
    print(f"  Poids réel    : {specs.weight_kg:.3f} kg" if specs.weight_kg else "  Poids réel    : —")
    print(f"  Dimensions    : {specs.dims_str}" if specs.dims_str else "  Dimensions    : —")
    if specs.volume_cm3:
        print(f"  Volume        : {specs.volume_cm3:.1f} cm³")
    print(f"  Source        : {specs.source_url[:70]}" if specs.source_url else "")
    print(f"  Confiance     : {specs.confidence.upper()}")

    if specs.os:        print(f"  OS            : {specs.os}")
    if specs.cpu:       print(f"  Processeur    : {specs.cpu}")
    if specs.memory:    print(f"  Mémoire       : {specs.memory}")
    if specs.screen:    print(f"  Écran         : {specs.screen}")
    if specs.connectivity: print(f"  Connectivité  : {specs.connectivity}")
    if specs.card_reader:  print(f"  Lecteur carte : {specs.card_reader}")
    if specs.battery:   print(f"  Batterie      : {specs.battery}")
    if specs.certification: print(f"  Certification : {specs.certification}")

    if not quotes:
        print("\n  [INFO] Poids requis pour calculer les frais de port.")
        return

    print(f"\n  {'TRANSPORTEUR':<18} {'ZONE':<22} {'POIDS FACTURÉ':>14} {'TARIF HT':>10}  NOTE")
    print(f"  {'─'*18} {'─'*22} {'─'*14} {'─'*10}  {'─'*16}")
    for q in quotes:
        note = "(vol.)" if q.is_volumetric else q.note or ""
        if q.price_eur == 0.0:
            price_str = "hors gabarit"
        else:
            price_str = f"{q.price_eur:.2f} €"
        print(f"  {q.carrier:<18} {q.zone:<22} {q.billed_weight_kg:>11.3f} kg {price_str:>10}  {note}")


def format_odoo_import(specs: ProductSpecs) -> str:
    """Génère le texte pour l'assistant d'import du module."""
    lines = [f"# {specs.name}"]
    if specs.os:          lines.append(f"Système ; Système d'exploitation ; {specs.os}")
    if specs.cpu:         lines.append(f"Système ; Processeur ; {specs.cpu}")
    if specs.memory:      lines.append(f"Système ; Mémoire ; {specs.memory}")
    if specs.screen:      lines.append(f"Écran ; Taille ; {specs.screen}")
    if specs.connectivity: lines.append(f"Connectivité ; Réseaux ; {specs.connectivity}")
    if specs.card_reader: lines.append(f"Connectivité ; Lecteur de carte ; {specs.card_reader}")
    if specs.ports:       lines.append(f"Connectivité ; Ports ; {specs.ports}")
    if specs.battery:     lines.append(f"Alimentation ; Batterie ; {specs.battery}")
    if specs.certification: lines.append(f"Sécurité ; Certification ; {specs.certification}")
    if specs.weight_kg:   lines.append(f"Dimensions et poids ; Poids ; {specs.weight_kg:.3f} kg")
    if specs.dims_str:    lines.append(f"Dimensions et poids ; Encombrement ; {specs.dims_str}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
#  CSV OUTPUT
# ═══════════════════════════════════════════════════════════════════

def write_csv(results: list[tuple[ProductSpecs, list[ShippingQuote]]], path: str):
    """Exporte les résultats en CSV (un produit par ligne, tarifs en colonnes)."""
    # Collecter toutes les combinaisons transporteur+zone
    all_zones = []
    seen = set()
    for _, quotes in results:
        for q in quotes:
            key = f"{q.carrier} — {q.zone}"
            if key not in seen:
                seen.add(key)
                all_zones.append((q.carrier, q.zone, key))

    fieldnames = [
        "Produit", "Référence", "Poids (kg)", "Long. (mm)", "Larg. (mm)",
        "Haut. (mm)", "Volume (cm³)", "Source", "Confiance",
        "OS", "Processeur", "Mémoire", "Écran", "Connectivité",
        "Lecteur carte", "Batterie", "Certification",
    ] + [z[2] for z in all_zones] + ["Poids facturé (kg)", "Volumétrique ?"]

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for specs, quotes in results:
            row = {
                "Produit": specs.name,
                "Référence": specs.ref,
                "Poids (kg)": specs.weight_kg or "",
                "Long. (mm)": specs.length_mm or "",
                "Larg. (mm)": specs.width_mm or "",
                "Haut. (mm)": specs.height_mm or "",
                "Volume (cm³)": f"{specs.volume_cm3:.1f}" if specs.volume_cm3 else "",
                "Source": specs.source_url,
                "Confiance": specs.confidence,
                "OS": specs.os,
                "Processeur": specs.cpu,
                "Mémoire": specs.memory,
                "Écran": specs.screen,
                "Connectivité": specs.connectivity,
                "Lecteur carte": specs.card_reader,
                "Batterie": specs.battery,
                "Certification": specs.certification,
            }
            billed = ""
            is_vol = ""
            for q in quotes:
                key = f"{q.carrier} — {q.zone}"
                row[key] = f"{q.price_eur:.2f} €" if q.price_eur else "hors gabarit"
                billed = q.billed_weight_kg
                is_vol = "oui" if q.is_volumetric else "non"
            row["Poids facturé (kg)"] = billed
            row["Volumétrique ?"] = is_vol
            writer.writerow(row)

    print(f"\n✓ CSV exporté : {path}")


# ═══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Récupération specs produit + calcul frais de port")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--product", "-p", help="Nom du produit à rechercher")
    group.add_argument("--file", "-f", help="Fichier texte avec un produit par ligne")

    parser.add_argument("--csv", "-o", help="Export CSV des résultats")
    parser.add_argument("--odoo-output", help="Export fichier texte compatible assistant d'import Odoo")
    parser.add_argument("--api-key", help="Clé API Anthropic (ou variable ANTHROPIC_API_KEY)")
    args = parser.parse_args()

    products = []
    if args.product:
        products = [args.product.strip()]
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            products = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    if not products:
        sys.exit("Aucun produit à traiter.")

    results = []
    odoo_blocks = []

    for name in products:
        specs = fetch_product_specs(name, api_key=args.api_key)
        quotes = calculate_shipping(specs)
        print_report(specs, quotes)
        results.append((specs, quotes))
        odoo_blocks.append(format_odoo_import(specs))
        time.sleep(1)

    if args.csv:
        write_csv(results, args.csv)

    if args.odoo_output:
        with open(args.odoo_output, "w", encoding="utf-8") as f:
            f.write("\n\n".join(odoo_blocks))
        print(f"\n✓ Fichier Odoo exporté : {args.odoo_output}")

    print(f"\n{'═'*60}")
    print(f"  {len(products)} produit(s) traité(s)")
    print(f"{'═'*60}")


if __name__ == "__main__":
    main()
