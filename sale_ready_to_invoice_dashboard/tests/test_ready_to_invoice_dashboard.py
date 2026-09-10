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

from odoo.fields import Command
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestSaleReadyToInvoiceDashboard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Customer'})
        cls.product = cls.env['product.product'].create({
            'name': 'Test Storable Product',
            'type': 'consu',
            'is_storable': True,
            # Delivery-based invoicing, so invoice_status only turns "to
            # invoice" once something has actually been delivered - the
            # combination this module cares about.
            'invoice_policy': 'delivery',
        })

    def _create_and_confirm_order(self, quantity=1):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [Command.create({
                'product_id': self.product.id,
                'product_uom_qty': quantity,
            })],
        })
        order.action_confirm()
        return order

    def test_service_only_order_has_no_delivery_and_does_not_error(self):
        service_product = self.env['product.product'].create({'name': 'Test Service', 'type': 'service'})
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [Command.create({
                'product_id': service_product.id,
                'product_uom_qty': 1,
            })],
        })
        order.action_confirm()
        self.assertFalse(order.picking_ids)
        self.assertFalse(order.delivery_status)
        self.assertFalse(order.fully_delivery_date)

    def test_fully_delivery_date_empty_until_delivery_status_full(self):
        order = self._create_and_confirm_order(quantity=1)
        self.assertNotEqual(order.delivery_status, 'full')
        self.assertFalse(order.fully_delivery_date)

    def test_fully_delivery_date_uses_last_delivery_not_first(self):
        order = self._create_and_confirm_order(quantity=2)
        first_picking = order.picking_ids
        first_picking.move_ids.write({'quantity': 1, 'picked': True})
        Form.from_action(self.env, first_picking.button_validate()).save().process()

        second_picking = order.picking_ids.filtered('backorder_id')
        second_picking.move_ids.write({'quantity': 1, 'picked': True})
        second_picking.button_validate()
        self.assertEqual(order.delivery_status, 'full')

        first_picking.write({'date_done': '2026-01-01 10:00:00'})
        second_picking.write({'date_done': '2026-01-08 10:00:00'})
        # The order only becomes fully delivered when the *last* (backorder)
        # picking completes, not the first partial one.
        self.assertEqual(order.fully_delivery_date, second_picking.date_done.date())

    def test_already_invoiced_order_is_not_flagged(self):
        order = self._create_and_confirm_order(quantity=1)
        order.picking_ids.move_ids.write({'quantity': 1, 'picked': True})
        order.picking_ids.button_validate()
        order.picking_ids.write({'date_done': '2026-01-01 10:00:00'})

        self.assertEqual(order.delivery_status, 'full')
        self.assertEqual(order.invoice_status, 'to invoice')
        self.assertTrue(order.fully_delivery_date)

        order._create_invoices()
        self.assertEqual(order.invoice_status, 'invoiced')
