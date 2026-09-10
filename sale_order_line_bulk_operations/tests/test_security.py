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

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from .common import BulkOperationsCommon


@tagged('post_install', '-at_install')
class TestBulkOperationsSecurity(BulkOperationsCommon):

    def _order_and_line(self, user, company=None):
        order = self.env['sale.order'].with_user(user).with_company(company or self.company_a).create({
            'partner_id': self.partner.id,
        })
        line = self.env['sale.order.line'].with_user(user).create({
            'order_id': order.id,
            'product_id': self.product_a.id,
            'product_uom_qty': 1.0,
            'price_unit': 1000.0,
        })
        return order, line

    def test_regular_user_can_apply_bulk_update(self):
        _order, line = self._order_and_line(self.salesman)
        wizard = self._wizard(line, 'price_unit', user=self.salesman,
                               price_operation_type='set', price_value=1200.0)
        wizard.action_preview()
        wizard.action_apply()
        line.invalidate_recordset()
        self.assertEqual(line.price_unit, 1200.0)

    def test_outsider_without_group_cannot_use_wizard(self):
        _order, line = self._order_and_line(self.outsider)
        with self.assertRaises(AccessError):
            self._wizard(line, 'price_unit', user=self.outsider,
                         price_operation_type='set', price_value=1200.0)

    def test_undo_requires_manager_group(self):
        _order, line = self._order_and_line(self.salesman)
        wizard = self._wizard(line, 'price_unit', user=self.salesman,
                               price_operation_type='set', price_value=1200.0)
        wizard.action_preview()
        wizard.action_apply()
        operation = wizard.operation_id
        with self.assertRaises(UserError):
            operation.with_user(self.salesman).action_undo()

    def test_manager_can_undo(self):
        _order, line = self._order_and_line(self.salesman)
        wizard = self._wizard(line, 'price_unit', user=self.salesman,
                               price_operation_type='set', price_value=1200.0)
        wizard.action_preview()
        wizard.action_apply()
        operation = wizard.operation_id
        operation.with_user(self.manager).action_undo()
        self.assertEqual(operation.state, 'reverted')

    def test_user_sees_only_own_operations(self):
        _order_a, line_a = self._order_and_line(self.salesman)
        wizard_a = self._wizard(line_a, 'price_unit', user=self.salesman,
                                 price_operation_type='set', price_value=1200.0)
        wizard_a.action_preview()
        wizard_a.action_apply()

        _order_b, line_b = self._order_and_line(self.manager)
        wizard_b = self._wizard(line_b, 'price_unit', user=self.manager,
                                 price_operation_type='set', price_value=1300.0)
        wizard_b.action_preview()
        wizard_b.action_apply()

        visible_to_salesman = self.env['sale.order.line.bulk.operation'].with_user(self.salesman).search([])
        self.assertIn(wizard_a.operation_id, visible_to_salesman)
        self.assertNotIn(wizard_b.operation_id, visible_to_salesman)

    def test_manager_sees_all_operations(self):
        _order_a, line_a = self._order_and_line(self.salesman)
        wizard_a = self._wizard(line_a, 'price_unit', user=self.salesman,
                                 price_operation_type='set', price_value=1200.0)
        wizard_a.action_preview()
        wizard_a.action_apply()

        visible_to_manager = self.env['sale.order.line.bulk.operation'].with_user(self.manager).search([])
        self.assertIn(wizard_a.operation_id, visible_to_manager)
