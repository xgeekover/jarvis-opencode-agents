---
name: pdf-table-clip-check
description: Detect tables that are cut off at the right or bottom page edge in DRM-protected PDFs that cannot be parsed directly. Renders each page to an image via the authorized reader, then flags wide-table horizontal clipping and writes a CSV report. Use when the user asks to check whether PDF tables are cut off / truncated (표 짤림 검사), especially for DRM-locked PDFs.
---

# PDF Table Clip Check (DRM-safe)

The PDF bytes are DRM-encrypted and cannot be opened by PyMuPDF/pdfplumber. Detection therefore works on PAGE IMAGES only: render each page to a PNG via the authorized reader, then analyze the page edges. A wide table clipped on the right edge is the primary target.

## Steps
1. Produce page images. Using this environment's authorized DRM reader/viewer, render EVERY page of each target PDF to a PNG under `./page_images/`, named `<doc>_p<page3>.png` (e.g., `reportA_p003.png`). Capture the PAGE AREA ONLY — no viewer chrome, window borders, or extra margins.
2. Ensure dependencies (only if missing): `pip install pillow numpy`.
3. Run the bundled analyzer: `python pdf_image_qa.py ./page_images`.
4. Report: summarize `pdf_qa_summary.csv` as a table; list FAIL documents, their page numbers, and the source PNG filenames. Emphasize 표짤림(가로) (right-edge / wide-table clipping) since that is the goal.

## Detection rules (applied automatically by the script)
- 표짤림(가로): content touches the right page edge with no margin, running >= 8% of the page height -> a wide table clipped on the right.
- 표짤림(세로): content touches the bottom edge across >= 8% of the width.
- 렌더이상: page is almost fully black or almost empty.
- Text overlap is NOT a problem. A full four-sided border/background is treated as a frame and excluded.

## Notes
- Every FAIL is a suspicion: open the referenced PNG to confirm.
- If DRM watermarks cause false positives, raise CLIP_RUN in pdf_image_qa.py from 0.08 to ~0.12.
- If PNGs are full-window screenshots (with borders), crop to the page area before saving, otherwise the image edge won't equal the page edge.
- Output CSVs are utf-8-sig (Excel-safe Korean).
