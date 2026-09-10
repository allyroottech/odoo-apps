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
    'name': 'Partner Duplicate Warning',
    'version': '19.0.1.0.0',
    'category': 'Contacts',
    'summary': 'Warn about contacts sharing the same email or phone number',
    'description': """
        Flags a Contact as a potential duplicate when another contact already
        has the same email or phone number.

        - Non-blocking warning banner on the Contact form (same pattern as
          Odoo's own VAT / Company Registry duplicate warning).
        - "Potential Duplicates" filter in Contacts, so duplicates created via
          import, portal signup or API are also easy to review.

        Nothing is ever blocked. Use Odoo's built-in Merge Contacts wizard to
        clean up any duplicates found.
    """,
    # 'contacts' (not bare `base`) is required: `base` only ships the
    # res.partner model/form used internally by other apps (e.g. Settings ->
    # Users), it does not activate the standalone Contacts app menu/icon.
    # Depending on `contacts` guarantees the Contacts app is installed and
    # visible whenever this module is installed on its own.
    'depends': ['contacts', 'phone_validation'],
    'external_dependencies': {
        # phone_validation degrades silently without it (raw phone strings
        # aren't normalized), which would make same_phone_partner_id
        # unreliable across formats. Require it explicitly instead.
        'python': ['phonenumbers'],
    },
    'data': [
        'views/res_partner_views.xml',
    ],
    'author': 'AllyRoot Tech',
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
