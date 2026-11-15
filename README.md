# PlanMark V1.10 — PDF Page Organisation and Document Assembly

**Release status:** Engineering beta. Extends the actual V1.9 HTML application; does not replace the PDF canvas, annotation tools, Reference Board or local project file mechanism.

## Start

- Open `index.html` in Edge/Chrome. On mobile Safari/Chrome, hosting this folder over HTTPS is preferable to opening the file through iOS Files preview.
- Load a PDF, choose **Organise Pages** in the top application toolbar.
- Select pages using click, Ctrl/Cmd-click, Shift-click, the mobile **Multi** checkbox or **All**. Double-click a thumbnail to navigate. Use `⋯` for page actions; on desktop drag selected thumbnails to reorder.
- Choose an action and review options. Most edits commit to a **working copy** of the PDF and update the viewer and thumbnails. Use **Save PDF** inside Organise Pages to download a modified PDF. Save the **PlanMark .ereview.json project** to keep all editable markups, page IDs, reference metadata and Reference Board cards.

## Functionality added

- Insert blank ISO A0–A5, Letter/Legal, same-size or custom PDF pages. Portrait/landscape, 1–100 pages, white/ruled/grid/dot templates, insert before/after/start/end/position.
- Extract selected pages into one PDF, one PDF per page, or explicit groups. Source unchanged by default; optional removal. Native PlanMark annotation inclusion or exclusion, with extraction failure reported if unsupported.
- Split document every N pages, at starting page numbers, or by explicit complete page ranges. Multiple results bundled into a ZIP made in the browser. Source remains intact.
- Delete selected pages with confirmation, affected annotation/reference counts and Undo Pages; prevents zero-page PDFs.
- Reorder selected pages by drag/drop or position input, with stable page IDs and recalculated reference indexes.
- Duplicate pages with independent page IDs and PlanMark annotation IDs.
- Insert or replace PDF pages from a file or existing project PDF, preserving individual page dimensions and vector content. Existing annotations on replaced drawings are not silently transferred.
- Permanently rotate selected PDF pages by ±90° or 180°; PlanMark markup geometry and linked regions rotate in tandem.
- **Advanced** equal-grid Split Page into vector PDF regions; Crop Page adjusts PDF page boxes; Resize Page Box changes sheet size without scaling drawing content. See limitations.
- Modified-PDF export, ZIP export for multiple files, PDF-lib structural page-count validation, V1.10 editable project saving, older-project migration, stable page identities and missing-page warnings.
- Desktop and mobile organisation interface; page actions via context menu, touch button or long press; Light/Dark support.

## Data integrity

- `pageIds[]` is stored for each document. Existing annotation records stay with the physical page during insertion, reordering, duplication and deletion.
- References gain `targetPageId` / `sourcePageId` and are rebased when pages move. Deleted page targets become unavailable, **never redirected** to a new page at the same index.
- Each operation generates and structurally checks the output bytes **before** replacing the active document. Undo Pages/Redo Pages stores working PDF bytes plus annotation, calibration, page-ID and reference snapshots (up to 20 operations per session).
- The imported source PDF bytes remain separate from the modified working copy in the new project format. A full V1.10 `.ereview.json` can be large because it embeds working and original PDF data.
- PDF extraction and page organisation use PDF object copying instead of rasterising CAD sheets. The program does not silently convert vectors to bitmap pages.
- Digitally signed PDFs are blocked where detected. Unsupported encrypted PDFs cause clear failures. Documents with forms, bookmarks, layers or structural tagging show a warning: PDF-lib page reconstruction cannot reliably preserve every advanced object.

## Important limitations and known risks

1. **Actual third-party PDF compatibility is not independently verified for this release.** Browser UI, project round trips and page mapping were checked in Chromium. Page-writing regression tests used a *simulated* PDF-lib/PDF.js object model; a real PDF exported through the browser and reopened in PDF-XChange/Acrobat still needs verification. Never use an unverified output as the only copy of a controlled engineering document.
2. The app still needs compatible **PDF.js and PDF-lib** runtime scripts for full editing. It retains the V1.9/V1.71 on-demand library loading and read-only device preview fallback; an HTML attachment alone is not guaranteed to work offline on iOS. For self-hosted offline use, supply compatible local `vendor/` libraries following V1.9 instructions.
3. **Advanced Split Page:** equal rows/columns only; custom movable split lines and precise clipping of crossing annotations are not implemented. It warns when PlanMark annotations exist and outputs a multi-page PDF with vector page boxes. Inspect native PDF comments manually after splitting.
4. **Crop Page:** changes page boxes, not underlying secure content. It must never be used to redact confidential information. Existing drawing-specific links may need manual validation.
5. **Resize Page:** changes the page box without automatically scaling content or recomputing dimension calibration. The UI warns before proceeding with marked-up pages.
6. PDF-lib's `copyPages` can lose or alter bookmarks, AcroForm fields, tagged structure, layers and other advanced PDF data. The app warns and preserves original source bytes, but preservation is not guaranteed after opting in to rebuild.
7. Native annotation appearance/export is inherited from PlanMark V1.9; PDF-XChange/Acrobat compatibility of all annotation types is not certified. The editable PlanMark project remains authoritative for linked references and markup data.
8. Earlier markup-level Undo history is reset when a page operation commits to avoid mismatched page-index snapshots. Undoing the page operation restores its earlier markup history. Page-operation undo history is session-only and separate from reference Back/Forward navigation.
9. Generated split/extracted PDF documents in the project library are stored with their own page IDs. Their references to documents not present in the extracted PDF remain project-specific; standard PDF files cannot guarantee the interactive Reference Board.

## QA

- `qa_browser.py` runs Chromium desktop UI and *mock writer* tests for insertion, page reordering, reference rebasing, delete, Undo and Redo. It requires Python + Playwright **for developers/testers only**, not for application users.
- Manual test: open `CAD_A0_A3_Test.pdf`; insert two A3 landscape sheets after page 2; export; reopen the PDF externally and verify six total pages, vector linework, page sizes and correct annotations. Then test extraction, splitting, deletion, rotation and one V1.9 project restore.
- **Do not represent the mock test as a proof of real PDF binary interoperability.**

## Files

- `index.html`: complete browser HTML app.
- `page_organiser.js` and `.css`: readable additive V1.10 changes.
- `index_base_v19.html`: unchanged V1.9 baseline for diff/regression.
- `qa_browser.py`: browser QA tests.
- `CAD_A0_A3_Test.pdf`: mixed-size vector test drawing.
