from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import math
from datetime import datetime, timedelta
import hashlib
import re

app = Flask(__name__, static_folder='../dashboard', template_folder='../dashboard')
CORS(app, origins=['*'])  # Allow all origins for testing

DATA_FILE = 'data/tracker_data.json'
os.makedirs('data', exist_ok=True)

# ---- Data helpers ----

def load_data():
    if not os.path.exists(DATA_FILE):
        return {'products': {}, 'categories': {}, 'domains': {}, 'daily': {}, 'last_updated': None}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def make_key(title: str, domain: str) -> str:
    raw = f"{domain}::{title.lower().strip()[:80]}"
    return hashlib.md5(raw.encode()).hexdigest()[:20]


def parse_rating(raw) -> float | None:
    if not raw:
        return None
    match = re.search(r'[\d.]+', str(raw))
    if not match:
        return None
    val = float(match.group())
    if 0 < val <= 5:
        return val
    if 5 < val <= 10:
        return val / 2
    return None


def compute_trend_score(product: dict) -> float:
    now = datetime.utcnow()
    day = timedelta(days=1)

    view_log = product.get('view_log', [])
    views_7d = sum(1 for t in view_log if now - datetime.fromisoformat(t) < 7 * day)
    views_30d = sum(1 for t in view_log if now - datetime.fromisoformat(t) < 30 * day)
    velocity_score = views_7d * 3 + views_30d * 1

    views_3d = sum(1 for t in view_log if now - datetime.fromisoformat(t) < 3 * day)
    views_3to6d = sum(
        1 for t in view_log
        if 3 * day <= now - datetime.fromisoformat(t) < 6 * day
    )
    rising_multiplier = 1.5 if views_3d > 0 and views_3d > views_3to6d * 1.5 else 1.0

    purchase_score = product.get('purchase_count', 0) * 10

    sold_counts = product.get('sold_counts', [])
    sold_score = 0.0
    if len(sold_counts) >= 2:
        delta = sold_counts[-1]['value'] - sold_counts[0]['value']
        sold_score = max(0, delta) * 0.5
    elif len(sold_counts) == 1:
        sold_score = sold_counts[0]['value'] * 0.05

    price_signal = 0.0
    prices = product.get('prices', [])
    if len(prices) >= 2:
        values = [p['value'] for p in prices]
        avg_price = sum(values) / len(values)
        latest_price = values[-1]
        drop_pct = (avg_price - latest_price) / avg_price if avg_price > 0 else 0
        if drop_pct >= 0.05:
            price_signal = 8.0
        if drop_pct >= 0.15:
            price_signal = 15.0

    rating_signal = 0.0
    ratings = product.get('ratings', [])
    reviews = product.get('reviews', [])
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        review_count = reviews[-1] if reviews else 1
        try:
            review_count = int(review_count)
        except (ValueError, TypeError):
            review_count = 1
        rating_signal = avg_rating * math.log(1 + review_count) * 0.3

    raw_score = velocity_score + purchase_score + sold_score + price_signal + rating_signal
    return round(raw_score * rising_multiplier, 1)


def enrich_product(p: dict) -> dict:
    prices = p.get('prices', [])
    ratings = p.get('ratings', [])
    reviews = p.get('reviews', [])
    sold_counts = p.get('sold_counts', [])
    view_log = p.get('view_log', [])

    price_values = [x['value'] for x in prices]
    avg_price = round(sum(price_values) / len(price_values), 2) if price_values else None
    latest_price = price_values[-1] if price_values else None

    price_trend = None
    if avg_price and latest_price:
        price_trend = round((latest_price - avg_price) / avg_price * 100, 1)

    avg_rating = round(sum(float(r) for r in ratings) / len(ratings), 1) if ratings else None
    latest_sold = sold_counts[-1]['value'] if sold_counts else None

    sold_delta = None
    if len(sold_counts) >= 2:
        sold_delta = sold_counts[-1]['value'] - sold_counts[0]['value']

    now = datetime.utcnow()
    day = timedelta(days=1)
    views_7d = sum(1 for t in view_log if now - datetime.fromisoformat(t) < 7 * day)
    views_3d = sum(1 for t in view_log if now - datetime.fromisoformat(t) < 3 * day)
    views_3to6d = sum(
        1 for t in view_log
        if 3 * day <= now - datetime.fromisoformat(t) < 6 * day
    )
    is_rising = views_3d > 0 and views_3d > views_3to6d * 1.5

    return {
        **p,
        'avg_price': avg_price,
        'latest_price': latest_price,
        'price_trend': price_trend,
        'avg_rating': avg_rating,
        'latest_sold': latest_sold,
        'sold_delta': sold_delta,
        'views_7d': views_7d,
        'is_rising': is_rising,
        'trend_score': compute_trend_score(p),
    }


