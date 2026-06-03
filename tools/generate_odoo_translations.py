from io import BytesIO
from pathlib import Path

from babel.messages import pofile


ROOT = Path(__file__).resolve().parents[1]
MODULES = [
    "auto_base",
    "auto_website",
    "auto_booking",
    "auto_sale",
    "auto_financing",
    "auto_reviews",
    "auto_compare",
]


EN_REPLACEMENTS = {
    "\"EXOCOMS accompagne les entreprises avec des services fiables, innovants et adaptés à chaque besoin.\"":
        "\"EXOCOMS supports companies with reliable, innovative services tailored to every need.\"",
    "L'excellence automobile asiatique, accompagnée par EXOCOMS.":
        "Asian automotive excellence, supported by EXOCOMS.",
    "EXOCOMS accompagne les entreprises avec des solutions digitales fiables, modernes et adaptées à leurs enjeux.":
        "EXOCOMS supports companies with reliable, modern digital solutions tailored to their challenges.",
    "Les constructeurs asiatiques transforment la mobilité grâce à des plateformes 100% électriques,":
        "Asian manufacturers are transforming mobility through fully electric platforms,",
    "des systèmes d'aide à la conduite avancés et des coûts d'utilisation maîtrisés.":
        "advanced driver assistance systems and controlled running costs.",
    "Notre plateforme centralise l'offre, les disponibilités et les parcours clients pour convertir plus vite.":
        "Our platform centralizes inventory, availability and customer journeys to convert faster.",
    "Une question sur le catalogue automobile, un devis ou un accompagnement digital ?":
        "Do you have a question about the vehicle catalog, a quote or digital support?",
    "L'équipe EXOCOMS vous répondra dans les meilleurs délais.":
        "The EXOCOMS team will respond as quickly as possible.",
    "Véhicules vérifiés, prix transparents, accompagnement complet de la sélection à la livraison.":
        "Verified vehicles, transparent prices, full support from selection to delivery.",
    "Des prix réels, des fiches claires, des décisions plus rapides.":
        "Real prices, clear listings, faster decisions.",
    "Défilement continu des constructeurs disponibles sur la plateforme.":
        "Continuous scrolling of manufacturers available on the platform.",
    "avec équipements connectés, garanties constructeur":
        "with connected equipment and manufacturer warranties",
    "et accompagnement complet: devis, essai, réservation et financement.":
        "and full support: quote, test drive, reservation and financing.",
    "Merci, votre demande a bien été envoyée.":
        "Thank you, your request has been submitted.",
    "Un conseiller vous contacte rapidement avec disponibilité, options et proposition commerciale.":
        "An advisor will contact you shortly with availability, options and a commercial proposal.",
    "Notre équipe valide le créneau et vous contacte rapidement.":
        "Our team will confirm the time slot and contact you shortly.",
    "Notre équipe confirme rapidement la date, le lieu et le conseiller.":
        "Our team will quickly confirm the date, location and advisor.",
    "Un conseiller financement vous contacte après pré-analyse de votre dossier.":
        "A financing advisor will contact you after a preliminary review of your application.",
    "Sélectionnez au moins deux véhicules pour activer la comparaison.":
        "Select at least two vehicles to enable comparison.",
    "Aucun véhicule ne correspond à vos filtres.":
        "No vehicles match your filters.",
    "Aucun modèle publié pour cette marque.":
        "No models have been published for this brand.",
    "Aucun avis publié pour le moment.":
        "No reviews have been published yet.",
    "Aucun favori pour le moment.":
        "No favorites yet.",
    "Aucune réservation pour le moment.":
        "No reservations yet.",
    "Aucune demande d'essai pour le moment.":
        "No test drive requests yet.",
    "Aucune demande de financement pour le moment.":
        "No financing requests yet.",
    "Aucun avis soumis pour le moment.":
        "No reviews submitted yet.",
    "Aucun créneau sélectionné":
        "No time slot selected",
    "Précisez votre délai et la configuration souhaitée.":
        "Specify your desired timeframe and configuration.",
    "La capacité doit être au moins égale à 1.":
        "Capacity must be at least 1.",
    "La date de fin doit être supérieure à la date de début.":
        "The end date must be later than the start date.",
    "Un client ne peut déposer qu'un seul avis par véhicule.":
        "A customer can submit only one review per vehicle.",
    "Le BYD Atto 3 est l'un des SUV électriques les plus compétitifs de son segment.":
        "The BYD Atto 3 is one of the most competitive electric SUVs in its segment.",
    "BYD est un constructeur pionnier de la mobilité électrifiée avec une gamme complète de SUV, berlines et hybrides rechargeables.":
        "BYD is a pioneer in electrified mobility with a complete range of SUVs, sedans and plug-in hybrids.",
    "MG combine une approche prix/prestations très compétitive avec des technologies modernes et une distribution européenne solide.":
        "MG combines a highly competitive value proposition with modern technology and a strong European distribution network.",
    "XPeng est une marque orientée software, reconnue pour ses plateformes 800V, ses temps de charge rapides et ses interfaces connectées.":
        "XPeng is a software-focused brand known for its 800V platforms, fast charging times and connected interfaces.",
    "NIO cible le segment premium avec un fort accent sur le confort, la sécurité et l'écosystème de services.":
        "NIO targets the premium segment with a strong focus on comfort, safety and its service ecosystem.",
    "OMODA propose des SUV électriques modernes, connectés et bien équipés pour le marché urbain européen.":
        "OMODA offers modern, connected and well-equipped electric SUVs for the European urban market.",
    "Zeekr se positionne sur le premium technologique avec des performances élevées et une finition haut de gamme.":
        "Zeekr positions itself in technology-led premium vehicles with high performance and upscale finishes.",
    "Leapmotor apporte une alternative accessible dans le segment SUV électrique, avec des équipements complets et une autonomie solide.":
        "Leapmotor offers an accessible alternative in the electric SUV segment, with comprehensive equipment and solid range.",
    "Constructeur automobile chinois proposant une gamme moderne de véhicules électrifiés.":
        "Chinese automaker offering a modern range of electrified vehicles.",
    "Compacte électrique pratique, efficiente et adaptée aux déplacements urbains.":
        "Practical and efficient electric compact car designed for urban travel.",
    "Compacte hybride efficiente, agréable en ville et simple à utiliser au quotidien.":
        "Efficient hybrid compact car that is pleasant in the city and easy to use every day.",
    "Berline électrique élégante combinant efficience, performances et confort.":
        "Elegant electric sedan combining efficiency, performance and comfort.",
    "Crossover électrique polyvalent avec technologies connectées et conduite fluide.":
        "Versatile electric crossover with connected technology and smooth driving.",
    "SUV électrique moderne offrant confort, technologie et autonomie pour tous les trajets.":
        "Modern electric SUV offering comfort, technology and range for every journey.",
    "SUV hybride rechargeable polyvalent avec une grande autonomie combinée.":
        "Versatile plug-in hybrid SUV with a long combined range.",
    "Full Hybrid":
        "Full Hybrid",
    "SUV électrique familial avec autonomie solide et équipements de sécurité complets.":
        "Family electric SUV with solid range and comprehensive safety equipment.",
    "Berline électrique premium orientée performance et efficience.":
        "Premium electric sedan focused on performance and efficiency.",
    "SUV hybride rechargeable pour les longs trajets avec consommation optimisée.":
        "Plug-in hybrid SUV for long journeys with optimized consumption.",
    "Compacte électrique accessible avec un excellent rapport prix/autonomie.":
        "Accessible electric compact car with an excellent price-to-range ratio.",
    "SUV compact électrique avec coffre généreux et équipement complet.":
        "Compact electric SUV with a spacious trunk and comprehensive equipment.",
    "SUV 800V ultra-rapide à la recharge avec architecture software avancée.":
        "800V SUV with ultra-fast charging and advanced software architecture.",
    "Berline électrique efficiente avec grande autonomie et interface IA.":
        "Efficient electric sedan with long range and an AI interface.",
    "SUV flagship avec excellent confort de roulage et charge ultra-rapide.":
        "Flagship SUV with excellent ride comfort and ultra-fast charging.",
    "Touring premium électrique, performant et très confortable sur longue distance.":
        "Premium electric touring car, powerful and very comfortable over long distances.",
    "SUV premium polyvalent, silencieux et très équipé pour la famille.":
        "Versatile premium SUV, quiet and highly equipped for families.",
    "Crossover électrique au design marqué et aux technologies connectées.":
        "Electric crossover with distinctive design and connected technology.",
    "Crossover premium compact avec transmission AWD et intérieur haut de gamme.":
        "Compact premium crossover with AWD and an upscale interior.",
    "Shooting brake électrique performante, grand volume et finition premium.":
        "High-performance electric shooting brake with generous space and premium finish.",
    "SUV électrique familial avec prix d'entrée agressif et équipements essentiels.":
        "Family electric SUV with a competitive entry price and essential equipment.",
    "Recharge DC rapide et architecture batterie Blade.":
        "Fast DC charging and Blade battery architecture.",
    "Habitacle spacieux et cockpit digital.":
        "Spacious cabin and digital cockpit.",
    "Pack ADAS complet pour les trajets urbains et autoroutiers.":
        "Comprehensive ADAS package for urban and motorway journeys.",
    "Trouvez la voiture de vos rêves.":
        "Find the car of your dreams.",
    "Le catalogue premium des voitures chinoises.":
        "The premium catalog of Chinese vehicles.",
    "Accéder aux voitures de demain":
        "Drive tomorrow's vehicles",
    "Une expertise tech au service de votre mobilité":
        "Technology expertise serving your mobility",
    "Marketplace automobile portée par EXOCOMS Group.":
        "Automotive marketplace powered by EXOCOMS Group.",
    "Filtrez par marque, motorisation, disponibilité, année et budget.":
        "Filter by brand, powertrain, availability, year and budget.",
    "Spécifications détaillées en cours de publication.":
        "Detailed specifications are being published.",
    "Demande d'essai envoyée":
        "Test drive request submitted",
    "Demande de financement envoyée":
        "Financing request submitted",
    "Réservation envoyée":
        "Reservation submitted",
    "Demande de financement":
        "Financing request",
    "Demander un financement":
        "Request financing",
    "Demander un devis":
        "Request a quote",
    "Demander un essai":
        "Request a test drive",
    "Envoyer la demande d'essai":
        "Submit test drive request",
    "Envoyer la réservation":
        "Submit reservation",
    "Envoyer la demande":
        "Submit request",
    "Retour fiche véhicule":
        "Back to vehicle details",
    "Continuer le catalogue":
        "Continue browsing the catalog",
    "Choisir un créneau disponible":
        "Choose an available time slot",
    "Ou demander une autre date/heure":
        "Or request another date/time",
    "Note complémentaire":
        "Additional note",
    "Mes demandes de financement":
        "My financing requests",
    "Mes réservations":
        "My reservations",
    "Mes essais":
        "My test drives",
    "Mes véhicules favoris":
        "My favorite vehicles",
    "Comparer les véhicules":
        "Compare vehicles",
    "Vider la comparaison":
        "Clear comparison",
    "Ouvrir le catalogue complet":
        "Open the full catalog",
    "Catalogue des véhicules":
        "Vehicle catalog",
    "Modèles de la marque":
        "Brand models",
    "Modèles similaires":
        "Similar models",
    "Modèles vedettes":
        "Featured models",
    "Toutes les marques":
        "All brands",
    "Marques partenaires":
        "Partner brands",
    "Disponibles immédiatement":
        "Available now",
    "Véhicules publiés":
        "Published vehicles",
    "Prix de départ":
        "Starting price",
    "Prix croissant":
        "Price: low to high",
    "Prix décroissant":
        "Price: high to low",
    "Voir les meilleurs prix":
        "View the best prices",
    "Voir ce modèle":
        "View this model",
    "Voir les détails":
        "View details",
    "Ouvrir la fiche":
        "Open details",
    "Ouvrir le catalogue":
        "Open the catalog",
    "Accéder au catalogue":
        "Browse the catalog",
    "Explorer le catalogue":
        "Explore the catalog",
    "Explorer la catégorie":
        "Explore the category",
    "Retour catalogue":
        "Back to catalog",
    "Retour accueil":
        "Back to home",
    "Tout voir":
        "View all",
    "Ajouter au comparateur":
        "Add to comparison",
    "Ajouter au panier":
        "Add to cart",
    "Ajouter aux favoris":
        "Add to favorites",
    "Retirer des favoris":
        "Remove from favorites",
    "Planifier un essai":
        "Schedule a test drive",
    "Réserver ce véhicule":
        "Reserve this vehicle",
    "Laisser un avis":
        "Leave a review",
    "Connectez-vous pour laisser un avis":
        "Sign in to leave a review",
    "Envoyer pour modération":
        "Submit for moderation",
    "Avis clients":
        "Customer reviews",
    "Aucun avis":
        "No reviews",
    "Catalogue automobile premium":
        "Premium vehicle catalog",
    "EXOCOMS Mobilité":
        "EXOCOMS Mobility",
    "Langues":
        "Languages",
    "Liens utiles":
        "Useful links",
    "À propos":
        "About",
    "Accueil":
        "Home",
    "Catalogue":
        "Catalog",
    "Comparateur":
        "Compare",
    "Marques":
        "Brands",
    "Favoris":
        "Favorites",
    "Réinitialiser":
        "Reset",
    "Appliquer":
        "Apply",
    "Précédent":
        "Previous",
    "Suivant":
        "Next",
    "Plus récents":
        "Newest",
    "Rechercher un modèle":
        "Search for a model",
    "Marque":
        "Brand",
    "Catégorie":
        "Category",
    "Disponibilité":
        "Availability",
    "Motorisation":
        "Powertrain",
    "Autonomie":
        "Range",
    "Année modèle":
        "Model year",
    "Année min":
        "Min year",
    "Année max":
        "Max year",
    "Prix min":
        "Min price",
    "Prix max":
        "Max price",
    "Prix":
        "Price",
    "Puissance":
        "Power",
    "Batterie":
        "Battery",
    "Caractéristique":
        "Feature",
    "Places":
        "Seats",
    "Section":
        "Section",
    "Spécification":
        "Specification",
    "Spécifications":
        "Specifications",
    "Valeur":
        "Value",
    "Options":
        "Options",
    "Nom complet":
        "Full name",
    "Nom":
        "Name",
    "Téléphone":
        "Phone",
    "Société":
        "Company",
    "Sujet":
        "Subject",
    "Commentaire":
        "Comment",
    "Note":
        "Rating",
    "Titre":
        "Title",
    "Statut":
        "Status",
    "Lieu":
        "Location",
    "Durée":
        "Duration",
    "Durée (mois)":
        "Duration (months)",
    "Montant souhaité":
        "Requested amount",
    "Revenu mensuel":
        "Monthly income",
    "Apport initial":
        "Down payment",
    "Canal préféré":
        "Preferred contact",
    "Référence:":
        "Reference:",
    "Véhicule:":
        "Vehicle:",
    "Véhicule":
        "Vehicle",
    "Véhicules":
        "Vehicles",
    "Date/heure demandée":
        "Requested date/time",
    "Année":
        "Year",
    "Bientôt disponible":
        "Coming soon",
    "Disponible":
        "Available",
    "Réservé":
        "Reserved",
    "Vendu":
        "Sold",
    "Berline":
        "Sedan",
    "Compacte":
        "Compact",
    "Sièges avant ventilés":
        "Ventilated front seats",
    "km d'autonomie":
        "km range",
    "modèles publiés":
        "published models",
    "à partir de":
        "starting from",
    "%s à %s":
        "%s at %s",
    "Nouveau créneau":
        "New time slot",
    "Ouvrir les véhicules liés":
        "Open related vehicles",
    "Catégorie de véhicule":
        "Vehicle category",
    "Catégories de véhicules":
        "Vehicle categories",
    "Motorisation de véhicule":
        "Vehicle powertrain",
    "Options de véhicules":
        "Vehicle options",
    "Prix de vente":
        "Sale price",
    "Spécification du véhicule":
        "Vehicle specification",
    ": trouvez le modèle adapté":
        ": find the right model",
    "Comparer":
        "Compare",
    "Contacter EXOCOMS":
        "Contact EXOCOMS",
    "Envoyer":
        "Send",
    "Image du véhicule indisponible":
        "Vehicle image unavailable",
    "Image indisponible":
        "Image unavailable",
    "Sélection de véhicules":
        "Vehicle selection",
    "Confirmation de demande d'essai":
        "Test drive request confirmation",
    "Confirmation de réservation véhicule":
        "Vehicle reservation confirmation",
    "Demande d'essai reçue:":
        "Test drive request received:",
    "Demande de réservation reçue:":
        "Reservation request received:",
    "Demandes d'essai":
        "Test drive requests",
    "Essai de véhicule":
        "Vehicle test drive",
    "Essais":
        "Test drives",
    "Réservation de véhicule":
        "Vehicle reservation",
    "Réservations":
        "Reservations",
    "Confirmation de demande de devis véhicule":
        "Vehicle quote request confirmation",
    "Demande de devis véhicule":
        "Vehicle quote request",
    "Demande de devis:":
        "Quote request:",
    "Demandes de devis":
        "Quote requests",
    "Nous avons reçu votre demande de devis:":
        "We have received your quote request:",
    "Demandes de financement":
        "Financing requests",
    "Demande de financement véhicule":
        "Vehicle financing request",
    "Demande ID:":
        "Request ID:",
    "Mes demandes":
        "My requests",
    "Montant":
        "Amount",
    "Mes avis":
        "My reviews",
    "Retirer":
        "Remove",
    "Bonjour ${object.partner_id.name},":
        "Hello ${object.partner_id.name},",
    "Votre demande d'essai a bien été reçue pour":
        "Your test drive request has been received for",
    "Votre demande de réservation a bien été reçue pour":
        "Your reservation request has been received for",
    "Date demandée:":
        "Requested date:",
    "Merci pour votre intérêt pour":
        "Thank you for your interest in",
    "La référence de votre demande de devis est":
        "Your quote request reference is",
    "Notre équipe commerciale vous contactera rapidement.":
        "Our sales team will contact you shortly.",
    "Cordialement,":
        "Kind regards,",
    "L'équipe commerciale EXOCOMS Voitures":
        "The EXOCOMS Vehicles sales team",
    "Très bien":
        "Very good",
    "Bien":
        "Good",
    "Moyen":
        "Average",
    "Faible":
        "Poor",
    "Indicateur du carrousel":
        "Carousel indicator",
    "Le nom et l'email sont obligatoires.":
        "Name and email are required.",
    "Sélectionnez un créneau ou indiquez une date souhaitée.":
        "Select a time slot or enter a preferred date.",
    "Showroom principal":
        "Main showroom",
    "Aide à la conduite":
        "Driver assistance",
    "Chaque produit ne peut être lié qu'à un seul véhicule.":
        "Each product can only be linked to one vehicle.",
    "Couleur de véhicule":
        "Vehicle color",
    "Couleurs de véhicules":
        "Vehicle colors",
    "Gestionnaire de contenu automobile":
        "Automotive Content Manager",
    "Image de galerie véhicule":
        "Vehicle gallery image",
    "L'année du véhicule doit être comprise entre 1990 et l'année prochaine.":
        "The vehicle year must be between 1990 and next year.",
    "Le nom de l'option doit être unique.":
        "The option name must be unique.",
    "Le nom de la catégorie doit être unique.":
        "The category name must be unique.",
    "Le nom de la couleur doit être unique.":
        "The color name must be unique.",
    "Le nom de la marque doit être unique.":
        "The brand name must be unique.",
    "Le nom de la motorisation doit être unique.":
        "The powertrain name must be unique.",
    "Logo marque":
        "Brand logo",
    "Option du véhicule":
        "Vehicle option",
    "Produit de vente lie au vehicule. S'il est vide, il est cree automatiquement a l'enregistrement.":
        "Sale product linked to the vehicle. If empty, it is created automatically when saving.",
    "Publie sur le site":
        "Published on the website",
    "Publié":
        "Published",
    "Résumé":
        "Summary",
    "Temps de charge":
        "Charging time",
    "Énergie":
        "Energy",
    "Multimédia":
        "Multimedia",
    "Annulé":
        "Cancelled",
    "Annulée":
        "Cancelled",
    "Confirmé":
        "Confirmed",
    "Confirmée":
        "Confirmed",
    "Terminé":
        "Completed",
    "Terminée":
        "Completed",
    "État":
        "State",
    "Conseiller assigné":
        "Assigned advisor",
    "Créneau de rendez-vous":
        "Appointment slot",
    "Créneaux de rendez-vous":
        "Appointment slots",
    "Approuvée":
        "Approved",
    "En étude":
        "Under review",
    "Mettre en étude":
        "Set under review",
    "Rejetée":
        "Rejected",
    "Avis":
        "Reviews",
    "Avis client véhicule":
        "Vehicle customer review",
    "Approuvé":
        "Approved",
    "Rejeté":
        "Rejected",
    "Créer un bon de commande":
        "Create a sales order",
    "Créer une opportunité CRM":
        "Create a CRM opportunity",
    "Devis envoyé":
        "Quote sent",
    "Gagnée":
        "Won",
    "Qualifiée":
        "Qualified",
}


