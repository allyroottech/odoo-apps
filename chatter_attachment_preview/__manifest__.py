# -*- coding: utf-8 -*-
################################################################################
#
#    AllyRoot Tech
#
#    Copyright (C) 2026-TODAY AllyRoot Tech (allyroottech@gmail.com).
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

{
    "name": "Chatter Attachment Preview",
    "summary": "Preview chatter attachments instantly without downloading.",
    "description": """
Chatter Attachment Preview
===========================
Adds a Preview (eye) button to every chatter attachment so users can look at a file
without downloading it first. The file type is detected dynamically (magic bytes,
mimetype, content heuristics — never a hardcoded extension list), so new or unusual
formats fall back gracefully to a clean "Download" card instead of an error.

Office documents (.docx, .pptx, .odt, ...) and legacy/modern spreadsheets
(.xls, .xlsx) render through optional local software (LibreOffice, openpyxl, xlrd).
If that software isn't installed, the module still installs and runs fine — those
specific formats simply show a download notice until it is added.
""",
    "version": "19.0.1.1.0",
    "category": "Productivity",
    "author": "AllyRoot Tech",
    "support": "allyroottech@gmail.com",
    "license": "LGPL-3",
    "depends": ["mail", "web"],
    "data": [
        "views/attachment_preview_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "chatter_attachment_preview/static/src/attachment_preview/*",
            "chatter_attachment_preview/static/src/attachment_list/*",
        ],
    },
    "images": [
        "static/description/banner.png",
    ],
    "installable": True,
    "application": False,
}
