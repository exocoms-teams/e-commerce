{
    "name": "EXOCOMS - Titre des devis sans #",
    "version": "19.0.1.1.0",
    "category": "Sales/Sales",
    "summary": "Retire le # du titre des devis, commandes et factures pro forma imprimés, et des listes du portail",
    "author": "EXOCOMS",
    "website": "https://exocoms.fr",
    "license": "LGPL-3",
    "depends": ["sale"],
    "data": [
        "views/report_saleorder_document.xml",
        "views/portal_templates.xml",
    ],
    "installable": True,
    "application": False,
}
