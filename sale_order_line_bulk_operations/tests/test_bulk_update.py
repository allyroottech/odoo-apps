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

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import BulkOperationsCommon


@tagged('post_install', '-at_install')
class TestBulkUpdateDescription(BulkOperationsCommon):

    def setUp(self):
        super().setUp()
        self.order = self._create_order()
        self.line = self._create_line(self.order, self.product_a)
        self.line.name = 'Premium Support'

    def _apply(self, operation_type, value):
        wizard = self._wizard(self.line, 'name',
                               description_operation_type=operation_type, description_value=value)
        wizard.action_preview()
        wizard.action_apply()
        self.line.invalidate_recordset()
        return self.line.name

    def test_replace_description(self):
        self.assertEqual(self._apply('replace', 'New Description'), 'New Description')

    def test_append_description(self):
        self.assertEqual(self._apply('append', ' - Annual Contract'), 'Premium Support - Annual Contract')

    def test_prepend_description(self):
        self.assertEqual(self._apply('prepend', 'Renewed: '), 'Renewed: Premium Support')


@tagged('post_install', '-at_install')
class TestBulkUpdateSelection(BulkOperationsCommon):

    def test_selection_across_multiple_orders(self):
        order1 = self._create_order()
        order2 = self._create_order()
        line1 = self._create_line(order1, self.product_a)
        line2 = self._create_line(order1, self.product_b)
        line3 = self._create_line(order2, self.product_a)

        wizard = self._wizard(line1 | line2 | line3, 'price_unit',
                               price_operation_type='set', price_value=100.0)
        self.assertEqual(wizard.line_count, 3)
        self.assertEqual(wizard.order_count, 2)

        wizard.action_preview()
        wizard.action_apply()
        for line in (line1, line2, line3):
            line.invalidate_recordset()
            self.assertEqual(line.price_unit, 100.0)

    def test_only_explicitly_passed_lines_are_affected(self):
        order = self._create_order()
        target = self._create_line(order, self.product_a, price=1000.0)
        untouched = self._create_line(order, self.product_b, price=1000.0)

        wizard = self._wizard(target, 'price_unit', price_operation_type='set', price_value=1.0)
        wizard.action_preview()
        wizard.action_apply()

        target.invalidate_recordset()
        untouched.invalidate_recordset()
        self.assertEqual(target.price_unit, 1.0)
        self.assertEqual(untouched.price_unit, 1000.0)

    def test_apply_without_preview_is_rejected(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a)
        wizard = self._wizard(line, 'price_unit', price_operation_type='set', price_value=1.0)
        with self.assertRaises(UserError):
            wizard.action_apply()

    def test_empty_selection_is_rejected(self):
        wizard = self._wizard(self.env['sale.order.line'], 'price_unit',
                               price_operation_type='set', price_value=1.0)
        with self.assertRaises(UserError):
            wizard.action_preview()

    def test_preview_with_untouched_zero_value_is_rejected(self):
        # Regression test: opening the wizard and hitting Preview without
        # entering a value must not silently preview/apply "set to 0" for
        # every selected line's price/discount/quantity.
        order = self._create_order()
        line = self._create_line(order, self.product_a, price=1000.0)
        wizard = self._wizard(line, 'price_unit')  # price_value left at its 0.0 default
        with self.assertRaises(UserError):
            wizard.action_preview()
        line.invalidate_recordset()
        self.assertEqual(line.price_unit, 1000.0)

    def test_preview_with_zero_operation_value_is_rejected_for_every_numeric_field(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a)
        for field_name in ('price_unit', 'discount', 'product_uom_qty'):
            wizard = self._wizard(line, field_name)
            with self.assertRaises(UserError):
                wizard.action_preview()

    def test_preview_with_blank_replacement_text_is_rejected(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a)
        line.name = 'Original Description'
        wizard = self._wizard(line, 'name', description_operation_type='replace')  # no text entered
        with self.assertRaises(UserError):
            wizard.action_preview()
        line.invalidate_recordset()
        self.assertEqual(line.name, 'Original Description')

    def test_preview_with_a_real_value_still_works(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a, price=1000.0)
        wizard = self._wizard(line, 'price_unit', price_operation_type='set', price_value=1.0)
        wizard.action_preview()
        self.assertEqual(wizard.eligible_line_count, 1)

    def test_lines_can_be_narrowed_down_after_prefill(self):
        # Mirrors the order-form button prefilling all of an order's lines,
        # then the user removing some from the wizard before applying.
        order = self._create_order()
        line1 = self._create_line(order, self.product_a, price=1000.0)
        line2 = self._create_line(order, self.product_b, price=1000.0)
        line3 = self._create_line(order, self.product_a, price=1000.0)

        wizard = self._wizard(line1 | line2 | line3, 'price_unit',
                               price_operation_type='set', price_value=1.0)
        self.assertEqual(wizard.line_count, 3)

        wizard.line_ids = [(3, line2.id)]  # user removes line2 from the target set
        self.assertEqual(wizard.line_count, 2)

        wizard.action_preview()
        self.assertEqual(wizard.eligible_line_count, 2)
        wizard.action_apply()

        line1.invalidate_recordset()
        line2.invalidate_recordset()
        line3.invalidate_recordset()
        self.assertEqual(line1.price_unit, 1.0)
        self.assertEqual(line3.price_unit, 1.0)
        self.assertEqual(line2.price_unit, 1000.0, 'Removed line must be left untouched')

    def test_filter_by_product_at_scale(self):
        # Simulates the order-form button prefilling a large order (e.g. 60+
        # lines): one filter condition + Apply Filters should replace many
        # manual removals.
        order = self._create_order()
        lines = self.env['sale.order.line']
        for _i in range(20):
            lines |= self._create_line(order, self.product_a, price=1000.0)
        for _i in range(40):
            lines |= self._create_line(order, self.product_b, price=1000.0)

        wizard = self._wizard(lines, 'price_unit', price_operation_type='set', price_value=1.0)
        self.assertEqual(wizard.line_count, 60)

        wizard.line_filter_domain = str([('product_id', '=', self.product_a.id)])
        result = wizard.action_apply_filters()
        self.assertEqual(wizard.line_count, 20)
        self.assertEqual(result.get('res_model'), 'sale.order.line.bulk.update.wizard',
                          'Applying filters must keep the wizard open, not close it')
        self.assertEqual(result.get('res_id'), wizard.id)
        self.assertEqual(result.get('target'), 'new')

        wizard.action_preview()
        wizard.action_apply()
        for line in lines.filtered(lambda l: l.product_id == self.product_a):
            line.invalidate_recordset()
            self.assertEqual(line.price_unit, 1.0)
        for line in lines.filtered(lambda l: l.product_id == self.product_b):
            line.invalidate_recordset()
            self.assertEqual(line.price_unit, 1000.0, 'Lines outside the filtered selection must be untouched')

    def test_filter_by_category(self):
        other_category = self.env['product.category'].create({'name': 'Bulk Ops Filter Category'})
        categorized_product = self.env['product.product'].create({
            'name': 'Bulk Ops Filter Product', 'list_price': 100.0, 'type': 'consu',
            'categ_id': other_category.id,
        })
        order = self._create_order()
        line_a = self._create_line(order, self.product_a)
        line_categorized = self._create_line(order, categorized_product)

        wizard = self._wizard(line_a | line_categorized, 'price_unit', price_operation_type='set', price_value=1.0)
        wizard.line_filter_domain = str([('categ_id', '=', other_category.id)])
        wizard.action_apply_filters()
        self.assertEqual(wizard.line_ids, line_categorized)

    def test_filter_by_description_contains(self):
        order = self._create_order()
        matching = self._create_line(order, self.product_a)
        matching.name = 'Premium Support Package'
        other = self._create_line(order, self.product_b)
        other.name = 'Standard Package'

        wizard = self._wizard(matching | other, 'price_unit', price_operation_type='set', price_value=1.0)
        wizard.line_filter_domain = str([('name', 'ilike', 'Premium')])
        wizard.action_apply_filters()
        self.assertEqual(wizard.line_ids, matching)

    def test_filter_conditions_combine_with_and(self):
        # e.g. "Unit Price greater than 100 AND Discount equals 10%" -
        # the exact kind of multi-condition filter non-technical users need.
        # Odoo's native domain widget combines rules with AND by default.
        order = self._create_order()
        cheap = self._create_line(order, self.product_a, price=50.0, discount=10.0)
        expensive_discounted = self._create_line(order, self.product_a, price=500.0, discount=10.0)
        expensive_no_discount = self._create_line(order, self.product_a, price=500.0, discount=0.0)

        lines = cheap | expensive_discounted | expensive_no_discount
        wizard = self._wizard(lines, 'price_unit', price_operation_type='set', price_value=1.0)
        wizard.line_filter_domain = str([('price_unit', '>', 100.0), ('discount', '=', 10.0)])
        wizard.action_apply_filters()
        self.assertEqual(wizard.line_ids, expensive_discounted,
                          'Only the line matching every condition (AND) should remain')

    def test_apply_filters_with_no_conditions_keeps_full_selection(self):
        order = self._create_order()
        line_a = self._create_line(order, self.product_a)
        line_b = self._create_line(order, self.product_b)

        wizard = self._wizard(line_a | line_b, 'price_unit', price_operation_type='set', price_value=1.0)
        wizard.action_apply_filters()
        self.assertEqual(wizard.line_ids, line_a | line_b)

    def test_reset_filters_restores_full_selection(self):
        order = self._create_order()
        line_a = self._create_line(order, self.product_a)
        line_b = self._create_line(order, self.product_b)

        wizard = self._wizard(line_a | line_b, 'price_unit', price_operation_type='set', price_value=1.0)
        wizard.line_filter_domain = str([('product_id', '=', self.product_a.id)])
        wizard.action_apply_filters()
        self.assertEqual(wizard.line_count, 1)

        wizard.action_reset_filters()
        self.assertEqual(wizard.line_filter_domain, '[]')
        self.assertEqual(wizard.line_ids, line_a | line_b)

    def test_filter_only_matches_within_the_original_selection(self):
        # A domain matching lines elsewhere in the database must never pull
        # them into the wizard - filtering only ever narrows the original
        # candidate set, it never broadens it into a fresh search.
        order = self._create_order()
        in_scope = self._create_line(order, self.product_a, price=1000.0)
        other_order = self._create_order()
        out_of_scope = self._create_line(other_order, self.product_a, price=1000.0)

        wizard = self._wizard(in_scope, 'price_unit', price_operation_type='set', price_value=1.0)
        wizard.line_filter_domain = str([('product_id', '=', self.product_a.id)])
        wizard.action_apply_filters()
        self.assertEqual(wizard.line_ids, in_scope)
        self.assertNotIn(out_of_scope, wizard.line_ids)

    def test_create_backfills_original_line_ids_when_client_omits_it(self):
        # Regression test: the client only sends field values that are part
        # of the view's field spec. If 'original_line_ids' isn't declared in
        # the view, create() must still backfill it from line_ids so that
        # Apply/Reset Filters never wipes the selection out.
        order = self._create_order()
        line = self._create_line(order, self.product_a)
        wizard = self.env['sale.order.line.bulk.update.wizard'].create({
            'line_ids': [(6, 0, line.ids)],
            'field_name': 'price_unit', 'price_operation_type': 'set', 'price_value': 1.0,
        })
        self.assertEqual(wizard.original_line_ids, line)
        wizard.action_reset_filters()
        self.assertEqual(wizard.line_ids, line, 'Reset must not wipe out the selection')

    def test_default_get_reads_active_ids(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a)
        wizard = self.env['sale.order.line.bulk.update.wizard'].with_context(
            active_model='sale.order.line', active_ids=line.ids,
        ).create({'field_name': 'price_unit', 'price_operation_type': 'set', 'price_value': 1.0})
        self.assertEqual(wizard.line_ids, line)


