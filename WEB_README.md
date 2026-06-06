# Purchase Tracker - Web Application

A professional web dashboard for tracking purchasing tendencies and shopping behaviors across e-commerce sites.

## 🎯 Features

✅ **Beautiful Dashboard** - Real-time statistics and insights  
✅ **Purchase History** - Search and filter all purchases  
✅ **Advanced Analytics** - Charts and category breakdowns  
✅ **Trend Analysis** - Spending patterns and domain tracking  
✅ **Dark Mode** - Comfortable viewing in any lighting  
✅ **Data Export/Import** - Backup and restore your data  
✅ **Responsive Design** - Works on desktop, tablet, and mobile  
✅ **Privacy First** - All data stored locally in your browser  

## 📁 File Structure

```
views/
├── index.html                 # Main application page

static/
├── css/
│   ├── style.css             # Global styles & layout
│   └── dashboard.css         # Dashboard specific styles
├── js/
│   ├── app.js                # Application initialization
│   ├── chart.js              # Chart utilities (Chart.js wrapper)
│   ├── data-manager.js       # Data operations and storage
│   ├── dashboard.js          # Dashboard functions
│   └── ui-controller.js      # UI interactions and navigation

controllers/
├── purchase_controller.py    # Backend purchase endpoints
└── analytics_controller.py   # Analytics endpoints

models/
├── purchase.py               # Purchase data model
└── category.py               # Category data model

data/
├── purchases.db              # SQLite database (optional)
└── categories.json           # Categories configuration
```

## 🚀 Quick Start

### 1. Standalone (No Backend Required)

Simply open the web application in your browser:
```bash
# Using Python 3
python -m http.server 8000

# Using Python 2
python -m SimpleHTTPServer 8000

# Using Node.js http-server
npx http-server
```

Then visit: **http://localhost:8000/views/index.html**

### 2. With Flask Backend

```bash
# Install dependencies
pip install flask flask-cors

# Run the server
python app.py

# Visit http://localhost:5000
```

### 3. With Express.js

```bash
# Install dependencies
npm install express cors body-parser

# Run the server
npm start

# Visit http://localhost:3000
```

## 💾 Data Storage

The application uses **localStorage** by default, which means:
- ✅ No backend required
- ✅ Data stored locally in browser
- ✅ Works offline
- ✅ 100% private

You can also sync with the Chrome extension using Chrome's `chrome.storage.local` API.

## 🎨 UI Components

### Navigation
- Sidebar with main menu
- Responsive mobile navigation
- Quick search bar

### Dashboards
1. **Dashboard** - Overview with key metrics and charts
2. **History** - Complete purchase log with filters
3. **Analytics** - Category breakdown and price distribution
4. **Trends** - Domain tracking and spending trends
5. **Settings** - Configuration and data management
6. **About** - App information and links

### Charts
- Spending trend (line chart)
- Category breakdown (pie/doughnut chart)
- Price distribution (bar chart)
- Purchase frequency (line chart)

## 🎯 Key Metrics

**Dashboard displays:**
- 📊 Total Purchases
- 💰 Total Spent
- 📈 Average Price
- 🏷️ Categories Tracked

**Additional Metrics:**
- 📉 Highest Price
- 📊 Price Range Distribution
- 🌐 Top Shopping Domains
- 📅 Daily Spending Trends

## 🔧 Customization

### Change Theme Colors

Edit the CSS variables in `static/css/style.css`:
```css
:root {
    --primary: #667eea;           /* Main color */
    --primary-dark: #764ba2;      /* Dark variant */
    --secondary: #f093fb;         /* Accent color */
    --success: #48dbfb;           /* Success color */
    --danger: #ff6b6b;            /* Error/danger color */
    /* ... more variables */
}
```

### Add Custom Categories

Categories are automatically detected from purchases, but you can pre-define them in `data/categories.json`:
```json
{
    "Electronics": {"icon": "💻", "color": "#667eea"},
    "Clothing": {"icon": "👕", "color": "#f093fb"},
    "Food": {"icon": "🍔", "color": "#48dbfb"},
    "Home": {"icon": "🏠", "color": "#ffa502"}
}
```

### Integrate with Backend

The `data-manager.js` can be extended to use a backend API:
```javascript
async loadData() {
    const response = await fetch('/api/purchases');
    const data = await response.json();
    this.purchases = data.purchases || [];
    // ...
}
```

## 📊 Charts Library

The application uses **Chart.js** for visualizations. To enable charts:

1. Add Chart.js to your HTML:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

Or install locally:
```bash
npm install chart.js
```

## 🔐 Security & Privacy

✅ All data stored locally (localStorage or IndexedDB)  
✅ No data sent to external servers  
✅ No cookies or tracking  
✅ Open source - inspect the code  
✅ Export your data anytime  

## 📱 Mobile Responsive

The application is fully responsive:
- ✅ Desktop (1920px and up)
- ✅ Tablet (1024px - 1920px)
- ✅ Mobile (320px - 1024px)

Sidebar collapses on mobile, search bar adapts, charts responsive.

## 🌙 Dark Mode

Enable dark mode in Settings:
- Easier on the eyes
- Reduced power consumption
- Professional appearance
- Preference saved locally

## 📥 Import/Export

**Export Options:**
- JSON - Full backup (includes all metadata)
- CSV - Spreadsheet compatible

**Import:**
- Select exported JSON file
- Data merges with existing purchases
- Validation before import

## 🐛 Troubleshooting

**Charts not showing?**
- Ensure Chart.js is loaded
- Check browser console for errors
- Verify data is loading correctly

**Data not persisting?**
- Check browser storage settings
- Ensure localStorage is not disabled
- Try incognito/private window

**Sidebar not responsive?**
- Clear browser cache
- Check if CSS is loading (F12 → Network)
- Try different browser

## 📖 API Reference

### DataManager Class

```javascript
// Get purchases
dataManager.getPurchases()

// Get statistics
const stats = dataManager.getStats()
// Returns: {total, amount, average, max, min, categories, domains}

// Get top categories
dataManager.getTopCategories(5)

// Get spending by day
dataManager.getDailySpending(7)

// Export data
const json = dataManager.exportJSON()

// Import data
dataManager.importJSON(jsonData)

// Clear all data
dataManager.clearAll()
```

### UIController Class

```javascript
// Switch page
uiController.switchPage('dashboard')

// Perform search
uiController.performSearch('laptop')

// Export data
uiController.exportData()

// Import data
uiController.importData(file)
```

## 🚢 Deployment

### Deploy to GitHub Pages
```bash
# Push to gh-pages branch
git subtree push --prefix views/ origin gh-pages
```

### Deploy to Netlify
```bash
netlify deploy --prod --dir=views
```

### Deploy to Heroku
```bash
git push heroku main
```

## 📄 License

MIT License - Feel free to use, modify, and distribute!

## 🤝 Contributing

Found a bug? Have suggestions? Open an issue or submit a pull request!

## 📞 Support

- 📧 Email: support@purchasetracker.dev
- 💬 GitHub Issues: [Issues Page]
- 📚 Documentation: [Wiki]

---

**Happy tracking! 🛍️**
