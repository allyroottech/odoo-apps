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

from odoo.tests import common, tagged


@tagged('post_install', '-at_install')
class BulkOperationsCommon(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env['res.company'].create({'name': 'Bulk Ops Company A'})
        cls.company_b = cls.env['res.company'].create({'name': 'Bulk Ops Company B'})

        cls.product_a = cls.env['product.product'].create({
            'name': 'Bulk Ops Product A', 'list_price': 1000.0, 'type': 'consu'})
        cls.product_b = cls.env['product.product'].create({
            'name': 'Bulk Ops Product B', 'list_price': 500.0, 'type': 'consu'})
        cls.partner = cls.env['res.partner'].create({'name': 'Bulk Ops Test Customer'})

        cls.bulk_user_group = cls.env.ref('sale_order_line_bulk_operations.group_bulk_operations_user')
        cls.bulk_manager_group = cls.env.ref('sale_order_line_bulk_operations.group_bulk_operations_manager')
        cls.salesman_group = cls.env.ref('sales_team.group_sale_salesman')
        cls.sale_manager_group = cls.env.ref('sales_team.group_sale_manager')

        cls.salesman = cls.env['res.users'].create({
            'name': 'Bulk Ops Salesman',
            'login': 'bulk_ops_salesman',
            'email': 'bulk_ops_salesman@example.com',
            'group_ids': [(6, 0, [cls.salesman_group.id, cls.bulk_user_group.id])],
            'company_id': cls.company_a.id,
            'company_ids': [(6, 0, [cls.company_a.id, cls.company_b.id])],
        })
        cls.manager = cls.env['res.users'].create({
            'name': 'Bulk Ops Manager',
            'login': 'bulk_ops_manager',
            'email': 'bulk_ops_manager@example.com',
            'group_ids': [(6, 0, [cls.sale_manager_group.id, cls.bulk_manager_group.id])],
            'company_id': cls.company_a.id,
            'company_ids': [(6, 0, [cls.company_a.id, cls.company_b.id])],
        })
        cls.outsider = cls.env['res.users'].create({
            'name': 'Bulk Ops Outsider',
            'login': 'bulk_ops_outsider',
            'email': 'bulk_ops_outsider@example.com',
            'group_ids': [(6, 0, [cls.salesman_group.id])],
            'company_id': cls.company_a.id,
            'company_ids': [(6, 0, [cls.company_a.id])],
        })

    def _create_order(self, company=None, partner=None, user=None):
        env = self.env if user is None else self.env(user=user)
        return env['sale.order'].with_company(company or self.company_a).create({
            'partner_id': (partner or self.partner).id,
        })

    def _create_line(self, order, product, qty=1.0, price=None, discount=0.0):
        return self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': qty,
            'price_unit': price if price is not None else product.list_price,
            'discount': discount,
        })

    def _wizard(self, lines, field_name, user=None, **field_values):
        env = self.env if user is None else self.env(user=user)
        return env['sale.order.line.bulk.update.wizard'].create({
            'line_ids': [(6, 0, lines.ids)],
            'original_line_ids': [(6, 0, lines.ids)],
            'field_name': field_name,
            **field_values,
        })
