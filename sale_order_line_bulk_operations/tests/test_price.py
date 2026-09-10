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
class TestBulkPrice(BulkOperationsCommon):

    def setUp(self):
        super().setUp()
        self.order = self._create_order()
        self.line = self._create_line(self.order, self.product_a, price=1000.0)

    def _apply(self, operation_type, value):
        wizard = self._wizard(self.line, 'price_unit',
                               price_operation_type=operation_type, price_value=value)
        wizard.action_preview()
        wizard.action_apply()
        self.line.invalidate_recordset()
        return self.line.price_unit

    def test_set_price(self):
        self.assertEqual(self._apply('set', 1200.0), 1200.0)

    def test_increase_percent(self):
        self.assertEqual(self._apply('increase_percent', 10.0), 1100.0)

    def test_decrease_percent(self):
        self.assertEqual(self._apply('decrease_percent', 10.0), 900.0)

    def test_increase_fixed(self):
        self.assertEqual(self._apply('increase_fixed', 100.0), 1100.0)

    def test_decrease_fixed(self):
        self.assertEqual(self._apply('decrease_fixed', 100.0), 900.0)

    def test_decimal_rounding(self):
        # 1000 * 1.0333 = 1033.3, should round to currency precision (2 digits)
        price = self._apply('increase_percent', 3.33)
        self.assertEqual(price, 1033.3)

    def test_currency_precision_respected(self):
        precision = self.env['decimal.precision'].precision_get('Product Price')
        price = self._apply('increase_percent', 33.333)
        self.assertEqual(round(price, precision), price)

    def test_amount_recomputed_after_price_change(self):
        self._apply('set', 500.0)
        self.assertEqual(self.line.price_subtotal, 500.0)

    def test_apply_creates_history_record(self):
        wizard = self._wizard(self.line, 'price_unit', price_operation_type='set', price_value=1200.0)
        wizard.action_preview()
        wizard.action_apply()
        self.assertTrue(wizard.operation_id)
        self.assertEqual(wizard.operation_id.state, 'completed')
        self.assertEqual(wizard.operation_id.applied_line_count, 1)
        op_line = wizard.operation_id.operation_line_ids
        self.assertEqual(op_line.old_value_numeric, 1000.0)
        self.assertEqual(op_line.new_value_numeric, 1200.0)

    def test_preview_does_not_modify_records(self):
        wizard = self._wizard(self.line, 'price_unit', price_operation_type='set', price_value=1200.0)
        wizard.action_preview()
        self.line.invalidate_recordset()
        self.assertEqual(self.line.price_unit, 1000.0)
