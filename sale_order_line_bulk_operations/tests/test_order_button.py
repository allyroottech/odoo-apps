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
from odoo.exceptions import UserError

from .common import BulkOperationsCommon


@tagged('post_install', '-at_install')
class TestOrderBulkUpdateButton(BulkOperationsCommon):
    """The 'Update Multiple Lines' button on the Sale Order form itself,
    for editing this order's own lines without leaving the order."""

    def setUp(self):
        super().setUp()
        self.order = self._create_order(user=self.salesman)
        self.line1 = self._create_line(self.order, self.product_a, price=1000.0)
        self.line2 = self._create_line(self.order, self.product_b, price=500.0)

    def test_action_scopes_to_this_order_only(self):
        other_order = self._create_order()
        self._create_line(other_order, self.product_a)

        action = self.order.with_user(self.salesman).action_bulk_update_lines()
        self.assertEqual(action['res_model'], 'sale.order.line.bulk.update.wizard')
        self.assertEqual(action['context']['active_model'], 'sale.order.line')
        self.assertEqual(set(action['context']['active_ids']), {self.line1.id, self.line2.id})

    def test_wizard_created_from_action_picks_up_order_lines(self):
        action = self.order.with_user(self.salesman).action_bulk_update_lines()
        wizard = self.env['sale.order.line.bulk.update.wizard'].with_context(
            **action['context']).create({
                'field_name': 'price_unit', 'price_operation_type': 'set', 'price_value': 10.0,
            })
        self.assertEqual(wizard.line_count, 2)
        self.assertEqual(wizard.order_count, 1)

        wizard.action_preview()
        wizard.action_apply()
        self.line1.invalidate_recordset()
        self.line2.invalidate_recordset()
        self.assertEqual(self.line1.price_unit, 10.0)
        self.assertEqual(self.line2.price_unit, 10.0)

    def test_action_excludes_section_and_note_lines(self):
        self.env['sale.order.line'].create({
            'order_id': self.order.id, 'display_type': 'line_section', 'name': 'Section',
        })
        action = self.order.action_bulk_update_lines()
        self.assertEqual(set(action['context']['active_ids']), {self.line1.id, self.line2.id})

    def test_confirmed_order_cannot_open_bulk_update(self):
        self.order.action_confirm()
        with self.assertRaises(UserError):
            self.order.action_bulk_update_lines()
