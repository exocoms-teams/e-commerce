import os
import json
import time
from deep_translator import GoogleTranslator

module_dir = r"c:\Users\maram\e-commerce\oa_beauty_theme"
extracted_file = os.path.join(module_dir, "extracted_strings.json")

with open(extracted_file, "r", encoding="utf-8") as f:
    strings = json.load(f)

strings = [s for s in strings if s.strip()]
print(f"Loaded {len(strings)} strings.", flush=True)

en_translator = GoogleTranslator(source='fr', target='en')
ar_translator = GoogleTranslator(source='fr', target='ar')

en_translations = {}
ar_translations = {}

def safe_translate(translator, s):
    for _ in range(2):
        try:
            return translator.translate(s)
        except Exception:
            try:
                # Fallback lowercased
                res = translator.translate(s.lower())
                return res.upper() if s.isupper() else res
            except Exception:
                time.sleep(1)
    return s

print("Translating...", flush=True)
for i, s in enumerate(strings):
    en_tgt = safe_translate(en_translator, s)
    ar_tgt = safe_translate(ar_translator, s)
    
    if en_tgt and '%s' in s: en_tgt = en_tgt.replace(' % s', ' %s').replace('% s', '%s')
    if ar_tgt and '%s' in s: ar_tgt = ar_tgt.replace(' % s', ' %s').replace('% s', '%s')
        
    en_translations[s] = en_tgt or s
    ar_translations[s] = ar_tgt or s

    if (i+1) % 50 == 0:
        print(f"Processed {i+1} / {len(strings)}", flush=True)

def write_po(filepath, lang_code, translations):
    header = f"""# Translation of Odoo Server.
# This file contains the translation of the following modules:
# 	* oa_beauty_theme
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 17.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2026-08-17 12:00+0000\\n"
"PO-Revision-Date: 2026-08-17 12:00+0000\\n"
"Language-Team: {lang_code.upper()}\\n"
"Language: {lang_code}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: \\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header)
        for src, tgt in translations.items():
            if not tgt:
                continue
            src_escaped = src.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            tgt_escaped = tgt.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            f.write(f'#. module: oa_beauty_theme\n')
            f.write(f'msgid "{src_escaped}"\n')
            f.write(f'msgstr "{tgt_escaped}"\n\n')

os.makedirs(os.path.join(module_dir, "i18n"), exist_ok=True)
write_po(os.path.join(module_dir, "i18n", "en.po"), "en", en_translations)
write_po(os.path.join(module_dir, "i18n", "ar.po"), "ar", ar_translations)

print("PO files created successfully!", flush=True)
