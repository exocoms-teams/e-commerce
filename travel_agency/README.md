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
│   ├── travel_reservation_views.xml  ← موجود
│   └── payment_provider_views.xml    ← الجديد هنا
└── payment/
    ├── __init__.py
    └── payment_provider.py
```