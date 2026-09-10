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

from odoo import fields, models

from .bulk_operation import FIELD_SELECTION


class SaleOrderLineBulkOperationLine(models.Model):
    _name = 'sale.order.line.bulk.operation.line'
    _description = 'Sale Order Line Bulk Operation - Line Change'
    _order = 'id'

    operation_id = fields.Many2one(
        'sale.order.line.bulk.operation', string='Bulk Operation',
        required=True, ondelete='cascade', index=True)
    sale_order_line_id = fields.Many2one(
        'sale.order.line', string='Sale Order Line', ondelete='set null', index=True)
    order_id = fields.Many2one(
        'sale.order', string='Sale Order', required=True, ondelete='cascade', index=True, readonly=True)
    company_id = fields.Many2one(
        related='operation_id.company_id', store=True, readonly=True)
    field_name = fields.Selection(FIELD_SELECTION, string='Field', required=True, readonly=True)
    old_value_numeric = fields.Float(string='Old Value', readonly=True)
    new_value_numeric = fields.Float(string='New Value', readonly=True)
    old_value_text = fields.Char(string='Old Text', readonly=True)
    new_value_text = fields.Char(string='New Text', readonly=True)
    reverted = fields.Boolean(string='Reverted', default=False, readonly=True)
    skip_reason = fields.Char(string='Not Reverted Because', readonly=True)
