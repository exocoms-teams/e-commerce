# -*- coding: utf-8 -*-
"""
product_spec_sheet/scripts/import_ingenico_desk5000.py
=======================================================
Script d'import des caractéristiques Ingenico Desk/5000 (gamme Tetra).

UTILISATION (depuis la racine Odoo) :
    odoo shell -d <base> -c /etc/odoo/odoo.conf \
        --no-http < addons/product_spec_sheet/scripts/import_ingenico_desk5000.py

OU depuis un shell interactif :
    exec(open('addons/product_spec_sheet/scripts/import_ingenico_desk5000.py').read())

Le script recherche vos fiches produit par référence interne (default_code)
et/ou par motif dans le nom, puis applique les caractéristiques via l'assistant
product.spec.import.wizard. Les catégories et attributs manquants sont créés
automatiquement (option create_missing=True).
"""

# ------------------------------------------------------------------
# 1. CRITÈRES DE RECHERCHE — à adapter à votre catalogue
# ------------------------------------------------------------------
# Renseignez les références internes exactes de vos fiches produit :
DEFAULT_CODES = [
    # "ING-DESK5000",
    # "ING-DESK5000-4G",
    # "ING-DESK5000-IP",
]

# Ou des motifs de recherche dans le nom (insensible à la casse) :
NAME_PATTERNS = [
    "Desk/5000",
    "Desk 5000",
]

# ------------------------------------------------------------------
# 2. CARACTÉRISTIQUES À APPLIQUER
# ------------------------------------------------------------------
SPEC_DATA = """
Connectivité ; Réseaux ; 4G, 3G, GPRS, WiFi, Bluetooth, Ethernet, double SIM en option
Connectivité ; Lecteur de carte ; Piste magnétique (ISO 1/2/3), carte à puce EMV niveau 1 (500 000 cycles), sans contact EMV L1 3.0
Connectivité ; Ports ; Ethernet, connexion PIN pad Desk/1600
Écran ; Taille ; 3,5 pouces couleur rétroéclairé
Écran ; Résolution ; 480 × 320 pixels (HVGA)
Système ; Système d'exploitation ; Telium TETRA
Système ; Processeur ; Cortex A5 avec coprocesseur de chiffrement dédié
Système ; Mémoire ; 512 Mo Flash, 512 Mo RAM — microSD jusqu'à 32 Go en option
Sécurité ; Certification ; Conforme PCI PTS en vigueur, lecteurs EMV niveau 1
Sécurité ; Modules de sécurité ; Jusqu'à 3 emplacements SAM, 2 SIM en option, verrou Kensington
"""

# ------------------------------------------------------------------
# 3. RECHERCHE DES PRODUITS
# ------------------------------------------------------------------
Product = env['product.template']

domain = []
if DEFAULT_CODES:
    domain.append(('default_code', 'in', DEFAULT_CODES))
for pattern in NAME_PATTERNS:
    domain.append(('name', 'ilike', pattern))

if not domain:
    raise ValueError("Renseignez DEFAULT_CODES et/ou NAME_PATTERNS.")

if len(domain) > 1:
    domain = ['|'] * (len(domain) - 1) + domain

products = Product.search(domain)
print("Produits trouvés : %d" % len(products))
for p in products:
    print("  [%s] %s" % (p.default_code or '-', p.name))

if not products:
    print("Aucun produit trouvé. Vérifiez DEFAULT_CODES / NAME_PATTERNS.")
else:
    # ------------------------------------------------------------------
    # 4. APPLICATION VIA L'ASSISTANT D'IMPORT
    # ------------------------------------------------------------------
    wizard = env['product.spec.import.wizard'].create({
        'product_tmpl_ids': [(6, 0, products.ids)],
        'data': SPEC_DATA,
        'create_missing': True,
        'update_existing': True,
    })
    result = wizard.action_import()
    print(result['params']['message'])
    env.cr.commit()
    print("Terminé et validé.")
