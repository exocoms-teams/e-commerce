{
    "name": "Auto Booking",
    "version": "1.0.0",
    "summary": "Vehicle reservations and test-drive workflow",
    "category": "Website",
    "author": "Ecommerce Voitures Team",
    "license": "LGPL-3",
    "depends": ["website", "portal", "mail", "auto_base"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/sequence.xml",
        "data/mail_templates.xml",
        "views/auto_booking_views.xml",
        "views/auto_booking_templates.xml"
    ],
    "application": False,
    "installable": True
}
