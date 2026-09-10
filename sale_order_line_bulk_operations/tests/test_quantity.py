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
class TestBulkQuantity(BulkOperationsCommon):

    def setUp(self):
        super().setUp()
        self.order = self._create_order()
        self.line = self._create_line(self.order, self.product_a, qty=10.0)

    def _apply(self, operation_type, value):
        wizard = self._wizard(self.line, 'product_uom_qty',
                               quantity_operation_type=operation_type, quantity_value=value)
        wizard.action_preview()
        wizard.action_apply()
        self.line.invalidate_recordset()
        return self.line.product_uom_qty

    def test_set_quantity(self):
        self.assertEqual(self._apply('set', 20.0), 20.0)

    def test_increase_quantity(self):
        self.assertEqual(self._apply('increase_fixed', 5.0), 15.0)

    def test_decrease_quantity(self):
        self.assertEqual(self._apply('decrease_fixed', 2.0), 8.0)

    def test_zero_quantity_allowed(self):
        self.assertEqual(self._apply('decrease_fixed', 10.0), 0.0)

    def test_negative_quantity_is_blocked(self):
        wizard = self._wizard(self.line, 'product_uom_qty',
                               quantity_operation_type='decrease_fixed', quantity_value=20.0)
        wizard.action_preview()
        self.assertEqual(wizard.eligible_line_count, 0)
        self.assertEqual(wizard.skipped_line_count, 1)
        with self.assertRaises(Exception):
            wizard.action_apply()
        self.line.invalidate_recordset()
        self.assertEqual(self.line.product_uom_qty, 10.0)

    def test_section_and_note_lines_are_excluded(self):
        section = self.env['sale.order.line'].create({
            'order_id': self.order.id,
            'display_type': 'line_section',
            'name': 'Section',
        })
        wizard = self._wizard(self.line | section, 'product_uom_qty',
                               quantity_operation_type='set', quantity_value=1.0)
        self.assertEqual(wizard.line_count, 1)
