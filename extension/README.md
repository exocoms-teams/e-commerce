# 🛍️ Purchase Tracker Chrome Extension

A powerful Chrome extension for tracking purchasing tendencies and shopping behaviors across e-commerce sites.

## Features

✅ **Auto-Track Purchases** - Automatically detects and logs purchases on e-commerce sites  
✅ **Manual Logging** - Add purchases manually with a floating widget  
✅ **Category Tracking** - Organize purchases by category  
✅ **Purchase History** - View complete history with search and filters  
✅ **Analytics Dashboard** - View statistics, trends, and insights  
✅ **Data Export** - Export data as CSV or JSON for backup  
✅ **Desktop Notifications** - Get notified when purchases are tracked  
✅ **Privacy-Focused** - All data stored locally in your browser  

## Project Structure

```
extension/
├── manifest.json           # Extension configuration (Chrome Manifest v3)
├── popup/                  # Popup UI when clicking extension icon
│   ├── popup.html         # Popup interface
│   ├── popup.css          # Popup styling
│   └── popup.js           # Popup functionality
├── content/               # Content script (runs on all pages)
│   └── content.js         # Auto-tracking & floating widget
├── background/            # Background service worker
│   └── background.js      # Data persistence & notifications
├── options/               # Options/settings page
│   ├── options.html       # Settings interface
│   ├── options.css        # Settings styling
│   └── options.js         # Settings functionality
├── icons/                 # Extension icons
│   ├── icon16.png        # Taskbar icon
│   ├── icon48.png        # Management page icon
│   └── icon128.png       # Store icon
└── README.md             # This file
```

## Installation

### Manual Installation (for development)

1. **Download this extension** from your e-commerce repo
2. Open Chrome and go to: `chrome://extensions/`
3. Enable **Developer Mode** (top-right corner)
4. Click **Load unpacked**
5. Select the `extension` folder
6. The extension will appear in your Chrome toolbar!

### From Chrome Web Store (when published)
Soon available on the Chrome Web Store!

## How to Use

### Automatic Tracking
1. The extension automatically detects products on e-commerce sites
2. When you make a purchase, it's tracked and stored locally
3. Check the popup (🛍️ icon) to see today's stats

### Manual Tracking
1. Click the floating **📊** widget on any page
2. Enter product details (title, price, category)
3. Click "Save Purchase"

### View Statistics
1. Click the extension icon → **View History** button
2. Or go to Settings → view complete analytics
3. Search by product name or domain
4. Filter by category

### Export Data
- **CSV Export**: Perfect for spreadsheets
- **JSON Export**: Complete backup of all data
- Go to Settings → Data Management

## Permissions Explained

| Permission | Why | Privacy Impact |
|-----------|-----|-----------------|
| `storage` | Save purchase data locally | Data never leaves your device |
| `scripting` | Inject tracking code | Only detects products, no personal data collected |
| `tabs` | Access current page info | Used to get domain name for organization |
| `<all_urls>` | Run on all websites | Tracks purchases across any e-commerce site |

## Data Privacy

🔒 **Your data is yours alone**
- All data is stored **locally** in Chrome storage
- Nothing is sent to servers
- No tracking, no analytics, no ads
- You can export or delete anytime

## Features Breakdown

### Popup Dashboard
- Quick stats for today
- Items tracked count
- Total spent & average price
- Category breakdown
- Settings access

### Floating Widget
- Click 📊 icon on any page
- Quick purchase logging
- Auto-fills domain & URL
- Appears in bottom-right corner

### Options/Settings Page
Shows 4 tabs:
1. **Overview** - Statistics & top categories
2. **History** - Complete purchase log with search
3. **Trends** - Domain visit patterns
4. **Settings** - Configure notifications, auto-track, data export

## Development

### Edit Files
- Modify CSS in `/popup/popup.css` and `/options/options.css`
- Update logic in JS files
- Changes auto-reload in development mode

### Test on New Sites
1. Go to any e-commerce site
2. Check console (F12 → Console) for tracking logs
3. Use the floating widget to test manual tracking

### Add Custom Icons
Replace PNG files in `/icons/` folder (16x16, 48x48, 128x128 pixels)

## Troubleshooting

**Extension not tracking?**
- Ensure you're on an e-commerce site with product prices
- Check Chrome > Settings > Extensions > Purchase Tracker is enabled
- Open DevTools (F12) and check console for errors

**Data not saving?**
- Check Chrome storage isn't full
- Ensure extension has storage permission
- Try clearing browser cache

**Widget not appearing?**
- Refresh the page
- Check if content script is loaded (F12 → Sources)
- Try a different website

## Future Enhancements

- 📊 More detailed analytics charts
- 🎯 Budget tracking & alerts
- 📱 Sync across devices
- 🤖 AI-powered purchase insights
- 💾 Cloud backup option
- 🌍 Multi-language support

## Support

Found a bug? Have suggestions? Open an issue in the GitHub repo!

## License

MIT License - Feel free to use and modify!

---

**Happy tracking! 🛍️**
