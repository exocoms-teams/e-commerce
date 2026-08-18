import os
import json
import urllib.request
import urllib.parse
import time
from concurrent.futures import ThreadPoolExecutor

module_dir = r"c:\Users\maram\e-commerce\oa_beauty_theme"
extracted_file = os.path.join(module_dir, "extracted_blocks.json")

with open(extracted_file, "r", encoding="utf-8") as f:
    strings = json.load(f)

strings = [s for s in strings if s.strip()]

def translate(text, target_lang):
    if not text.strip():
        return text
        
    url = "https://api.mymemory.translated.net/get?"
    params = {
        'q': text,
        'langpair': f"fr|{target_lang}",
        'de': 'test@example.com'
    }
    url += urllib.parse.urlencode(params)
    
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                res = json.loads(response.read().decode('utf-8'))
                if res.get('responseStatus') == 200:
                    return res['responseData']['translatedText']
        except Exception:
            time.sleep(0.5)
    return text

en_translations = {}
ar_translations = {}

# We have manual translations generated previously in generate_po.py
# Let's import them so we don't need to re-translate the homepage.
import sys
sys.path.append(module_dir)
try:
    from generate_po import translations as manual_dict
except Exception:
    manual_dict = {}

def process_string(s):
    # Check manual dict first
    if s in manual_dict:
        return (s, manual_dict[s].get('en', s), manual_dict[s].get('ar', s))
        
    # Translate
    import re
    if re.search(r'[a-zA-ZÀ-ÿ]{3,}', s):
        en = translate(s, 'en')
        ar = translate(s, 'ar')
        return (s, en, ar)
    else:
        return (s, s, s)

print(f"Translating {len(strings)} strings using threads...", flush=True)

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(process_string, strings))

for s, en, ar in results:
    en_translations[s] = en
    ar_translations[s] = ar

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
