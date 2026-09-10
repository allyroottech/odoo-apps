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

from odoo import fields, models, tools


class SaleOrderLineBulkFilterFields(models.Model):
    """Read-only SQL view exposing only the handful of sale.order.line fields
    that make sense to filter on in the bulk update wizard. Pointing the
    native domain widget at this view (instead of at sale.order.line itself)
    keeps its field picker to Product/Category/Unit Price/Discount/Quantity/
    Description instead of every technical field on the real model, while
    still producing a domain whose field names match sale.order.line exactly."""
    _name = 'sale.order.line.bulk.filter.fields'
    _description = 'Sale Order Line Bulk Update - Filterable Fields'
    _auto = False

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    categ_id = fields.Many2one('product.category', string='Category', readonly=True)
    price_unit = fields.Float(string='Unit Price', readonly=True)
    discount = fields.Float(string='Discount (%)', readonly=True)
    product_uom_qty = fields.Float(string='Quantity', readonly=True)
    name = fields.Char(string='Description', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE VIEW {self._table} AS (
                SELECT
                    sol.id AS id,
                    sol.product_id AS product_id,
                    pt.categ_id AS categ_id,
                    sol.price_unit AS price_unit,
                    sol.discount AS discount,
                    sol.product_uom_qty AS product_uom_qty,
                    sol.name AS name
                FROM sale_order_line sol
                LEFT JOIN product_product pp ON pp.id = sol.product_id
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            )
        """)
