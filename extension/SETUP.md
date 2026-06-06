# Installation & Setup Guide

## Quick Start (5 minutes)

### Step 1: Prepare the Extension
The extension folder is located at: `/home/edwin/Documents/GitHub/e-commerce/extension/`

All files are ready to go! ✅

### Step 2: Load into Chrome

1. **Open Chrome** and navigate to: `chrome://extensions/`

2. **Enable Developer Mode** 
   - Toggle the switch in the top-right corner

3. **Click "Load unpacked"**
   - Button appears in top-left after enabling Developer Mode

4. **Select the extension folder**
   - Navigate to your workspace: `extension` folder
   - Click "Select Folder"

5. **Done!** 🎉
   - Extension appears in your Chrome toolbar
   - Click the 🛍️ icon to start using it

## What Each Folder Contains

| Folder | Purpose |
|--------|---------|
| `popup/` | Click extension icon → see daily stats |
| `content/` | Runs on web pages → tracks purchases |
| `background/` | Stores data & sends notifications |
| `options/` | Settings & analytics page |
| `icons/` | Extension icons (add your own!) |

## Important Files

**manifest.json** - Extension configuration
- Tells Chrome what permissions to grant
- Sets up all scripts and pages
- ⚠️ Don't modify version numbers without testing

**popup/popup.html** - What you see when clicking the icon
**options/options.html** - Full analytics dashboard

## Testing

### Test Automatic Tracking
1. Go to any e-commerce site (Amazon, eBay, Shopify store, etc.)
2. Open DevTools (F12)
3. Look for logs: `[Purchase Tracker] Content script loaded`
4. Use the floating 📊 widget on the page

### Test Manual Tracking
1. Click floating 📊 widget
2. Enter: Product Title, Price ($), Category
3. Click "Save Purchase"
4. Check popup to see it counted

### Test Settings
1. Right-click extension → Options
2. View different tabs: Overview, History, Trends, Settings
3. Test export/import features

## Customize

### Change Colors
Edit gradient colors in CSS:
- `#667eea` (purple) → your color
- `#764ba2` (dark purple) → your color

### Add Icons
Replace files in `icons/`:
- `icon16.png` - 16×16 pixels
- `icon48.png` - 48×48 pixels  
- `icon128.png` - 128×128 pixels

### Change Extension Name
Edit `manifest.json`:
```json
"name": "Your Custom Name"
```

## Common Issues

**Extension doesn't appear?**
- Refresh page (Cmd+R or Ctrl+R)
- Check it's enabled in extensions page

**Scripts not running?**
- Check browser console for errors (F12)
- Ensure `<all_urls>` permission is granted

**Data not saving?**
- Open DevTools → Application → Storage → Local Storage
- Should see your purchases listed

## Next Steps

1. **Add Your Logo** → Create icons and add to `/icons/` folder
2. **Customize Colors** → Edit `popup.css` and `options.css`
3. **Test Thoroughly** → Try on different e-commerce sites
4. **Publish** → Submit to Chrome Web Store when ready

## File Sizes

```
popup.html         ~2KB
popup.js           ~3KB
popup.css          ~4KB
content.js         ~8KB
background.js      ~5KB
options.html       ~6KB
options.js         ~7KB
options.css        ~6KB
manifest.json      ~1KB
─────────────────────
TOTAL              ~42KB
```

## Performance Notes

✅ Very lightweight (~42KB total)
✅ No external dependencies
✅ Minimal CPU/memory usage
✅ Local storage only (no network calls)

## Questions?

- Chrome Extension docs: https://developer.chrome.com/docs/extensions/
- Manifest v3 guide: https://developer.chrome.com/docs/extensions/mv3/
- Debug extension: Use DevTools (F12) in extension pages

---

**You're all set! Start tracking purchases! 🎉**
