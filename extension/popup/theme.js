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
    btn.textContent = dark ? '☀️ Light' : '🌙 Dark';
    btn.setAttribute('aria-pressed', String(dark));
  });
}

function initTheme() {
  applyTheme(getStoredTheme());
  document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
    btn.addEventListener('click', toggleTheme);
  });
}

// Run on load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initTheme);
} else {
  initTheme();
}