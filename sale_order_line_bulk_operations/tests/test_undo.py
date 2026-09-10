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

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import BulkOperationsCommon


@tagged('post_install', '-at_install')
class TestBulkUndo(BulkOperationsCommon):

    def setUp(self):
        super().setUp()
        self.order = self._create_order(user=self.salesman)
        self.line1 = self._create_line(self.order, self.product_a, price=1000.0)
        self.line2 = self._create_line(self.order, self.product_b, price=2000.0)

    def _apply_price_set(self, lines, value):
        wizard = self._wizard(lines, 'price_unit', user=self.salesman,
                               price_operation_type='set', price_value=value)
        wizard.action_preview()
        wizard.action_apply()
        return wizard.operation_id

    def test_successful_undo(self):
        operation = self._apply_price_set(self.line1, 1200.0)
        operation.with_user(self.manager).action_undo()
        self.line1.invalidate_recordset()
        self.assertEqual(self.line1.price_unit, 1000.0)
        self.assertEqual(operation.state, 'reverted')
        self.assertTrue(operation.operation_line_ids.reverted)

    def test_undo_does_not_overwrite_later_manual_change(self):
        operation = self._apply_price_set(self.line1, 1070.0)
        # A salesperson manually changes the price after the bulk operation.
        self.line1.price_unit = 1125.0

        operation.with_user(self.manager).action_undo()

        self.line1.invalidate_recordset()
        self.assertEqual(self.line1.price_unit, 1125.0, 'Undo must not overwrite a later manual change')
        self.assertFalse(operation.operation_line_ids.reverted)
        self.assertIn('changed after', operation.operation_line_ids.skip_reason)

    def test_partial_undo(self):
        operation = self._apply_price_set(self.line1 | self.line2, 1500.0)
        # Only line2 gets manually changed afterwards.
        self.line2.price_unit = 999.0

        operation.with_user(self.manager).action_undo()

        self.line1.invalidate_recordset()
        self.line2.invalidate_recordset()
        self.assertEqual(self.line1.price_unit, 1000.0)
        self.assertEqual(self.line2.price_unit, 999.0)
        self.assertEqual(operation.state, 'partially_reverted')

    def test_repeated_undo_is_idempotent(self):
        operation = self._apply_price_set(self.line1 | self.line2, 1500.0)
        self.line2.price_unit = 999.0

        operation.with_user(self.manager).action_undo()
        self.assertEqual(operation.state, 'partially_reverted')

        # Calling undo again should not error and should not re-revert line1.
        operation.with_user(self.manager).action_undo()
        self.assertEqual(operation.state, 'partially_reverted')
        self.line1.invalidate_recordset()
        self.assertEqual(self.line1.price_unit, 1000.0)

    def test_unauthorized_undo_is_rejected(self):
        operation = self._apply_price_set(self.line1, 1200.0)
        with self.assertRaises(UserError):
            operation.with_user(self.salesman).action_undo()

    def test_undo_skips_locked_order(self):
        operation = self._apply_price_set(self.line1, 1200.0)
        self.order.locked = True
        operation.with_user(self.manager).action_undo()
        self.line1.invalidate_recordset()
        self.assertEqual(self.line1.price_unit, 1200.0, 'Undo must not touch a locked order')
        self.assertIn('no longer an open quotation or is locked', operation.operation_line_ids.skip_reason)
