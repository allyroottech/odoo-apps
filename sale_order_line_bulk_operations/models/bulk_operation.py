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

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

FIELD_SELECTION = [
    ('price_unit', 'Unit Price'),
    ('discount', 'Discount'),
    ('product_uom_qty', 'Quantity'),
    ('name', 'Description'),
]

OPERATION_SELECTION = [
    ('set', 'Set'),
    ('increase_percent', 'Increase by %'),
    ('decrease_percent', 'Decrease by %'),
    ('increase_fixed', 'Increase by amount'),
    ('decrease_fixed', 'Decrease by amount'),
    ('replace', 'Replace'),
    ('append', 'Append'),
    ('prepend', 'Prepend'),
]

# sale.order.line fields whose editability is protected by core (see
# sale.order.line._get_protected_fields()) once the order is locked.
NUMERIC_FIELDS = ('price_unit', 'discount', 'product_uom_qty')

PRECISION_BY_FIELD = {
    'price_unit': 'Product Price',
    'discount': 'Discount',
    'product_uom_qty': 'Product Unit',
}


def batched_write(lines, field_name, value_map):
    """Write value_map (line.id -> new value) onto field_name, grouping lines
    that end up with an identical value into a single write() call instead of
    writing one record at a time."""
    groups = defaultdict(list)
    for line in lines:
        groups[value_map[line.id]].append(line.id)
    for value, ids in groups.items():
        lines.browse(ids).write({field_name: value})


def is_order_editable(order):
    """Bulk updates are available only for editable quotations.

    Confirmed, cancelled and locked orders are excluded so a bulk operation
    can never alter a sales order after confirmation.
    """
    return order.state in ('draft', 'sent') and not order.locked


class SaleOrderLineBulkOperation(models.Model):
    _name = 'sale.order.line.bulk.operation'
    _description = 'Sale Order Line Bulk Operation'
    _order = 'id desc'
    _rec_name = 'name'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                        default=lambda self: _('New'))
    user_id = fields.Many2one('res.users', string='Performed By', required=True,
                               readonly=True, default=lambda self: self.env.user)
    date = fields.Datetime(string='Date', required=True, readonly=True,
                            default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                  default=lambda self: self.env.company)
    field_name = fields.Selection(FIELD_SELECTION, string='Field', required=True, readonly=True)
    operation_type = fields.Selection(OPERATION_SELECTION, string='Operation', required=True, readonly=True)
    value_numeric = fields.Float(string='Requested Value', readonly=True)
    value_text = fields.Char(string='Requested Text', readonly=True)
    line_count = fields.Integer(string='Selected Lines', readonly=True)
    order_count = fields.Integer(string='Affected Sale Orders', readonly=True)
    applied_line_count = fields.Integer(string='Lines Updated', readonly=True)
    skipped_line_count = fields.Integer(string='Lines Skipped', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('partially_reverted', 'Partially Reverted'),
        ('reverted', 'Reverted'),
        ('failed', 'Failed'),
    ], string='Status', default='draft', required=True, readonly=True)
    operation_line_ids = fields.One2many(
        'sale.order.line.bulk.operation.line', 'operation_id', string='Line Changes', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'sale.order.line.bulk.operation') or _('New')
        return super().create(vals_list)

    def action_undo(self):
        self.ensure_one()
        if not self.env.user.has_group('sale_order_line_bulk_operations.group_bulk_operations_manager'):
            raise UserError(_('Only a Sale Order Line Bulk Operations Manager can undo an operation.'))
        if self.state not in ('completed', 'partially_reverted'):
            raise UserError(_('Only a completed operation can be undone.'))

        precision = PRECISION_BY_FIELD.get(self.field_name)
        digits = self.env['decimal.precision'].precision_get(precision) if precision else None

        candidates = self.operation_line_ids.filtered(lambda l: not l.reverted)
        value_map = {}
        revert_op_line_ids = []
        skip_groups = defaultdict(list)
        for op_line in candidates:
            line = op_line.sale_order_line_id
            if not line:
                skip_groups[_('Sale Order Line no longer exists.')].append(op_line.id)
                continue
            if not is_order_editable(line.order_id):
                skip_groups[_('Sale Order is no longer an open quotation or is locked.')].append(op_line.id)
                continue
            if self.field_name == 'name':
                current = line.name or ''
                matches = current == (op_line.new_value_text or '')
            else:
                current = line[self.field_name]
                matches = float_compare(current, op_line.new_value_numeric, precision_digits=digits) == 0
            if not matches:
                skip_groups[_('Value was changed after the bulk operation.')].append(op_line.id)
                continue
            value_map[line.id] = op_line.old_value_text if self.field_name == 'name' else op_line.old_value_numeric
            revert_op_line_ids.append(op_line.id)

        op_line_model = self.env['sale.order.line.bulk.operation.line']
        for reason, ids in skip_groups.items():
            op_line_model.browse(ids).write({'skip_reason': reason})

        if value_map:
            target_lines = self.env['sale.order.line'].browse(list(value_map.keys()))
            batched_write(target_lines, self.field_name, value_map)
            op_line_model.browse(revert_op_line_ids).write({'reverted': True, 'skip_reason': False})

        total = len(self.operation_line_ids)
        reverted_total = len(self.operation_line_ids.filtered('reverted'))
        if reverted_total >= total:
            self.state = 'reverted'
        elif reverted_total > 0:
            self.state = 'partially_reverted'
        return True
