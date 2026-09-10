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

from odoo.tests import tagged

from .common import BulkOperationsCommon


@tagged('post_install', '-at_install')
class TestBulkFilterFieldsView(BulkOperationsCommon):
    """sale.order.line.bulk.filter.fields is a read-only SQL view that backs
    the wizard's filter builder, exposing only the handful of fields users
    should filter on instead of every technical field on sale.order.line."""

    def test_view_exposes_only_the_intended_fields(self):
        # 'id' and 'display_name' are unavoidable (every Odoo model has them),
        # but none of sale.order.line's ~100 other technical fields
        # (currency_id, company_id, state, sequence, ...) should leak in.
        fields_get = self.env['sale.order.line.bulk.filter.fields'].fields_get()
        expected = {'id', 'display_name', 'product_id', 'categ_id', 'price_unit', 'discount', 'product_uom_qty', 'name'}
        self.assertEqual(set(fields_get.keys()), expected)

    def test_view_mirrors_real_sale_order_line_data(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a, price=1234.0, discount=5.0, qty=3.0)

        row = self.env['sale.order.line.bulk.filter.fields'].browse(line.id)
        self.assertEqual(row.product_id, self.product_a)
        self.assertEqual(row.categ_id, self.product_a.categ_id)
        self.assertEqual(row.price_unit, 1234.0)
        self.assertEqual(row.discount, 5.0)
        self.assertEqual(row.product_uom_qty, 3.0)

    def test_view_domain_matches_the_same_lines_as_filtered_domain(self):
        order = self._create_order()
        cheap = self._create_line(order, self.product_a, price=50.0)
        expensive = self._create_line(order, self.product_a, price=500.0)

        domain = [('price_unit', '>', 100.0)]
        view_matches = self.env['sale.order.line.bulk.filter.fields'].search(domain).ids
        self.assertIn(expensive.id, view_matches)
        self.assertNotIn(cheap.id, view_matches)
