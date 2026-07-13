# Image de fond du hero

Le CSS (`static/src/scss/s_bluespa_hero.scss`) attend un fichier à ce chemin exact :

```
bluespa_theme/static/src/img/hero_bg.jpg
```

Dépose ici la photo (spa/jacuzzi en terrasse, vue lac et montagnes) envoyée le
12/07/2026. Recommandations :
- format `.jpg`, ~1900×1200px ou plus, poids < 500 Ko (compresser si besoin,
  ex. squoosh.app) pour ne pas alourdir le chargement de la page d'accueil ;
- une fois le fichier ajouté, supprime ce README ou laisse-le, il n'est pas
  chargé par Odoo (pas référencé dans `__manifest__.py`).

Tant que le fichier n'existe pas, le bloc hero retombe automatiquement sur un
fond dégradé marine (`background-color` de secours dans le CSS) — rien n'est
cassé, juste moins joli.
