import re

with open(r'c:\Users\maram\e-commerce\oa_beauty_theme\i18n\en.po', 'r', encoding='utf-8') as f:
    content = f.read()

entries = re.findall(r'msgid "(.*?)"\nmsgstr "(.*?)"', content)
untranslated = 0
translated = 0
untranslated_samples = []
for msgid, msgstr in entries:
    if msgid == '':
        continue
    if msgid == msgstr:
        untranslated += 1
        if len(untranslated_samples) < 10:
            untranslated_samples.append(msgid[:80])
    else:
        translated += 1
print(f'Translated: {translated}')
print(f'Untranslated (msgid==msgstr): {untranslated}')
print(f'Total: {translated + untranslated}')
print("\nSample untranslated:")
for s in untranslated_samples:
    print(f"  - {s}")
