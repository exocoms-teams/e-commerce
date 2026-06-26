# -*- coding: utf-8 -*-
"""Correspondance géographique zone artisan ↔ adresse mission."""
import re
import unicodedata


def normalize_zone_text(text):
    if not text:
        return ''
    text = unicodedata.normalize('NFD', text.lower().strip())
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')


def extract_location_keys(adresse):
    """Extrait codes postaux, départements et libellés utiles depuis une adresse."""
    if not adresse:
        return set()

    keys = set()
    norm = normalize_zone_text(adresse)

    for cp in re.findall(r'\b(\d{5})\b', adresse):
        keys.add(cp)
        if cp.startswith(('97', '98')):
            keys.add(cp[:3])
        else:
            keys.add(cp[:2])

    for dept in re.findall(r'\b(\d{2})\b', adresse):
        keys.add(dept)

    for arr in re.findall(r'paris\s*(\d{1,2})(?:e|er|re|eme|ème)?', norm):
        arr_num = int(arr)
        if 1 <= arr_num <= 20:
            keys.add(f'750{arr_num:02d}')
            keys.add('75')
            keys.add(f'paris{arr_num}')

    if 'paris' in norm:
        keys.add('paris')
        keys.add('75')

    for part in adresse.split(','):
        cleaned = normalize_zone_text(part)
        cleaned = re.sub(r'\b\d{5}\b', '', cleaned).strip()
        cleaned = re.sub(r'\s+\d{1,2}(?:e|er|re|eme|ème)?$', '', cleaned).strip()
        if cleaned and len(cleaned) >= 3 and not cleaned.isdigit():
            keys.add(cleaned)

    return keys


def parse_zone_tokens(zone_str):
    """
    Parse la zone artisan.
    Retourne None si la zone est vide (= couvre tous les secteurs).
    """
    if not zone_str or not str(zone_str).strip():
        return None

    tokens = set()
    for raw in re.split(r'[,;/|\n]+', str(zone_str)):
        chunk = raw.strip()
        if not chunk:
            continue
        norm = normalize_zone_text(chunk)
        tokens.add(norm)

        for cp in re.findall(r'\b(\d{5})\b', chunk):
            tokens.add(cp)
            if cp.startswith(('97', '98')):
                tokens.add(cp[:3])
            else:
                tokens.add(cp[:2])

        for dept in re.findall(r'\b(\d{2})\b', chunk):
            tokens.add(dept)

        if 'paris' in norm:
            tokens.add('paris')
            tokens.add('75')
            m_cp = re.search(r'paris\s*(\d{5})', norm)
            if m_cp:
                cp = m_cp.group(1)
                tokens.add(cp)
                tokens.add(cp[:2])
            m_arr = re.search(r'paris\s*(\d{1,2})', norm)
            if m_arr:
                arr_num = int(m_arr.group(1))
                if 1 <= arr_num <= 20:
                    tokens.add(f'750{arr_num:02d}')
                    tokens.add(f'paris{arr_num}')

    return tokens or None


def _token_matches_key(token, key):
    if token == key:
        return True
    if len(token) == 2 and token.isdigit() and key.startswith(token):
        return True
    if len(token) == 3 and token.isdigit() and key.startswith(token):
        return True
    if len(key) == 2 and key.isdigit() and token.startswith(key):
        return True
    if len(token) >= 3 and not token.isdigit() and token in key:
        return True
    if len(key) >= 3 and not key.isdigit() and key in token:
        return True
    return False


def adresse_dans_zone(adresse, zone_intervention):
    """True si l'adresse mission est couverte par la zone de l'artisan."""
    tokens = parse_zone_tokens(zone_intervention)
    if tokens is None:
        return True

    keys = extract_location_keys(adresse)
    if not keys:
        return False

    return any(
        _token_matches_key(token, key)
        for token in tokens
        for key in keys
    )
