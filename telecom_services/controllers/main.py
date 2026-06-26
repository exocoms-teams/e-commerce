from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_TELECOM_XML_IDS = [
    'telecom_services.product_dstny_ucaas',
    'telecom_services.product_telephonie_voip',
    'telecom_services.product_mobile',
    'telecom_services.product_convergence_fixe_mobile',
    'telecom_services.product_dstny_call_intelligence',
    'telecom_services.product_dstny_crm_intelligence',
    'telecom_services.product_dstny_call2teams',
    'telecom_services.product_dstny_digital_assistants',
    'telecom_services.product_acces_internet',
    'telecom_services.product_reseau_prive_entreprise',
    'telecom_services.product_sd_wan',
    'telecom_services.product_infrastructure_cloud_iaas',
    'telecom_services.product_hebergement',
    'telecom_services.product_sauvegarde_donnees',
    'telecom_services.product_plan_reprise_activite',
    'telecom_services.product_detection_anticipation',
    'telecom_services.product_gestion_identites',
    'telecom_services.product_protection_messagerie',
    'telecom_services.product_diagnostic_securite',
]

_CATALOGUE = {
    'fr_FR': [
        {
            'id': 'voix',
            'category': 'Voix',
            'products': [
                {'name': 'Dstny UCaaS', 'xml_id': 'telecom_services.product_dstny_ucaas',
                 'description': 'Plateforme UCaaS nouvelle génération. Convergence exclusive fixe-mobile-Teams-CRM. Sans engagement, déploiement en 24h.'},
                {'name': 'Téléphonie VoIP', 'xml_id': 'telecom_services.product_telephonie_voip',
                 'description': 'Communiquez en illimité via Internet. Flexibilité, nouvelles fonctionnalités et coûts réduits par rapport au RTC traditionnel.'},
                {'name': 'Mobile', 'xml_id': 'telecom_services.product_mobile',
                 'description': 'Forfaits mobiles pro avec gestion centralisée MDM. Smartphones reconditionnés disponibles via Dstny x Back Market Pro.'},
                {'name': 'Convergence Fixe-Mobile', 'xml_id': 'telecom_services.product_convergence_fixe_mobile',
                 'description': "Numéro fixe et mobile sur une seule carte SIM. Profitez des fonctionnalités d'entreprise en mobilité via le réseau GSM."},
            ],
        },
        {
            'id': 'intelligence',
            'category': 'Intelligence',
            'products': [
                {'name': 'Dstny Call Intelligence', 'xml_id': 'telecom_services.product_dstny_call_intelligence',
                 'description': 'Analysez et valorisez vos échanges téléphoniques. Tableaux de bord en temps réel, KPIs et rapports détaillés sur vos communications.'},
                {'name': 'Dstny CRM Intelligence', 'xml_id': 'telecom_services.product_dstny_crm_intelligence',
                 'description': 'Remontée automatique des fiches CRM à chaque appel. Identifiez vos interlocuteurs avant même de décrocher et enrichissez vos données.'},
            ],
        },
        {
            'id': 'teams',
            'category': 'Teams',
            'products': [
                {'name': 'Dstny Call2Teams', 'xml_id': 'telecom_services.product_dstny_call2teams',
                 'description': "Passez tous vos appels, même externes, directement depuis l'onglet Appels de Microsoft Teams avec votre numéro d'entreprise."},
            ],
        },
        {
            'id': 'agents-ia',
            'category': 'Agents IA',
            'products': [
                {'name': 'Dstny Digital Assistants', 'xml_id': 'telecom_services.product_dstny_digital_assistants',
                 'description': 'Agent vocal IA disponible 24h/24, 7j/7. Répond, oriente les appels et planifie des rendez-vous automatiquement. Multilingue, intégré à votre CRM.'},
            ],
        },
        {
            'id': 'connectivite',
            'category': 'Connectivité & Réseaux',
            'products': [
                {'name': 'Accès internet', 'xml_id': 'telecom_services.product_acces_internet',
                 'description': "Offres Très Haut Débit FTTH/FTTE/FTTO multi-opérateurs. Débit jusqu'à 10 Gbps, GTR incluse et option Backup 4G."},
                {'name': "Réseau privé d'entreprise", 'xml_id': 'telecom_services.product_reseau_prive_entreprise',
                 'description': 'Architecture MPLS/VPN sécurisée et maîtrisée de bout en bout. SLA, supervision 24/7 et interlocuteur unique multi-opérateurs.'},
                {'name': 'SD-WAN', 'xml_id': 'telecom_services.product_sd_wan',
                 'description': 'Optimisez vos liens WAN et performances applicatives. Déploiement Zero-Touch, sécurité intégrée nouvelle génération.'},
            ],
        },
        {
            'id': 'cloud',
            'category': 'Cloud & Hébergement',
            'products': [
                {'name': 'Infrastructure cloud IaaS', 'xml_id': 'telecom_services.product_infrastructure_cloud_iaas',
                 'description': 'Cloud privé, public ou hybride certifié ISO 27001. Haute disponibilité garantie, datacenters français, accompagnement expert de bout en bout.'},
                {'name': 'Hébergement', 'xml_id': 'telecom_services.product_hebergement',
                 'description': 'Hébergement réglementaire pour protéger vos données sensibles et répondre aux exigences légales spécifiques de votre secteur.'},
                {'name': 'Sauvegarde de données', 'xml_id': 'telecom_services.product_sauvegarde_donnees',
                 'description': 'Sauvegarde certifiée ISO 27001 & HDS. Stockage chiffré en datacenter français, supervision 24/7 et extension cloud évolutive.'},
                {'name': "Plan de reprise d'activité", 'xml_id': 'telecom_services.product_plan_reprise_activite',
                 'description': 'Redémarrez votre SI après sinistre grâce au PRA cloud. Conforme ISO 27001 & HDS, mis en place par des experts certifiés.'},
            ],
        },
        {
            'id': 'cybersecurite',
            'category': 'Cybersécurité',
            'products': [
                {'name': 'Détection et anticipation', 'xml_id': 'telecom_services.product_detection_anticipation',
                 'description': 'Détection proactive des menaces cyber, surveillance 24/7 Cloud & OnPrem. Solution SaaS Made in France labellisée France Cybersecurity.'},
                {'name': 'Gestion des identités', 'xml_id': 'telecom_services.product_gestion_identites',
                 'description': 'Contrôlez les accès à privilège, tracez chaque action admin et dynamisez vos authentifications avec le MFA. Solution SaaS Made in France.'},
                {'name': 'Protection messagerie pro', 'xml_id': 'telecom_services.product_protection_messagerie',
                 'description': "Bloquez les emails malveillants avant réception. Détection IA, remédiation en temps réel, déploiement en moins de 24h sans impact utilisateur."},
                {'name': 'Diagnostic sécurité', 'xml_id': 'telecom_services.product_diagnostic_securite',
                 'description': "Évaluez votre niveau de protection, identifiez les priorités et obtenez un plan d'action clair. Réalisé par des experts, sans intervention technique."},
            ],
        },
    ],
    'en_US': [
        {
            'id': 'voix',
            'category': 'Voice',
            'products': [
                {'name': 'Dstny UCaaS', 'xml_id': 'telecom_services.product_dstny_ucaas',
                 'description': 'Next-gen UCaaS platform. Native fixed-mobile-Teams-CRM convergence. No commitment, deployed in 24h.'},
                {'name': 'VoIP Telephony', 'xml_id': 'telecom_services.product_telephonie_voip',
                 'description': 'Communicate without limits via the Internet. Flexibility, new features and lower costs compared to traditional PSTN.'},
                {'name': 'Mobile', 'xml_id': 'telecom_services.product_mobile',
                 'description': 'Pro mobile plans with centralized MDM management. Refurbished smartphones available via Dstny x Back Market Pro.'},
                {'name': 'Fixed-Mobile Convergence', 'xml_id': 'telecom_services.product_convergence_fixe_mobile',
                 'description': 'Fixed and mobile number on a single SIM card. Enjoy enterprise telephony features on the go via the GSM network.'},
            ],
        },
        {
            'id': 'intelligence',
            'category': 'Intelligence',
            'products': [
                {'name': 'Dstny Call Intelligence', 'xml_id': 'telecom_services.product_dstny_call_intelligence',
                 'description': 'Analyze and leverage your phone conversations. Real-time dashboards, KPIs and detailed reports on your communications.'},
                {'name': 'Dstny CRM Intelligence', 'xml_id': 'telecom_services.product_dstny_crm_intelligence',
                 'description': 'Automatic CRM contact pop-up on every call. Identify your contacts before picking up and keep your data up to date.'},
            ],
        },
        {
            'id': 'teams',
            'category': 'Teams',
            'products': [
                {'name': 'Dstny Call2Teams', 'xml_id': 'telecom_services.product_dstny_call2teams',
                 'description': "Make all your calls, even external ones, directly from Microsoft Teams' Calls tab with your company number."},
            ],
        },
        {
            'id': 'agents-ia',
            'category': 'AI Agents',
            'products': [
                {'name': 'Dstny Digital Assistants', 'xml_id': 'telecom_services.product_dstny_digital_assistants',
                 'description': 'AI voice agent available 24/7. Answers, routes calls and schedules appointments automatically. Multilingual, CRM-integrated.'},
            ],
        },
        {
            'id': 'connectivite',
            'category': 'Connectivity & Networks',
            'products': [
                {'name': 'Internet Access', 'xml_id': 'telecom_services.product_acces_internet',
                 'description': 'Multi-operator Very High-Speed FTTH/FTTE/FTTO offers. Up to 10 Gbps, SLA included and optional 4G Backup.'},
                {'name': 'Private Enterprise Network', 'xml_id': 'telecom_services.product_reseau_prive_entreprise',
                 'description': 'Secure MPLS/VPN architecture, controlled end-to-end. SLA, 24/7 monitoring and a single point of contact across operators.'},
                {'name': 'SD-WAN', 'xml_id': 'telecom_services.product_sd_wan',
                 'description': 'Optimize your WAN links and application performance. Zero-Touch deployment, next-generation integrated security.'},
            ],
        },
        {
            'id': 'cloud',
            'category': 'Cloud & Hosting',
            'products': [
                {'name': 'Cloud IaaS Infrastructure', 'xml_id': 'telecom_services.product_infrastructure_cloud_iaas',
                 'description': 'Private, public or hybrid cloud, ISO 27001 certified. Guaranteed high availability, French datacenters, expert support end-to-end.'},
                {'name': 'Hosting', 'xml_id': 'telecom_services.product_hebergement',
                 'description': 'Regulatory hosting to protect your sensitive data and meet the specific legal requirements of your industry.'},
                {'name': 'Data Backup', 'xml_id': 'telecom_services.product_sauvegarde_donnees',
                 'description': 'ISO 27001 & HDS certified backup. Encrypted storage in French datacenters, 24/7 monitoring and scalable cloud extension.'},
                {'name': 'Business Continuity Plan', 'xml_id': 'telecom_services.product_plan_reprise_activite',
                 'description': 'Restart your IT systems after a disaster with a cloud BCP. ISO 27001 & HDS compliant, implemented by certified experts.'},
            ],
        },
        {
            'id': 'cybersecurite',
            'category': 'Cybersecurity',
            'products': [
                {'name': 'Threat Detection & Anticipation', 'xml_id': 'telecom_services.product_detection_anticipation',
                 'description': 'Proactive cyber threat detection, 24/7 Cloud & OnPrem monitoring. SaaS solution Made in France, France Cybersecurity certified.'},
                {'name': 'Identity Management', 'xml_id': 'telecom_services.product_gestion_identites',
                 'description': 'Control privileged access, trace every admin action and strengthen your authentications with MFA. SaaS solution Made in France.'},
                {'name': 'Business Email Protection', 'xml_id': 'telecom_services.product_protection_messagerie',
                 'description': 'Block malicious emails before they reach your teams. AI detection, real-time remediation, deployed in under 24h with no user impact.'},
                {'name': 'Security Assessment', 'xml_id': 'telecom_services.product_diagnostic_securite',
                 'description': 'Assess your security level, identify priorities and get a clear action plan. Conducted by experts, no technical intervention required.'},
            ],
        },
    ],
}

