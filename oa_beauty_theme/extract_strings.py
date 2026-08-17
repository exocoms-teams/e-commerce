import os
import re
import xml.etree.ElementTree as ET
import json

module_dir = r"c:\Users\maram\e-commerce\oa_beauty_theme"
strings = set()

# 1. Parse XML Views (Static text)
views_dir = os.path.join(module_dir, "views")
for filename in os.listdir(views_dir):
    if filename.endswith(".xml"):
        filepath = os.path.join(views_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)
            content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL)
            for match in re.findall(r'>([^<]+)<', content):
                text = match.strip()
                if re.search(r'[a-zA-ZÀ-ÿ]', text) and not text.startswith(('{{', '{#', 't-esc')):
                    strings.add(text)

# 2. Parse JS files
js_dir = os.path.join(module_dir, "static", "src", "js")
if os.path.exists(js_dir):
    for filename in os.listdir(js_dir):
        if filename.endswith(".js"):
            with open(os.path.join(js_dir, filename), "r", encoding="utf-8") as f:
                content = f.read()
                for match in re.findall(r"_t\(\s*['\"](.*?)['\"]\s*\)", content):
                    strings.add(match)

# 3. Parse Data files
data_dir = os.path.join(module_dir, "data")
translatable_fields = {
    'name', 'description', 'description_sale', 'oa_benefits', 'oa_how_to_use', 
    'oa_key_ingredients', 'oa_type', 'oa_finish', 'oa_best_for', 'oa_skin_type', 
    'oa_concern', 'oa_routine_step', 'oa_fragrance_family', 'oa_occasion', 
    'oa_fragrance_top_notes', 'oa_fragrance_heart_notes', 'oa_fragrance_base_notes', 
    'oa_mood', 'oa_seo_keywords'
}
if os.path.exists(data_dir):
    for filename in os.listdir(data_dir):
        if filename.endswith(".xml"):
            filepath = os.path.join(data_dir, filename)
            try:
                tree = ET.parse(filepath)
                for field in tree.iter("field"):
                    if field.get("name") in translatable_fields:
                        if field.text and re.search(r'[a-zA-ZÀ-ÿ]', field.text):
                            strings.add(field.text.strip())
            except Exception as e:
                pass

output_path = os.path.join(module_dir, "extracted_strings.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(list(strings), f, indent=2, ensure_ascii=False)

print(f"Extracted {len(strings)} unique strings.")