# ---- Routes ----

@app.route('/')
def index():
    return send_from_directory('../website', 'index.html')


@app.route('/website/<path:filename>')
def website_files(filename):
    return send_from_directory('../website', filename)


@app.route('/dashboard/')
def dashboard_index():
    return send_from_directory('../dashboard', 'index.html')


@app.route('/dashboard/<path:filename>')
def dashboard_files(filename):
    return send_from_directory('../dashboard', filename)


@app.route('/api/track', methods=['POST'])
def track_product():
    body = request.get_json(force=True, silent=True) or {}
    product = body.get('product')
    is_purchase = body.get('isPurchase', False)

    if not product or not product.get('title'):
        return jsonify({'error': 'Missing product title'}), 400

    domain = product.get('domain', 'unknown')
    domain_root = domain.replace('www.', '').split('.')[0].lower()
    title = product.get('title', '')
    if domain_root in title.lower() and len(title) < 30:
        return jsonify({'error': 'Low-quality title rejected'}), 400

    data = load_data()
    key = make_key(title, domain)
    products = data['products']
    now = datetime.utcnow().isoformat()

    if key not in products:
        products[key] = {
            'id': key,
            'title': title[:200],
            'domain': domain,
            'category': product.get('category', 'General'),
            'image': product.get('image'),
            'url': product.get('url', ''),
            'first_seen': product.get('timestamp', now),
            'last_seen': product.get('timestamp', now),
            'view_count': 0,
            'purchase_count': 0,
            'prices': [],
            'ratings': [],
            'reviews': [],
            'sold_counts': [],
            'view_log': [],
        }

    entry = products[key]
    entry['view_count'] += 1
    entry['last_seen'] = now

    entry.setdefault('view_log', [])
    entry['view_log'].append(now)
    if len(entry['view_log']) > 60:
        entry['view_log'] = entry['view_log'][-60:]

    if is_purchase:
        entry['purchase_count'] += 1

    if product.get('price') and float(product['price']) > 0:
        entry['prices'].append({'value': float(product['price']), 'date': now})
        entry['prices'] = entry['prices'][-50:]

    parsed_rating = parse_rating(product.get('rating'))
    if parsed_rating is not None:
        entry['ratings'].append(parsed_rating)
        entry['ratings'] = entry['ratings'][-20:]

    if product.get('reviews'):
        try:
            review_count = int(str(product['reviews']).replace(',', '').replace('.', '').split()[0])
            entry['reviews'].append(review_count)
            entry['reviews'] = entry['reviews'][-20:]
        except (ValueError, IndexError):
            pass

    if product.get('soldCount'):
        raw = str(product['soldCount'])
        is_floor = '+' in raw
        try:
            value = int(raw.replace('+', '').replace(',', '').strip().split()[0])
            entry['sold_counts'].append({'value': value, 'is_floor': is_floor, 'date': now})
            entry['sold_counts'] = entry['sold_counts'][-20:]
        except (ValueError, IndexError):
            pass

    cat = product.get('category', 'General')
    data['categories'][cat] = data['categories'].get(cat, 0) + 1
    data['domains'][domain] = data['domains'].get(domain, 0) + 1

    today = datetime.utcnow().strftime('%Y-%m-%d')
    if today not in data['daily']:
        data['daily'][today] = {'views': 0, 'purchases': 0}
    data['daily'][today]['views'] += 1
    if is_purchase:
        data['daily'][today]['purchases'] += 1

    data['last_updated'] = now
    save_data(data)

    print(f"[Tracker] ✅ Tracked: {title[:50]}... (views: {entry['view_count']})")
    return jsonify({'success': True, 'key': key})


