import os
import json
import urllib.request
import urllib.parse
import time

module_dir = r"c:\Users\maram\e-commerce\oa_beauty_theme"
extracted_file = os.path.join(module_dir, "extracted_blocks.json")

with open(extracted_file, "r", encoding="utf-8") as f:
    strings = json.load(f)

strings = [s for s in strings if s.strip()]
print(f"Loaded {len(strings)} strings.", flush=True)

def translate(text, target_lang):
    if not text.strip():
        return text
        
    url = "https://api.mymemory.translated.net/get?"
    params = {
        'q': text,
        'langpair': f"fr|{target_lang}",
        'de': 'test@example.com' # valid email increases limit
    }
    url += urllib.parse.urlencode(params)
    
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode('utf-8'))
                if res.get('responseStatus') == 200:
                    return res['responseData']['translatedText']
        except Exception as e:
            time.sleep(1)
    return text

en_translations = {}
ar_translations = {}

print("Translating...", flush=True)
for i, s in enumerate(strings):
    # Only translate strings that actually contain letters
    import re
    if re.search(r'[a-zA-ZÀ-ÿ]', s):
        en_translations[s] = translate(s, 'en')
        ar_translations[s] = translate(s, 'ar')
    else:
        en_translations[s] = s
        ar_translations[s] = s

    if (i+1) % 50 == 0:
        print(f"Processed {i+1} / {len(strings)}", flush=True)

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
            f.write(f'msgid "{src_escaped}"\n')
            f.write(f'msgstr "{tgt_escaped}"\n\n')

os.makedirs(os.path.join(module_dir, "i18n"), exist_ok=True)
write_po(os.path.join(module_dir, "i18n", "en.po"), "en", en_translations)
write_po(os.path.join(module_dir, "i18n", "ar.po"), "ar", ar_translations)

print("PO files created successfully!", flush=True)
