# -*- coding: utf-8 -*-
"""Contenu éditorial du catalogue Télécom (vitrine KISSGROUP).

Aucune donnée n'est lue depuis l'API ici : tout est du contenu marketing
statique, bilingue (fr_FR / en_US). La commande réelle se fait sur le portail
KISSGROUP (bouton « Commander »).

Structure d'une offre :
    'slug': {
        'cat': <clé catégorie>, 'icon': <classe FontAwesome>,
        'fr_FR' / 'en_US': {
            name, tagline, summary, intro,
            benefits: [{icon, title, text}],
            sections: [{title, text, points: [...]}],
            faq: [{q, a}],
        },
    }
"""

# (clé, libellé FR, libellé EN)
CATEGORIES = [
    ('voix', 'Voix', 'Voice'),
    ('mobile', 'Mobile', 'Mobile'),
    ('internet', 'Internet', 'Internet'),
    ('cloud', 'Cloud', 'Cloud'),
    ('securite', 'Sécurité', 'Security'),
]

# Ordre d'affichage des cartes sur /telecom
ORDER = [
    'centrex-wazo', 'trunk-sip',
    'mobile-illimite', 'data-only',
    'liens-fibre', 'kissbox-secours',
    'sauvegarde-ms365', 'stockage-s3',
    'cybersecurite',
]

