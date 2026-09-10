Sale Order Line Bulk Operations
=================================

Once a company has hundreds of open quotations, a routine change like
raising the price of one product by five percent, or clearing a discount
that was left at zero by mistake, stops being a five minute job. Opening
every quotation one at a time doesn't scale, and mass editing a whole list
without a chance to review it first is asking for a mistake that's hard to
notice until a customer complains. This module gives that kind of change a
proper workflow: filter, select, preview, apply, and if needed, undo.

Odoo's own list view already lets you select several rows and edit one cell
to write the same value across all of them, and that's still the right tool
for "set this field to this exact value for everyone I picked." This module
is for what that doesn't cover: relative changes like "increase by 5%", a
preview of every old and new value before anything is written, a record of
who did what and when, and a safe way to undo it afterwards.

What it does
------------

From the Sale Order Lines list, or from a quotation itself, you filter down
to the lines you care about, select them, and open Bulk Update. Pick a
field (Unit Price, Discount, Quantity or Description) and an operation such
as set, increase by percentage, or increase by a fixed amount, then run
Preview. Nothing is written at this point, you just see the current and
proposed value for every affected line, along with a clear count of how
many lines are eligible and why any are being skipped.

Only lines belonging to open quotations can be changed this way.
Confirmed, locked or cancelled sales orders are automatically excluded
rather than silently skipped, so it's always clear what did and didn't get
touched. Once you apply the change, it's recorded in a history log with the
field, the operation, who ran it and how many lines were affected. From
there, a manager can undo it, though only lines that still hold the value
the bulk update produced are reverted. If someone has changed a line since,
it's left alone and reported rather than overwritten a second time.

Features
--------

- Filter Sale Order Lines by order state, product, discount, quantity,
  customer or salesperson, using Odoo's own search and group by tools.
- Select lines across any number of sales orders at once, including
  Odoo's "select all records matching this search" option.
- Bulk Unit Price updates: set, increase or decrease by percentage,
  increase or decrease by a fixed amount.
- Bulk Discount updates: set, increase or decrease by percentage points.
- Bulk Quantity updates: set, increase or decrease by amount.
- Bulk Description updates: replace, append or prepend text.
- Preview of every old and new value before anything is written, with
  eligible and excluded lines clearly reported.
- Full history of every applied bulk update, including who ran it, what
  changed, and how many lines and orders were involved.
- Safe undo that only reverts lines still holding the value the update
  produced, leaving anything changed afterwards untouched.

Installation
------------

1. Copy the ``sale_order_line_bulk_operations`` folder into an addons path
   alongside the standard ``sale_management`` app.
2. Update the apps list in Odoo and install **Sale Order Line Bulk
   Operations**.
3. Assign the "Bulk Operations User" or "Bulk Operations Manager" group
   (Settings, Users) to whoever should use this feature.

Usage
-----

1. Go to **Sales, Orders, Sale Order Lines**.
2. Filter and group the list down to the lines you're interested in.
3. Select the relevant lines and click **Bulk Update**.
4. Choose the field and operation, for example Unit Price, increase by
   percent, 5.
5. Click **Preview** to see the old and new value for every line before
   committing to anything.
6. Click **Apply Changes**. You land on the resulting history record.
7. To review or undo a past update, open **Sales, Orders, Bulk Operation
   History**, or the Bulk Updates smart button on a sales order.

Security
--------

- **Bulk Operations User** can filter and select lines, run previews and
  apply updates, and see their own history.
- **Bulk Operations Manager** additionally sees every operation, not just
  their own, and can use Undo.
- Which sales orders and lines a user can see and edit is still governed
  entirely by the existing ``sale`` module access rights and record rules,
  this module doesn't widen that in any way.
- Every write happens as the acting user through the ORM, there is no use
  of ``sudo()`` anywhere in the module.

Out of scope
------------

Delivery, purchasing, invoicing, manufacturing, CRM, helpdesk, projects,
the customer portal, payments, and changing the product on an existing
line are all outside what this module does. The module description in the
app itself covers the reasoning behind leaving product changes for a later
version.

License
-------

This module is licensed under the GNU Lesser General Public License v3
(LGPL-3). See the header of each source file for the full notice.

Support
-------

AllyRoot Tech
allyroottech@gmail.com
