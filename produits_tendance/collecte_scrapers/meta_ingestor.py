import requests
import time
import urllib.parse
from datetime import datetime

def fetch_meta_ads(keyword, access_token, attempt=1):
    """Recherche des publicités et extrait les données dynamiques."""
    if not access_token:
        print("❌ Erreur : Jeton d'accès Meta manquant.")
        return []

    safe_keyword = urllib.parse.quote(keyword)
    url = "https://graph.facebook.com/v19.0/ads_archive"
    
    # NOUVEAU : On demande explicitement ad_delivery_start_time et ad_delivery_stop_time
    params = {
        "access_token": access_token,
        "search_terms": safe_keyword,
        # États-Unis, Canada, Royaume-Uni, Australie, France, Allemagne, Espagne, Italie, Maroc
        "ad_reached_countries": "['US', 'CA', 'GB', 'AU', 'FR', 'DE', 'ES', 'IT', 'MA']", 
        "ad_active_status": "ALL", 
        "fields": "id,page_name,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,publisher_platforms",
        "limit": 15 # On augmente un peu la limite pour ratisser plus large
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 429:
            pause_minutes = 5 * attempt 
            print(f"🛑 [ERREUR 429] Quota Meta atteint. Pause de {pause_minutes} minutes.")
            time.sleep(pause_minutes * 60)
            return fetch_meta_ads(keyword, access_token, attempt + 1)
            
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"❌ Erreur API Meta : Code {response.status_code} - {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur Réseau (Meta Fetch) : {e}")
        return []

def calculate_days_active(start_time_str, stop_time_str=None):
    """Calcule le nombre de jours d'activité, même si la pub a été coupée."""
    if not start_time_str:
        return 0, False
    try:
        start_date = datetime.strptime(start_time_str.split('T')[0], "%Y-%m-%d")
        
        # Si la pub a une date de fin, on calcule la durée jusqu'à la fin
        if stop_time_str:
            stop_date = datetime.strptime(stop_time_str.split('T')[0], "%Y-%m-%d")
            days = (stop_date - start_date).days
        else:
            # Sinon, on calcule la durée jusqu'à aujourd'hui
            today = datetime.now()
            days = (today - start_date).days
            
        return max(0, days), start_date.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"⚠️ Erreur de conversion de date : {e}")
        return 0, False

def push_ad_to_odoo(ad, keyword, odoo_url, odoo_api_key):
    """Envoie la publicité vers Odoo avec des valeurs 100% dynamiques."""
    ad_id = ad.get('id')
    if not ad_id:
        return False
        
    normalized_product_ref = f"REF-{keyword.upper().replace(' ', '')}"
    
    # --- 1. DYNAMISME : Dates et statut d'activité ---
    start_time = ad.get('ad_delivery_start_time')
    stop_time = ad.get('ad_delivery_stop_time')
    
    days_active, ad_start_date = calculate_days_active(start_time, stop_time)
    
    # Si Meta nous donne une date de fin (stop_time), c'est que la pub n'est plus active
    is_active_dynamic = False if stop_time else True
    
    # --- 2. DYNAMISME : Réseau social principal ---
    raw_platforms = ad.get('publisher_platforms', [])
    platforms_str = ", ".join(raw_platforms) if isinstance(raw_platforms, list) else "facebook"
    
    # Si la pub tourne UNIQUEMENT sur Instagram, on la tague Instagram, sinon Facebook
    if isinstance(raw_platforms, list) and 'instagram' in raw_platforms and 'facebook' not in raw_platforms:
        social_network_dynamic = 'instagram'
    else:
        social_network_dynamic = 'facebook'
    
    payload = {
        "api_key": odoo_api_key,
        "type": "ad",
        "data": {
            "ad_ref": f"META-AD-{ad_id}",
            "product_ref": normalized_product_ref,
            "product_name": keyword.capitalize(),
            "country": "US",
            
            # Les champs dynamiques injectés ici :
            "social_network": social_network_dynamic,
            "is_active": is_active_dynamic,
            
            "days_active": days_active,
            "ad_start_date": ad_start_date,
            "competitor_page": ad.get('page_name', 'Boutique Inconnue'),
            "snapshot_url": ad.get('ad_snapshot_url', ''),
            "platforms": platforms_str
        }
    }
    
    try:
        res = requests.post(odoo_url, json=payload, timeout=10)
        if res.status_code != 200:
            print(f"❌ Erreur Odoo (Ad) : Code {res.status_code} - {res.text}")
        return res.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion vers Odoo (Meta Push) : {e}")
        return False

def run_meta_ingestion(keyword, access_token, odoo_url, odoo_api_key):
    ads = fetch_meta_ads(keyword, access_token)
    success_count = 0
    
    for ad in ads:
        if push_ad_to_odoo(ad, keyword, odoo_url, odoo_api_key):
            success_count += 1
        time.sleep(1)
        
    return {"status": "success", "inserted": success_count}