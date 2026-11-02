#!/usr/bin/env python3
"""Build the BRD and SRS HTML and PDF documents."""

from __future__ import annotations

import subprocess
from pathlib import Path

from weasyprint import HTML

ROOT = Path(__file__).resolve().parent

BRD_COVER = """
<div class="cover">
  <div class="kicker">Software blueprint · Phase 2</div>
  <h1>Business<br/>Requirements</h1>
  <div class="rule"></div>
  <div class="subtitle">Objectives, operating model and business requirements for the bounded
  general merchandise marketplace</div>
  <div class="working">Working name only — no Usiri affiliation is implied.</div>
  <div class="meta">
    <strong>Prepared for:</strong> the founding group<br/>
    <strong>Document:</strong> UM-BRD-001 &nbsp;·&nbsp; <strong>Version:</strong> 1.0<br/>
    <strong>Date:</strong> 30 October 2026<br/>
    <strong>Baseline:</strong> UM-DISC-001 v0.2 &nbsp;·&nbsp; UM-AMD-001 v1.0
  </div>
  <div class="status">
    <strong>DRAFT FOR APPROVAL.</strong> No implementation is authorized. Usiri is a potential
    logistics and brand partner, not a confirmed one. No API, rate card, franchise term or
    licence is assumed.
  </div>
  <div class="confidential">Confidential — for internal discussion</div>
</div>
"""

SRS_COVER = """
<div class="cover">
  <div class="kicker">Software blueprint · Phase 2</div>
  <h1>Software<br/>Requirements</h1>
  <div class="rule"></div>
  <div class="subtitle">Numbered, testable requirements, use cases and state models for the
  proposed Usiri Marketplace</div>
  <div class="working">Working name only — no Usiri affiliation is implied.</div>
  <div class="meta">
    <strong>Prepared for:</strong> founders, technical lead, design, security and test reviewers<br/>
    <strong>Document:</strong> UM-SRS-001 &nbsp;·&nbsp; <strong>Version:</strong> 1.0<br/>
    <strong>Date:</strong> 30 October 2026<br/>
    <strong>Baseline:</strong> UM-BRD-001 v1.0
  </div>
  <div class="status">
    <strong>DRAFT FOR REVIEW.</strong> No implementation is authorized. Requirements marked
    Must form the launch scope. Values marked TBC come from configuration, not code.
  </div>
  <div class="confidential">Confidential — for internal discussion</div>
</div>
"""

DOCS = [
    (
        "04_Business_Requirements_Document.md",
        "Business_Requirements_Document",
        "brd.css",
        "Usiri Marketplace — Business Requirements",
        BRD_COVER,
    ),
    (
        "05_Software_Requirements_Specification.md",
        "Software_Requirements_Specification",
        "srs.css",
        "Usiri Marketplace — Software Requirements",
        SRS_COVER,
    ),
]


def build(source: str, stem: str, css: str, title: str, cover: str) -> None:
    cmd = [
        "pandoc",
        source,
        "-f",
        "markdown",
        "-t",
        "html5",
        "--standalone",
        "--css",
        css,
        "--metadata",
        f"pagetitle={title}",
        "--toc",
        "--toc-depth=1",
        "--section-divs",
    ]
    html = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True).stdout
    html = html.replace("<body>", '<body class="doc">', 1)
    html = html.replace('<body class="doc">', '<body class="doc">\n' + cover, 1)
    html_path = ROOT / f"{stem}.html"
    html_path.write_text(html, encoding="utf-8")
    HTML(string=html, base_url=str(ROOT)).write_pdf(ROOT / f"{stem}.pdf")
    print("built", html_path.name, "and", f"{stem}.pdf")


def main() -> None:
    for doc in DOCS:
        build(*doc)


if __name__ == "__main__":
    main()
