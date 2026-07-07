/**
 * Planet Mobil — Client-side EN translations
 * Runs on every page; if lang = en, replaces French text nodes + attributes.
 */
(function () {
    'use strict';

    /* ── Dictionary: French → English ────────────────────────────────────── */
    // Sorted longest-first so partial matches don't clobber longer ones.
    var T = [
        // ── Long sentences / titles ─────────────────────────────────────────
        ['Smartphones, tablettes, accessoires', 'Smartphones, tablets, accessories'],
        ['les meilleurs prix, livrés chez vous', 'the best prices, delivered to your door'],
        ['Des milliers de clients satisfaits parlent de leur expérience', 'Thousands of satisfied customers share their experience'],
        ['Recevez nos offres exclusives, nouveautés et bons plans directement dans votre boîte mail', 'Receive our exclusive offers, new arrivals and deals directly in your inbox'],
        ['Recevez vos commandes en 24h en France métropolitaine, et jusqu\'en Europe en 48h', 'Receive your orders in 24h in mainland France, and up to 48h in Europe'],
        ['Chaque produit est contrôlé et testé par nos experts avant d\'être mis en vente', 'Every product is checked and tested by our experts before going on sale'],
        ['Toutes vos transactions sont chiffrées et protégées', 'All your transactions are encrypted and protected'],
        ['Pas satisfait ? Retournez votre produit facilement et obtenez un remboursement rapide sans question', 'Not satisfied? Return your product easily and get a quick refund, no questions asked'],
        ['Notre équipe est disponible du lundi au samedi pour répondre', 'Our team is available Monday to Saturday to answer'],
        ['Remplissez le formulaire, on vous répond sous 24h', 'Fill in the form, we\'ll get back to you within 24h'],
        ['Plusieurs façons de nous joindre', 'Multiple ways to reach us'],
        ['à toutes vos questions', 'all your questions'],
        ['Offres valables jusqu\'à épuisement des stocks', 'Offers valid while stocks last'],
        ['Votre retour aide d\'autres clients à faire le bon choix', 'Your feedback helps other customers make the right choice'],
        ['Décrivez votre expérience avec ce produit ou notre service', 'Describe your experience with this product or our service'],
        ['Décrivez votre demande en détail', 'Describe your request in detail'],

        // ── Page / SEO titles ────────────────────────────────────────────────
        ['Avis clients — Planet Mobil à Paris', 'Customer Reviews — Planet Mobil in Paris'],
        ['Contactez-nous — Planet Mobil Paris', 'Contact us — Planet Mobil Paris'],
        ['Livraison & Retours · Planet Mobil', 'Shipping & Returns · Planet Mobil'],
        ['CGV — Conditions Générales de Vente · Planet Mobil', 'Terms & Conditions · Planet Mobil'],
        ['Politique de confidentialité · Planet Mobil', 'Privacy Policy · Planet Mobil'],
        ['Politique de cookies — Planet Mobil', 'Cookie Policy — Planet Mobil'],
        ['Smartphones, Accessoires & Réparations à Paris', 'Smartphones, Accessories & Repairs in Paris'],
        ['À propos de Planet Mobil', 'About Planet Mobil'],

        // ── Section headings ─────────────────────────────────────────────────
        ['Explorez par catégorie', 'Browse by category'],
        ['Pourquoi nous choisir', 'Why choose us'],
        ['Une expérience d\'achat sans compromis', 'A shopping experience without compromise'],
        ['Restez dans la boucle', 'Stay in the loop'],
        ['Parlons de votre projet', 'Let\'s talk about your project'],
        ['Avis de nos clients', 'Customer reviews'],
        ['Partagez votre expérience', 'Share your experience'],
        ['Votre avis compte', 'Your review matters'],
        ['Nos coordonnées', 'Our contact details'],
        ['Envoyer un message', 'Send a message'],
        ['Tous les avis', 'All reviews'],
        ['Aucun avis pour l\'instant', 'No reviews yet'],
        ['Cliquez pour noter', 'Click to rate'],
        ['Merci pour votre avis', 'Thank you for your review'],
        ['Merci pour votre message', 'Thank you for your message'],
        ['Questions fréquentes', 'Frequently asked questions'],
        ['Délais et tarifs', 'Lead times and pricing'],
        ['Procédure de retour', 'Return procedure'],
        ['Conditions de retour', 'Return conditions'],
        ['Suivi de commande', 'Order tracking'],
        ['Zones de livraison', 'Delivery zones'],
        ['Caractéristiques non renseignées', 'Specifications not available'],

        // ── Navigation ───────────────────────────────────────────────────────
        ['Tous les produits', 'All products'],
        ['Explorer le catalogue', 'Browse catalogue'],
        ['Nouveautés', 'New arrivals'],
        ['Avis clients', 'Customer reviews'],
        ['Promotions', 'Promotions'],
        ['À propos', 'About us'],
        ['Livraison & Retours', 'Shipping & Returns'],
        ['Livraison & retours', 'Shipping & returns'],
        ['Mentions légales', 'Legal notice'],
        ['Conditions Générales de Vente', 'Terms & Conditions'],
        ['Politique de confidentialité', 'Privacy policy'],
        ['Page d\'accueil', 'Home page'],
        ['Accueil', 'Home'],

        // ── Buttons & CTAs ───────────────────────────────────────────────────
        ['Ajouter au panier', 'Add to cart'],
        ['Envoyer le message', 'Send message'],
        ['Publier mon avis', 'Publish my review'],
        ['Écrire un avis', 'Write a review'],
        ['Profiter des promos', 'Get the deals'],
        ['Voir les promos', 'View promotions'],
        ['Voir la sélection', 'View selection'],
        ['Voir tout', 'View all'],
        ['S\'inscrire', 'Subscribe'],
        ['Ajouter', 'Add'],
        ['Filtrer', 'Filter'],
        ['Filtrer :', 'Filter:'],
        ['Imprimer', 'Print'],
        ['Partager', 'Share'],
        ['Toutes', 'All'],
        ['Voir', 'View'],

        // ── Form labels ──────────────────────────────────────────────────────
        ['Votre commentaire', 'Your comment'],
        ['Votre note', 'Your rating'],
        ['Votre nom', 'Your name'],
        ['Votre prénom', 'Your first name'],
        ['Produit acheté', 'Product purchased'],
        ['Achat vérifié', 'Verified purchase'],
        ['Basé sur', 'Based on'],

        // ── Categories / product specs ───────────────────────────────────────
        ['Caractéristiques', 'Specifications'],
        ['Compatibilité', 'Compatibility'],
        ['Disponibilité', 'Availability'],
        ['Taille écran', 'Screen size'],
        ['Résolution', 'Resolution'],
        ['Compléments', 'Add-ons'],
        ['Stockage', 'Storage'],
        ['Tablettes', 'Tablets'],
        ['Accessoires', 'Accessories'],
        ['Montres', 'Watches'],
        ['Son & musique', 'Sound & music'],
        ['Marque', 'Brand'],
        ['Couleur', 'Colour'],
        ['Système', 'System'],
        ['Taille', 'Size'],
        ['Tarif', 'Price'],
        ['Note', 'Rating'],

        // ── Labels & badges ──────────────────────────────────────────────────
        ['Livraison express', 'Express delivery'],
        ['Livraison gratuite', 'Free delivery'],
        ['Livraison 24h', 'Delivery in 24h'],
        ['Retours 30 jours', '30-day returns'],
        ['Retours sous 30 jours', 'Returns within 30 days'],
        ['Remboursement garanti', 'Guaranteed refund'],
        ['Paiement sécurisé', 'Secure payment'],
        ['Qualité certifiée', 'Certified quality'],
        ['Support 7j/7', '7/7 support'],
        ['Réponse sous 24h', 'Reply within 24h'],
        ['Réponse sous 2h', 'Reply within 2h'],
        ['Offre limitée', 'Limited offer'],
        ['JUSQU\'À', 'UP TO'],
        ['Collection 2025', 'Collection 2025'],
        ['Collections', 'Collections'],
        ['La technologie', 'Technology'],

        // ── Footer / contact ─────────────────────────────────────────────────
        ['Tous droits réservés', 'All rights reserved'],
        ['Suivez-nous', 'Follow us'],
        ['À propos de nous', 'About us'],
        ['Horaires', 'Opening hours'],
        ['Adresse', 'Address'],
        ['Téléphone', 'Phone'],
        ['Lun – Sam · 9h à 18h', 'Mon – Sat · 9am to 6pm'],
        ['Lun – Ven : 9h – 18h', 'Mon – Fri: 9am – 6pm'],
        ['Samedi : 10h – 16h', 'Saturday: 10am – 4pm'],
        ['Offerte dès 50 € d\'achat', 'Free from €50 purchase'],

        // ── Delivery page ────────────────────────────────────────────────────
        ['France métropolitaine', 'Mainland France'],
        ['DOM-TOM (délais étendus)', 'Overseas territories (extended lead times)'],
        ['Union Européenne (sur devis)', 'European Union (on request)'],
        ['Livraison standard (Colissimo)', 'Standard delivery (Colissimo)'],
        ['Livraison standard', 'Standard delivery'],
        ['Livraison express (24h)', 'Express delivery (24h)'],
        ['Point relais', 'Collection point'],
        ['Mode de livraison', 'Delivery method'],
        ['Délai estimé', 'Estimated lead time'],
        ['1 jour ouvré', '1 working day'],
        ['3 à 5 jours ouvrés', '3 to 5 working days'],
        ['Comment suivre ma commande ?', 'How do I track my order?'],
        ['Comment retourner un produit ?', 'How do I return a product?'],
        ['Quels sont les délais de livraison ?', 'What are the delivery lead times?'],
        ['Quels moyens de paiement acceptez-vous ?', 'What payment methods do you accept?'],
        ['Les produits sont-ils garantis ?', 'Are the products guaranteed?'],
        ['Retours & Remboursements', 'Returns & Refunds'],

        // ── Generic ──────────────────────────────────────────────────────────
        ['Navigation', 'Navigation'],
        ['Newsletter', 'Newsletter'],
        ['Informations', 'Information'],
        ['Témoignages', 'Testimonials'],
        ['Confidentialité', 'Privacy'],
        ['Cookies', 'Cookies'],
        ['Ex : iPhone 15 Pro', 'E.g.: iPhone 15 Pro'],
        ['Ex : Question sur une commande', 'E.g.: Question about an order'],
        ['votre@email.com', 'your@email.com'],
        ['exemple@email.com', 'example@email.com'],
    ];

    /* ── Attribute keys to translate ────────────────────────────────────────── */
    var ATTRS = ['placeholder', 'title', 'alt', 'aria-label'];

    /* ── Helpers ─────────────────────────────────────────────────────────────── */
    function applyDict(str) {
        var s = str;
        for (var i = 0; i < T.length; i++) {
            if (s.indexOf(T[i][0]) !== -1) {
                s = s.split(T[i][0]).join(T[i][1]);
            }
        }
        return s;
    }

    function translateNode(node) {
        // Text node
        if (node.nodeType === 3) {
            var orig = node.textContent;
            var translated = applyDict(orig);
            if (translated !== orig) node.textContent = translated;
            return;
        }
        // Element node — skip scripts, styles, inputs (handled via attributes)
        if (node.nodeType !== 1) return;
        var tag = node.tagName;
        if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT') return;

        // Translate attributes
        for (var a = 0; a < ATTRS.length; a++) {
            var attr = node.getAttribute(ATTRS[a]);
            if (attr) {
                var tAttr = applyDict(attr);
                if (tAttr !== attr) node.setAttribute(ATTRS[a], tAttr);
            }
        }

        // Recurse into children
        var children = node.childNodes;
        for (var c = 0; c < children.length; c++) {
            translateNode(children[c]);
        }
    }

    /* ── Main ────────────────────────────────────────────────────────────────── */
    function run() {
        var lang = (document.documentElement.lang || 'fr').toLowerCase();
        if (!lang.startsWith('en')) return;

        if (document.body) {
            translateNode(document.body);
        }

        // Also watch for dynamically inserted content (dropdown menus, etc.)
        if (window.MutationObserver) {
            var observer = new MutationObserver(function (mutations) {
                mutations.forEach(function (m) {
                    m.addedNodes.forEach(function (n) { translateNode(n); });
                });
            });
            observer.observe(document.body, { childList: true, subtree: true });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
    } else {
        run();
    }
})();
