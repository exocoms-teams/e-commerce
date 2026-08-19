/**
 * O&A Beauty intelligent search overlay.
 */
(function () {
    'use strict';

    const _t = (key) => (window.odoo && window.odoo._t) ? window.odoo._t(key) : key;

    const state = {
        timer: null,
        query: '',
        isOpen: false,
    };

    function $(selector) {
        return document.querySelector(selector);
    }

    function escapeHtml(value) {
        return String(value || '').replace(/[&<>"']/g, function (char) {
            return {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;',
            }[char];
        });
    }

    function jsonRpc(url, params) {
        return fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: params || {} }),
        }).then(function (response) {
            return response.json();
        }).then(function (payload) {
            return payload.result || {};
        });
    }

    function openSearch(event) {
        if (event) {
            event.preventDefault();
        }
        const overlay = $('#oa_search_overlay');
        const input = $('#oa_search_input');
        if (!overlay || !input) {
            window.location.href = '/shop';
            return;
        }
        state.isOpen = true;
        overlay.classList.add('is-open');
        overlay.setAttribute('aria-hidden', 'false');
        document.body.classList.add('oa-search-lock');
        window.setTimeout(function () { input.focus(); }, 80);
    }

    function closeSearch() {
        const overlay = $('#oa_search_overlay');
        if (!overlay) {
            return;
        }
        state.isOpen = false;
        overlay.classList.remove('is-open');
        overlay.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('oa-search-lock');
    }

    function renderSuggestions(suggestions, query) {
        const container = $('#oa_search_suggestions');
        if (!container) {
            return;
        }
        container.innerHTML = '';
        if (!suggestions || !suggestions.length) {
            return;
        }
        suggestions.forEach(function (item) {
            const link = document.createElement('a');
            link.className = 'oa-search-suggestion';
            link.href = item.url || ('/shop?search=' + encodeURIComponent(query));
            link.innerHTML = '<i class="fa fa-arrow-right"></i><span>' + escapeHtml(item.label) + '</span>';
            if (item.type === 'category') {
                link.addEventListener('click', function () {
                    jsonRpc('/api/oa/search/click', {
                        query: query,
                        category_id: item.id,
                        event_type: 'category_click',
                    });
                });
            }
            container.appendChild(link);
        });
    }

    function renderResults(payload) {
        const resultsEl = $('#oa_search_results');
        const statusEl = $('.oa-search-status');
        const emptyEl = $('#oa_search_empty');
        const allEl = $('#oa_search_all');
        const query = payload.query || state.query;
        const results = payload.results || [];

        if (!resultsEl || !statusEl || !emptyEl || !allEl) {
            return;
        }

        resultsEl.innerHTML = '';
        allEl.href = '/shop?search=' + encodeURIComponent(query);
        allEl.hidden = !query;

        if (query.length < 2) {
            statusEl.textContent = _t('Tapez au moins 2 caractères.');
            emptyEl.hidden = true;
            allEl.hidden = true;
            renderSuggestions([], query);
            return;
        }

        statusEl.textContent = results.length ? (payload.count + _t(' résultat(s) pertinent(s)')) : '';
        emptyEl.hidden = results.length > 0;
        if (!results.length) {
            emptyEl.querySelector('.oa-search-empty-title').textContent = _t('No results found for "') + query + '".';
        }

        results.forEach(function (product) {
            const link = document.createElement('a');
            link.className = 'oa-search-product';
            link.href = product.url;
            link.innerHTML =
                '<img src="' + escapeHtml(product.image) + '" alt="' + escapeHtml(product.name) + '" loading="lazy"/>' +
                '<span class="oa-search-product-body">' +
                    '<span class="oa-search-product-category">' + escapeHtml(product.category || 'O&A Beauty') + '</span>' +
                    '<span class="oa-search-product-name">' + escapeHtml(product.name) + '</span>' +
                '</span>' +
                '<span class="oa-search-product-price">' + (product.price_formatted || escapeHtml(product.price)) + '</span>';
            link.addEventListener('click', function () {
                jsonRpc('/api/oa/search/click', { query: query, product_id: product.id });
            });
            resultsEl.appendChild(link);
        });

        renderSuggestions(payload.suggestions || [], query);
    }

    function search(query) {
        state.query = query;
        window.clearTimeout(state.timer);
        state.timer = window.setTimeout(function () {
            if (query.length < 2) {
                renderResults({ query: query, results: [], suggestions: [], count: 0 });
                return;
            }
            $('.oa-search-status').textContent = _t('Recherche...');
            jsonRpc('/api/oa/search', { query: query, limit: 8 })
                .then(renderResults)
                .catch(function () {
                    $('.oa-search-status').textContent = _t('La recherche est momentanément indisponible.');
                });
        }, 260);
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.js-oa-search-open, [data-bs-target="#o_search_modal"]').forEach(function (trigger) {
            trigger.addEventListener('click', openSearch);
        });

        $('#oa_search_overlay')?.addEventListener('click', function (event) {
            if (event.target.id === 'oa_search_overlay') {
                closeSearch();
            }
        });
        $('.oa-search-close')?.addEventListener('click', closeSearch);
        $('#oa_search_input')?.addEventListener('input', function (event) {
            search(event.target.value.trim());
        });
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && state.isOpen) {
                closeSearch();
            }
        });
    });
})();
