const STORAGE_KEY = 'tracker-theme';

function getStoredTheme() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved === 'light' || saved === 'dark') return saved;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(STORAGE_KEY, theme);
  updateThemeToggleLabels();
  document.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

function updateThemeToggleLabels() {
  const dark = document.documentElement.getAttribute('data-theme') === 'dark';
  document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
    btn.textContent = dark ? 'Light mode' : 'Dark mode';
    btn.setAttribute('aria-pressed', String(dark));
  });
}

function initTheme() {
  applyTheme(getStoredTheme());
  document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
    btn.addEventListener('click', toggleTheme);
  });
}

function chartTheme() {
  const s = getComputedStyle(document.documentElement);
  const pick = (name) => s.getPropertyValue(name).trim();
  return {
    grid: pick('--chart-grid'),
    text: pick('--chart-text'),
    label: pick('--chart-label'),
    primary: pick('--chart-primary'),
    secondary: pick('--chart-secondary'),
    palette: [
      pick('--chart-primary'),
      pick('--chart-secondary'),
      pick('--chart-text'),
      pick('--chart-label'),
      pick('--chart-grid'),
      '#525252', '#737373', '#a3a3a3', '#404040', '#d4d4d4',
    ],
    border: pick('--bg'),
  };
}

// Run before DOM ready for toggle wiring
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initTheme);
} else {
  initTheme();
}
