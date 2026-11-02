#!/usr/bin/env python3
"""Build the concept pack HTML and PDFs from Markdown using pandoc + WeasyPrint."""

from __future__ import annotations

import subprocess
from pathlib import Path

from weasyprint import HTML

ROOT = Path(__file__).resolve().parent

COVER = """
<div class="cover">
  <div class="kicker">Project concept document</div>
  <h1>Usiri<br/>Marketplace</h1>
  <div class="rule"></div>
  <div class="subtitle">A proposed multi-vendor e-commerce and coordinated-delivery platform for Tanzania</div>
  <div class="working">Working name only — no Usiri affiliation is implied.</div>
  <div class="meta">
    <strong>Prepared for:</strong> the founding group<br/>
    <strong>Version:</strong> 1.0 &nbsp;·&nbsp; <strong>Date:</strong> 29 October 2026<br/>
    <strong>Author:</strong> project initiator
  </div>
  <div class="status">
    <strong>CONCEPT UNDER INVESTIGATION.</strong> This is not an approved project and not a Usiri project.
    No partnership, franchise, licence, funding or technical integration exists. All financial figures are
    planning assumptions, not quotations.
  </div>
  <div class="confidential">Confidential — for internal discussion</div>
</div>
"""


def pandoc_to_html(source: Path, *, toc: bool, body_class: str) -> str:
    cmd = [
        "pandoc",
        str(source),
        "-f",
        "markdown",
        "-t",
        "html5",
        "--standalone",
        "--css",
        "style.css",
        "--metadata",
        "pagetitle=Usiri Marketplace — Project Concept",
    ]
    if toc:
        cmd += ["--toc", "--toc-depth=1"]
    html = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True).stdout
    html = html.replace("<body>", f'<body class="{body_class}">', 1)
    return html


def build_main() -> None:
    html = pandoc_to_html(ROOT / "Usiri_Marketplace_Project_Concept.md", toc=True, body_class="doc")
    html = html.replace(
        '<li><a href="#usiri-marketplace" id="toc-usiri-marketplace">Usiri\nMarketplace</a></li>\n',
        "",
        1,
    )
    html = html.replace("<body class=\"doc\">", "<body class=\"doc\">\n" + COVER, 1)
    html_path = ROOT / "Concept_Pack.html"
    html_path.write_text(html, encoding="utf-8")
    HTML(string=html, base_url=str(ROOT)).write_pdf(ROOT / "Usiri_Marketplace_Project_Concept.pdf")
    print("built", html_path.name, "and PDF")


def build_single(source: str, output_pdf: str, body_class: str) -> None:
    html = pandoc_to_html(ROOT / source, toc=False, body_class=body_class)
    html_path = ROOT / output_pdf.replace(".pdf", ".html")
    html_path.write_text(html, encoding="utf-8")
    HTML(string=html, base_url=str(ROOT)).write_pdf(ROOT / output_pdf)
    print("built", html_path.name, "and", output_pdf)


if __name__ == "__main__":
    build_main()
    build_single("Executive_Summary_One_Page.md", "Executive_Summary_One_Page.pdf", "single")
    build_single("Group_Meeting_Pack.md", "Group_Meeting_Pack.pdf", "pack")
