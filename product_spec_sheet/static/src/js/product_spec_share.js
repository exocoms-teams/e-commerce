(function () {
    'use strict';

    /* ---- Copier dans le presse-papier ---- */
    function copyToClipboard(text, btn) {
        navigator.clipboard.writeText(text).then(function () {
            var orig = btn.innerHTML;
            btn.innerHTML = '<i class="fa fa-check me-1"></i> Copié !';
            setTimeout(function () { btn.innerHTML = orig; }, 2000);
        });
    }

    /* ---- Partage natif (mobile) ou fallback ---- */
    function shareSpec(title, url, btn) {
        if (navigator.share) {
            navigator.share({ title: title, url: url });
        } else {
            copyToClipboard(url, btn);
        }
    }

    /* ---- Lien e-mail ---- */
    function shareEmail(subject, body) {
        window.location.href = 'mailto:?subject=' +
            encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    }

    /* ---- WhatsApp ---- */
    function shareWhatsapp(text) {
        window.open('https://wa.me/?text=' + encodeURIComponent(text), '_blank');
    }

    /* ---- LinkedIn ---- */
    function shareLinkedin(url) {
        window.open(
            'https://www.linkedin.com/sharing/share-offsite/?url=' +
            encodeURIComponent(url),
            '_blank', 'width=600,height=600'
        );
    }

    /* ---- Facebook ---- */
    function shareFacebook(url) {
        window.open(
            'https://www.facebook.com/sharer/sharer.php?u=' +
            encodeURIComponent(url),
            '_blank', 'width=600,height=600'
        );
    }

    /* ---- X (Twitter) ---- */
    function shareX(text, url) {
        window.open(
            'https://twitter.com/intent/tweet?text=' +
            encodeURIComponent(text) + '&url=' + encodeURIComponent(url),
            '_blank', 'width=600,height=400'
        );
    }

    /* ---- Telegram ---- */
    function shareTelegram(text, url) {
        window.open(
            'https://t.me/share/url?url=' + encodeURIComponent(url) +
            '&text=' + encodeURIComponent(text),
            '_blank'
        );
    }

    /* ---- Toggle dropdown ---- */
    function initShareDropdowns() {
        document.querySelectorAll('.o_spec_share_toggle').forEach(function (toggle) {
            toggle.addEventListener('click', function (e) {
                e.stopPropagation();
                var menu = toggle.nextElementSibling;
                var isOpen = menu.classList.contains('show');
                document.querySelectorAll('.o_spec_share_menu').forEach(function (m) {
                    m.classList.remove('show');
                });
                if (!isOpen) menu.classList.add('show');
            });
        });
        document.addEventListener('click', function () {
            document.querySelectorAll('.o_spec_share_menu').forEach(function (m) {
                m.classList.remove('show');
            });
        });
    }

    /* ---- Boutons d'action ---- */
    function initShareActions() {
        /* Copier le lien fiche produit */
        document.querySelectorAll('[data-spec-action="copy-link"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                copyToClipboard(window.location.href, btn);
            });
        });

        /* Partager (natif ou clipboard) */
        document.querySelectorAll('[data-spec-action="share"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var title = btn.dataset.specTitle || document.title;
                shareSpec(title, window.location.href, btn);
            });
        });

        /* E-mail fiche */
        document.querySelectorAll('[data-spec-action="email"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var title = btn.dataset.specTitle || document.title;
                var url   = window.location.href;
                shareEmail(
                    'Fiche technique : ' + title,
                    'Bonjour,\n\nVoici la fiche technique du produit ' + title +
                    ' :\n' + url + '\n\nCordialement.'
                );
            });
        });

        /* WhatsApp fiche */
        document.querySelectorAll('[data-spec-action="whatsapp"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var title = btn.dataset.specTitle || document.title;
                shareWhatsapp('Fiche technique ' + title + ' : ' + window.location.href);
            });
        });

        /* LinkedIn — fiche produit */
        document.querySelectorAll('[data-spec-action="linkedin"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                shareLinkedin(window.location.href);
            });
        });

        /* Facebook — fiche produit */
        document.querySelectorAll('[data-spec-action="facebook"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                shareFacebook(window.location.href);
            });
        });

        /* X — fiche produit */
        document.querySelectorAll('[data-spec-action="x"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var title = btn.dataset.specTitle || document.title;
                shareX(title, window.location.href);
            });
        });

        /* Telegram — fiche produit */
        document.querySelectorAll('[data-spec-action="telegram"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var title = btn.dataset.specTitle || document.title;
                shareTelegram(title, window.location.href);
            });
        });

        /* LinkedIn — comparatif */
        document.querySelectorAll('[data-spec-action="linkedin-compare"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var ids = btn.dataset.productIds || '';
                shareLinkedin(window.location.origin +
                    '/product-specs/compare?product_ids=' + ids);
            });
        });

        /* X — comparatif */
        document.querySelectorAll('[data-spec-action="x-compare"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var ids = btn.dataset.productIds || '';
                shareX('Comparatif produits',
                    window.location.origin +
                    '/product-specs/compare?product_ids=' + ids);
            });
        });

        /* Copier lien comparatif */
        document.querySelectorAll('[data-spec-action="copy-compare"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var ids = btn.dataset.productIds || '';
                var url = window.location.origin +
                    '/product-specs/compare?product_ids=' + ids;
                copyToClipboard(url, btn);
            });
        });

        /* E-mail comparatif */
        document.querySelectorAll('[data-spec-action="email-compare"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var ids = btn.dataset.productIds || '';
                var url = window.location.origin +
                    '/product-specs/compare?product_ids=' + ids;
                shareEmail(
                    'Comparatif produits',
                    'Bonjour,\n\nVoici le comparatif des produits sélectionnés :\n' +
                    url + '\n\nCordialement.'
                );
            });
        });

        /* WhatsApp comparatif */
        document.querySelectorAll('[data-spec-action="whatsapp-compare"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var ids = btn.dataset.productIds || '';
                var url = window.location.origin +
                    '/product-specs/compare?product_ids=' + ids;
                shareWhatsapp('Comparatif produits : ' + url);
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initShareDropdowns();
        initShareActions();
    });
})();
