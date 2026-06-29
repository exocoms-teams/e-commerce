# -*- coding: utf-8 -*-
"""Génère views/rejoindre_departements.xml (usage local uniquement)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))
from departements_fr import DEPARTEMENTS_FR  # noqa: E402

out = os.path.join(os.path.dirname(__file__), '..', 'views', 'rejoindre_departements.xml')
lines = [
    '<?xml version="1.0" encoding="utf-8"?>',
    '<odoo>',
    '<template id="rejoindre_departements_options" name="Rejoindre departements">',
]
for code, label in DEPARTEMENTS_FR:
    esc = label.replace('&', '&amp;').replace('<', '&lt;')
    lines.append(
        f'    <label class="mn-checkbox-item">'
        f'<input type="checkbox" name="departements" value="{code}"/>'
        f'<span>{esc}</span></label>'
    )
lines += ['</template>', '</odoo>']
with open(out, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'OK: {len(DEPARTEMENTS_FR)} departements -> {out}')
