#!/usr/bin/env python3
"""Build the requirements discovery report HTML and PDF."""

from __future__ import annotations

import subprocess
from pathlib import Path

from weasyprint import HTML

ROOT = Path(__file__).resolve().parent

COVER = """
<div class="cover">
  <div class="kicker">Software blueprint · Phase 1</div>
  <h1>Requirements<br/>Discovery</h1>
  <div class="rule"></div>
  <div class="subtitle">Business, system and access baseline for the proposed Usiri Marketplace</div>
  <div class="working">Working name only — no Usiri affiliation is implied.</div>
  <div class="meta">
    <strong>Prepared for:</strong> the founding group<br/>
    <strong>Document:</strong> UM-DISC-001 &nbsp;·&nbsp; <strong>Version:</strong> 0.2<br/>
    <strong>Date:</strong> 30 October 2026<br/>
    <strong>Author:</strong> project initiator
  </div>
  <div class="status">
    <strong>DISCOVERY ONLY.</strong> No implementation is authorized. Usiri is a potential
    logistics and brand partner, not a confirmed one. No API, rate card, franchise term,
    supplier commitment or funding commitment is assumed.
  </div>
  <div class="confidential">Confidential — for internal discussion</div>
</div>
"""


def pandoc_to_html(source: Path) -> str:
    cmd = [
        "pandoc",
        str(source),
        "-f",
        "markdown",
        "-t",
        "html5",
        "--standalone",
        "--css",
        "report.css",
        "--metadata",
        "pagetitle=Usiri Marketplace — Requirements Discovery",
        "--toc",
        "--toc-depth=1",
    ]
    html = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True).stdout
    html = html.replace("<body>", '<body class="doc">', 1)
    html = html.replace('<body class="doc">', '<body class="doc">\n' + COVER, 1)
    return html


def main() -> None:
    source = ROOT / "00_Requirements_Discovery_Report.md"
    html = pandoc_to_html(source)
    html_path = ROOT / "Requirements_Discovery_Report.html"
    html_path.write_text(html, encoding="utf-8")
    HTML(string=html, base_url=str(ROOT)).write_pdf(ROOT / "Requirements_Discovery_Report.pdf")
    print("built", html_path.name, "and Requirements_Discovery_Report.pdf")


if __name__ == "__main__":
    main()
