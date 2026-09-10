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
class TestBulkDiscount(BulkOperationsCommon):

    def setUp(self):
        super().setUp()
        self.order = self._create_order()
        self.line = self._create_line(self.order, self.product_a, discount=0.0)

    def _apply(self, operation_type, value):
        wizard = self._wizard(self.line, 'discount',
                               discount_operation_type=operation_type, discount_value=value)
        wizard.action_preview()
        wizard.action_apply()
        self.line.invalidate_recordset()
        return self.line.discount

    def test_set_discount(self):
        self.assertEqual(self._apply('set', 5.0), 5.0)

    def test_increase_discount(self):
        self.line.discount = 10.0
        self.assertEqual(self._apply('increase_fixed', 5.0), 15.0)

    def test_decrease_discount(self):
        self.line.discount = 15.0
        self.assertEqual(self._apply('decrease_fixed', 5.0), 10.0)

    def test_out_of_range_discount_is_flagged_as_warning_not_blocked(self):
        wizard = self._wizard(self.line, 'discount', discount_operation_type='set', discount_value=150.0)
        wizard.action_preview()
        self.assertEqual(wizard.eligible_line_count, 1)
        self.assertTrue(wizard.warning_message)
        wizard.action_apply()
        self.line.invalidate_recordset()
        self.assertEqual(self.line.discount, 150.0)
