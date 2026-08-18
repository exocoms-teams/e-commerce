import re
import json

with open(r'c:\Users\maram\e-commerce\oa_beauty_theme\i18n\en.po', 'r', encoding='utf-8') as f:
    content = f.read()

entries = re.findall(r'msgid "(.*?)"\nmsgstr "(.*?)"', content)
untranslated = []
for msgid, msgstr in entries:
    if msgid == '':
        continue
    if msgid == msgstr:
        untranslated.append(msgid)

with open(r'c:\Users\maram\e-commerce\oa_beauty_theme\untranslated.json', 'w', encoding='utf-8') as f:
    json.dump(untranslated, f, indent=2, ensure_ascii=False)

print(f"Exported {len(untranslated)} untranslated strings")
