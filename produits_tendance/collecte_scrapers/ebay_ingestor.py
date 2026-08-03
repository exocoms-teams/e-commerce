import os
import requests
import base64
import time
from datetime import datetime, timedelta
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Sur Odoo.sh, python-dotenv n'est pas installé, ce n'est pas grave.
    # Les variables sont gérées nativement par la plateforme.
    pass

# ==========================================
# CONFIGURATION
# ==========================================
ODOO_URL = os.getenv("ODOO_URL")
ODOO_API_KEY = os.getenv("ODOO_API_KEY")
EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_CERT_ID = os.getenv("EBAY_CERT_ID")

def get_real_ebay_token():
    """Génère le Token d'accès OAuth 2.0 pour eBay"""
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    auth_str = f"{EBAY_APP_ID}:{EBAY_CERT_ID}"
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
    url = (
        f"https://api.ebay.com/buy/browse/v1/item_summary/search?"
        f"q={keyword}&limit=3&"
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

def push_to_odoo(item):
    """Envoie le produit vers Odoo selon le contrat JSON strict"""
    seller_score = item.get("seller", {}).get("feedbackScore", 0.0)
    sales_count = item.get("soldQuantity", 0) 
    country_code = item.get("itemLocation", {}).get("country", "US")
    
    payload = {
        "api_key": ODOO_API_KEY,
        "type": "product",
        "data": {
            "name": item.get("title", "Produit Inconnu")[:100],
            "product_ref": item.get("itemId"),
            "category": "Tech & Gadgets", 
            "sales_count": sales_count,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "score_site_x": seller_score, 
            "country": country_code,
            "source": "api"
        }
    }
    
    try:
        res = requests.post(ODOO_URL, json=payload, timeout=10)
        if res.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
         return False

def run_ingestion_for_keyword(keyword):
    """Fonction principale à appeler depuis le contrôleur Odoo"""
    token = get_real_ebay_token()
    if not token:
        return {"status": "error", "message": "Échec de l'authentification eBay"}
        
    items = fetch_winning_products(keyword, token)
    success_count = 0
    
    for item in items:
        if push_to_odoo(item):
            success_count += 1
        time.sleep(1)
        
    return {"status": "success", "inserted": success_count}