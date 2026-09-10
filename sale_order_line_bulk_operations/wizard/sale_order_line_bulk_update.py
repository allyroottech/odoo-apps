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

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round
from odoo.tools.safe_eval import safe_eval

from ..models.bulk_operation import FIELD_SELECTION, batched_write, is_order_editable

PRICE_OPERATIONS = [
    ('set', 'Set to'),
    ('increase_percent', 'Increase by %'),
    ('decrease_percent', 'Decrease by %'),
    ('increase_fixed', 'Increase by amount'),
    ('decrease_fixed', 'Decrease by amount'),
]
DISCOUNT_OPERATIONS = [
    ('set', 'Set to'),
    ('increase_fixed', 'Increase by percentage points'),
    ('decrease_fixed', 'Decrease by percentage points'),
]
QUANTITY_OPERATIONS = [
    ('set', 'Set to'),
    ('increase_fixed', 'Increase by amount'),
    ('decrease_fixed', 'Decrease by amount'),
]
DESCRIPTION_OPERATIONS = [
    ('replace', 'Replace with'),
    ('append', 'Append'),
    ('prepend', 'Prepend'),
]

PREVIEW_LIMIT = 200


class SaleOrderLineBulkUpdateWizard(models.TransientModel):
    _name = 'sale.order.line.bulk.update.wizard'
    _description = 'Bulk Update Sale Order Lines'

    state = fields.Selection([('select', 'Select'), ('preview', 'Preview')], default='select', required=True)

    line_ids = fields.Many2many('sale.order.line', string='Sale Order Lines')
    original_line_ids = fields.Many2many(
        'sale.order.line', relation='sale_order_line_bulk_wizard_original_rel', string='All Candidate Lines',
        help='The full set of lines the wizard was opened with, before any filter was applied. '
             'Filters always narrow down from this set, never from an already-narrowed one.')
    line_count = fields.Integer(compute='_compute_counts')
    order_count = fields.Integer(compute='_compute_counts')

    line_filter_domain = fields.Char(string='Filters', default='[]')

    field_name = fields.Selection(FIELD_SELECTION, string='Field to Update', required=True, default='price_unit')

    price_operation_type = fields.Selection(PRICE_OPERATIONS, string='Price Operation', default='set')
    price_value = fields.Float(string='Price Value', digits='Product Price')

    discount_operation_type = fields.Selection(DISCOUNT_OPERATIONS, string='Discount Operation', default='set')
    discount_value = fields.Float(string='Discount Value', digits='Discount')

    quantity_operation_type = fields.Selection(QUANTITY_OPERATIONS, string='Quantity Operation', default='set')
    quantity_value = fields.Float(string='Quantity Value', digits='Product Unit')

    description_operation_type = fields.Selection(DESCRIPTION_OPERATIONS, string='Description Operation', default='replace')
    description_value = fields.Char(string='Description Text')

    eligible_line_count = fields.Integer(readonly=True)
    skipped_line_count = fields.Integer(readonly=True)
    warning_message = fields.Text(readonly=True)
    preview_more_count = fields.Integer(readonly=True)
    preview_line_ids = fields.One2many(
        'sale.order.line.bulk.update.wizard.line', 'wizard_id', string='Preview')

    operation_id = fields.Many2one('sale.order.line.bulk.operation', readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'line_ids' in fields_list and not res.get('line_ids'):
            ctx = self.env.context
            lines = self.env['sale.order.line']
            if ctx.get('active_model') == 'sale.order.line' and ctx.get('active_ids'):
                lines = self.env['sale.order.line'].browse(ctx['active_ids'])
            elif ctx.get('active_domain'):
                lines = self.env['sale.order.line'].search(ctx['active_domain'])
            if lines:
                res['line_ids'] = [(6, 0, lines.ids)]
                res['original_line_ids'] = [(6, 0, lines.ids)]
        return res

    @api.model_create_multi
    def create(self, vals_list):
        wizards = super().create(vals_list)
        for wizard in wizards:
            # Guard against the client not sending 'original_line_ids' (e.g. it isn't
            # part of the view's field spec): filters must always narrow down from the
            # full initial selection, so make sure it's never left empty while line_ids
            # isn't - an empty original_line_ids would make Reset/Apply Filters wipe
            # the selection instead of restoring/narrowing it.
            if not wizard.original_line_ids and wizard.line_ids:
                wizard.original_line_ids = [(6, 0, wizard.line_ids.ids)]
        return wizards

    @api.depends('line_ids')
    def _compute_counts(self):
        for wizard in self:
            lines = wizard._target_lines()
            wizard.line_count = len(lines)
            wizard.order_count = len(lines.order_id)

    def _target_lines(self):
        return self.line_ids.filtered(lambda l: not l.display_type)

    def action_apply_filters(self):
        self.ensure_one()
        base = self.original_line_ids.filtered(lambda l: not l.display_type)
        domain = safe_eval(self.line_filter_domain or '[]')
        lines = base.filtered_domain(domain) if domain else base
        self.line_ids = [(6, 0, lines.ids)]
        return self._reopen_view()

    def action_reset_filters(self):
        self.ensure_one()
        self.write({
            'line_filter_domain': '[]',
            'line_ids': [(6, 0, self.original_line_ids.filtered(lambda l: not l.display_type).ids)],
        })
        return self._reopen_view()

    def _get_operation_params(self):
        self.ensure_one()
        if self.field_name == 'price_unit':
            field_name, operation_type, numeric_value, text_value = (
                'price_unit', self.price_operation_type, self.price_value, False)
        elif self.field_name == 'discount':
            field_name, operation_type, numeric_value, text_value = (
                'discount', self.discount_operation_type, self.discount_value, False)
        elif self.field_name == 'product_uom_qty':
            field_name, operation_type, numeric_value, text_value = (
                'product_uom_qty', self.quantity_operation_type, self.quantity_value, False)
        elif self.field_name == 'name':
            field_name, operation_type, numeric_value, text_value = (
                'name', self.description_operation_type, False, self.description_value)
        else:
            raise UserError(_('Unsupported field selected.'))

        # Guard against previewing/applying the untouched defaults (e.g. Value left
        # at 0.00, Description left blank) - without this, an accidental Preview +
        # Apply would silently zero out price/discount/quantity or blank out every
        # selected line's description.
        if field_name == 'name':
            if operation_type == 'replace' and not (text_value or '').strip():
                raise UserError(_('Enter the replacement text first - it is currently empty.'))
        elif not numeric_value:
            raise UserError(_('Enter a value first - it is currently 0, which would have no '
                               'effect or would zero out every selected line.'))

        return field_name, operation_type, numeric_value, text_value

    def _compute_new_value(self, line, field_name, operation_type, numeric_value, text_value):
        if field_name == 'name':
            old = line.name or ''
            text_value = text_value or ''
            if operation_type == 'replace':
                new = text_value
            elif operation_type == 'append':
                new = old + text_value
            elif operation_type == 'prepend':
                new = text_value + old
            else:
                raise UserError(_('Unsupported description operation.'))
            return old, new

        old = line[field_name]
        precision_key = {
            'price_unit': 'Product Price',
            'discount': 'Discount',
            'product_uom_qty': 'Product Unit',
        }[field_name]
        digits = self.env['decimal.precision'].precision_get(precision_key)
        if operation_type == 'set':
            new = numeric_value
        elif operation_type == 'increase_percent':
            new = old * (1 + numeric_value / 100.0)
        elif operation_type == 'decrease_percent':
            new = old * (1 - numeric_value / 100.0)
        elif operation_type == 'increase_fixed':
            new = old + numeric_value
        elif operation_type == 'decrease_fixed':
            new = old - numeric_value
        else:
            raise UserError(_('Unsupported operation.'))
        return old, float_round(new, precision_digits=digits)

    def _evaluate_line(self, line, field_name, operation_type, numeric_value, text_value):
        order = line.order_id
        if not is_order_editable(order):
            return {
                'can_apply': False,
                'skip_reason': _('Only open quotations that are not locked can be updated.'),
            }
        old, new = self._compute_new_value(line, field_name, operation_type, numeric_value, text_value)
        warning = False
        if field_name == 'product_uom_qty' and new < 0:
            return {
                'can_apply': False,
                'skip_reason': _('Resulting quantity would be negative.'),
                'old': old, 'new': new,
            }
        if field_name == 'price_unit' and new < 0:
            warning = _('Resulting unit price is negative.')
        if field_name == 'discount' and (new < 0 or new > 100):
            warning = _('Resulting discount is outside the usual 0-100%s range.') % '%'
        if field_name == 'discount' and order.pricelist_id:
            note = _('This order uses a pricelist; a later quantity or product change '
                      'may automatically recompute this discount.')
            warning = (warning + ' ' + note) if warning else note
        return {'can_apply': True, 'old': old, 'new': new, 'warning': warning}

    def action_preview(self):
        self.ensure_one()
        field_name, operation_type, numeric_value, text_value = self._get_operation_params()
        lines = self._target_lines()
        if not lines:
            raise UserError(_('No Sale Order Lines selected. Select lines from the Sale Order Lines '
                               'list before starting a bulk update.'))

        self.preview_line_ids.unlink()

        eligible = 0
        skipped = 0
        warnings = set()
        preview_vals = []
        for line in lines:
            result = self._evaluate_line(line, field_name, operation_type, numeric_value, text_value)
            if result['can_apply']:
                eligible += 1
                if result.get('warning'):
                    warnings.add(result['warning'])
            else:
                skipped += 1
            if len(preview_vals) < PREVIEW_LIMIT:
                vals = {
                    'sale_order_line_id': line.id,
                    'field_name': field_name,
                    'can_apply': result['can_apply'],
                    'skip_reason': result.get('skip_reason', False),
                }
                if field_name == 'name':
                    vals['old_value_text'] = result.get('old')
                    vals['new_value_text'] = result.get('new')
                else:
                    vals['old_value_numeric'] = result.get('old')
                    vals['new_value_numeric'] = result.get('new')
                preview_vals.append((0, 0, vals))

        self.write({
            'state': 'preview',
            'preview_line_ids': preview_vals,
            'eligible_line_count': eligible,
            'skipped_line_count': skipped,
            'preview_more_count': max(0, len(lines) - PREVIEW_LIMIT),
            'warning_message': '\n'.join(sorted(warnings)) or False,
        })
        return self._reopen_view()

    def action_back(self):
        self.ensure_one()
        self.preview_line_ids.unlink()
        self.state = 'select'
        return self._reopen_view()

    def action_apply(self):
        self.ensure_one()
        if self.state != 'preview':
            raise UserError(_('Please preview the changes before applying them.'))
        field_name, operation_type, numeric_value, text_value = self._get_operation_params()
        lines = self._target_lines()

        value_map = {}
        op_line_vals = []
        applied_orders = self.env['sale.order']
        for line in lines:
            result = self._evaluate_line(line, field_name, operation_type, numeric_value, text_value)
            if not result['can_apply']:
                continue
            value_map[line.id] = result['new']
            vals = {
                'sale_order_line_id': line.id,
                'order_id': line.order_id.id,
                'field_name': field_name,
            }
            if field_name == 'name':
                vals.update(old_value_text=result['old'], new_value_text=result['new'])
            else:
                vals.update(old_value_numeric=result['old'], new_value_numeric=result['new'])
            op_line_vals.append(vals)
            applied_orders |= line.order_id

        if not value_map:
            raise UserError(_('No Sale Order Lines are eligible to be updated. '
                               'Only open quotations that are not locked can be updated.'))

        target_lines = self.env['sale.order.line'].browse(list(value_map.keys()))
        batched_write(target_lines, field_name, value_map)

        operation = self.env['sale.order.line.bulk.operation'].create({
            'field_name': field_name,
            'operation_type': operation_type,
            'value_numeric': numeric_value or 0.0,
            'value_text': text_value or False,
            'line_count': len(lines),
            'order_count': len(lines.order_id),
            'applied_line_count': len(value_map),
            'skipped_line_count': len(lines) - len(value_map),
            'state': 'completed',
            'operation_line_ids': [(0, 0, v) for v in op_line_vals],
        })
        self.operation_id = operation.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line.bulk.operation',
            'res_id': operation.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _reopen_view(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class SaleOrderLineBulkUpdateWizardLine(models.TransientModel):
    _name = 'sale.order.line.bulk.update.wizard.line'
    _description = 'Bulk Update Sale Order Lines - Preview Line'
    _order = 'id'

    wizard_id = fields.Many2one('sale.order.line.bulk.update.wizard', required=True, ondelete='cascade')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', readonly=True)
    order_id = fields.Many2one(related='sale_order_line_id.order_id', string='Sale Order', readonly=True)
    field_name = fields.Selection(FIELD_SELECTION, readonly=True)
    can_apply = fields.Boolean(readonly=True)
    skip_reason = fields.Char(readonly=True)
    old_value_numeric = fields.Float(readonly=True)
    new_value_numeric = fields.Float(readonly=True)
    old_value_text = fields.Char(readonly=True)
    new_value_text = fields.Char(readonly=True)
