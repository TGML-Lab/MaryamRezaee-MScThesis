# ==============================================================================
# LATEXMK AUTOMATED BUILD CONFIGURATION (latexmkrc)
# ==============================================================================
#
# This file configures `latexmk` for one-click compilation of the thesis.
# It sets XeLaTeX as the primary engine, links BibTeX, ensures PDF 1.7
# vector compatibility, and triggers the automated dictionary generator hook.
#
# ------------------------------------------------------------------------------
# HOW TO COMPILE:
# ------------------------------------------------------------------------------
# Terminal:
#     latexmk -xelatex -synctex=1 -interaction=nonstopmode thesis.tex
#
# Clean build artifacts:
#     latexmk -c thesis.tex   (cleans auxiliary files)
#     latexmk -C thesis.tex   (cleans auxiliary files + output PDF)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Pre-Compilation Hook: Automated Dictionary & Glossary Generation
# ------------------------------------------------------------------------------
# Regenerates sorted, alphabetically grouped dictionaries from backmatter/words.tex
# if Python is available in the system PATH.
# Pre-compiled fallback files exist in backmatter/, so compilation succeeds even
# on machines without Python.
if (-e "scripts/build_dictionaries.py") {
    my $py = ($^O eq 'MSWin32') ? 'python' : 'python3';
    eval {
        my $status = system("$py scripts/build_dictionaries.py");
        if ($status != 0 && $^O ne 'MSWin32') {
            # On some Linux / macOS systems, the binary name is 'python' instead of 'python3'
            system("python scripts/build_dictionaries.py");
        }
    };
}

# ------------------------------------------------------------------------------
# 2. Compilation Engine & Flags
# ------------------------------------------------------------------------------
$pdf_mode = 5; # 5 = XeLaTeX mode
$xelatex = 'xelatex -synctex=1 -interaction=nonstopmode %O %S';
$xdvipdfmx = 'xdvipdfmx -E -V 7 -o %D %O %S'; # Target PDF 1.7 to prevent version warnings
$bibtex = 'bibtex %O %B';
