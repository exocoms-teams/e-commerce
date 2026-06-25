import uuid

import requests


class IngramApiClient:
    def __init__(
        self,
        client_id,
        client_secret,
        customer_number,
        country_code="US",
        sender_id="Exocoms",
    ):
        self.base_url = "https://api.ingrammicro.com:443"
        self.client_id = client_id
        self.client_secret = client_secret
        self.customer_number = customer_number
        self.country_code = country_code
        self.sender_id = sender_id
        self.access_token = None

    def get_token(self):
        url = f"{self.base_url}/oauth/oauth30/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(url, data=data, timeout=30)
        response.raise_for_status()

        self.access_token = response.json()["access_token"]
        return self.access_token

    def test_connection(self):
        return bool(self.get_token())

    def _headers(self):
        if not self.access_token:
            self.get_token()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "IM-CustomerNumber": self.customer_number,
            "IM-CountryCode": self.country_code,
            "IM-SenderID": self.sender_id,
            "IM-CorrelationID": str(uuid.uuid4()),
            "Accept": "application/json",
        }

    def _request(self, method, url, retry_on_unauthorized=True, **kwargs):
        response = requests.request(method, url, timeout=30, **kwargs)
        if response.status_code == 401 and retry_on_unauthorized:
            self.access_token = None
            headers = kwargs.get("headers") or {}
            headers = {
                key: value for key, value in headers.items()
                if key.lower() != "authorization"
            }
            headers.update(self._headers())
            kwargs["headers"] = headers
            return self._request(
                method, url, retry_on_unauthorized=False, **kwargs
            )
        response.raise_for_status()
        return response.json()

    def search_products(self, keyword, page_size=10, page_number=1):
        url = f"{self.base_url}/resellers/v6/catalog"

        params = {
            "keyword": keyword,
            "type": "IM::any",
            "pageSize": page_size,
            "pageNumber": page_number,
        }

        return self._request(
            "get", url, headers=self._headers(), params=params
        )

    def get_product_details(self, ingram_part_number):
        url = f"{self.base_url}/resellers/v6/catalog/details/{ingram_part_number}"

        return self._request("get", url, headers=self._headers())

    def get_price_and_availability(self, products):
        url = f"{self.base_url}/resellers/v6/catalog/priceandavailability"

        params = {
            "includeAvailability": "true",
            "includePricing": "true",
        }

        payload = {
            "showAvailableDiscounts": False,
            "showReserveInventoryDetails": False,
            "products": products,
        }

        return self._request(
            "post",
            url,
            headers={**self._headers(), "Content-Type": "application/json"},
            params=params,
            json=payload,
        )

    def create_order_v7(self, payload):
        url = f"{self.base_url}/resellers/v7/orders"

        return self._request(
            "post",
            url,
            headers={**self._headers(), "Content-Type": "application/json"},
            json=payload,
        )

    def create_order_v6(self, payload):
        url = f"{self.base_url}/resellers/v6/orders"

        return self._request(
            "post",
            url,
            headers={**self._headers(), "Content-Type": "application/json"},
            json=payload,
        )

    def get_order(self, order_number):
        url = f"{self.base_url}/resellers/v6/orders/{order_number}"

        return self._request("get", url, headers=self._headers())

    def modify_order(self, order_number, payload, action_code=None):
        url = f"{self.base_url}/resellers/v6/orders/{order_number}"

        params = {}
        if action_code:
            params["actionCode"] = action_code

        return self._request(
            "put",
            url,
            headers={**self._headers(), "Content-Type": "application/json"},
            params=params,
            json=payload,
        )

    def cancel_order(self, order_number):
        url = f"{self.base_url}/resellers/v6/orders/{order_number}"

        return self._request("delete", url, headers=self._headers())
