Scripts d'import et de récupération de caractéristiques
========================================================


fetch_specs_shipping.py  — SCRIPT PRINCIPAL
--------------------------------------------
Récupère les specs complètes (poids, dimensions, caractéristiques techniques)
sur internet, puis calcule les frais de port par transporteur.

Dépendances :
    pip install requests beautifulsoup4 lxml
    pip install anthropic  # optionnel — améliore la précision d'extraction

Utilisation :
    # Un seul produit
    python3 fetch_specs_shipping.py --product "Ingenico Desk/5000"

    # Toute la liste EXOCOMS
    python3 fetch_specs_shipping.py --file produits_exocoms.txt --csv resultats.csv

    # Avec export Odoo (texte pour l'assistant d'import)
    python3 fetch_specs_shipping.py --file produits_exocoms.txt \
        --csv resultats.csv \
        --odoo-output odoo_import.txt

    # Avec l'API Anthropic pour une extraction plus précise
    python3 fetch_specs_shipping.py --file produits_exocoms.txt \
        --api-key sk-ant-xxx \
        --csv resultats.csv

Sorties :
    - Console : rapport poids/dimensions + tableau frais de port par transporteur
    - --csv    : fichier CSV avec toutes les specs et les tarifs par zone/transporteur
    - --odoo-output : texte à coller dans l'assistant d'import Odoo


apply_weight_dims_to_odoo.py  — MISE À JOUR ODOO
--------------------------------------------------
Lit le CSV généré par fetch_specs_shipping.py et met à jour dans Odoo :
  - product.template.weight (poids kg — champ standard)
  - product.template.volume (volume m³ — champ standard)
  - les lignes de caractéristiques Poids et Encombrement

Utilisation (depuis la racine Odoo) :
    # 1. Éditez CSV_PATH dans le script pour pointer vers votre fichier CSV
    # 2. Lancez :
    odoo shell -d <base> -c /etc/odoo/odoo.conf \
        --no-http < addons/product_spec_sheet/scripts/apply_weight_dims_to_odoo.py


import_ingenico_desk5000.py
----------------------------
Script Odoo Shell ciblé sur l'Ingenico Desk/5000.
Utilisation :
    odoo shell -d <base> -c /etc/odoo/odoo.conf \
        --no-http < addons/product_spec_sheet/scripts/import_ingenico_desk5000.py


import_ingenico_desk5000.txt
-----------------------------
Texte à coller directement dans Actions > Importer des caractéristiques.


produits_exocoms.txt
--------------------
Liste des produits du catalogue EXOCOMS, prête à passer dans fetch_specs_shipping.py.


WORKFLOW COMPLET
----------------
1. Lancer fetch_specs_shipping.py sur la liste produits → resultats.csv
2. Vérifier/corriger manuellement les valeurs dans le CSV si nécessaire
3. Lancer apply_weight_dims_to_odoo.py en DRY_RUN=True pour simuler
4. Relancer avec DRY_RUN=False pour appliquer
5. Les poids/dimensions sont maintenant dans Odoo :
   - dans product.template.weight / volume (calculs de port côté Odoo)
   - dans l'onglet Caractéristiques (fiche produit et site e-commerce)
