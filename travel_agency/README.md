Travel Agency
=============

Module de gestion des offres de voyage, des reservations et des paiements.

Structure du module
-------------------

* ``models/`` : extension des produits et modele de reservation.
* ``payment/`` : configuration des prestataires de paiement.
* ``payment_module/`` : transactions de paiement liees aux reservations.
* ``views/`` : vues de reservation, produits et prestataires.
* ``report/`` : rapport de reservation.
* ``security/`` : droits d'acces du module.

<!-- Code Precedant
# travel_agency

## Structure du projet

```bash
travel_agency/
├── models/
│   ├── __init__.py
│   ├── product.py
│   └── reservation.py
├── security/
│   └── ir.model.access.csv
├── views/
│   ├── travel_product_views.xml
│   └── travel_reservation_views.xml
├── __init__.py
└── __manifest__.py
```


```bash
travel_agency/
├── views/
│   ├── travel_reservation_views.xml    
│   └── payment_provider_views.xml   
└── payment/
    ├── __init__.py
    └── payment_provider.py
```

```bash
travel_agency/
└── report/
    ├── __init__.py        
    └── reservation_report.xml
```    

``` bash
travel_agency/
└── payment_module/
    ├── __init__.py
    ├── models/
    │   ├── __init__.py
    │   └── payment_transaction.py
    └── views/
        └── payment_transaction_views.xml  
```         
 -->