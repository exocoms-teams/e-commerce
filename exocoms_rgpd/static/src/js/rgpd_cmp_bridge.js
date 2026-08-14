/**
 * Client de journalisation des consentements cookies.
 * ---------------------------------------------------
 * À coller sur exocoms.fr pour que le bandeau cookies alimente réellement le
 * journal RGPD. Sans ce pont, l'endpoint /rgpd/consent/log reste inutilisé et
 * aucune preuve n'est conservée pour les traceurs.
 *
 * Ce fichier est volontairement autonome (aucune dépendance Odoo) : il doit
 * pouvoir être servi tel quel ou copié dans la configuration du CMP.
 *
 * Codes de finalité attendus côté Odoo (RGPD ‣ Consentements ‣ Finalités) :
 *   cookies_essential, cookies_analytics, cookies_marketing
 * Adaptez la table CMP_PURPOSE_MAP ci-dessous à vos propres codes.
 */
(function () {
    "use strict";

    var ENDPOINT = "/rgpd/consent/log";

    // Correspondance entre les identifiants du CMP et les codes de finalité
    // Odoo. Les clés sont celles du CMP, les valeurs celles du module.
    var CMP_PURPOSE_MAP = {
        // Axeptio
        google_analytics: "cookies_analytics",
        matomo: "cookies_analytics",
        facebook_pixel: "cookies_marketing",
        google_ads: "cookies_marketing",
        // tarteaucitron
        analytics: "cookies_analytics",
        gtag: "cookies_analytics",
        facebookpixel: "cookies_marketing",
    };

    /**
     * Journalise un consentement.
     *
     * L'e-mail est requis : sans lui l'entrée ne peut être rattachée à personne
     * et n'aurait aucune valeur probante. Sur un site public, on ne le connaît
     * qu'après identification — d'où la file d'attente ci-dessous.
     */
    function logConsent(purposeCode, granted, options) {
        options = options || {};
        var email = options.email || currentEmail();
        if (!email) {
            queue.push([purposeCode, granted, options]);
            return Promise.resolve({ status: "queued" });
        }
        var payload = {
            jsonrpc: "2.0",
            method: "call",
            params: {
                purpose: purposeCode,
                email: email,
                granted: !!granted,
                method: "cookie_banner",
                source_url: window.location.href,
                external_ref: options.externalRef || null,
                consent_text: options.consentText || null,
            },
        };
        var headers = { "Content-Type": "application/json" };
        // La clé n'a de sens que si l'appel part d'un serveur. Depuis un
        // navigateur elle serait publique : laissez le paramètre
        // exocoms_rgpd.consent_api_key vide pour les appels front, ou proxifiez
        // l'appel côté serveur si vous voulez l'authentifier.
        if (options.apiKey) {
            headers["X-RGPD-Key"] = options.apiKey;
        }
        return fetch(ENDPOINT, {
            method: "POST",
            headers: headers,
            credentials: "same-origin",
            body: JSON.stringify(payload),
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                return (data && data.result) || { status: "error" };
            })
            .catch(function (error) {
                // Un échec de journalisation ne doit jamais casser la
                // navigation : on trace en console et on continue.
                console.warn("RGPD: journalisation du consentement échouée", error);
                return { status: "error" };
            });
    }

    // ------------------------------------------------------------------
    // File d'attente : consentements donnés avant que l'identité soit connue
    // ------------------------------------------------------------------
    var queue = [];

    function currentEmail() {
        if (window.rgpdCurrentEmail) {
            return window.rgpdCurrentEmail;
        }
        // Odoo expose l'utilisateur connecté via la session sur les pages
        // portail. Sur les pages publiques, l'appelant doit renseigner
        // window.rgpdCurrentEmail après identification.
        var session = window.odoo && window.odoo.__session_info__;
        if (session && session.user_email) {
            return session.user_email;
        }
        return null;
    }

    /** À appeler dès que l'adresse est connue (connexion, formulaire). */
    function flushQueue(email) {
        if (email) {
            window.rgpdCurrentEmail = email;
        }
        var pending = queue.splice(0, queue.length);
        return Promise.all(
            pending.map(function (args) {
                return logConsent(args[0], args[1], args[2]);
            })
        );
    }

    // ------------------------------------------------------------------
    // Ponts vers les CMP courants
    // ------------------------------------------------------------------

    /** Axeptio : écoute les choix de l'utilisateur. */
    function bindAxeptio() {
        window._axcb = window._axcb || [];
        window._axcb.push(function (sdk) {
            sdk.on("cookies:complete", function (choices) {
                Object.keys(choices).forEach(function (vendor) {
                    var code = CMP_PURPOSE_MAP[vendor];
                    if (code) {
                        logConsent(code, choices[vendor], { externalRef: vendor });
                    }
                });
            });
        });
    }

    /** tarteaucitron : un événement par service accepté ou refusé. */
    function bindTarteaucitron() {
        Object.keys(CMP_PURPOSE_MAP).forEach(function (service) {
            var code = CMP_PURPOSE_MAP[service];
            document.addEventListener(service + "_allowed", function () {
                logConsent(code, true, { externalRef: service });
            });
            document.addEventListener(service + "_disallowed", function () {
                logConsent(code, false, { externalRef: service });
            });
        });
    }

    // ------------------------------------------------------------------
    document.addEventListener("DOMContentLoaded", function () {
        bindAxeptio();
        bindTarteaucitron();
    });

    // API publique, utilisable depuis n'importe quel autre CMP.
    window.rgpdConsent = {
        log: logConsent,
        flush: flushQueue,
        map: CMP_PURPOSE_MAP,
    };
})();
