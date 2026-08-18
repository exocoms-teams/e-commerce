import os
import json
import time
from deep_translator import GoogleTranslator

module_dir = r"c:\Users\maram\e-commerce\oa_beauty_theme"
extracted_file = os.path.join(module_dir, "extracted_blocks.json")

with open(extracted_file, "r", encoding="utf-8") as f:
    strings = json.load(f)

# Filter
strings = [s for s in strings if s.strip()]
print(f"Loaded {len(strings)} strings.", flush=True)

en_translator = GoogleTranslator(source='fr', target='en')
ar_translator = GoogleTranslator(source='fr', target='ar')

en_translations = {}
ar_translations = {}

def safe_translate(translator, s):
    for _ in range(2):
        try:
            res = translator.translate(s)
            if res:
                return res
        except Exception:
            try:
                res = translator.translate(s.lower())
                if res:
                    return res.upper() if s.isupper() else res
            except Exception:
                pass
    return s

# Fast batching
batch_size = 40
for i in range(0, len(strings), batch_size):
    batch = strings[i:i+batch_size]
    
    # EN
    try:
        en_batch = en_translator.translate_batch(batch)
        for src, tgt in zip(batch, en_batch):
            en_translations[src] = tgt or src
    except Exception as e:
        for s in batch:
            en_translations[s] = safe_translate(en_translator, s)
            
    # AR
    try:
        ar_batch = ar_translator.translate_batch(batch)
        for src, tgt in zip(batch, ar_batch):
            ar_translations[src] = tgt or src
    except Exception as e:
        for s in batch:
            ar_translations[s] = safe_translate(ar_translator, s)

    print(f"Processed up to {i+len(batch)} / {len(strings)}", flush=True)

def write_po(filepath, lang_code, translations):
    header = f"""# Translation of Odoo Server.
# This file contains the translation of the following modules:
# 	* oa_beauty_theme
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 19.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2026-08-18 12:00+0000\\n"
"PO-Revision-Date: 2026-08-18 12:00+0000\\n"
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
            # Odoo multi-line msgid format correctly handled by basic escaping 
            # if we just don't split it. Odoo accepts single line msgid with \n inside!
            f.write(f'msgid "{src_escaped}"\n')
            f.write(f'msgstr "{tgt_escaped}"\n\n')

os.makedirs(os.path.join(module_dir, "i18n"), exist_ok=True)
write_po(os.path.join(module_dir, "i18n", "en.po"), "en", en_translations)
write_po(os.path.join(module_dir, "i18n", "ar.po"), "ar", ar_translations)

print("PO files created successfully!", flush=True)
