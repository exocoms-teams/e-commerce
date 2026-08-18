import os
import json
import time
from deep_translator import GoogleTranslator

module_dir = r"c:\Users\maram\e-commerce\oa_beauty_theme"
extracted_file = os.path.join(module_dir, "extracted_strings.json")

with open(extracted_file, "r", encoding="utf-8") as f:
    strings = json.load(f)

# Filter valid strings
strings = [s for s in strings if s.strip()]
print(f"Loaded {len(strings)} strings.")

en_translator = GoogleTranslator(source='fr', target='en')
ar_translator = GoogleTranslator(source='fr', target='ar')

en_translations = {}
ar_translations = {}

def translate_individual(strings, translator, target_dict):
    for s in strings:
        for _ in range(3):
            try:
                tgt = translator.translate(s)
                if tgt and '%s' in s:
                    tgt = tgt.replace(' % s', ' %s').replace('% s', '%s')
                target_dict[s] = tgt or s
                break
            except Exception as e:
                time.sleep(1)
        else:
            target_dict[s] = s

batch_size = 50
print("Translating in batches with fallback...", flush=True)
for i in range(0, len(strings), batch_size):
    batch = strings[i:i+batch_size]
    
    # EN
    try:
        en_batch = en_translator.translate_batch(batch)
        for src, tgt in zip(batch, en_batch):
            if tgt and '%s' in src:
                tgt = tgt.replace(' % s', ' %s').replace('% s', '%s')
            en_translations[src] = tgt or src
    except Exception as e:
        print(f"Batch EN failed, falling back to individual. Error: {e}", flush=True)
        translate_individual(batch, en_translator, en_translations)
            
    # AR
    try:
        ar_batch = ar_translator.translate_batch(batch)
        for src, tgt in zip(batch, ar_batch):
            if tgt and '%s' in src:
                tgt = tgt.replace(' % s', ' %s').replace('% s', '%s')
            ar_translations[src] = tgt or src
    except Exception as e:
        print(f"Batch AR failed, falling back to individual. Error: {e}", flush=True)
        translate_individual(batch, ar_translator, ar_translations)

    print(f"Processed up to {i+len(batch)} / {len(strings)}", flush=True)

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
