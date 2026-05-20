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