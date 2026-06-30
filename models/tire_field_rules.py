# TIRE_FIELD_RULES_MATRIX définit l'applicabilité des champs par catégorie de pneus.
#
# Si un champ pneu est OBLIGATOIRE qu'importe sa catégorie:
#   "tire_fieldname": {"hidden": ()},
# Sinon il ne sera pas vérifié lors de write/create.


TIRE_FIELD_RULES_MATRIX = {
    "tire_brand": {"hidden": ()},
    "tire_model": {"hidden": ()},
    "tire_season": {"visible": ("car_suv", "4x4_offroad")},
    "tire_usage_id": {"hidden": ()},
    "tire_tread_pattern_id": {"hidden": ()},
    "tire_width": {"hidden": ()},
    "tire_height": {"hidden": ()},
    "tire_construction": {"hidden": ()},
    "tire_rim": {"hidden": ()},
    "tire_load_index": {"hidden": ()},
    "tire_speed_index": {"hidden": ("agricultural",)},
    "tire_extra_load": {
        "hidden": (
            "motorcycle",
            "scooter",
            "quad",
            "buggy",
            "light_truck",
            "truck",
            "agricultural",
        )
    },
    "tire_runflat": {
        "hidden": (
            "motorcycle",
            "scooter",
            "quad",
            "buggy",
            "truck",
            "agricultural",
        )
    },
    "tire_seal": {
        "hidden": (
            "motorcycle",
            "scooter",
            "quad",
            "buggy",
            "truck",
            "agricultural",
        )
    },
    "tire_snow_homologation": {
        "hidden": (
            "motorcycle",
            "agricultural",
            "quad",
            "buggy",
        )
    },
    "tire_new_or_retreaded": {
        "hidden": (
            "motorcycle",
            "scooter",
            "quad",
            "buggy",
        )
    },
    "tire_sidewall_lettering": {"hidden": ("agricultural",)},
    "tire_eprel": {
        "visible": (
            "car_suv",
            "4x4_offroad",
            "light_truck",
            "truck",
            "camping_car",
        )
    },
    "tire_label_image": {
        "visible": (
            "car_suv",
            "4x4_offroad",
            "light_truck",
            "truck",
            "camping_car",
        )
    },
    "tire_fuel_efficiency": {
        "visible": (
            "car_suv",
            "4x4_offroad",
            "light_truck",
            "truck",
            "camping_car",
        )
    },
    "tire_wet_grip": {
        "visible": (
            "car_suv",
            "4x4_offroad",
            "light_truck",
            "truck",
            "camping_car",
        )
    },
    "tire_noise_db": {
        "visible": (
            "car_suv",
            "4x4_offroad",
            "light_truck",
            "truck",
            "camping_car",
        )
    },
}
