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

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fully_delivery_date = fields.Date(
        compute='_compute_fully_delivery_date', store=True,
        help="Date the order became fully delivered, i.e. when its last "
             "delivery to the customer was completed. Empty until "
             "delivery_status is 'full'.")

    @api.depends('delivery_status', 'picking_ids.date_done')
    def _compute_fully_delivery_date(self):
        for order in self:
            if order.delivery_status != 'full':
                order.fully_delivery_date = False
                continue
            # Same picking domain as sale_stock's own _compute_effective_date,
            # but the *last* completed delivery rather than the first:
            # effective_date answers "when did delivery start", this answers
            # "when did the order become fully delivered".
            pickings = order.picking_ids.filtered(
                lambda p: p.state == 'done' and p.location_dest_id.usage == 'customer')
            dates_list = [date for date in pickings.mapped('date_done') if date]
            last_delivery = max(dates_list, default=False)
            order.fully_delivery_date = last_delivery.date() if last_delivery else False