@app.route('/api/products', methods=['GET'])
def get_products():
    data = load_data()
    search = request.args.get('q', '').lower()
    category = request.args.get('category', '')
    limit = min(int(request.args.get('limit', 100)), 500)
    rising_only = request.args.get('rising', '').lower() == 'true'

    products = [enrich_product(p) for p in data['products'].values()]

    if search:
        products = [p for p in products if search in p['title'].lower() or search in p['domain']]
    if category:
        products = [p for p in products if p.get('category') == category]
    if rising_only:
        products = [p for p in products if p.get('is_rising')]

    products.sort(key=lambda p: p['trend_score'], reverse=True)

    total_views = sum(p['view_count'] for p in data['products'].values())
    total_purchases = sum(p['purchase_count'] for p in data['products'].values())

    return jsonify({
        'products': products[:limit],
        'total': len(products),
        'categories': data['categories'],
        'domains': data['domains'],
        'daily': data['daily'],
        'last_updated': data.get('last_updated'),
        'total_products': len(data['products']),
        'total_views': total_views,
        'total_purchases': total_purchases,
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    data = load_data()
    products = [enrich_product(p) for p in data['products'].values()]

    total_views = sum(p['view_count'] for p in products)
    total_purchases = sum(p['purchase_count'] for p in products)
    all_prices = [pr['value'] for p in products for pr in p.get('prices', [])]
    avg_price = round(sum(all_prices) / len(all_prices), 2) if all_prices else 0

    sorted_products = sorted(products, key=lambda p: p['trend_score'], reverse=True)
    top_product = sorted_products[0]['title'] if sorted_products else None

    cats = data.get('categories', {})
    top_cat = max(cats, key=cats.get) if cats else None

    domains = data.get('domains', {})
    top_domain = max(domains, key=domains.get) if domains else None

    daily = data.get('daily', {})
    today = datetime.utcnow().date()
    week_views = sum(daily.get(str(today - timedelta(days=i)), {}).get('views', 0) for i in range(7))
    week_purchases = sum(daily.get(str(today - timedelta(days=i)), {}).get('purchases', 0) for i in range(7))

    rising_count = sum(1 for p in products if p.get('is_rising'))

    return jsonify({
        'total_products': len(products),
        'total_views': total_views,
        'total_purchases': total_purchases,
        'avg_price': avg_price,
        'top_product': top_product,
        'top_category': top_cat,
        'top_domain': top_domain,
        'week_views': week_views,
        'week_purchases': week_purchases,
        'conversion_rate': round(total_purchases / total_views * 100, 1) if total_views > 0 else 0,
        'rising_count': rising_count,
    })


@app.route('/api/export', methods=['GET'])
def export_data():
    return jsonify(load_data())


@app.route('/api/import', methods=['POST'])
def import_data():
    body = request.get_json(force=True, silent=True)
    if not body or 'products' not in body:
        return jsonify({'error': 'Invalid data format'}), 400
    save_data(body)
    return jsonify({'success': True, 'imported': len(body.get('products', {}))})


@app.route('/api/clear', methods=['DELETE'])
def clear_data():
    save_data({'products': {}, 'categories': {}, 'domains': {}, 'daily': {}, 'last_updated': None})
    return jsonify({'success': True})


if __name__ == '__main__':
    print('=' * 50)
    print('🔍 Tracker Backend')
    print('=' * 50)
    print(f'📍 Running at: http://localhost:5000')
    print(f'📊 Dashboard: http://localhost:5000/dashboard/')
    print(f'📥 Download: http://localhost:5000/')
    print('=' * 50)
    app.run(debug=True, port=5000, host='0.0.0.0')