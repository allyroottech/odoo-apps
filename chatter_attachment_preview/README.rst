Chatter Attachment Preview
============================

Downloading a file just to glance at it and then dragging it back out of
your downloads folder is a small annoyance that happens dozens of times a
day in a busy chatter thread. This module removes that step. It adds a
Preview button to every chatter attachment, so a PDF, spreadsheet, image or
document opens right there in a dialog, and downloading stays an option
rather than the only way to look at a file.

What it does
------------

Hovering over any chatter attachment now shows an eye icon next to the
existing download and delete actions. Clicking it opens a dialog with the
file rendered inline: images and video and audio play directly, PDFs and
Office documents render as pages, spreadsheets show as a scrollable table,
archives show their file tree with entries you can click into individually,
and Markdown or source code renders in a readable viewer. Whatever the file
type turns out to be, a Download button is always available in the dialog
footer as a fallback.

File type is never guessed from the extension alone. The module looks at
the actual file content, magic bytes and mimetype, before deciding how to
render it, so a wrongly named file, or a format nobody thought to add to a
list, still gets handled sensibly instead of throwing an error. When a
format genuinely can't be previewed, or the optional software needed for
Office conversion isn't installed on the server, the dialog shows a clean
notice with a Download button instead of breaking.

Features
--------

- One click preview for chatter attachments, no download or new browser
  tab required.
- Images, video and audio play natively in the dialog.
- PDF, Word, PowerPoint, OpenDocument and RTF files render as pages.
- Excel, legacy XLS and CSV files display as a scrollable table.
- ZIP and TAR archives (including gzip, bzip2 and xz variants) show a
  browsable file tree, with entries previewed individually on click.
- Markdown renders as formatted text, and common source code and config
  files open in a readable code viewer.
- File type is detected from actual content, not filename, so unusual or
  mislabeled files still fall back gracefully to a download notice rather
  than an error.
- Works from the backend, the customer portal, and guest chatter access.

Installation
------------

1. Copy the ``chatter_attachment_preview`` folder into your addons path.
2. Update the apps list in Odoo and install **Chatter Attachment
   Preview**.
3. That's it, the Preview button appears automatically on every chatter
   attachment across the system.

Optional dependencies
----------------------

Office documents (DOCX, PPTX, ODT and similar) and legacy or modern
spreadsheets rely on optional software:

- ``openpyxl`` and ``xlrd`` for XLSX and XLS previews.
- LibreOffice, installed and available on the server, for converting
  Office documents to a previewable format.

None of these are required for the module to install or work. If they
aren't present, those specific file types simply show a download notice
until the software is added, everything else keeps working normally.

Usage
-----

1. Open any record with a chatter, and attach a file as usual, or open an
   existing attachment.
2. Hover the attachment and click the eye icon that appears next to it.
3. The file opens in a preview dialog. Close it, or use the Download
   button if you'd rather save a copy.

License
-------

This module is licensed under the GNU Lesser General Public License v3
(LGPL-3). See the header of each source file for the full notice.

Support
-------

AllyRoot Tech
allyroottech@gmail.com
