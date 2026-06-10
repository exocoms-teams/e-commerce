#!/usr/bin/env python3
"""Package the Chrome extension as a zip for download."""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTENSION_DIR = os.path.join(ROOT, 'extension')
OUTPUT = os.path.join(ROOT, 'website', 'tracker-extension.zip')


def main():
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zf:
        for dirpath, _, filenames in os.walk(EXTENSION_DIR):
            for name in filenames:
                if name == '.DS_Store':
                    continue
                path = os.path.join(dirpath, name)
                arcname = os.path.relpath(path, EXTENSION_DIR)
                zf.write(path, arcname)
    print(f'Created {OUTPUT} ({os.path.getsize(OUTPUT)} bytes)')


if __name__ == '__main__':
    main()
