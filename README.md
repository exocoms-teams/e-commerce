# 🛍️ Purchase Tracker - Complete System

A comprehensive purchase tracking system consisting of:
- 📊 **Web Dashboard** - Professional analytics interface
- 🔌 **Chrome Extension** - Auto-tracking on e-commerce sites
- 💾 **Data Manager** - Secure local storage with backup/restore
- 📈 **Analytics Engine** - Charts, trends, and insights

## 🎯 Quick Start

### Fastest Way (5 minutes)

**Option A: Open Web App Directly**
```bash
# Windows
start views/index.html

# macOS
open views/index.html

# Linux
xdg-open views/index.html
```

**Option B: Local Server (Recommended)**
```bash
# Python 3
python -m http.server 8000
# Then visit: http://localhost:8000/views/

# Node.js
npx http-server
# Then visit: http://localhost:8080/views/
```

**Option C: Install & Run Chrome Extension**
1. Open `chrome://extensions/`
2. Enable Developer Mode
3. Click "Load unpacked"
4. Select `extension/` folder
5. Done! 🎉

## 📁 Project Structure

```
e-commerce/
│
├── 📄 README.md (this file)
├── 📦 package.json
│
├── 🔌 extension/                    (Chrome Extension)
│   ├── manifest.json
│   ├── popup/
│   ├── content/
│   ├── background/
│   ├── options/
│   ├── icons/
│   └── README.md
│
├── 🌐 views/                        (Web Dashboard)
│   └── index.html
│
├── 🎨 static/                       (Web Assets)
│   ├── css/
│   │   ├── style.css
│   │   └── dashboard.css
│   └── js/
│       ├── app.js
│       ├── chart.js
│       ├── data-manager.js
│       ├── dashboard.js
│       └── ui-controller.js
│
├── 🔧 controllers/                  (Backend Optional)
│   ├── purchase_controller.py
│   └── analytics_controller.py
│
├── 📊 models/                       (Data Models Optional)
│   ├── purchase.py
│   └── category.py
│
├── 💾 data/                         (Data Storage)
│   ├── purchases.db
│   └── categories.json
│
└── 📚 Documentation
    ├── README.md (this file)
    ├── extension/README.md
    ├── WEB_README.md
    ├── WEB_SETUP.md
    └── SETUP.md

```

## ✨ Features

### 🌐 Web Application
- ✅ Real-time dashboard with key metrics
- ✅ Purchase history with advanced search
- ✅ Analytics with multiple chart types
- ✅ Trend analysis and domain tracking
- ✅ Dark mode support
- ✅ Data export/import (JSON & CSV)
- ✅ Fully responsive design
- ✅ No backend required

### 🔌 Chrome Extension
- ✅ Auto-track purchases on e-commerce sites
- ✅ Manual purchase logging with floating widget
- ✅ Real-time notifications
- ✅ Popup dashboard
- ✅ Full options/settings page
- ✅ Category organization
- ✅ Data export functionality
- ✅ 100% privacy - no data sent to servers

### 💾 Data Management
- ✅ Local storage (localStorage)
- ✅ Chrome extension sync
- ✅ JSON export/import
- ✅ CSV export for spreadsheets
- ✅ Automatic categorization
- ✅ Domain tracking
- ✅ Purchase history with metadata

### 📊 Analytics
- ✅ Spending trends (7, 14, 30 days)
- ✅ Category breakdown
- ✅ Price distribution
- ✅ Purchase frequency
- ✅ Top domains
- ✅ Statistics (average, max, min)

## 🚀 Getting Started

### 1. Web Application

**Standalone (No Backend):**
```bash
# Just open the file
open views/index.html
```

**With Local Server:**
```bash
# Python
python -m http.server 8000
# Visit: http://localhost:8000/views/

# Node.js
npx http-server -p 8000
# Visit: http://localhost:8000/views/
```

**With Flask Backend:**
```bash
pip install flask flask-cors
python app.py
# Visit: http://localhost:5000
```

### 2. Chrome Extension

**Installation:**
1. Navigate to `chrome://extensions/`
2. Enable "Developer Mode" (top-right)
3. Click "Load unpacked"
4. Select `extension` folder
5. Click the 🛍️ icon to start using

**Usage:**
- Auto-tracks purchases on e-commerce sites
- Click floating widget (📊) to log manually
- View stats in popup dashboard
- Manage settings in options page

### 3. Integration

**Connect Extension to Web App:**
- Install both extension and web app
- Open web app in browser
- Extension automatically syncs data
- See purchases update in real-time

## 📊 Dashboard Overview

### Pages

| Page | Purpose | Features |
|------|---------|----------|
| **Dashboard** | Overview | Stats, charts, recent purchases |
| **History** | Purchase log | Search, filter, view all purchases |
| **Analytics** | Data analysis | Charts, category breakdown |
| **Trends** | Patterns | Spending trends, domain stats |
| **Settings** | Configuration | Dark mode, export/import, cleanup |
| **About** | Info | App version, storage size, links |

### Key Metrics

- **Total Purchases** - Count of all tracked purchases
- **Total Spent** - Sum of all purchase amounts
- **Average Price** - Mean price per purchase
- **Categories** - Number of purchase categories
- **Top Domains** - Most shopped websites
- **Spending Trends** - Daily/weekly/monthly analysis

## 🔐 Privacy & Security