AR_REPLACEMENTS = {
    "Constructeur automobile chinois proposant une gamme moderne de véhicules électrifiés.":
        "شركة صينية لصناعة السيارات تقدم مجموعة حديثة من المركبات الكهربائية.",
    "Compacte électrique pratique, efficiente et adaptée aux déplacements urbains.":
        "سيارة كهربائية مدمجة عملية وفعالة ومناسبة للتنقل داخل المدينة.",
    "Compacte hybride efficiente, agréable en ville et simple à utiliser au quotidien.":
        "سيارة هجينة مدمجة فعالة ومريحة في المدينة وسهلة الاستخدام يوميًا.",
    "Berline électrique élégante combinant efficience, performances et confort.":
        "سيدان كهربائية أنيقة تجمع بين الكفاءة والأداء والراحة.",
    "Crossover électrique polyvalent avec technologies connectées et conduite fluide.":
        "كروس أوفر كهربائية متعددة الاستخدامات بتقنيات متصلة وقيادة سلسة.",
    "SUV électrique moderne offrant confort, technologie et autonomie pour tous les trajets.":
        "سيارة SUV كهربائية حديثة توفر الراحة والتقنية والمدى لجميع الرحلات.",
    "SUV hybride rechargeable polyvalent avec une grande autonomie combinée.":
        "سيارة SUV هجينة قابلة للشحن متعددة الاستخدامات بمدى إجمالي طويل.",
    "Full Hybrid":
        "هجين كامل",
    "\"EXOCOMS accompagne les entreprises avec des services fiables, innovants et adaptés à chaque besoin.\"":
        "\"تدعم EXOCOMS الشركات بخدمات موثوقة ومبتكرة ومصممة لتلبية كل احتياج.\"",
    "L'excellence automobile asiatique, accompagnée par EXOCOMS.":
        "تميّز السيارات الآسيوية بدعم من EXOCOMS.",
    "EXOCOMS accompagne les entreprises avec des solutions digitales fiables, modernes et adaptées à leurs enjeux.":
        "تدعم EXOCOMS الشركات بحلول رقمية موثوقة وحديثة ومصممة لتلبية تحدياتها.",
    "Les constructeurs asiatiques transforment la mobilité grâce à des plateformes 100% électriques,":
        "يغيّر المصنعون الآسيويون مفهوم التنقل عبر منصات كهربائية بالكامل،",
    "des systèmes d'aide à la conduite avancés et des coûts d'utilisation maîtrisés.":
        "وأنظمة متقدمة لمساعدة السائق وتكاليف تشغيل مدروسة.",
    "Notre plateforme centralise l'offre, les disponibilités et les parcours clients pour convertir plus vite.":
        "تجمع منصتنا العروض والتوفر ومسارات العملاء لتسريع عملية الشراء.",
    "Une question sur le catalogue automobile, un devis ou un accompagnement digital ?":
        "هل لديك سؤال حول كتالوج السيارات أو عرض سعر أو الدعم الرقمي؟",
    "L'équipe EXOCOMS vous répondra dans les meilleurs délais.":
        "سيرد عليك فريق EXOCOMS في أقرب وقت ممكن.",
    "Véhicules vérifiés, prix transparents, accompagnement complet de la sélection à la livraison.":
        "سيارات موثوقة، أسعار شفافة، ودعم كامل من الاختيار حتى التسليم.",
    "Des prix réels, des fiches claires, des décisions plus rapides.":
        "أسعار حقيقية، معلومات واضحة، وقرارات أسرع.",
    "Défilement continu des constructeurs disponibles sur la plateforme.":
        "تمرير مستمر للمصنّعين المتاحين على المنصة.",
    "avec équipements connectés, garanties constructeur":
        "مع تجهيزات متصلة وضمانات الشركة المصنعة",
    "et accompagnement complet: devis, essai, réservation et financement.":
        "ودعم كامل: عرض سعر وتجربة قيادة وحجز وتمويل.",
    "Merci, votre demande a bien été envoyée.":
        "شكرًا لك، تم إرسال طلبك بنجاح.",
    "Un conseiller vous contacte rapidement avec disponibilité, options et proposition commerciale.":
        "سيتواصل معك مستشار قريبًا لتزويدك بالتوفر والخيارات والعرض التجاري.",
    "Notre équipe valide le créneau et vous contacte rapidement.":
        "سيؤكد فريقنا الموعد ويتواصل معك قريبًا.",
    "Notre équipe confirme rapidement la date, le lieu et le conseiller.":
        "سيؤكد فريقنا بسرعة التاريخ والموقع والمستشار.",
    "Un conseiller financement vous contacte après pré-analyse de votre dossier.":
        "سيتواصل معك مستشار تمويل بعد المراجعة الأولية لملفك.",
    "Sélectionnez au moins deux véhicules pour activer la comparaison.":
        "اختر سيارتين على الأقل لتفعيل المقارنة.",
    "Aucun véhicule ne correspond à vos filtres.":
        "لا توجد سيارات تطابق عوامل التصفية.",
    "Aucun modèle publié pour cette marque.":
        "لا توجد طرازات منشورة لهذه العلامة التجارية.",
    "Aucun avis publié pour le moment.":
        "لا توجد مراجعات منشورة حتى الآن.",
    "Aucun favori pour le moment.":
        "لا توجد عناصر مفضلة حتى الآن.",
    "Aucune réservation pour le moment.":
        "لا توجد حجوزات حتى الآن.",
    "Aucune demande d'essai pour le moment.":
        "لا توجد طلبات تجربة قيادة حتى الآن.",
    "Aucune demande de financement pour le moment.":
        "لا توجد طلبات تمويل حتى الآن.",
    "Aucun avis soumis pour le moment.":
        "لا توجد مراجعات مرسلة حتى الآن.",
    "Aucun créneau sélectionné":
        "لم يتم اختيار موعد",
    "Précisez votre délai et la configuration souhaitée.":
        "حدّد الإطار الزمني والتجهيز المطلوب.",
    "La capacité doit être au moins égale à 1.":
        "يجب أن تكون السعة 1 على الأقل.",
    "La date de fin doit être supérieure à la date de début.":
        "يجب أن يكون تاريخ الانتهاء بعد تاريخ البدء.",
    "Un client ne peut déposer qu'un seul avis par véhicule.":
        "يمكن للعميل إرسال مراجعة واحدة فقط لكل سيارة.",
    "Le BYD Atto 3 est l'un des SUV électriques les plus compétitifs de son segment.":
        "تعد BYD Atto 3 واحدة من أكثر سيارات SUV الكهربائية تنافسية في فئتها.",
    "BYD est un constructeur pionnier de la mobilité électrifiée avec une gamme complète de SUV, berlines et hybrides rechargeables.":
        "تعد BYD شركة رائدة في التنقل الكهربائي مع مجموعة متكاملة من سيارات SUV والسيدان والهجينة القابلة للشحن.",
    "MG combine une approche prix/prestations très compétitive avec des technologies modernes et une distribution européenne solide.":
        "تجمع MG بين قيمة تنافسية للغاية وتقنيات حديثة وشبكة توزيع أوروبية قوية.",
    "XPeng est une marque orientée software, reconnue pour ses plateformes 800V, ses temps de charge rapides et ses interfaces connectées.":
        "XPeng علامة تركز على البرمجيات، وتشتهر بمنصات 800 فولت والشحن السريع والواجهات المتصلة.",
    "NIO cible le segment premium avec un fort accent sur le confort, la sécurité et l'écosystème de services.":
        "تستهدف NIO الفئة الفاخرة مع تركيز قوي على الراحة والسلامة ومنظومة الخدمات.",
    "OMODA propose des SUV électriques modernes, connectés et bien équipés pour le marché urbain européen.":
        "تقدم OMODA سيارات SUV كهربائية حديثة ومتصلة ومجهزة جيدًا للسوق الحضري الأوروبي.",
    "Zeekr se positionne sur le premium technologique avec des performances élevées et une finition haut de gamme.":
        "تتمركز Zeekr في فئة السيارات التقنية الفاخرة بأداء عالٍ وتشطيبات راقية.",
    "Leapmotor apporte une alternative accessible dans le segment SUV électrique, avec des équipements complets et une autonomie solide.":
        "تقدم Leapmotor بديلًا ميسورًا في فئة SUV الكهربائية مع تجهيزات متكاملة ومدى قوي.",
    "SUV électrique familial avec autonomie solide et équipements de sécurité complets.":
        "سيارة SUV كهربائية عائلية بمدى قوي وتجهيزات سلامة متكاملة.",
    "Berline électrique premium orientée performance et efficience.":
        "سيدان كهربائية فاخرة تركز على الأداء والكفاءة.",
    "SUV hybride rechargeable pour les longs trajets avec consommation optimisée.":
        "سيارة SUV هجينة قابلة للشحن للرحلات الطويلة باستهلاك محسّن.",
    "Compacte électrique accessible avec un excellent rapport prix/autonomie.":
        "سيارة كهربائية مدمجة ميسورة مع نسبة ممتازة بين السعر والمدى.",
    "SUV compact électrique avec coffre généreux et équipement complet.":
        "سيارة SUV كهربائية مدمجة بصندوق واسع وتجهيزات متكاملة.",
    "SUV 800V ultra-rapide à la recharge avec architecture software avancée.":
        "سيارة SUV بمنصة 800 فولت وشحن فائق السرعة وبنية برمجية متقدمة.",
    "Berline électrique efficiente avec grande autonomie et interface IA.":
        "سيدان كهربائية فعالة بمدى طويل وواجهة ذكاء اصطناعي.",
    "SUV flagship avec excellent confort de roulage et charge ultra-rapide.":
        "سيارة SUV رائدة براحة قيادة ممتازة وشحن فائق السرعة.",
    "Touring premium électrique, performant et très confortable sur longue distance.":
        "سيارة تورينغ كهربائية فاخرة قوية ومريحة جدًا للمسافات الطويلة.",
    "SUV premium polyvalent, silencieux et très équipé pour la famille.":
        "سيارة SUV فاخرة متعددة الاستخدامات وهادئة ومجهزة جيدًا للعائلة.",
    "Crossover électrique au design marqué et aux technologies connectées.":
        "كروس أوفر كهربائية بتصميم مميز وتقنيات متصلة.",
    "Crossover premium compact avec transmission AWD et intérieur haut de gamme.":
        "كروس أوفر فاخرة مدمجة بدفع رباعي ومقصورة راقية.",
    "Shooting brake électrique performante, grand volume et finition premium.":
        "شوتينغ بريك كهربائية عالية الأداء بمساحة كبيرة وتشطيب فاخر.",
    "SUV électrique familial avec prix d'entrée agressif et équipements essentiels.":
        "سيارة SUV كهربائية عائلية بسعر دخول تنافسي وتجهيزات أساسية.",
    "Recharge DC rapide et architecture batterie Blade.":
        "شحن سريع بالتيار المستمر وبنية بطارية Blade.",
    "Habitacle spacieux et cockpit digital.":
        "مقصورة رحبة وقمرة قيادة رقمية.",
    "Pack ADAS complet pour les trajets urbains et autoroutiers.":
        "حزمة ADAS متكاملة للقيادة داخل المدن وعلى الطرق السريعة.",
    "Trouvez la voiture de vos rêves.":
        "اعثر على سيارة أحلامك.",
    "Le catalogue premium des voitures chinoises.":
        "الكتالوج المتميز للسيارات الصينية.",
    "Accéder aux voitures de demain":
        "قد سيارات الغد",
    "Une expertise tech au service de votre mobilité":
        "خبرة تقنية في خدمة تنقلك",
    "Marketplace automobile portée par EXOCOMS Group.":
        "سوق سيارات تديره مجموعة EXOCOMS.",
    "Filtrez par marque, motorisation, disponibilité, année et budget.":
        "صفِّ حسب العلامة التجارية ونظام الدفع والتوفر والسنة والميزانية.",
    "Spécifications détaillées en cours de publication.":
        "يتم نشر المواصفات التفصيلية.",
    "Demande d'essai envoyée":
        "تم إرسال طلب تجربة القيادة",
    "Demande de financement envoyée":
        "تم إرسال طلب التمويل",
    "Réservation envoyée":
        "تم إرسال الحجز",
    "Demande de financement":
        "طلب تمويل",
    "Demander un financement":
        "طلب تمويل",
    "Demander un devis":
        "طلب عرض سعر",
    "Demander un essai":
        "طلب تجربة قيادة",
    "Envoyer la demande d'essai":
        "إرسال طلب تجربة القيادة",
    "Envoyer la réservation":
        "إرسال الحجز",
    "Envoyer la demande":
        "إرسال الطلب",
    "Retour fiche véhicule":
        "العودة إلى تفاصيل السيارة",
    "Continuer le catalogue":
        "متابعة تصفح الكتالوج",
    "Choisir un créneau disponible":
        "اختر موعدًا متاحًا",
    "Ou demander une autre date/heure":
        "أو اطلب تاريخًا ووقتًا آخر",
    "Note complémentaire":
        "ملاحظة إضافية",
    "Mes demandes de financement":
        "طلبات التمويل الخاصة بي",
    "Mes réservations":
        "حجوزاتي",
    "Mes essais":
        "تجارب القيادة الخاصة بي",
    "Mes véhicules favoris":
        "سياراتي المفضلة",
    "Comparer les véhicules":
        "مقارنة السيارات",
    "Vider la comparaison":
        "مسح المقارنة",
    "Ouvrir le catalogue complet":
        "فتح الكتالوج الكامل",
    "Catalogue des véhicules":
        "كتالوج السيارات",
    "Modèles de la marque":
        "طرازات العلامة التجارية",
    "Modèles similaires":
        "طرازات مشابهة",
    "Modèles vedettes":
        "طرازات مميزة",
    "Toutes les marques":
        "جميع العلامات التجارية",
    "Marques partenaires":
        "العلامات التجارية الشريكة",
    "Disponibles immédiatement":
        "متاحة فورًا",
    "Véhicules publiés":
        "السيارات المنشورة",
    "Prix de départ":
        "السعر الابتدائي",
    "Prix croissant":
        "السعر من الأقل إلى الأعلى",
    "Prix décroissant":
        "السعر من الأعلى إلى الأقل",
    "Voir les meilleurs prix":
        "عرض أفضل الأسعار",
    "Voir ce modèle":
        "عرض هذا الطراز",
    "Voir les détails":
        "عرض التفاصيل",
    "Ouvrir la fiche":
        "فتح التفاصيل",
    "Ouvrir le catalogue":
        "فتح الكتالوج",
    "Accéder au catalogue":
        "تصفح الكتالوج",
    "Explorer le catalogue":
        "استكشف الكتالوج",
    "Explorer la catégorie":
        "استكشف الفئة",
    "Retour catalogue":
        "العودة إلى الكتالوج",
    "Retour accueil":
        "العودة إلى الرئيسية",
    "Tout voir":
        "عرض الكل",
    "Ajouter au comparateur":
        "أضف إلى المقارنة",
    "Ajouter au panier":
        "أضف إلى السلة",
    "Ajouter aux favoris":
        "أضف إلى المفضلة",
    "Retirer des favoris":
        "إزالة من المفضلة",
    "Planifier un essai":
        "حجز تجربة قيادة",
    "Réserver ce véhicule":
        "احجز هذه السيارة",
    "Laisser un avis":
        "اترك مراجعة",
    "Connectez-vous pour laisser un avis":
        "سجّل الدخول لترك مراجعة",
    "Envoyer pour modération":
        "إرسال للمراجعة",
    "Avis clients":
        "آراء العملاء",
    "Catalogue automobile premium":
        "كتالوج سيارات متميز",
    "EXOCOMS Mobilité":
        "EXOCOMS للتنقل",
    "Langues":
        "اللغات",
    "Liens utiles":
        "روابط مفيدة",
    "À propos":
        "من نحن",
    "Accueil":
        "الرئيسية",
    "Catalogue":
        "الكتالوج",
    "Comparateur":
        "مقارنة",
    "Marques":
        "العلامات التجارية",
    "Favoris":
        "المفضلة",
    "Réinitialiser":
        "إعادة تعيين",
    "Appliquer":
        "تطبيق",
    "Précédent":
        "السابق",
    "Suivant":
        "التالي",
    "Plus récents":
        "الأحدث",
    "Rechercher un modèle":
        "ابحث عن طراز",
    "Marque":
        "العلامة التجارية",
    "Catégorie":
        "الفئة",
    "Disponibilité":
        "التوفر",
    "Motorisation":
        "نظام الدفع",
    "Autonomie":
        "المدى",
    "Année modèle":
        "سنة الطراز",
    "Année min":
        "السنة الدنيا",
    "Année max":
        "السنة القصوى",
    "Prix min":
        "السعر الأدنى",
    "Prix max":
        "السعر الأقصى",
    "Prix":
        "السعر",
    "Puissance":
        "القدرة",
    "Batterie":
        "البطارية",
    "Caractéristique":
        "الخاصية",
    "Places":
        "المقاعد",
    "Section":
        "القسم",
    "Spécification":
        "المواصفة",
    "Spécifications":
        "المواصفات",
    "Valeur":
        "القيمة",
    "Options":
        "الخيارات",
    "Nom complet":
        "الاسم الكامل",
    "Nom":
        "الاسم",
    "Email":
        "البريد الإلكتروني",
    "Téléphone":
        "الهاتف",
    "Société":
        "الشركة",
    "Sujet":
        "الموضوع",
    "Message":
        "الرسالة",
    "Commentaire":
        "تعليق",
    "Comment":
        "تعليق",
    "Note":
        "التقييم",
    "Titre":
        "العنوان",
    "Title":
        "العنوان",
    "Statut":
        "الحالة",
    "Lieu":
        "الموقع",
    "Location":
        "الموقع",
    "Durée":
        "المدة",
    "Durée (mois)":
        "المدة (بالأشهر)",
    "Montant souhaité":
        "المبلغ المطلوب",
    "Revenu mensuel":
        "الدخل الشهري",
    "Apport initial":
        "الدفعة الأولى",
    "Budget":
        "الميزانية",
    "Canal préféré":
        "طريقة التواصل المفضلة",
    "Référence:":
        "المرجع:",
    "Reference":
        "المرجع",
    "Véhicule:":
        "السيارة:",
    "Véhicule":
        "السيارة",
    "Véhicules":
        "السيارات",
    "Vehicle":
        "السيارة",
    "Date/heure demandée":
        "التاريخ والوقت المطلوبان",
    "Année":
        "السنة",
    "Bientôt disponible":
        "متاحة قريبًا",
    "Disponible":
        "متاحة",
    "Réservé":
        "محجوزة",
    "Vendu":
        "مباعة",
    "Nouvelle":
        "جديدة",
    "Brouillon":
        "مسودة",
    "Confirmée":
        "مؤكدة",
    "Confirmé":
        "مؤكد",
    "Terminée":
        "مكتملة",
    "Terminé":
        "مكتمل",
    "Annulée":
        "ملغاة",
    "Annulé":
        "ملغى",
    "En étude":
        "قيد الدراسة",
    "Approuvée":
        "موافق عليها",
    "Rejetée":
        "مرفوضة",
    "En attente":
        "قيد الانتظار",
    "Approuvé":
        "موافق عليه",
    "Rejeté":
        "مرفوض",
    "Berline":
        "سيدان",
    "Compacte":
        "مدمجة",
    "Crossover":
        "كروس أوفر",
    "Electric":
        "كهربائية",
    "Plug-in Hybrid":
        "هجينة قابلة للشحن",
    "Fast Charging":
        "شحن سريع",
    "Panoramic Roof":
        "سقف بانورامي",
    "Heat Pump":
        "مضخة حرارية",
    "V2L External Power":
        "طاقة خارجية V2L",
    "360 Camera":
        "كاميرا 360 درجة",
    "Premium Audio":
        "نظام صوتي فاخر",
    "Sièges avant ventilés":
        "مقاعد أمامية مهواة",
    "Pearl White":
        "أبيض لؤلؤي",
    "Midnight Black":
        "أسود ليلي",
    "Glacier Blue":
        "أزرق جليدي",
    "Graphite Grey":
        "رمادي غرافيتي",
    "Emerald Green":
        "أخضر زمردي",
    "Trunk volume":
        "حجم الصندوق",
    "Length":
        "الطول",
    "Wheelbase":
        "قاعدة العجلات",
    "DC max charging":
        "أقصى قدرة شحن بالتيار المستمر",
    "Peak charging power":
        "قدرة الشحن القصوى",
    "Consumption WLTP":
        "استهلاك WLTP",
    "WLTP Consumption":
        "استهلاك WLTP",
    "Parking sensors":
        "حساسات ركن",
    "Front + Rear":
        "أمامية وخلفية",
    "Airbags":
        "وسائد هوائية",
    "Performance":
        "الأداء",
    "Énergie":
        "الطاقة",
    "Dimensions":
        "الأبعاد",
    "Sécurité":
        "السلامة",
    "Recharge":
        "الشحن",
    "Confort":
        "الراحة",
    "Multimédia":
        "الوسائط المتعددة",
    "Autre":
        "أخرى",
    "km d'autonomie":
        "كم من المدى",
    "modèles publiés":
        "طرازات منشورة",
    "à partir de":
        "ابتداءً من",
    "%s à %s":
        "%s عند %s",
    "Nouveau créneau":
        "موعد جديد",
    "Ouvrir les véhicules liés":
        "فتح السيارات المرتبطة",
    "Catégorie de véhicule":
        "فئة السيارة",
    "Catégories de véhicules":
        "فئات السيارات",
    "Motorisation de véhicule":
        "نظام دفع السيارة",
    "Options de véhicules":
        "خيارات السيارات",
    "Prix de vente":
        "سعر البيع",
    "Spécification du véhicule":
        "مواصفات السيارة",
    ": trouvez le modèle adapté":
        ": اعثر على الطراز المناسب",
    "Contacter EXOCOMS":
        "اتصل بـ EXOCOMS",
    "Image du véhicule indisponible":
        "صورة السيارة غير متاحة",
    "Image indisponible":
        "الصورة غير متاحة",
    "Sélection de véhicules":
        "مجموعة مختارة من السيارات",
    "Confirmation de demande d'essai":
        "تأكيد طلب تجربة القيادة",
    "Confirmation de réservation véhicule":
        "تأكيد حجز السيارة",
    "Demande d'essai reçue:":
        "تم استلام طلب تجربة القيادة:",
    "Demande de réservation reçue:":
        "تم استلام طلب الحجز:",
    "Demandes d'essai":
        "طلبات تجربة القيادة",
    "Essai de véhicule":
        "تجربة قيادة السيارة",
    "Essais":
        "تجارب القيادة",
    "Réservation de véhicule":
        "حجز السيارة",
    "Réservations":
        "الحجوزات",
    "Confirmation de demande de devis véhicule":
        "تأكيد طلب عرض سعر السيارة",
    "Demande de devis véhicule":
        "طلب عرض سعر سيارة",
    "Demande de devis:":
        "طلب عرض السعر:",
    "Demandes de devis":
        "طلبات عروض الأسعار",
    "Nous avons reçu votre demande de devis:":
        "لقد استلمنا طلب عرض السعر الخاص بك:",
    "Demandes de financement":
        "طلبات التمويل",
    "Demande de financement véhicule":
        "طلب تمويل سيارة",
    "Demande ID:":
        "معرف الطلب:",
    "Mes demandes":
        "طلباتي",
    "Montant":
        "المبلغ",
    "Mes avis":
        "مراجعاتي",
    "Preferred Contact":
        "طريقة التواصل المفضلة",
    "Bonjour ${object.partner_id.name},":
        "مرحبًا ${object.partner_id.name}،",
    "Votre demande d'essai a bien été reçue pour":
        "تم استلام طلب تجربة القيادة الخاص بك لـ",
    "Votre demande de réservation a bien été reçue pour":
        "تم استلام طلب الحجز الخاص بك لـ",
    "Date demandée:":
        "التاريخ المطلوب:",
    "Merci pour votre intérêt pour":
        "شكرًا لاهتمامك بـ",
    "La référence de votre demande de devis est":
        "مرجع طلب عرض السعر الخاص بك هو",
    "Notre équipe commerciale vous contactera rapidement.":
        "سيتواصل معك فريق المبيعات قريبًا.",
    "Cordialement,":
        "مع خالص التحية،",
    "L'équipe commerciale EXOCOMS Voitures":
        "فريق مبيعات سيارات EXOCOMS",
    "Très bien":
        "جيد جدًا",
    "Bien":
        "جيد",
    "Moyen":
        "متوسط",
    "Faible":
        "ضعيف",
    "Indicateur du carrousel":
        "مؤشر عرض الشرائح",
    "Le nom et l'email sont obligatoires.":
        "الاسم والبريد الإلكتروني مطلوبان.",
    "Sélectionnez un créneau ou indiquez une date souhaitée.":
        "اختر موعدًا أو أدخل التاريخ المطلوب.",
    "Showroom principal":
        "صالة العرض الرئيسية",
    "Aide à la conduite":
        "مساعدة السائق",
    "Chaque produit ne peut être lié qu'à un seul véhicule.":
        "يمكن ربط كل منتج بسيارة واحدة فقط.",
    "Couleur de véhicule":
        "لون السيارة",
    "Couleurs de véhicules":
        "ألوان السيارات",
    "Gestionnaire de contenu automobile":
        "مدير محتوى السيارات",
    "Image de galerie véhicule":
        "صورة معرض السيارة",
    "L'année du véhicule doit être comprise entre 1990 et l'année prochaine.":
        "يجب أن تكون سنة السيارة بين 1990 والسنة القادمة.",
    "Le nom de l'option doit être unique.":
        "يجب أن يكون اسم الخيار فريدًا.",
    "Le nom de la catégorie doit être unique.":
        "يجب أن يكون اسم الفئة فريدًا.",
    "Le nom de la couleur doit être unique.":
        "يجب أن يكون اسم اللون فريدًا.",
    "Le nom de la marque doit être unique.":
        "يجب أن يكون اسم العلامة التجارية فريدًا.",
    "Le nom de la motorisation doit être unique.":
        "يجب أن يكون اسم نظام الدفع فريدًا.",
    "Logo marque":
        "شعار العلامة التجارية",
    "Option du véhicule":
        "خيار السيارة",
    "Produit de vente lie au vehicule. S'il est vide, il est cree automatiquement a l'enregistrement.":
        "منتج البيع المرتبط بالسيارة. إذا كان فارغًا، فسيتم إنشاؤه تلقائيًا عند الحفظ.",
    "Publie sur le site":
        "منشور على الموقع",
    "Publié":
        "منشور",
    "Résumé":
        "الملخص",
    "Temps de charge":
        "وقت الشحن",
    "Conseiller assigné":
        "المستشار المعيّن",
    "Créneau de rendez-vous":
        "موعد متاح",
    "Créneaux de rendez-vous":
        "المواعيد المتاحة",
    "Mettre en étude":
        "وضع قيد الدراسة",
    "Avis":
        "المراجعات",
    "Avis client véhicule":
        "مراجعة عميل للسيارة",
    "Créer un bon de commande":
        "إنشاء أمر بيع",
    "Créer une opportunité CRM":
        "إنشاء فرصة في إدارة علاقات العملاء",
    "Devis envoyé":
        "تم إرسال عرض السعر",
    "Gagnée":
        "ناجحة",
    "Qualifiée":
        "مؤهلة",
    "État":
        "الحالة",
    "Contact":
        "اتصل بنا",
    "Envoyer":
        "إرسال",
    "Retirer":
        "إزالة",
    "Comparer":
        "مقارنة",
    "Status":
        "الحالة",
    "Price":
        "السعر",
    "Rating":
        "التقييم",
}


def translate(text, replacements):
    translated = text
    for source, target in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        translated = translated.replace(source, target)
    return translated


def write_po(module, locale, replacements):
    i18n_dir = ROOT / "custom_addons" / module / "i18n"
    pot_path = i18n_dir / f"{module}.pot"
    po_path = i18n_dir / f"{locale}.po"
    with pot_path.open(encoding="utf-8") as pot_file:
        catalog = pofile.read_po(pot_file, locale=locale)

    translated_count = 0
    for message in catalog:
        if not message.id:
            continue
        source = message.id if isinstance(message.id, str) else message.id[0]
        translated = translate(source, replacements)
        if translated != source:
            message.string = translated
            translated_count += 1

    catalog.locale = locale
    output = BytesIO()
    pofile.write_po(output, catalog, width=120, omit_header=False)
    po_path.write_bytes(output.getvalue().rstrip(b"\r\n") + b"\n")
    print(f"{module}: {locale}: {translated_count} translated terms")


def main():
    for module in MODULES:
        write_po(module, "en_GB", EN_REPLACEMENTS)
        write_po(module, "ar_001", AR_REPLACEMENTS)


if __name__ == "__main__":
    main()
