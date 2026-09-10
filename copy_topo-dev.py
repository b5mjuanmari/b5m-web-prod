#!/usr/bin/env python3

import shutil
import sys
from pathlib import Path

dir1 = "TOPO-DEV"
dir2 = "topo"

source = Path("..") / dir1
destination = Path(".") / dir2

old_text = "r_oronimia_p-dev2"
new_text = "r_oronimia_p-dev-tmp"

try:
    # Direktorioa kopiatu
    shutil.rmtree(destination, ignore_errors=True)

    if not source.exists():
        print(f"Errorea: '{source}' direktorioa ez da existitzen.", file=sys.stderr)
        sys.exit(1)

    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(".git", "log")
    )

    # Kate-ordezkapena fitxategi guztietan
    for file_path in destination.rglob("*"):
        if file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8")
                new_content = content.replace(old_text, new_text)

                if new_content != content:
                    file_path.write_text(new_content, encoding="utf-8")
                    print(f"Aldatuta: {file_path}")

            except UnicodeDecodeError:
                # Fitxategi bitarrak (irudiak, zip-ak, etab.) saltatu
                pass

    sys.exit(0)

except Exception as e:
    print(f"Errorea: {e}", file=sys.stderr)
    sys.exit(1)
