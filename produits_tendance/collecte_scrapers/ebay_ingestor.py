import requests
import base64
import time
from datetime import datetime
import urllib.parse

def get_real_ebay_token(app_id, cert_id):
    """Génère le Token d'accès OAuth 2.0 pour eBay"""
    if not app_id or not cert_id:
        return None
        
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    auth_str = f"{app_id}:{cert_id}"
    b64_auth = base64.b64encode(auth_str.encode()).decode('utf-8')
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_auth}"
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10) 
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"❌ Erreur Authentification eBay : {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur Réseau (Auth) : {e}")
        return None

def fetch_winning_products(keyword, token, attempt=1):
    """Recherche ciblée : Uniquement Achat Immédiat + Neuf"""
    safe_keyword = urllib.parse.quote(keyword)
    
    url = (
        f"https://api.ebay.com/buy/browse/v1/item_summary/search?"
        f"q={safe_keyword}&limit=3&"
        f"filter=buyingOptions:{{FIXED_PRICE}},conditionIds:{{1000}}"
    )
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 429:
            pause_minutes = 5 * attempt 
            print(f"🛑 [ERREUR 429] Quota atteint. Pause de {pause_minutes} minutes.")
            time.sleep(pause_minutes * 60)
            return fetch_winning_products(keyword, token, attempt + 1)
        
        if response.status_code == 200:
            return response.json().get("itemSummaries", [])
        else:
            print(f"❌ Erreur API eBay : {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur Réseau (Fetch) : {e}")
        return []

def push_to_odoo(item, odoo_url, odoo_api_key):
    """Envoie le produit vers Odoo selon le contrat JSON strict"""
    seller_score = item.get("seller", {}).get("feedbackScore", 0.0)
    sales_count = item.get("soldQuantity", 0) 
    country_code = item.get("itemLocation", {}).get("country", "US")
    image_url = item.get("image", {}).get("imageUrl", False)
    categories_list = item.get("categories", [])
    
    if categories_list and len(categories_list) > 0:
        real_category = categories_list[0].get("categoryName", "Tech & Gadgets")
    else:
        real_category = "Tech & Gadgets"
    
    payload = {
        "api_key": odoo_api_key,
        "type": "product",
        "data": {
            "name": item.get("title", "Produit Inconnu")[:100],
            "product_ref": item.get("itemId"),
            "category": real_category,  # <-- Utilisation de la catégorie dynamique ici
            "sales_count": sales_count,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "score_site_x": seller_score, 
            "country": country_code,
            "source": "api",
            "image_url": image_url
        }
    }
    
    try:
        res = requests.post(odoo_url, json=payload, timeout=10)
        if res.status_code != 200:
            print(f"❌ Erreur Odoo : Code {res.status_code} - Détails : {res.text}")
        return res.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion vers Odoo : {e}")
        return False

def run_ingestion_for_keyword(keyword, app_id, cert_id, odoo_url, odoo_api_key):
    """Fonction principale appelée depuis le contrôleur Odoo"""
    token = get_real_ebay_token(app_id, cert_id)
    if not token:
        return {"status": "error", "message": "Échec de l'authentification eBay"}
        
    items = fetch_winning_products(keyword, token)
    success_count = 0
    
    for item in items:
        if push_to_odoo(item, odoo_url, odoo_api_key):
            success_count += 1
        time.sleep(1)
        
    return {"status": "success", "inserted": success_count}