✅ **No Data Collection** - We don't collect any data  
✅ **Local Storage Only** - Everything stays on your device  
✅ **No Servers** - No data sent anywhere  
✅ **No Tracking** - No analytics or tracking code  
✅ **Open Source** - Inspect the code yourself  
✅ **Export Anytime** - Download your data in JSON format  
✅ **Delete Anytime** - Clear all data with one click  

## 💻 System Requirements

**Browser Requirements:**
- Chrome 90+ (recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

**Storage Requirements:**
- ~100 KB for application files
- ~10 MB for 10,000 purchases
- Depends on your data volume

**Optional Backend:**
- Python 3.7+ (Flask)
- Node.js 12+ (Express)
- SQLite or PostgreSQL

## 📖 Documentation

### User Guides
- [Web App README](WEB_README.md) - Features and usage
- [Web App Setup](WEB_SETUP.md) - Installation guide
- [Extension README](extension/README.md) - Chrome extension guide
- [Extension Setup](extension/SETUP.md) - Installation steps

### Developer Guides
- [API Documentation](#api-documentation)
- [Extending the App](#extending)
- [Deployment Guide](#deployment)

## 🛠️ API Documentation

### DataManager Class

```javascript
// Get all purchases
const purchases = dataManager.getPurchases()

// Get statistics
const stats = dataManager.getStats()
// {total, amount, average, max, min, categories, domains}

// Get top categories
const topCats = dataManager.getTopCategories(5)

// Get spending by day
const spending = dataManager.getDailySpending(7)

// Add a purchase
dataManager.addPurchase({
    title: 'Product Name',
    price: 29.99,
    category: 'Electronics',
    domain: 'amazon.com'
})

// Export data
const json = dataManager.exportJSON()
const csv = dataManager.exportCSV()

// Import data
dataManager.importJSON(jsonData)

// Clear all
dataManager.clearAll()
```

### UIController Class

```javascript
// Switch page
uiController.switchPage('dashboard')

// Search purchases
uiController.performSearch('laptop')

// Export data
uiController.exportData()

// Import data
uiController.importData(file)
```

## 🎨 Customization

### Change Theme Colors

Edit `static/css/style.css`:
```css
:root {
    --primary: #667eea;        /* Main color */
    --primary-dark: #764ba2;   /* Dark variant */
    --secondary: #f093fb;      /* Accent */
    --danger: #ff6b6b;         /* Error */
}
```

### Add Categories

Edit `data/categories.json`:
```json
{
    "Electronics": {"icon": "💻", "color": "#667eea"},
    "Clothing": {"icon": "👕", "color": "#f093fb"}
}
```

### Integrate Backend

Modify `static/js/data-manager.js`:
```javascript
async loadData() {
    const response = await fetch('/api/purchases');
    this.purchases = await response.json();
}
```

## 🚢 Deployment

### GitHub Pages
```bash
git subtree push --prefix views/ origin gh-pages
```

### Netlify
```bash
netlify deploy --prod --dir=views
```

### Heroku
```bash
git push heroku main
```

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install flask flask-cors
CMD ["python", "app.py"]
```

## 📱 Features by Platform

| Feature | Web | Extension |
|---------|-----|-----------|
| Dashboard | ✅ | ✅ |
| History | ✅ | ✅ |
| Analytics | ✅ | ✅ |
| Export | ✅ | ✅ |
| Import | ✅ | ✅ |
| Dark Mode | ✅ | ✅ |
| Auto Track | ❌ | ✅ |
| Manual Log | ❌ | ✅ |
| Sync | ✅ | ✅ |

## 🐛 Troubleshooting

**Charts not showing?**
- Ensure Chart.js is loaded
- Check F12 console for errors
- Verify data exists

**Data not saving?**
- Check browser storage enabled
- Try incognito mode
- Check storage limit

**Extension not tracking?**
- Ensure on e-commerce site
- Check extension is enabled
- Verify permissions granted

**Styles broken?**
- Clear browser cache
- Hard refresh (Ctrl+Shift+R)
- Check CSS files exist

## 📚 Learning Resources

- [Chrome Extension API Docs](https://developer.chrome.com/docs/extensions/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -am 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📄 License

MIT License - Feel free to use, modify, and distribute!

## 🙏 Acknowledgments

- Chart.js for beautiful charts
- Chrome Extension API
- Community feedback and contributions

## 📞 Support

- 🐛 **Report Bugs** - Open GitHub Issue
- 💡 **Suggest Features** - GitHub Discussions
- 📧 **Contact** - support@example.com
- 💬 **Chat** - Discord Community (Coming Soon)

## 📝 Changelog

### v1.0.0 - Initial Release
- ✨ Web dashboard
- ✨ Chrome extension
- ✨ Data management
- ✨ Analytics engine
- ✨ Documentation

## 🎯 Roadmap

- [ ] Multi-device sync
- [ ] Cloud backup
- [ ] User accounts
- [ ] Advanced filters
- [ ] Budget tracking
- [ ] AI insights
- [ ] Mobile app
- [ ] Cryptocurrency tracking

## 🎉 Ready to Start?

1. **Web App**: `python -m http.server 8000` then open http://localhost:8000/views/
2. **Extension**: Load unpacked from `extension/` folder
3. **Documentation**: Read setup guides
4. **Contribute**: Submit PRs and issues

---

**Happy tracking! 📊🛍️**

*Last Updated: June 5, 2024*
*Version: 1.0.0*
