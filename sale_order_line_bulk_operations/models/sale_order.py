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

from odoo import fields, models, _
from odoo.exceptions import UserError

from .bulk_operation import is_order_editable


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bulk_operation_line_count = fields.Integer(
        string='Bulk Update Changes', compute='_compute_bulk_operation_line_count')

    def _compute_bulk_operation_line_count(self):
        counts = dict(self.env['sale.order.line.bulk.operation.line']._read_group(
            [('order_id', 'in', self.ids)], ['order_id'], ['__count']))
        for order in self:
            order.bulk_operation_line_count = counts.get(order, 0)

    def action_view_bulk_operations(self):
        self.ensure_one()
        operation_ids = self.env['sale.order.line.bulk.operation.line'].search(
            [('order_id', '=', self.id)]).operation_id.ids
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Operations'),
            'res_model': 'sale.order.line.bulk.operation',
            'view_mode': 'list,form',
            'domain': [('id', 'in', operation_ids)],
        }

    def action_bulk_update_lines(self):
        self.ensure_one()
        if not is_order_editable(self):
            raise UserError(_('Bulk updates are only available for quotations that are not locked.'))
        lines = self.order_line.filtered(lambda l: not l.display_type)
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sale_order_line_bulk_operations.action_sale_order_line_bulk_update_wizard')
        action['context'] = {
            'active_model': 'sale.order.line',
            'active_ids': lines.ids,
        }
        return action
