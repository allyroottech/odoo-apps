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
class TestBulkMultiCompany(BulkOperationsCommon):

    def test_cross_company_selection_updates_each_line(self):
        order_a = self._create_order(company=self.company_a)
        order_b = self._create_order(company=self.company_b)
        line_a = self._create_line(order_a, self.product_a, price=1000.0)
        line_b = self._create_line(order_b, self.product_a, price=2000.0)

        wizard = self._wizard(line_a | line_b, 'price_unit', user=self.manager,
                               price_operation_type='increase_percent', price_value=10.0)
        self.assertEqual(wizard.order_count, 2)
        wizard.action_preview()
        wizard.action_apply()

        line_a.invalidate_recordset()
        line_b.invalidate_recordset()
        self.assertEqual(line_a.price_unit, 1100.0)
        self.assertEqual(line_b.price_unit, 2200.0)

    def test_line_selection_is_company_isolated(self):
        order_c = self._create_order(company=self.company_a)  # admin-owned, company A
        foreign_line = self._create_line(order_c, self.product_a)

        company_c = self.env['res.company'].create({'name': 'Bulk Ops Company C'})
        isolated_user = self.env['res.users'].create({
            'name': 'Bulk Ops Isolated User',
            'login': 'bulk_ops_isolated',
            'email': 'bulk_ops_isolated@example.com',
            'group_ids': [(6, 0, [self.salesman_group.id, self.bulk_user_group.id])],
            'company_id': company_c.id,
            'company_ids': [(6, 0, [company_c.id])],
        })

        visible = self.env['sale.order.line'].with_user(isolated_user).search(
            [('id', '=', foreign_line.id)])
        self.assertFalse(visible, 'A user with no access to Company A must not see its Sale Order Lines')

    def test_operation_history_is_company_scoped(self):
        order_a = self._create_order(company=self.company_a)
        line_a = self._create_line(order_a, self.product_a, price=1000.0)
        wizard = self._wizard(line_a, 'price_unit', user=self.manager,
                               price_operation_type='set', price_value=1200.0)
        wizard.action_preview()
        wizard.action_apply()
        operation = wizard.operation_id
        self.assertEqual(operation.company_id, self.company_a)

        company_c = self.env['res.company'].create({'name': 'Bulk Ops Company C'})
        other_manager = self.env['res.users'].create({
            'name': 'Bulk Ops Other Manager',
            'login': 'bulk_ops_other_manager',
            'email': 'bulk_ops_other_manager@example.com',
            'group_ids': [(6, 0, [self.sale_manager_group.id, self.bulk_manager_group.id])],
            'company_id': company_c.id,
            'company_ids': [(6, 0, [company_c.id])],
        })
        visible = self.env['sale.order.line.bulk.operation'].with_user(other_manager).search(
            [('id', '=', operation.id)])
        self.assertFalse(visible, 'Bulk Operation history must respect multi-company record rules')
