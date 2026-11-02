#!/usr/bin/env python3
"""Build the decision outcome and scope amendment HTML and PDF."""

from __future__ import annotations

import subprocess
from pathlib import Path

from weasyprint import HTML

ROOT = Path(__file__).resolve().parent

COVER = """
<div class="cover">
  <div class="kicker">Software blueprint · Phase 1 · Amendment</div>
  <h1>Scope<br/>Amendment</h1>
  <div class="rule"></div>
  <div class="subtitle">Recorded founder decisions and the bounded general merchandise launch scope</div>
  <div class="working">Working name only — no Usiri affiliation is implied.</div>
  <div class="meta">
    <strong>Prepared for:</strong> the founding group<br/>
    <strong>Document:</strong> UM-AMD-001 &nbsp;·&nbsp; <strong>Version:</strong> 1.0<br/>
    <strong>Date:</strong> 30 October 2026<br/>
    <strong>Amends:</strong> UM-DISC-001 v0.2 &nbsp;·&nbsp; <strong>Log:</strong> UM-DEC-001 v0.2
  </div>
  <div class="status">
    <strong>DECISIONS RECORDED.</strong> D-01 to D-04 are closed. The launch scope is general
    merchandise, bounded to six departments in Dar es Salaam. No implementation is authorized.
    Usiri remains a potential logistics and brand partner, not a confirmed one.
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
        "amendment.css",
        "--metadata",
        "pagetitle=Usiri Marketplace — Scope Amendment",
        "--toc",
        "--toc-depth=1",
    ]
    html = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True).stdout
    html = html.replace("<body>", '<body class="doc">', 1)
    html = html.replace('<body class="doc">', '<body class="doc">\n' + COVER, 1)
    return html


def main() -> None:
    source = ROOT / "03_Decision_Outcome_and_Scope_Amendment.md"
    html = pandoc_to_html(source)
    html_path = ROOT / "Decision_Outcome_and_Scope_Amendment.html"
    html_path.write_text(html, encoding="utf-8")
    HTML(string=html, base_url=str(ROOT)).write_pdf(
        ROOT / "Decision_Outcome_and_Scope_Amendment.pdf"
    )
    print("built", html_path.name, "and Decision_Outcome_and_Scope_Amendment.pdf")


if __name__ == "__main__":
    main()
