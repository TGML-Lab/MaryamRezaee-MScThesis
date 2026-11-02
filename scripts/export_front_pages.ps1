# ==============================================================================
# POWERSHELL WRAPPER: EXPORT FRONT PAGES (scripts/export_front_pages.ps1)
# ==============================================================================
#
# Convenient Windows PowerShell wrapper for `scripts/export_front_pages.py`.
# Generates standalone, single-page PDFs of frontmatter pages for printing or
# administrative submission (e.g., تصویب‌نامه and اظهارنامه).
#
# ------------------------------------------------------------------------------
# USAGE EXAMPLES:
# ------------------------------------------------------------------------------
# Export both signatures and declaration (default):
#     .\scripts\export_front_pages.ps1
#
# Export only the signatures page (تصویب‌نامه):
#     .\scripts\export_front_pages.ps1 signatures
#
# Export only the declaration page (اظهارنامه):
#     .\scripts\export_front_pages.ps1 declaration
#
# Extract pages directly from thesis.pdf instead of standalone compilation:
#     .\scripts\export_front_pages.ps1 -Target signatures -Extract
#
# Export directly to frontmatter/ directory for signed PDF substitution:
#     .\scripts\export_front_pages.ps1 -Frontmatter
# ==============================================================================

param (
    [string]$Target = "all",
    [switch]$Extract,
    [switch]$Frontmatter
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir "export_front_pages.py"

$argsList = @($pythonScript, $Target)
if ($Extract) {
    $argsList += "--extract"
}
if ($Frontmatter) {
    $argsList += "--frontmatter"
}

python @argsList
