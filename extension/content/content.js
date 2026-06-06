// Content script - runs on all web pages
console.log('[Purchase Tracker] Content script loaded');

// Track purchases on the page
function trackPurchases() {
    // Common patterns for e-commerce product prices and titles
    const pricePatterns = [
        { selector: '[data-price]', priceAttr: 'data-price', titleAttr: 'data-title' },
        { selector: '.price', priceAttr: 'textContent' },
        { selector: '[itemprop="price"]', priceAttr: 'textContent', titleAttr: 'textContent' },
        { selector: '.product-price', priceAttr: 'textContent' },
        { selector: '[class*="price"]', priceAttr: 'textContent' }
    ];

    const products = [];

    // Search for products on the page
    for (const pattern of pricePatterns) {
        const elements = document.querySelectorAll(pattern.selector);
        elements.forEach(el => {
            let price = pattern.priceAttr === 'textContent' ? el.textContent : el.getAttribute(pattern.priceAttr);
            
            if (price) {
                // Extract numeric value from price string
                const numericPrice = parseFloat(price.replace(/[^0-9.]/g, ''));
                
                if (!isNaN(numericPrice) && numericPrice > 0) {
                    const product = {
                        price: numericPrice,
                        title: el.getAttribute(pattern.titleAttr) || el.textContent.substring(0, 50),
                        url: window.location.href,
                        domain: window.location.hostname,
                        date: new Date().toISOString()
                    };
                    products.push(product);
                }
            }
        });
    }

    // Send tracked products to background script
    if (products.length > 0) {
        chrome.runtime.sendMessage({
            action: 'trackPurchase',
            products: products
        }, response => {
            if (chrome.runtime.lastError) {
                console.log('[Purchase Tracker] Error:', chrome.runtime.lastError);
            }
        });
    }
}

// Listen for messages from popup or background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'trackManual') {
        // Handle manual purchase tracking
        const purchase = {
            price: request.price,
            title: request.title,
            category: request.category,
            url: window.location.href,
            domain: window.location.hostname,
            date: new Date().toISOString()
        };

        chrome.runtime.sendMessage({
            action: 'trackPurchase',
            products: [purchase]
        });

        sendResponse({ success: true });
    }
});

// Inject a floating tracker widget
function injectTrackerWidget() {
    const widget = document.createElement('div');
    widget.id = 'purchase-tracker-widget';
    widget.innerHTML = `
        <style>
            #purchase-tracker-widget {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 10000;
                font-size: 28px;
                transition: transform 0.2s;
            }
            #purchase-tracker-widget:hover {
                transform: scale(1.1);
            }
            #purchase-tracker-widget:active {
                transform: scale(0.95);
            }
            .tracker-popup {
                position: fixed;
                bottom: 100px;
                right: 20px;
                width: 300px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                padding: 16px;
                z-index: 10001;
            }
            .tracker-popup input {
                width: 100%;
                padding: 8px;
                margin-bottom: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            .tracker-popup button {
                width: 100%;
                padding: 10px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
            }
        </style>
        <span></span>
    `;

    widget.addEventListener('click', () => {
        showTrackerPopup();
    });

    document.body.appendChild(widget);
}

function showTrackerPopup() {
    let popup = document.getElementById('tracker-popup');
    if (popup) {
        popup.remove();
        return;
    }

    popup = document.createElement('div');
    popup.id = 'tracker-popup';
    popup.className = 'tracker-popup';
    popup.innerHTML = `
        <h3 style="margin-bottom: 12px; font-size: 14px;">Log Purchase</h3>
        <input type="text" id="product-title" placeholder="Product title">
        <input type="number" id="product-price" placeholder="Price" step="0.01">
        <input type="text" id="product-category" placeholder="Category">
        <button id="save-purchase">Save Purchase</button>
    `;

    document.body.appendChild(popup);

    document.getElementById('save-purchase').addEventListener('click', () => {
        const title = document.getElementById('product-title').value;
        const price = parseFloat(document.getElementById('product-price').value);
        const category = document.getElementById('product-category').value;

        if (title && price && price > 0) {
            chrome.runtime.sendMessage({
                action: 'trackPurchase',
                products: [{
                    title,
                    price,
                    category,
                    url: window.location.href,
                    domain: window.location.hostname,
                    date: new Date().toISOString()
                }]
            });
            popup.remove();
        }
    });
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        trackPurchases();
        injectTrackerWidget();
    });
} else {
    trackPurchases();
    injectTrackerWidget();
}

// Re-track when new content is added to the page
const observer = new MutationObserver(() => {
    trackPurchases();
});

observer.observe(document.body, { childList: true, subtree: true });
