import hashlib
import hmac
import time

from odoo import http as odoo_http
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestSneakerRouteGuards(HttpCase):
    """Multi-site isolation for the guarded sneaker routes.

    With ``x_sneakers_theme`` enabled, each route must serve the sneaker
    page. With it disabled, each route must fall back to the current
    website's own content (or 404) and never expose any sneaker theme
    markup — regression test for the exocoms.fr leak.
    """

    SNEAKER_MARKERS = ('sn-header', 'o_sneakers')

    # The 14 guarded routes: 10 public GET pages, the product page,
    # and 3 authenticated routes (GET /wishlist, GET /my/orders,
    # POST /payment).
    PUBLIC_ROUTES = (
        '/shop-sneakers',
        '/contact',
        '/terms',
        '/about',
        '/faq',
        '/careers',
        '/shipping',
        '/returns',
        '/privacy-policy',
        '/confirmation',
    )
    AUTH_ROUTES = (
        '/wishlist',
        '/my/orders',
    )

    def setUp(self):
        super().setUp()
        self.website = self.env['website'].search([], limit=1)
        self.product = self.env['product.template'].create({
            'name': 'Route Guard Test Product',
            'website_published': True,
        })

    # === HELPERS === #

    def _csrf_token(self):
        """Build a valid CSRF token for the authenticated test session."""
        secret = self.env['ir.config_parameter'].sudo().get_param('database.secret')
        max_ts = int(time.time()) + 3600
        session_id = self.session.sid[:odoo_http.STORED_SESSION_BYTES]
        digest = hmac.new(
            secret.encode('ascii'), f'{session_id}{max_ts}'.encode(), hashlib.sha1,
        ).hexdigest()
        return f'{digest}o{max_ts}'

    def _assert_sneaker_page(self, response, url):
        """The sneaker theme must be fully served on this route."""
        self.assertEqual(
            response.status_code, 200, f'{url} returned {response.status_code}',
        )
        for marker in self.SNEAKER_MARKERS:
            self.assertIn(marker, response.text, f'{url} is not a sneaker page')

    def _assert_not_sneaker(self, response, url):
        """The current website must never see sneaker theme markup.

        Allowed outcomes: the website's own page (200) or no match (404).
        """
        self.assertIn(
            response.status_code, (200, 404),
            f'{url} returned {response.status_code}',
        )
        for marker in self.SNEAKER_MARKERS:
            self.assertNotIn(marker, response.text, f'{url} leaked the sneaker theme')

    # === FLAG ENABLED === #

    def test_flag_enabled_serves_sneaker_pages(self):
        self.website.x_sneakers_theme = True
        urls = [*self.PUBLIC_ROUTES, f'/product/{self.product.id}']
        for url in urls:
            with self.subTest(url=url):
                self._assert_sneaker_page(self.url_open(url), url)

    def test_flag_enabled_authenticated_routes(self):
        self.website.x_sneakers_theme = True
        self.authenticate('admin', 'admin')
        for url in self.AUTH_ROUTES:
            with self.subTest(url=url):
                self._assert_sneaker_page(self.url_open(url), url)
        # /my is routed to the sneaker homepage while the flag is on
        # (it overrides portal.CustomerPortal.home).
        self._assert_sneaker_page(self.url_open('/my'), '/my')
        # POST /payment redirects to the core payment page.
        response = self.url_open(
            '/payment',
            data={'csrf_token': self._csrf_token()},
            allow_redirects=False,
        )
        self.assertIn(
            response.status_code, (302, 303),
            f'/payment must redirect, got {response.status_code}',
        )
        self.assertTrue(
            response.headers.get('Location', '').endswith('/shop/payment'),
            f'/payment redirected to {response.headers.get("Location")}',
        )

    # === FLAG DISABLED (multi-site isolation) === #

    def test_flag_disabled_does_not_serve_sneaker_pages(self):
        self.website.x_sneakers_theme = False
        urls = [*self.PUBLIC_ROUTES, f'/product/{self.product.id}']
        for url in urls:
            with self.subTest(url=url):
                self._assert_not_sneaker(self.url_open(url), url)

    def test_flag_disabled_authenticated_routes(self):
        self.website.x_sneakers_theme = False
        self.authenticate('admin', 'admin')
        for url in self.AUTH_ROUTES:
            with self.subTest(url=url):
                self._assert_not_sneaker(self.url_open(url), url)
        # /my must fall back to the portal dashboard: the sneaker homepage
        # content (sn-hero) must never be served while the flag is off,
        # even though it carries no global theme markers.
        response = self.url_open('/my')
        self._assert_not_sneaker(response, '/my')
        self.assertNotIn(
            'sn-hero', response.text,
            '/my leaked the sneaker homepage while the flag is off',
        )
        response = self.url_open(
            '/payment',
            data={'csrf_token': self._csrf_token()},
            allow_redirects=False,
        )
        self._assert_not_sneaker(response, '/payment')
