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
    'name': 'Sale Order Line Bulk Operations',
    'version': '19.0.1.0.1',
    'category': 'Sales',
    'summary': 'Filter, preview, bulk-update and safely undo changes across Sale Order Lines',
    'description': """
Sale Order Line Bulk Operations
================================

Update price, discount, quantity and description across large numbers of
Sale Order Lines spanning multiple Sale Orders, without opening every order
individually.

Workflow: Filter -> Select -> Preview -> Apply -> History -> Undo

* Reuses Odoo's own search/filter/group-by on Sale Order Lines.
* Selects lines across any number of Sale Orders at once.
* Preview shows old/new values before anything is written.
* Every bulk update is recorded with an audit trail.
* Bulk updates can be safely undone, without overwriting later manual edits.
""",
    'author': 'AllyRoot Tech',
    'images': [
        'static/description/banner.png',
    ],
    # sale_management (not bare `sale`) is required: `sale` ships its own
    # "Sales" app menus with active=False, and it is sale_management's
    # post_init_hook that activates them. Depending on `sale` alone installs
    # the models/views but leaves the Sales app invisible in the UI.
    'depends': ['sale_management'],
    'data': [
        'security/bulk_operations_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/sale_order_line_bulk_update_views.xml',
        'views/sale_order_line_views.xml',
        'views/bulk_operation_views.xml',
        'views/sale_order_views.xml',
        'views/bulk_operations_menus.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
