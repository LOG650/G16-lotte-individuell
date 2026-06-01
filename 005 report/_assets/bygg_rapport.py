#!/usr/bin/env python3
"""Bygg rapport_LATEX.pdf og oppdater «Antall sider» / «Antall ord» på forsiden.

Dette er den kanoniske byggemåten for rapporten. Den teller ord (hele dokumentet
via pandoc -> ren tekst), bygger PDF for å lese sidetall, skriver begge tallene inn
i forsidekommandoene i _assets/latex_header.tex, og bygger på nytt så forsiden viser
de oppdaterte tallene. Kjør den hver gang rapporten endres.

Bruk (fra hvor som helst):  python "005 report/_assets/bygg_rapport.py"
"""
import os, re, sys, glob, shutil, subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))   # .../005 report/_assets
REPORT_DIR = os.path.dirname(SCRIPT_DIR)                   # .../005 report
os.chdir(REPORT_DIR)

REPORT = "rapport.md"
PDF = "LOG650_Rapport_Lotte_Picard.pdf"
HEADER = "_assets/latex_header.tex"

MIKTEX_BIN = os.path.expanduser(r"~\AppData\Local\Programs\MiKTeX\miktex\bin\x64")
if os.path.isdir(MIKTEX_BIN):
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + MIKTEX_BIN


def find_exe(name, fallback_globs):
    p = shutil.which(name)
    if p:
        return p
    for g in fallback_globs:
        hits = glob.glob(os.path.expanduser(g))
        if hits:
            return hits[0]
    sys.exit(f"Fant ikke {name}. Legg det på PATH og prøv igjen.")


PANDOC = find_exe("pandoc", [
    r"~\AppData\Local\Microsoft\WinGet\Packages\JohnMacFarlane.Pandoc_*\pandoc-*\pandoc.exe",
])
XELATEX = find_exe("xelatex", [os.path.join(MIKTEX_BIN, "xelatex.exe")])
MGS = find_exe("mgs", [os.path.join(MIKTEX_BIN, "mgs.exe")])

PANDOC_ARGS = [
    PANDOC, REPORT, "-o", PDF, "--pdf-engine=" + XELATEX,
    "-f", "markdown-implicit_figures",
    "--lua-filter=_assets/figurer_float.lua",
    "-V", "lang=nb-NO", "-V", "geometry:margin=2.5cm",
    "-V", "fontsize=11pt", "-V", "linestretch=1.4",
    "-V", "mainfont=Georgia", "-V", "monofont=Consolas",
    "-H", HEADER,
]


def count_words():
    """Antall ord i hele dokumentet (rå LaTeX-blokker som tittelsiden droppes av pandoc)."""
    out = subprocess.run([PANDOC, REPORT, "-t", "plain"],
                         capture_output=True, text=True, encoding="utf-8")
    return len(out.stdout.split())


def fmt_thousands(n):
    s = str(n)
    parts = []
    while len(s) > 3:
        parts.insert(0, s[-3:])
        s = s[:-3]
    parts.insert(0, s)
    return r"\,".join(parts)   # tynt mellomrom som tusenskille i LaTeX


def update_header(pages, words):
    with open(HEADER, encoding="utf-8") as f:
        txt = f.read()
    txt = re.sub(r"(\\newcommand\{\\antallsider\}\{)[^}]*\}",
                 lambda m: m.group(1) + str(pages) + "}", txt)
    txt = re.sub(r"(\\newcommand\{\\antallord\}\{)[^}]*\}",
                 lambda m: m.group(1) + fmt_thousands(words) + "}", txt)
    with open(HEADER, "w", encoding="utf-8") as f:
        f.write(txt)


def build():
    subprocess.run(PANDOC_ARGS, check=True)


def page_count():
    out = subprocess.run(
        [MGS, "-q", "-dNODISPLAY", "-dBATCH", "-c",
         f"({PDF}) (r) file runpdfbegin pdfpagecount == quit"],
        capture_output=True, text=True)
    return int(out.stdout.strip())


def main():
    words = count_words()
    build()                      # bygg én gang for å lese sidetall
    pages = page_count()
    update_header(pages, words)  # skriv inn tallene
    build()                      # bygg på nytt så forsiden er oppdatert
    p2 = page_count()
    if p2 != pages:              # sjeldent: tallene endret pagineringen
        update_header(p2, words)
        build()
        pages = p2
    print(f"Ferdig: {pages} sider, {words} ord  ->  {os.path.join(REPORT_DIR, PDF)}")


if __name__ == "__main__":
    main()