_UI_STRINGS = {
    'fr_FR': {
        'page_title': 'Solutions Télécom',
        'page_subtitle': (
            'Voix, mobilité, intelligence conversationnelle, '
            'connectivité et cybersécurité pour les professionnels.'
        ),
    },
    'en_US': {
        'page_title': 'Telecom Solutions',
        'page_subtitle': (
            'Voice, mobility, conversational intelligence, '
            'connectivity and cybersecurity for professionals.'
        ),
    },
}


class TelecomController(http.Controller):

    @http.route('/telecom', type='http', auth='public', website=True)
    def telecom_page(self, **kwargs):
        lang = request.env.context.get('lang', 'fr_FR')
        catalogue = _CATALOGUE.get(lang, _CATALOGUE['fr_FR'])
        strings = _UI_STRINGS.get(lang, _UI_STRINGS['fr_FR'])

        # Resolve website_url for each product from DB via its XML ID
        product_urls = {}
        for xml_id in _TELECOM_XML_IDS:
            rec = request.env.ref(xml_id, raise_if_not_found=False)
            if rec:
                product_urls[xml_id] = rec.website_url

        return request.render('telecom_services.telecom_page', {
            'universes': catalogue,
            'product_urls': product_urls,
            **strings,
        })


class TelecomShopOverride(WebsiteSale):

    def _get_search_domain(self, *args, **kwargs):
        domain = super()._get_search_domain(*args, **kwargs)
        ids = self._telecom_product_ids()
        if ids:
            domain += [('id', 'not in', ids)]
        return domain

    def _telecom_product_ids(self):
        ids = []
        for xml_id in _TELECOM_XML_IDS:
            rec = request.env.ref(xml_id, raise_if_not_found=False)
            if rec:
                ids.append(rec.id)
        return ids
