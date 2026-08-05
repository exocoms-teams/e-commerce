# -*- coding: utf-8 -*-
import requests
import logging

_logger = logging.getLogger(__name__)

class IngramApiClient:
    """
    Client for interacting with the Ingram Micro IT Catalog API.
    Handles authentication and catalog retrieval.
    """
    
    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None

    def _authenticate(self):
        """
        Authenticate with Ingram Micro to get a Bearer token.
        (Mocked behavior for now, replace with actual Ingram auth endpoint)
        """
        # Example OAuth2 flow
        auth_url = f"{self.base_url}/oauth/oauth20/token"
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        try:
            # Uncomment for real API:
            # response = requests.post(auth_url, data=payload, timeout=10)
            # response.raise_for_status()
            # self.token = response.json().get('access_token')
            
            # MOCK TOKEN FOR NOW
            self.token = "MOCK_INGRAM_TOKEN_12345"
            _logger.info("Ingram Micro API authenticated successfully.")
            return True
        except Exception as e:
            _logger.error("Failed to authenticate with Ingram Micro API: %s", str(e))
            return False

    def fetch_catalog(self, limit=50):
        """
        Fetch products from the Ingram Micro catalog.
        """
        if not self.token:
            if not self._authenticate():
                return []

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json',
            'IM-CustomerNumber': 'YOUR_CUSTOMER_NUMBER', # Usually required by Ingram
            'IM-CountryCode': 'FR'
        }
        
        catalog_url = f"{self.base_url}/catalog/v6/search"
        
        try:
            # Real API Call:
            # response = requests.get(catalog_url, headers=headers, timeout=20)
            # response.raise_for_status()
            # return response.json().get('catalog', [])
            
            # MOCK DATA RETURN
            _logger.info("Mocking Ingram Micro Catalog fetch...")
            return [
                {
                    "vendorNumber": "1234",
                    "vendorName": "HP",
                    "partNumber": "HP-ENVY-15",
                    "ingramPartNumber": "ING-HP-15-001",
                    "description": "HP Envy 15 Laptop, 16GB RAM, 512GB SSD",
                    "customerPrice": 1299.99,
                    "availability": {"availableQuantity": 15}
                },
                {
                    "vendorNumber": "5678",
                    "vendorName": "Dell",
                    "partNumber": "DELL-XPS-13",
                    "ingramPartNumber": "ING-DELL-13-002",
                    "description": "Dell XPS 13, 8GB RAM, 256GB SSD",
                    "customerPrice": 999.50,
                    "availability": {"availableQuantity": 5}
                }
            ]
        except Exception as e:
            _logger.error("Failed to fetch catalog from Ingram Micro: %s", str(e))
            return []
