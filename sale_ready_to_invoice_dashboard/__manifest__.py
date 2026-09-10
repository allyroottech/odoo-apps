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
    'name': 'Sale Ready to Invoice Dashboard',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Dashboard of sales orders that are fully delivered but still not invoiced',
    'description': """
        Tracks Sales Orders that are fully delivered but still have an
        outstanding amount to invoice, so they don't get forgotten and
        quietly turn into lost revenue.

        - "Delivered, Not Invoiced" filter on Sales Orders, so these orders
          are easy to find regardless of who is looking at the list.
        - "Ready to Invoice" dashboard - its own app icon on the home
          screen, a Kanban grouped by Salesperson, so these orders are a
          one-click habitual check instead of something only visible from
          inside each order.

        Nothing is ever blocked. Invoice the order as usual once reviewed.
    """,
    # sale_management (not bare `sale`) is required, same reasoning as
    # sale_order_line_bulk_operations: `sale`/`sale_stock` ship the "Sales"
    # app menus with active=False, and it is sale_management's
    # post_init_hook that activates them. sale_stock is still required on
    # top of it for the delivery/picking fields this module depends on.
    'depends': ['sale_management', 'sale_stock'],
    'data': [
        'security/sale_ready_to_invoice_security.xml',
        'views/sale_order_views.xml',
        'views/sale_order_dashboard_views.xml',
    ],
    'author': 'AllyRoot Tech',
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
