#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# STANDALONE FRONT PAGES EXPORTER (scripts/export_front_pages.py)
# ==============================================================================
# Author: Maryam Rezaee / SUT Thesis Template
#
# This script generates standalone, single-page PDFs of frontmatter pages
# (e.g., signatures / تصویب‌نامه and declaration / اظهارنامه).
#
# ------------------------------------------------------------------------------
# USAGE & TARGETS:
# ------------------------------------------------------------------------------
# Usage:
#     python scripts/export_front_pages.py [target] [--extract]
#
# Targets:
#     signatures  (aliases: sig, tasvib)    -> outputs signatures.pdf
#     declaration (aliases: decl, ezhar)   -> outputs declaration.pdf
#     besmellah   (aliases: bismillah)     -> outputs besmellah.pdf
#     title                                -> outputs title.pdf
#     title_en                             -> outputs title_en.pdf
#     all         (default)                -> outputs signatures.pdf & declaration.pdf
#
# Options:
#     --extract   Extract the page from thesis.pdf instead of compiling standalone.
# ==============================================================================

import sys
import os
import argparse
import subprocess
import tempfile
import shutil

# Ensure stdout handles UTF-8 characters cleanly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PAGE_CONFIGS = {
    "signatures": {
        "file": "frontmatter/signatures.tex",
        "output": "signatures.pdf",
        "title": "Signatures Page (صفحه تصویب‌نامه)",
        "keywords": ["تصویب", "کمیته ممتحنین", "استاد راهنما"]
    },
    "declaration": {
        "file": "frontmatter/declaration.tex",
        "output": "declaration.pdf",
        "title": "Declaration Page (صفحه اظهارنامه)",
        "keywords": ["اظهارنامه", "اظهار", "اصالت متن"]
    },
    "besmellah": {
        "file": "frontmatter/besmellah.tex",
        "output": "besmellah.pdf",
        "title": "Besmellah Page (صفحه بسم الله)",
        "keywords": []
    },
    "title": {
        "file": "frontmatter/title.tex",
        "output": "title.pdf",
        "title": "Persian Title Page (صفحه عنوان فارسی)",
        "keywords": ["دانشگاه صنعتی شریف", "پایان‌نامه"]
    },
    "title_en": {
        "file": "backmatter/title_en.tex",
        "output": "title_en.pdf",
        "title": "English Title Page (صفحه عنوان انگلیسی)",
        "keywords": ["Sharif University of Technology", "Thesis"]
    }
}

ALIASES = {
    "sig": "signatures",
    "tasvib": "signatures",
    "decl": "declaration",
    "ezhar": "declaration",
    "bismillah": "besmellah",
    "en_title": "title_en",
    "english_title": "title_en"
}

