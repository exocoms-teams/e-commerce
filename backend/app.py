from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import re
import time
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

app = Flask(__name__, static_folder='dashboard/static', template_folder='dashboard/templates')
CORS(app, origins=['chrome-extension://*', 'http://localhost:*'])

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


def compute_trend_score(product: dict) -> float:
    views = product.get('view_count', 0)
    purchases = product.get('purchase_count', 0)
    sold_counts = product.get('sold_counts', [])
    latest_sold = sold_counts[-1] if sold_counts else 0
    return views * 1 + purchases * 10 + latest_sold * 0.1


# ---- Routes ----

@app.route('/')
def index():
    return send_from_directory('website', 'index.html')


@app.route('/website/<path:filename>')
def website_files(filename):
    return send_from_directory('website', filename)


@app.route('/extension/<path:filename>')
def extension_assets(filename):
    return send_from_directory('extension', filename)


@app.route('/dashboard/')
@app.route('/dashboard/<path:filename>')
def dashboard(filename='index.html'):
    return send_from_directory('dashboard', filename)


@app.route('/api/track', methods=['POST'])
def track_product():
    """Receive product data from the Chrome extension or web clients."""
    body = request.get_json(force=True, silent=True) or {}
    product = body.get('product')
    is_purchase = body.get('isPurchase', False)

    if not product or not product.get('title'):
        return jsonify({'error': 'Missing product title'}), 400

    data = load_data()
    key = make_key(product['title'], product.get('domain', 'unknown'))
    products = data['products']

    if key not in products:
        products[key] = {
            'id': key,
            'title': product['title'][:200],
            'domain': product.get('domain', 'unknown'),
            'category': product.get('category', 'General'),
            'image': product.get('image'),
            'url': product.get('url', ''),
            'first_seen': product.get('timestamp', datetime.utcnow().isoformat()),
            'last_seen': product.get('timestamp', datetime.utcnow().isoformat()),
            'view_count': 0,
            'purchase_count': 0,
            'prices': [],
            'ratings': [],
            'reviews': [],
            'sold_counts': [],
        }

    entry = products[key]
    entry['view_count'] += 1
    entry['last_seen'] = product.get('timestamp', datetime.utcnow().isoformat())

    if is_purchase:
        entry['purchase_count'] += 1

    if product.get('price') and float(product['price']) > 0:
        entry['prices'].append({'value': float(product['price']), 'date': entry['last_seen']})
        entry['prices'] = entry['prices'][-50:]

    for field, key_name in [('rating', 'ratings'), ('reviews', 'reviews'), ('soldCount', 'sold_counts')]:
        val = product.get(field)
        if val:
            entry[key_name].append(val)
            entry[key_name] = entry[key_name][-20:]

    # Update aggregates
    cat = product.get('category', 'General')
    data['categories'][cat] = data['categories'].get(cat, 0) + 1

    domain = product.get('domain', 'unknown')
    data['domains'][domain] = data['domains'].get(domain, 0) + 1

    today = datetime.utcnow().strftime('%Y-%m-%d')
    if today not in data['daily']:
        data['daily'][today] = {'views': 0, 'purchases': 0}
    data['daily'][today]['views'] += 1
    if is_purchase:
        data['daily'][today]['purchases'] += 1

    data['last_updated'] = datetime.utcnow().isoformat()
    save_data(data)

    return jsonify({'success': True, 'key': key})


@app.route('/api/products', methods=['GET'])
def get_products():
    """Return products sorted by trend score."""
    data = load_data()
    search = request.args.get('q', '').lower()
    category = request.args.get('category', '')
    limit = min(int(request.args.get('limit', 100)), 500)

    products = list(data['products'].values())

    # Enrich
    for p in products:
        prices = p.get('prices', [])
        ratings = p.get('ratings', [])
        p['avg_price'] = round(sum(x['value'] for x in prices) / len(prices), 2) if prices else None
        p['latest_price'] = prices[-1]['value'] if prices else None
        p['avg_rating'] = round(sum(float(r) for r in ratings) / len(ratings), 1) if ratings else None
        p['latest_sold'] = p['sold_counts'][-1] if p.get('sold_counts') else None
        p['trend_score'] = compute_trend_score(p)

    # Filter
    if search:
        products = [p for p in products if search in p['title'].lower() or search in p['domain']]
    if category:
        products = [p for p in products if p.get('category') == category]

    products.sort(key=lambda p: p['trend_score'], reverse=True)

    return jsonify({
        'products': products[:limit],
        'total': len(products),
        'categories': data['categories'],
        'domains': data['domains'],
        'daily': data['daily'],
        'last_updated': data.get('last_updated'),
        'total_products': len(data['products']),
        'total_views': sum(p['view_count'] for p in data['products'].values()),
        'total_purchases': sum(p['purchase_count'] for p in data['products'].values()),
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Summary statistics."""
    data = load_data()
    products = list(data['products'].values())

    total_views = sum(p['view_count'] for p in products)
    total_purchases = sum(p['purchase_count'] for p in products)
    all_prices = [pr['value'] for p in products for pr in p.get('prices', [])]
    avg_price = round(sum(all_prices) / len(all_prices), 2) if all_prices else 0

    # Top product
    top = sorted(products, key=compute_trend_score, reverse=True)
    top_product = top[0]['title'] if top else None

    # Top category
    cats = data.get('categories', {})
    top_cat = max(cats, key=cats.get) if cats else None

    # Top domain
    domains = data.get('domains', {})
    top_domain = max(domains, key=domains.get) if domains else None

    # 7-day activity
    daily = data.get('daily', {})
    today = datetime.utcnow().date()
    week_views = sum(daily.get(str(today - timedelta(days=i)), {}).get('views', 0) for i in range(7))
    week_purchases = sum(daily.get(str(today - timedelta(days=i)), {}).get('purchases', 0) for i in range(7))

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
    })


@app.route('/api/trending', methods=['GET'])
def get_trending():
    """Top N trending products."""
    data = load_data()
    n = min(int(request.args.get('n', 20)), 100)
    products = list(data['products'].values())

    for p in products:
        p['trend_score'] = compute_trend_score(p)
        prices = p.get('prices', [])
        p['latest_price'] = prices[-1]['value'] if prices else None

    products.sort(key=lambda p: p['trend_score'], reverse=True)
    return jsonify({'trending': products[:n]})


@app.route('/api/categories', methods=['GET'])
def get_categories():
    data = load_data()
    cats = data.get('categories', {})
    return jsonify({
        'categories': [{'name': k, 'count': v} for k, v in sorted(cats.items(), key=lambda x: -x[1])]
    })


@app.route('/api/export', methods=['GET'])
def export_data():
    data = load_data()
    return jsonify(data)


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
    print('Python Backend')
    print('Running at http://localhost:5000')
    print('Download page at http://localhost:5000/')
    print('Dashboard at http://localhost:5000/dashboard/')
    app.run(debug=True, port=5000)
