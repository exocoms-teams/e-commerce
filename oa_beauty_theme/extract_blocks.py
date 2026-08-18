import os
from bs4 import BeautifulSoup
import json
import re

module_dir = r"c:\Users\maram\e-commerce\oa_beauty_theme"
views_dir = os.path.join(module_dir, "views")
data_dir = os.path.join(module_dir, "data")
js_dir = os.path.join(module_dir, "static", "src", "js")

extracted = set()

# 1. JS Extraction
for root, _, files in os.walk(js_dir):
    for f in files:
        if f.endswith('.js'):
            with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                content = file.read()
                matches = re.findall(r'_t\(\s*[\'"](.*?)[\'"]\s*\)', content)
                for m in matches:
                    extracted.add(m)

# 2. XML Extraction using BeautifulSoup
def extract_xml_strings(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        
    soup = BeautifulSoup(content, 'xml')
    
    # Text nodes in XML that should be translated
    # Odoo extracts text from elements that have text.
    # It trims leading/trailing whitespace, and normalizes internal whitespace.
    
    for element in soup.find_all():
        # If the element has text directly inside it (not just inside children)
        # We can get its inner HTML.
        # But beautifulsoup doesn't easily give exact inner XML string matching original.
        pass

    # Alternative: use regex to find tags that commonly contain text
    # This is a heuristic but works for 99% of cases.
    tags_to_extract = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'button', 'li', 'span', 'strong', 'em', 'div', 'td', 'th', 'label']
    
    for tag in tags_to_extract:
        # Regex to find <tag ...>content</tag>
        pattern = r'<' + tag + r'[^>]*>(.*?)</' + tag + r'>'
        for match in re.finditer(pattern, content, re.DOTALL):
            inner_html = match.group(1)
            # Check if inner_html has actual text (letters/numbers)
            if re.search(r'[a-zA-ZÀ-ÿ]', inner_html):
                # Check if it doesn't contain block tags that would split it
                if not re.search(r'<(div|p|h[1-6]|ul|li|table)[^>]*>', inner_html, re.IGNORECASE):
                    # Clean up: Odoo normalizes whitespace
                    cleaned = re.sub(r'\s+', ' ', inner_html).strip()
                    if cleaned:
                        extracted.add(cleaned)

for root, _, files in os.walk(views_dir):
    for f in files:
        if f.endswith('.xml'):
            extract_xml_strings(os.path.join(root, f))
            
for root, _, files in os.walk(data_dir):
    for f in files:
        if f.endswith('.xml'):
            extract_xml_strings(os.path.join(root, f))

# Also extract from python files (fields.Char, translate=True)
# Odoo extracts the string value
extracted_list = sorted(list(extracted))
print(f"Extracted {len(extracted_list)} strings.")

with open(os.path.join(module_dir, "extracted_blocks.json"), "w", encoding="utf-8") as f:
    json.dump(extracted_list, f, indent=4, ensure_ascii=False)