def compile_standalone(target_key, config, workspace_dir, dest_dir=None):
    """Compiles a standalone single-page PDF directly using XeLaTeX in a temporary sandbox."""
    tex_source = config["file"]
    output_pdf_name = config["output"]
    target_dir = dest_dir if dest_dir else workspace_dir
    os.makedirs(target_dir, exist_ok=True)
    output_path = os.path.join(target_dir, output_pdf_name)

    print(f"[*] Compiling standalone: {config['title']} -> {output_pdf_name}")

    wrapper_tex = f"""\\documentclass[oneside,a4paper,12pt]{{book}}
\\input{{styles/common.tex}}
\\input{{styles/custom.tex}}
\\input{{frontmatter/info.tex}}
\\begin{{document}}
\\pagestyle{{empty}}
\\input{{{tex_source.replace('\\\\', '/')}}}
\\end{{document}}
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_tex_path = os.path.join(tmpdir, "wrapper.tex")
        with open(temp_tex_path, "w", encoding="utf-8") as f:
            f.write(wrapper_tex)

        cmd = [
            "xelatex",
            "-interaction=nonstopmode",
            f"-output-directory={tmpdir}",
            f"-jobname={os.path.splitext(output_pdf_name)[0]}",
            temp_tex_path
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=workspace_dir)
        temp_pdf = os.path.join(tmpdir, output_pdf_name)

        if proc.returncode == 0 and os.path.exists(temp_pdf):
            shutil.copy2(temp_pdf, output_path)
            print(f"[+] Successfully generated: {output_path} (1 page)")
            return True
        else:
            print(f"[!] Compilation failed for {target_key}:")
            # Print last few lines of log
            log_file = os.path.join(tmpdir, f"{os.path.splitext(output_pdf_name)[0]}.log")
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8", errors="ignore") as lf:
                    lines = lf.readlines()
                    print("".join(lines[-25:]))
            else:
                print(proc.stdout[-500:])
            return False

def extract_from_thesis(target_key, config, workspace_dir, dest_dir=None):
    """Extracts the page from an existing thesis.pdf using PyMuPDF."""
    thesis_pdf = os.path.join(workspace_dir, "thesis.pdf")
    output_pdf_name = config["output"]
    target_dir = dest_dir if dest_dir else workspace_dir
    os.makedirs(target_dir, exist_ok=True)
    output_path = os.path.join(target_dir, output_pdf_name)

    if not os.path.exists(thesis_pdf):
        print("[!] thesis.pdf not found. Falling back to standalone compilation.")
        return compile_standalone(target_key, config, workspace_dir, dest_dir=dest_dir)

    try:
        import fitz
    except ImportError:
        print("[!] PyMuPDF (fitz) not installed. Falling back to standalone compilation.")
        return compile_standalone(target_key, config, workspace_dir, dest_dir=dest_dir)

    print("[*] Searching thesis.pdf for {config['title']}...")
    doc = fitz.open(thesis_pdf)
    matched_page_idx = None

    import unicodedata

    # Search for characteristic keywords
    keywords = [unicodedata.normalize("NFKD", kw) for kw in config.get("keywords", [])]
    if keywords:
        for idx, page in enumerate(doc):
            text = unicodedata.normalize("NFKD", page.get_text())
            if any(kw in text for kw in keywords):
                matched_page_idx = idx
                break
    elif target_key == "besmellah":
        # Besmellah has no text, usually page 2 (index 1) with an image
        for idx in range(min(5, len(doc))):
            page = doc[idx]
            if len(page.get_images()) > 0 and len(page.get_text().strip()) == 0:
                matched_page_idx = idx
                break

    if matched_page_idx is not None:
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=matched_page_idx, to_page=matched_page_idx)
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        print(f"[+] Extracted page {matched_page_idx + 1} from thesis.pdf -> {output_path}")
        return True
    else:
        print("[-] Page not found in thesis.pdf (maybe commented out?). Compiling standalone...")
        doc.close()
        return compile_standalone(target_key, config, workspace_dir)

def main():
    parser = argparse.ArgumentParser(description="Export standalone frontmatter PDFs.")
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        help="Target to generate: signatures, declaration, besmellah, title, title_en, or all (default: all)"
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Extract from thesis.pdf rather than compiling standalone."
    )
    parser.add_argument(
        "--frontmatter",
        action="store_true",
        help="Output directly into frontmatter/ directory for signed PDF substitution."
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Custom destination directory for output PDFs."
    )

    args = parser.parse_args()
    target_raw = args.target.lower().strip()
    target = ALIASES.get(target_raw, target_raw)

    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    dest_dir = os.path.join(workspace_dir, "frontmatter") if args.frontmatter else (
        os.path.abspath(args.out_dir) if args.out_dir else workspace_dir
    )

    if target in ("all", "forms"):
        targets = ["signatures", "declaration"]
    elif target in PAGE_CONFIGS:
        targets = [target]
    else:
        print(f"[!] Unknown target: '{target_raw}'. Available options: {list(PAGE_CONFIGS.keys())} or 'all'")
        sys.exit(1)

    success_count = 0
    for t in targets:
        cfg = PAGE_CONFIGS[t]
        if args.extract:
            ok = extract_from_thesis(t, cfg, workspace_dir, dest_dir=dest_dir)
        else:
            ok = compile_standalone(t, cfg, workspace_dir, dest_dir=dest_dir)
        if ok:
            success_count += 1

    print(f"\n[✓] Done! Generated {success_count}/{len(targets)} requested standalone PDF(s).")

if __name__ == "__main__":
    main()