@tagged('post_install', '-at_install')
class TestBulkUpdateStateHandling(BulkOperationsCommon):
    """Bulk updates are limited to open quotations."""

    def _wizard_for_state(self, line, price_value=1.0):
        return self._wizard(line, 'price_unit', price_operation_type='set', price_value=price_value)

    def test_quotation_line_is_editable(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a)
        wizard = self._wizard_for_state(line)
        wizard.action_preview()
        self.assertEqual(wizard.eligible_line_count, 1)

    def test_sent_quotation_line_is_editable(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a)
        order.state = 'sent'
        wizard = self._wizard_for_state(line)
        wizard.action_preview()
        self.assertEqual(wizard.eligible_line_count, 1)

    def test_confirmed_order_line_is_not_editable(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a)
        original_price = line.price_unit
        order.action_confirm()
        wizard = self._wizard_for_state(line)
        wizard.action_preview()
        self.assertEqual(wizard.eligible_line_count, 0)
        self.assertEqual(wizard.skipped_line_count, 1)
        line.invalidate_recordset()
        self.assertEqual(line.price_unit, original_price)

    def test_locked_order_line_is_not_editable(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a, price=1000.0)
        order.action_confirm()
        order.locked = True
        wizard = self._wizard_for_state(line)
        wizard.action_preview()
        self.assertEqual(wizard.eligible_line_count, 0)
        self.assertEqual(wizard.skipped_line_count, 1)
        line.invalidate_recordset()
        self.assertEqual(line.price_unit, 1000.0)

    def test_cancelled_order_line_is_not_editable(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a, price=1000.0)
        order.action_cancel()
        wizard = self._wizard_for_state(line)
        wizard.action_preview()
        self.assertEqual(wizard.eligible_line_count, 0)
        self.assertEqual(wizard.skipped_line_count, 1)

    def test_mixed_editable_and_locked_lines_partial_apply(self):
        editable_order = self._create_order()
        locked_order = self._create_order()
        editable_line = self._create_line(editable_order, self.product_a, price=1000.0)
        locked_line = self._create_line(locked_order, self.product_a, price=1000.0)
        locked_order.action_confirm()
        locked_order.locked = True

        wizard = self._wizard(editable_line | locked_line, 'price_unit',
                               price_operation_type='set', price_value=1.0)
        wizard.action_preview()
        self.assertEqual(wizard.eligible_line_count, 1)
        self.assertEqual(wizard.skipped_line_count, 1)
        wizard.action_apply()

        editable_line.invalidate_recordset()
        locked_line.invalidate_recordset()
        self.assertEqual(editable_line.price_unit, 1.0)
        self.assertEqual(locked_line.price_unit, 1000.0)