PRODUCTS = {
    # ------------------------------------------------------------------ VOIX
    'centrex-wazo': {
        'cat': 'voix', 'icon': 'fa-phone',
        'fr_FR': {
            'name': 'Centrex Wazo',
            'tagline': "La téléphonie d'entreprise hébergée, sans standard à gérer",
            'summary': "Téléphonie hébergée clé en main : infra, licences, trunk et communications incluses.",
            'intro': (
                "Centrex Wazo remplace votre standard téléphonique physique par une solution "
                "100 % hébergée dans nos datacenters français. Vos collaborateurs appellent "
                "depuis un téléphone IP, un ordinateur ou leur mobile, avec les mêmes numéros et "
                "les mêmes fonctionnalités, où qu'ils soient."
            ),
            'benefits': [
                {'icon': 'fa-cloud', 'title': 'Zéro matériel à administrer',
                 'text': "L'IPBX est hébergé et maintenu par nos équipes : plus de standard à gérer sur site."},
                {'icon': 'fa-users', 'title': 'Collaboration unifiée',
                 'text': "Appels, messagerie vocale, groupes d'appels, SVI et softphone dans une seule interface."},
                {'icon': 'fa-euro', 'title': 'Facture prévisible',
                 'text': "Infra, licences, trunk et communications inclus dans un abonnement mensuel clair."},
            ],
            'sections': [
                {'title': 'Une solution complète, prête à l\'emploi',
                 'text': "Tout est fourni et pré-configuré : il ne vous reste qu'à brancher vos postes.",
                 'points': [
                     "Serveur téléphonique hébergé en haute disponibilité",
                     "Postes IP, softphone Windows/Mac et application mobile",
                     "Trunk SIP et communications nationales incluses",
                     "Serveur vocal interactif (SVI), files d'attente et enregistrement",
                 ]},
                {'title': 'Pensée pour le travail hybride',
                 'text': "Vos équipes restent joignables sur leur numéro fixe, au bureau comme en télétravail.",
                 'points': [
                     "Un même numéro sur le poste, l'ordinateur et le mobile",
                     "Renvois et supervision en temps réel depuis l'interface",
                     "Statistiques d'appels et suivi de la qualité de service",
                 ]},
            ],
            'faq': [
                {'q': "Puis-je conserver mes numéros actuels ?",
                 'a': "Oui, la portabilité de vos numéros fixes est prise en charge, sans coupure de service."},
                {'q': "Faut-il changer nos téléphones ?",
                 'a': "Pas nécessairement : les postes IP compatibles SIP fonctionnent, et le softphone évite tout matériel."},
                {'q': "Quel est le délai de mise en service ?",
                 'a': "Le déploiement standard prend quelques jours ouvrés selon le nombre de postes et la portabilité."},
            ],
        },
        'en_US': {
            'name': 'Centrex Wazo',
            'tagline': "Hosted business telephony, with no PBX to manage",
            'summary': "Turnkey hosted telephony: infrastructure, licenses, trunk and calls included.",
            'intro': (
                "Centrex Wazo replaces your physical phone system with a fully hosted solution "
                "running in our French datacenters. Your teams call from an IP phone, a computer "
                "or their mobile, with the same numbers and features, wherever they are."
            ),
            'benefits': [
                {'icon': 'fa-cloud', 'title': 'No hardware to manage',
                 'text': "The PBX is hosted and maintained by our teams — no on-site system to run."},
                {'icon': 'fa-users', 'title': 'Unified collaboration',
                 'text': "Calls, voicemail, call groups, IVR and softphone in a single interface."},
                {'icon': 'fa-euro', 'title': 'Predictable billing',
                 'text': "Infrastructure, licenses, trunk and calls bundled in one clear monthly fee."},
            ],
            'sections': [
                {'title': 'A complete, ready-to-use solution',
                 'text': "Everything is provided and pre-configured — just plug in your phones.",
                 'points': [
                     "Highly available hosted phone server",
                     "IP phones, Windows/Mac softphone and mobile app",
                     "SIP trunk and national calls included",
                     "Interactive voice response (IVR), queues and recording",
                 ]},
                {'title': 'Built for hybrid work',
                 'text': "Your teams stay reachable on their landline number, at the office or remotely.",
                 'points': [
                     "One number on the desk phone, computer and mobile",
                     "Real-time forwarding and supervision from the interface",
                     "Call analytics and quality-of-service monitoring",
                 ]},
            ],
            'faq': [
                {'q': "Can I keep my current numbers?",
                 'a': "Yes, porting of your landline numbers is handled with no service interruption."},
                {'q': "Do we need to change our phones?",
                 'a': "Not necessarily: SIP-compatible IP phones work, and the softphone avoids any hardware."},
                {'q': "How long does it take to go live?",
                 'a': "Standard deployment takes a few business days depending on the number of seats and porting."},
            ],
        },
    },
    'trunk-sip': {
        'cat': 'voix', 'icon': 'fa-phone-square',
        'fr_FR': {
            'name': 'Trunk SIP',
            'tagline': "Connectez votre IPBX existant au réseau téléphonique",
            'summary': "Raccordez tout IPBX existant. Compatible Microsoft Teams, provisionné en live.",
            'intro': (
                "Le Trunk SIP relie votre standard téléphonique (IPBX, Asterisk, 3CX, Microsoft "
                "Teams…) au réseau public via Internet. Vous conservez votre installation et gagnez "
                "en flexibilité, en capacité et en tarifs, sans lignes analogiques ni T0/T2."
            ),
            'benefits': [
                {'icon': 'fa-plug', 'title': 'Compatible tout IPBX',
                 'text': "S'intègre à vos équipements SIP existants, y compris Microsoft Teams (Direct Routing)."},
                {'icon': 'fa-bolt', 'title': 'Provisionné en live',
                 'text': "Canaux et numéros activés en temps réel depuis notre portail, ajustables à la demande."},
                {'icon': 'fa-line-chart', 'title': 'Élastique',
                 'text': "Augmentez ou réduisez le nombre de canaux selon votre activité, sans engagement lourd."},
            ],
            'sections': [
                {'title': 'Microsoft Teams comme téléphone d\'entreprise',
                 'text': "Passez et recevez vos appels externes directement dans Teams grâce au Direct Routing.",
                 'points': [
                     "Numéros fixes français rattachés à vos utilisateurs Teams",
                     "Aucune passerelle matérielle à installer",
                     "Conservation de vos numéros par portabilité",
                 ]},
                {'title': 'Qualité et sécurité opérateur',
                 'text': "Le trunk s'appuie sur notre réseau supervisé, avec les garanties d'un opérateur.",
                 'points': [
                     "Chiffrement des flux et restriction par IP",
                     "Supervision et journalisation des appels",
                     "Présentation du numéro et gestion des SDA",
                 ]},
            ],
            'faq': [
                {'q': "Est-ce compatible avec mon standard actuel ?",
                 'a': "Oui, tout IPBX compatible SIP est supporté. Nous fournissons les paramètres de raccordement."},
                {'q': "Combien de canaux me faut-il ?",
                 'a': "Un canal = un appel simultané. On dimensionne ensemble selon vos pics d'appels."},
            ],
        },
        'en_US': {
            'name': 'SIP Trunk',
            'tagline': "Connect your existing IPBX to the phone network",
            'summary': "Connect any existing IPBX. Microsoft Teams compatible, provisioned live.",
            'intro': (
                "The SIP Trunk links your phone system (IPBX, Asterisk, 3CX, Microsoft Teams…) to "
                "the public network over the Internet. You keep your setup and gain flexibility, "
                "capacity and better rates, with no analog or ISDN lines."
            ),
            'benefits': [
                {'icon': 'fa-plug', 'title': 'Works with any IPBX',
                 'text': "Integrates with your existing SIP equipment, including Microsoft Teams (Direct Routing)."},
                {'icon': 'fa-bolt', 'title': 'Provisioned live',
                 'text': "Channels and numbers activated in real time from our portal, adjustable on demand."},
                {'icon': 'fa-line-chart', 'title': 'Elastic',
                 'text': "Scale channels up or down with your activity, without heavy commitment."},
            ],
            'sections': [
                {'title': 'Microsoft Teams as your business phone',
                 'text': "Make and receive external calls straight from Teams via Direct Routing.",
                 'points': [
                     "French landline numbers assigned to your Teams users",
                     "No hardware gateway to install",
                     "Keep your numbers through porting",
                 ]},
                {'title': 'Carrier-grade quality and security',
                 'text': "The trunk runs on our supervised network, with true carrier guarantees.",
                 'points': [
                     "Traffic encryption and IP restriction",
                     "Call supervision and logging",
                     "Caller-ID presentation and DID management",
                 ]},
            ],
            'faq': [
                {'q': "Is it compatible with my current PBX?",
                 'a': "Yes, any SIP-compatible IPBX is supported. We provide the connection settings."},
                {'q': "How many channels do I need?",
                 'a': "One channel = one simultaneous call. We size it together based on your call peaks."},
            ],
        },
    },
    # ---------------------------------------------------------------- MOBILE
    'mobile-illimite': {
        'cat': 'mobile', 'icon': 'fa-mobile',
        'fr_FR': {
            'name': 'Mobile illimité',
            'tagline': "Des forfaits pros sur les meilleurs réseaux français",
            'summary': "Forfaits illimités sur les réseaux Orange et Bouygues. eSIM, VoLTE, VoWiFi.",
            'intro': (
                "Nos forfaits Mobile illimité offrent appels, SMS et data en abondance sur les "
                "réseaux Orange et Bouygues Telecom. Gestion centralisée de vos lignes, eSIM et "
                "technologies VoLTE / VoWiFi pour une qualité d'appel optimale partout."
            ),
            'benefits': [
                {'icon': 'fa-signal', 'title': 'Les meilleurs réseaux',
                 'text': "Couverture nationale Orange ou Bouygues Telecom, au choix selon vos zones."},
                {'icon': 'fa-cogs', 'title': 'Gestion centralisée',
                 'text': "Ajoutez, suspendez ou changez vos forfaits depuis une console unique."},
                {'icon': 'fa-microchip', 'title': 'eSIM & VoLTE / VoWiFi',
                 'text': "Activation eSIM immédiate, appels HD et continuité en Wi-Fi dans les zones blanches."},
            ],
            'sections': [
                {'title': 'Conçu pour les flottes d\'entreprise',
                 'text': "Pilotez l'ensemble de vos lignes mobiles sans passer par plusieurs interlocuteurs.",
                 'points': [
                     "Forfaits voix/SMS illimités et data généreuse",
                     "eSIM ou SIM physique, selon vos terminaux",
                     "Suivi de consommation et blocage hors-forfait",
                 ]},
                {'title': 'Simplicité et maîtrise des coûts',
                 'text': "Un interlocuteur unique pour toutes vos lignes, une facture claire par mois.",
                 'points': [
                     "Portabilité de vos numéros mobiles existants",
                     "Options data à la demande et roaming Europe",
                     "Sans engagement long selon l'offre choisie",
                 ]},
            ],
            'faq': [
                {'q': "Puis-je choisir le réseau ?",
                 'a': "Oui, selon votre couverture, vous optez pour le réseau Orange ou Bouygues Telecom."},
                {'q': "L'eSIM est-elle disponible ?",
                 'a': "Oui sur les forfaits et terminaux compatibles, avec activation immédiate."},
            ],
        },
        'en_US': {
            'name': 'Unlimited Mobile',
            'tagline': "Business plans on the best French networks",
            'summary': "Unlimited plans on the Orange and Bouygues networks. eSIM, VoLTE, VoWiFi.",
            'intro': (
                "Our Unlimited Mobile plans provide generous calls, SMS and data on the Orange and "
                "Bouygues Telecom networks. Centralized line management, eSIM and VoLTE / VoWiFi "
                "for optimal call quality everywhere."
            ),
            'benefits': [
                {'icon': 'fa-signal', 'title': 'The best networks',
                 'text': "National Orange or Bouygues Telecom coverage, chosen to match your areas."},
                {'icon': 'fa-cogs', 'title': 'Centralized management',
                 'text': "Add, suspend or switch plans from a single console."},
                {'icon': 'fa-microchip', 'title': 'eSIM & VoLTE / VoWiFi',
                 'text': "Instant eSIM activation, HD calls and Wi-Fi continuity in dead zones."},
            ],
            'sections': [
                {'title': 'Built for company fleets',
                 'text': "Manage all your mobile lines without juggling several contacts.",
                 'points': [
                     "Unlimited voice/SMS plans with generous data",
                     "eSIM or physical SIM, depending on your devices",
                     "Usage tracking and out-of-plan blocking",
                 ]},
                {'title': 'Simplicity and cost control',
                 'text': "A single contact for all your lines, one clear bill per month.",
                 'points': [
                     "Porting of your existing mobile numbers",
                     "On-demand data options and Europe roaming",
                     "No long commitment depending on the plan",
                 ]},
            ],
            'faq': [
                {'q': "Can I choose the network?",
                 'a': "Yes, depending on your coverage you pick the Orange or Bouygues Telecom network."},
                {'q': "Is eSIM available?",
                 'a': "Yes on compatible plans and devices, with instant activation."},
            ],
        },
    },
    'data-only': {
        'cat': 'mobile', 'icon': 'fa-wifi',
        'fr_FR': {
            'name': 'Data Only',
            'tagline': "La connectivité cellulaire pour vos objets et vos routeurs",
            'summary': "SIM data pour routeurs 4G/5G, tablettes et objets connectés. IP publiques.",
            'intro': (
                "Les cartes SIM Data Only alimentent en Internet vos routeurs 4G/5G, tablettes, "
                "terminaux de paiement et objets connectés. Idéales pour le secours de lien, la "
                "mobilité ou l'IoT, avec possibilité d'IP publiques fixes."
            ),
            'benefits': [
                {'icon': 'fa-wifi', 'title': 'Data pure',
                 'text': "Des forfaits pensés pour la donnée : routeurs, IoT, télésurveillance, affichage."},
                {'icon': 'fa-globe', 'title': 'IP publiques',
                 'text': "Adresses IP publiques fixes en option pour accéder à distance à vos équipements."},
                {'icon': 'fa-cogs', 'title': 'Parc maîtrisé',
                 'text': "Suivi de consommation par SIM et gestion centralisée de votre parc."},
            ],
            'sections': [
                {'title': 'Des usages multiples',
                 'text': "Une même SIM data couvre de nombreux scénarios professionnels.",
                 'points': [
                     "Secours 4G/5G de votre lien fibre principal",
                     "Connexion de sites temporaires ou mobiles",
                     "IoT : capteurs, TPE, bornes, affichage dynamique",
                 ]},
                {'title': 'Contrôle et sécurité',
                 'text': "Gardez la main sur votre parc et sécurisez les accès distants.",
                 'points': [
                     "Enveloppes data mutualisées ou par SIM",
                     "IP fixe et routage privé possibles",
                     "Alertes et blocage au dépassement",
                 ]},
            ],
            'faq': [
                {'q': "Puis-je obtenir une IP publique fixe ?",
                 'a': "Oui, en option, pour joindre vos équipements depuis l'extérieur en toute sécurité."},
                {'q': "La data est-elle mutualisable ?",
                 'a': "Oui, vous pouvez partager une enveloppe data entre plusieurs SIM du parc."},
            ],
        },
        'en_US': {
            'name': 'Data Only',
            'tagline': "Cellular connectivity for your devices and routers",
            'summary': "Data SIMs for 4G/5G routers, tablets and connected devices. Public IPs.",
            'intro': (
                "Data Only SIM cards bring Internet to your 4G/5G routers, tablets, payment "
                "terminals and connected objects. Ideal for link backup, mobility or IoT, with "
                "optional fixed public IPs."
            ),
            'benefits': [
                {'icon': 'fa-wifi', 'title': 'Pure data',
                 'text': "Plans designed for data: routers, IoT, remote monitoring, digital signage."},
                {'icon': 'fa-globe', 'title': 'Public IPs',
                 'text': "Optional fixed public IP addresses to reach your equipment remotely."},
                {'icon': 'fa-cogs', 'title': 'Managed fleet',
                 'text': "Per-SIM usage tracking and centralized fleet management."},
            ],
            'sections': [
                {'title': 'Many use cases',
                 'text': "A single data SIM covers a wide range of professional scenarios.",
                 'points': [
                     "4G/5G backup for your primary fiber link",
                     "Connecting temporary or mobile sites",
                     "IoT: sensors, payment terminals, kiosks, signage",
                 ]},
                {'title': 'Control and security',
                 'text': "Stay in control of your fleet and secure remote access.",
                 'points': [
                     "Shared or per-SIM data allowances",
                     "Fixed IP and private routing available",
                     "Alerts and blocking on overage",
                 ]},
            ],
            'faq': [
                {'q': "Can I get a fixed public IP?",
                 'a': "Yes, as an option, to securely reach your equipment from outside."},
                {'q': "Can data be shared?",
                 'a': "Yes, you can share a data allowance across several SIMs in the fleet."},
            ],
        },
    },
    # -------------------------------------------------------------- INTERNET
    'liens-fibre': {
        'cat': 'internet', 'icon': 'fa-sitemap',
        'fr_FR': {
            'name': 'Liens Fibre',
            'tagline': "Une connectivité fibre neutre, agrégée et pilotée",
            'summary': "Agrégation neutre de liens fibre, centralisés et pilotés à distance.",
            'intro': (
                "Nos Liens Fibre agrègent plusieurs accès opérateurs en une connectivité unique, "
                "neutre et redondée. Débits garantis, supervision permanente et pilotage à "
                "distance pour connecter vos sites en toute sérénité."
            ),
            'benefits': [
                {'icon': 'fa-sitemap', 'title': 'Neutre & multi-opérateurs',
                 'text': "Nous sélectionnons les meilleurs accès disponibles à chaque adresse, sans dépendance."},
                {'icon': 'fa-shield', 'title': 'Redondance',
                 'text': "Agrégation et bascule automatique pour éviter toute coupure de service."},
                {'icon': 'fa-line-chart', 'title': 'Débits garantis',
                 'text': "Engagements de débit et de rétablissement (GTR) adaptés à vos usages critiques."},
            ],
            'sections': [
                {'title': 'Un lien conçu pour les entreprises',
                 'text': "La fibre professionnelle offre des garanties absentes des offres grand public.",
                 'points': [
                     "FTTH / FTTO selon l'éligibilité de vos sites",
                     "Garantie de temps de rétablissement (GTR)",
                     "Supervision 24/7 et interlocuteur unique",
                 ]},
                {'title': 'Piloté et évolutif',
                 'text': "Votre connectivité est centralisée et administrable à distance.",
                 'points': [
                     "Agrégation de plusieurs liens pour plus de débit et de résilience",
                     "Backup 4G/5G en complément (voir KissBox secours)",
                     "Adaptation des débits selon la croissance de votre activité",
                 ]},
            ],
            'faq': [
                {'q': "Comment vérifier mon éligibilité ?",
                 'a': "Nous réalisons une étude d'éligibilité par adresse pour identifier les meilleurs accès disponibles."},
                {'q': "Proposez-vous une garantie de rétablissement ?",
                 'a': "Oui, une GTR est disponible selon l'offre, avec supervision 24/7."},
            ],
        },
        'en_US': {
            'name': 'Fiber Links',
            'tagline': "Neutral fiber connectivity, aggregated and managed",
            'summary': "Neutral aggregation of fiber links, centralized and managed remotely.",
            'intro': (
                "Our Fiber Links aggregate several carrier accesses into a single, neutral and "
                "redundant connection. Guaranteed throughput, continuous supervision and remote "
                "management to connect your sites with peace of mind."
            ),
            'benefits': [
                {'icon': 'fa-sitemap', 'title': 'Neutral & multi-carrier',
                 'text': "We pick the best access available at each address, with no lock-in."},
                {'icon': 'fa-shield', 'title': 'Redundancy',
                 'text': "Aggregation and automatic failover to avoid any service interruption."},
                {'icon': 'fa-line-chart', 'title': 'Guaranteed throughput',
                 'text': "Throughput and restoration (SLA) commitments matched to your critical needs."},
            ],
            'sections': [
                {'title': 'A link built for business',
                 'text': "Professional fiber offers guarantees that consumer offers lack.",
                 'points': [
                     "FTTH / FTTO depending on your sites' eligibility",
                     "Guaranteed restoration time (SLA)",
                     "24/7 supervision and a single point of contact",
                 ]},
                {'title': 'Managed and scalable',
                 'text': "Your connectivity is centralized and remotely administrable.",
                 'points': [
                     "Aggregation of several links for more throughput and resilience",
                     "4G/5G backup as a complement (see KissBox Backup)",
                     "Throughput adjusted as your business grows",
                 ]},
            ],
            'faq': [
                {'q': "How do I check eligibility?",
                 'a': "We run an address-level eligibility study to identify the best available accesses."},
                {'q': "Do you offer a restoration guarantee?",
                 'a': "Yes, an SLA is available depending on the offer, with 24/7 supervision."},
            ],
        },
    },
    'kissbox-secours': {
        'cat': 'internet', 'icon': 'fa-server',
        'fr_FR': {
            'name': 'KissBox secours',
            'tagline': "Le secours Internet qui garde vos sites connectés",
            'summary': "Secours 4G illimité et Starlink via boîtiers Mikrotik.",
            'intro': (
                "KissBox est un boîtier de secours prêt à l'emploi qui bascule automatiquement "
                "vos sites sur un accès 4G illimité ou Starlink en cas de coupure de votre lien "
                "principal. Zéro interruption, zéro manipulation."
            ),
            'benefits': [
                {'icon': 'fa-life-ring', 'title': 'Continuité assurée',
                 'text': "Bascule automatique en cas de panne de votre lien fibre ou xDSL principal."},
                {'icon': 'fa-bolt', 'title': 'Prêt à l\'emploi',
                 'text': "Boîtier Mikrotik pré-configuré : il suffit de le brancher pour être protégé."},
                {'icon': 'fa-globe', 'title': '4G illimité ou Starlink',
                 'text': "Choisissez le secours cellulaire illimité ou satellite selon vos zones."},
            ],
            'sections': [
                {'title': 'Une protection sans intervention',
                 'text': "KissBox surveille votre lien et prend le relais instantanément.",
                 'points': [
                     "Détection de coupure et bascule automatiques",
                     "Retour sur le lien principal dès qu'il est rétabli",
                     "Boîtier Mikrotik robuste et supervisé",
                 ]},
                {'title': 'Idéal pour les sites critiques',
                 'text': "Commerces, agences, sites de production : gardez vos services en ligne.",
                 'points': [
                     "Maintien des paiements, caisses et VPN",
                     "Secours 4G illimité sans surprise de facturation",
                     "Option Starlink pour les zones mal couvertes",
                 ]},
            ],
            'faq': [
                {'q': "La bascule est-elle automatique ?",
                 'a': "Oui, KissBox détecte la coupure et bascule seul, puis revient sur le lien principal automatiquement."},
                {'q': "Faut-il configurer le boîtier ?",
                 'a': "Non, il arrive pré-configuré. Vous n'avez qu'à le raccorder à votre réseau."},
            ],
        },
        'en_US': {
            'name': 'KissBox Backup',
            'tagline': "The Internet backup that keeps your sites online",
            'summary': "4G unlimited and Starlink failover via Mikrotik boxes.",
            'intro': (
                "KissBox is a ready-to-use backup appliance that automatically switches your sites "
                "to unlimited 4G or Starlink if your primary link goes down. Zero interruption, "
                "zero handling."
            ),
            'benefits': [
                {'icon': 'fa-life-ring', 'title': 'Guaranteed continuity',
                 'text': "Automatic failover if your primary fiber or xDSL link fails."},
                {'icon': 'fa-bolt', 'title': 'Plug and play',
                 'text': "Pre-configured Mikrotik box: just plug it in to be protected."},
                {'icon': 'fa-globe', 'title': 'Unlimited 4G or Starlink',
                 'text': "Choose unlimited cellular or satellite backup depending on your areas."},
            ],
            'sections': [
                {'title': 'Protection with no intervention',
                 'text': "KissBox monitors your link and takes over instantly.",
                 'points': [
                     "Automatic outage detection and failover",
                     "Return to the primary link as soon as it recovers",
                     "Rugged, supervised Mikrotik appliance",
                 ]},
                {'title': 'Ideal for critical sites',
                 'text': "Shops, branches, production sites: keep your services online.",
                 'points': [
                     "Keeps payments, POS and VPN running",
                     "Unlimited 4G backup with no billing surprises",
                     "Starlink option for poorly covered areas",
                 ]},
            ],
            'faq': [
                {'q': "Is failover automatic?",
                 'a': "Yes, KissBox detects the outage and switches on its own, then returns to the primary link automatically."},
                {'q': "Do I need to configure the box?",
                 'a': "No, it arrives pre-configured. You just connect it to your network."},
            ],
        },
    },
    # ----------------------------------------------------------------- CLOUD
    'sauvegarde-ms365': {
        'cat': 'cloud', 'icon': 'fa-cloud',
        'fr_FR': {
            'name': 'Sauvegarde MS 365',
            'tagline': "Protégez vos données Microsoft 365 contre toute perte",
            'summary': "Backup facturé à l'agent, sans limite de stockage, 1 an de rétention.",
            'intro': (
                "Microsoft ne garantit pas la restauration de vos données 365 en cas de "
                "suppression, d'erreur ou de rançongiciel. Notre sauvegarde protège e-mails, "
                "OneDrive, SharePoint et Teams, avec stockage illimité et restauration granulaire."
            ),
            'benefits': [
                {'icon': 'fa-cloud', 'title': 'Stockage illimité',
                 'text': "Sauvegardez sans compter : la facturation se fait à l'utilisateur, pas au volume."},
                {'icon': 'fa-history', 'title': 'Rétention 1 an',
                 'text': "Retrouvez une version antérieure de vos données jusqu'à un an en arrière."},
                {'icon': 'fa-undo', 'title': 'Restauration granulaire',
                 'text': "Restaurez un e-mail, un fichier ou une boîte entière en quelques clics."},
            ],
            'sections': [
                {'title': 'Couvre tout votre environnement 365',
                 'text': "Une seule solution pour l'ensemble des services Microsoft 365.",
                 'points': [
                     "Exchange Online (e-mails, contacts, agendas)",
                     "OneDrive et SharePoint (fichiers et sites)",
                     "Microsoft Teams (conversations et fichiers)",
                 ]},
                {'title': 'Sécurité et conformité',
                 'text': "Vos sauvegardes sont chiffrées et hébergées de façon souveraine.",
                 'points': [
                     "Chiffrement des données au repos et en transit",
                     "Protection contre les rançongiciels et suppressions",
                     "Restaurations illimitées, sans frais cachés",
                 ]},
            ],
            'faq': [
                {'q': "Microsoft ne sauvegarde-t-il pas déjà mes données ?",
                 'a': "Microsoft assure la disponibilité de la plateforme, mais la protection de vos données vous incombe (modèle de responsabilité partagée)."},
                {'q': "Comment se fait la facturation ?",
                 'a': "À l'utilisateur protégé, avec un stockage illimité — pas de surcoût au volume."},
            ],
        },
        'en_US': {
            'name': 'MS 365 Backup',
            'tagline': "Protect your Microsoft 365 data against any loss",
            'summary': "Per-agent backup billing, unlimited storage, 1-year retention.",
            'intro': (
                "Microsoft does not guarantee recovery of your 365 data in case of deletion, "
                "mistake or ransomware. Our backup protects email, OneDrive, SharePoint and Teams, "
                "with unlimited storage and granular restore."
            ),
            'benefits': [
                {'icon': 'fa-cloud', 'title': 'Unlimited storage',
                 'text': "Back up without counting: billing is per user, not per volume."},
                {'icon': 'fa-history', 'title': '1-year retention',
                 'text': "Recover a previous version of your data up to a year back."},
                {'icon': 'fa-undo', 'title': 'Granular restore',
                 'text': "Restore an email, a file or an entire mailbox in a few clicks."},
            ],
            'sections': [
                {'title': 'Covers your whole 365 environment',
                 'text': "A single solution for all Microsoft 365 services.",
                 'points': [
                     "Exchange Online (email, contacts, calendars)",
                     "OneDrive and SharePoint (files and sites)",
                     "Microsoft Teams (chats and files)",
                 ]},
                {'title': 'Security and compliance',
                 'text': "Your backups are encrypted and hosted sovereignly.",
                 'points': [
                     "Encryption at rest and in transit",
                     "Protection against ransomware and deletions",
                     "Unlimited restores, no hidden fees",
                 ]},
            ],
            'faq': [
                {'q': "Doesn't Microsoft already back up my data?",
                 'a': "Microsoft ensures platform availability, but protecting your data is your responsibility (shared responsibility model)."},
                {'q': "How is it billed?",
                 'a': "Per protected user, with unlimited storage — no extra cost by volume."},
            ],
        },
    },
    'stockage-s3': {
        'cat': 'cloud', 'icon': 'fa-database',
        'fr_FR': {
            'name': 'Stockage S3',
            'tagline': "Du stockage objet compatible S3, hébergé en France",
            'summary': "Stockage objet S3 hébergé en France, facturé au Go par mois.",
            'intro': (
                "Notre Stockage S3 offre un espace objet compatible avec l'API Amazon S3, hébergé "
                "dans des datacenters français. Idéal pour vos sauvegardes, archives, sites web et "
                "applications, avec une facturation simple au Go consommé."
            ),
            'benefits': [
                {'icon': 'fa-database', 'title': 'Compatible S3',
                 'text': "Utilisez vos outils et applications existants qui parlent l'API S3, sans réécriture."},
                {'icon': 'fa-map-marker', 'title': 'Hébergé en France',
                 'text': "Vos données restent sur le territoire, pour la souveraineté et la conformité."},
                {'icon': 'fa-euro', 'title': 'Facturation au Go',
                 'text': "Vous ne payez que ce que vous stockez réellement, sans engagement de volume."},
            ],
            'sections': [
                {'title': 'Des usages sans limite',
                 'text': "Le stockage objet s'adapte à de nombreux besoins professionnels.",
                 'points': [
                     "Cibles de sauvegarde (Veeam, restic, etc.)",
                     "Archivage longue durée et données froides",
                     "Hébergement de médias pour vos applications et sites",
                 ]},
                {'title': 'Fiable et sécurisé',
                 'text': "Vos objets sont stockés de façon durable et protégée.",
                 'points': [
                     "Redondance des données pour la durabilité",
                     "Chiffrement et gestion fine des accès (clés/buckets)",
                     "Datacenters français certifiés",
                 ]},
            ],
            'faq': [
                {'q': "Est-ce vraiment compatible Amazon S3 ?",
                 'a': "Oui, l'API est compatible S3 : vos outils existants fonctionnent en changeant simplement l'endpoint."},
                {'q': "Comment suis-je facturé ?",
                 'a': "Au Go stocké par mois, sans engagement de volume ni frais cachés."},
            ],
        },
        'en_US': {
            'name': 'S3 Storage',
            'tagline': "S3-compatible object storage, hosted in France",
            'summary': "S3 object storage hosted in France, billed per GB per month.",
            'intro': (
                "Our S3 Storage offers object space compatible with the Amazon S3 API, hosted in "
                "French datacenters. Ideal for your backups, archives, websites and applications, "
                "with simple billing per GB used."
            ),
            'benefits': [
                {'icon': 'fa-database', 'title': 'S3-compatible',
                 'text': "Use your existing tools and apps that speak the S3 API, with no rewrite."},
                {'icon': 'fa-map-marker', 'title': 'Hosted in France',
                 'text': "Your data stays on national soil, for sovereignty and compliance."},
                {'icon': 'fa-euro', 'title': 'Billed per GB',
                 'text': "You only pay for what you actually store, with no volume commitment."},
            ],
            'sections': [
                {'title': 'Unlimited use cases',
                 'text': "Object storage adapts to many professional needs.",
                 'points': [
                     "Backup targets (Veeam, restic, etc.)",
                     "Long-term archiving and cold data",
                     "Media hosting for your apps and websites",
                 ]},
                {'title': 'Reliable and secure',
                 'text': "Your objects are stored durably and protected.",
                 'points': [
                     "Data redundancy for durability",
                     "Encryption and fine-grained access (keys/buckets)",
                     "Certified French datacenters",
                 ]},
            ],
            'faq': [
                {'q': "Is it really Amazon S3-compatible?",
                 'a': "Yes, the API is S3-compatible: your existing tools work by simply changing the endpoint."},
                {'q': "How am I billed?",
                 'a': "Per GB stored per month, with no volume commitment or hidden fees."},
            ],
        },
    },
    # -------------------------------------------------------------- SECURITE
    'cybersecurite': {
        'cat': 'securite', 'icon': 'fa-shield',
        'fr_FR': {
            'name': 'Cybersécurité',
            'tagline': "Sécurisez l'ensemble de vos sites, de bout en bout",
            'summary': "MPLS et pare-feu managés pour sécuriser l'ensemble des sites.",
            'intro': (
                "Notre offre Cybersécurité protège l'ensemble de votre réseau multi-sites grâce à "
                "un réseau privé MPLS et des pare-feu managés. Filtrage, VPN et supervision "
                "permanente pour garder vos données et vos échanges à l'abri."
            ),
            'benefits': [
                {'icon': 'fa-shield', 'title': 'Pare-feu managés',
                 'text': "Des pare-feu configurés, mis à jour et supervisés par nos experts sécurité."},
                {'icon': 'fa-lock', 'title': 'Réseau privé MPLS',
                 'text': "Interconnexion sécurisée de vos sites, isolée d'Internet public."},
                {'icon': 'fa-eye', 'title': 'Supervision 24/7',
                 'text': "Détection et réponse aux menaces en continu, avec alertes en temps réel."},
            ],
            'sections': [
                {'title': 'Une sécurité de bout en bout',
                 'text': "Nous couvrons le réseau, les accès et les échanges entre vos sites.",
                 'points': [
                     "Réseau privé MPLS multi-sites",
                     "Filtrage applicatif et anti-menaces sur les pare-feu",
                     "VPN sécurisés pour les accès distants",
                 ]},
                {'title': 'Managé par des experts',
                 'text': "Vous déléguez l'exploitation et gardez la visibilité.",
                 'points': [
                     "Configuration et maintien en condition de sécurité",
                     "Supervision et journalisation centralisées",
                     "Accompagnement et reporting réguliers",
                 ]},
            ],
            'faq': [
                {'q': "Gérez-vous entièrement les équipements ?",
                 'a': "Oui, les pare-feu sont managés : configuration, mises à jour et supervision sont assurées par nos équipes."},
                {'q': "Convient-il aux entreprises multi-sites ?",
                 'a': "Oui, le réseau MPLS est justement conçu pour interconnecter et sécuriser plusieurs sites."},
            ],
        },
        'en_US': {
            'name': 'Cybersecurity',
            'tagline': "Secure all your sites, end to end",
            'summary': "Managed MPLS and firewalls to secure all your sites.",
            'intro': (
                "Our Cybersecurity offer protects your entire multi-site network with a private "
                "MPLS network and managed firewalls. Filtering, VPN and continuous supervision to "
                "keep your data and communications safe."
            ),
            'benefits': [
                {'icon': 'fa-shield', 'title': 'Managed firewalls',
                 'text': "Firewalls configured, updated and supervised by our security experts."},
                {'icon': 'fa-lock', 'title': 'Private MPLS network',
                 'text': "Secure interconnection of your sites, isolated from the public Internet."},
                {'icon': 'fa-eye', 'title': '24/7 supervision',
                 'text': "Continuous threat detection and response, with real-time alerts."},
            ],
            'sections': [
                {'title': 'End-to-end security',
                 'text': "We cover the network, access and communications between your sites.",
                 'points': [
                     "Multi-site private MPLS network",
                     "Application filtering and anti-threat on firewalls",
                     "Secure VPNs for remote access",
                 ]},
                {'title': 'Managed by experts',
                 'text': "You delegate operations and keep the visibility.",
                 'points': [
                     "Configuration and security maintenance",
                     "Centralized supervision and logging",
                     "Regular guidance and reporting",
                 ]},
            ],
            'faq': [
                {'q': "Do you fully manage the equipment?",
                 'a': "Yes, firewalls are managed: configuration, updates and supervision are handled by our teams."},
                {'q': "Is it suitable for multi-site companies?",
                 'a': "Yes, the MPLS network is precisely designed to interconnect and secure multiple sites."},
            ],
        },
    },
}