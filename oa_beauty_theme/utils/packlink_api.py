import requests
import logging

_logger = logging.getLogger(__name__)

class PacklinkAPIConnector:
    """
    Modular connector for Packlink PRO API.
    Provides methods to retrieve services, create shipments, and track parcels.
    """
    
    def __init__(self, api_key, sandbox=True):
        self.api_key = api_key
        self.sandbox = sandbox
        self.base_url = 'https://api.sandbox.packlink.com/v1' if sandbox else 'https://api.packlink.com/v1'
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _make_request(self, method, endpoint, data=None, params=None):
        if not self.api_key:
            _logger.warning("Packlink API Key is missing. Returning mocked data.")
            return self._get_mocked_response(endpoint)

        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f"Packlink API Error on {endpoint}: {str(e)}")
            return None

    def get_services(self, from_country, from_zip, to_country, to_zip, packages):
        """Fetch available shipping services and prices"""
        # Packlink requires specific payload structure for services
        # This is a skeleton ready for the real API
        params = {
            'from[country]': from_country,
            'from[zip]': from_zip,
            'to[country]': to_country,
            'to[zip]': to_zip,
        }
        # In a real implementation, packages would be appended to params
        return self._make_request('GET', 'services', params=params)

    def create_shipment(self, shipment_data):
        """Create a new shipment/draft in Packlink PRO"""
        return self._make_request('POST', 'shipments', data=shipment_data)

    def get_tracking(self, tracking_number):
        """Retrieve tracking events for a shipment"""
        return self._make_request('GET', f'shipments/{tracking_number}/track')

    def _get_mocked_response(self, endpoint):
        """Return mocked data when API key is missing (for architecture preparation)"""
        if 'track' in endpoint:
            return {
                'history': [
                    {'description': 'Delivered', 'city': 'Paris', 'date': '2026-07-05T10:00:00Z'},
                    {'description': 'In transit', 'city': 'Lyon', 'date': '2026-07-04T14:30:00Z'},
                    {'description': 'Label created', 'city': 'Warehouse', 'date': '2026-07-03T09:15:00Z'}
                ],
                'status': 'DELIVERED'
            }
        return {}