@tagged('post_install', '-at_install')
class TestProductCategoryFilter(BulkOperationsCommon):
    """The Sale Order Lines search view exposes sale.order.line's own (core)
    categ_id field, so users can filter/group by product category (e.g.
    'change rates for this product category') directly from the search bar,
    without an ad-hoc custom filter."""

    def test_search_by_product_category(self):
        other_category = self.env['product.category'].create({'name': 'Bulk Ops Test Category'})
        categorized_product = self.env['product.product'].create({
            'name': 'Bulk Ops Categorized Product', 'list_price': 100.0, 'type': 'consu',
            'categ_id': other_category.id,
        })
        order = self._create_order()
        line_a = self._create_line(order, self.product_a)
        line_categorized = self._create_line(order, categorized_product)

        found = self.env['sale.order.line'].search(
            [('categ_id', '=', other_category.id), ('id', 'in', (line_a | line_categorized).ids)])
        self.assertEqual(found, line_categorized)


@tagged('post_install', '-at_install')
class TestBulkUpdateRegression(BulkOperationsCommon):
    """Sanity check that standard Sale Order behaviour is unaffected by
    installing this module (no core methods are overridden; only new fields,
    a button and an unrelated model are added)."""

    def test_standard_quotation_lifecycle_still_works(self):
        order = self._create_order()
        line = self._create_line(order, self.product_a)
        order.write({'order_line': [(0, 0, {
            'product_id': self.product_b.id,
            'product_uom_qty': 2.0,
            'price_unit': self.product_b.list_price,
        })]})
        self.assertEqual(len(order.order_line), 2)

        line.unlink()
        self.assertEqual(len(order.order_line), 1)

        duplicate = order.copy()
        self.assertEqual(len(duplicate.order_line), 1)

        order.action_confirm()
        self.assertEqual(order.state, 'sale')

        other_order = self._create_order()
        other_order.action_cancel()
        self.assertEqual(other_order.state, 'cancel')
