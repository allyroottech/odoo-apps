Sale Ready to Invoice Dashboard
=================================

A delivered order that never gets invoiced is revenue you already earned
and just forgot to collect. It usually isn't anyone's fault on purpose, the
order simply falls out of sight once the delivery is done and there's
nothing left in the normal workflow reminding anyone to go back and bill
it. This module gives sales teams a dedicated place to catch those orders
before they turn into lost income.

What it does
------------

The module tracks the moment a sales order becomes fully delivered, and
adds a standalone "Ready to Invoice" app with its own icon on the home
screen. Open it and you see exactly the orders that are fully delivered but
still have an amount left to invoice, grouped in a Kanban by salesperson,
with the oldest ones surfaced first. Each salesperson sees their own
pending orders by default, and anyone with the wider access right can
switch to a view of every salesperson at once.

The same information is also available without leaving the regular Sales
app, through a "Delivered, Not Invoiced" filter on the Sales Orders list,
for people who are already working there and just want to narrow the list
down.

Nothing about the invoicing process itself changes. The dashboard is a
finder, not a workflow change. Once you've reviewed an order, you invoice
it exactly the way you always have.

Features
--------

- Standalone "Ready to Invoice" dashboard app, opening straight to orders
  that are delivered but not yet invoiced.
- Kanban grouped by salesperson, with orders delivered seven or more days
  ago highlighted first.
- Personal view by default, with an optional "see all salespersons" access
  right for managers who need the full picture.
- "Delivered, Not Invoiced" filter available directly on the Sales Orders
  list, for the same search without leaving that screen.
- Tracks the date an order became fully delivered, so aging is based on
  when the work actually finished, not on when someone happened to look.

Installation
------------

1. Copy the ``sale_ready_to_invoice_dashboard`` folder into an addons path
   alongside the standard ``sale_management`` and ``sale_stock`` apps.
2. Update the apps list in Odoo and install **Sale Ready to Invoice
   Dashboard**.
3. Assign the "See All Salespersons" access right (Settings, Users) to
   anyone who should see every pending order rather than just their own.

Usage
-----

1. Deliver a sales order as usual. Once the last delivery to the customer
   is completed, the order becomes eligible for the dashboard.
2. Open the **Ready to Invoice** app from the home screen to review orders
   that still need billing.
3. Open any order from the dashboard and invoice it the normal way.
4. Alternatively, stay in **Sales, Orders** and apply the "Delivered, Not
   Invoiced" filter to find the same set of orders there.

License
-------

This module is licensed under the GNU Lesser General Public License v3
(LGPL-3). See the header of each source file for the full notice.

Support
-------

AllyRoot Tech
allyroottech@gmail.com
