Partner Duplicate Warning
==========================

Contact lists get messy over time. The same customer gets entered twice
because a salesperson didn't check first, a portal signup creates a second
record for someone who already exists, or an import brings in data that was
never cleaned up. This module gives you an early warning when that happens,
right on the Contact form, instead of finding out months later when two
invoices go to two different addresses for the same person.

What it does
------------

When a contact is saved with an email address or phone number that already
belongs to another contact, a warning banner appears on the form. It names
the other contact and links straight to it, so whoever is working on the
record can check in a few seconds whether it's really a duplicate or just a
coincidence (shared company mailboxes and phone lines are common, so the
module quietly skips contacts under the same parent company).

The module also flags a likely email typo. If someone types
john@gmial.com and a contact with john@gmail.com already exists, that gets
picked up too, since a mistyped domain is one of the more common ways
duplicates sneak in.

Nothing is ever blocked. This is a warning, not a validation rule. Your team
stays free to save the contact regardless, and can use Odoo's own Merge
Contacts wizard afterwards if it does turn out to be a duplicate.

Features
--------

- Warns when a new or edited contact shares an email address with an
  existing contact.
- Warns when a new or edited contact shares a phone number with an existing
  contact, matching across common formats rather than exact string equality.
- Flags a likely typo in the email domain when the username already matches.
- Adds a "Potential Duplicates" filter to the Contacts list, so duplicates
  created through imports, portal signups or API calls (which never pass
  through the form warning) can still be found and reviewed.
- Ignores contacts that share a parent company, since those legitimately
  share a general mailbox or phone line.

Installation
------------

1. Copy the ``partner_duplicate_warning`` folder into an addons path that
   also has the standard ``contacts`` app available.
2. Update the apps list in Odoo and install **Partner Duplicate Warning**.
3. That's it. There is nothing to configure and no new menu to find, the
   warning simply starts appearing on the Contact form.

Usage
-----

1. Open a contact, or create a new one, and fill in an email or phone
   number as usual.
2. If it matches an existing contact, a banner appears explaining what
   matched and pointing to the other record.
3. Decide whether to keep the contact as is or merge it using Odoo's
   built in Merge Contacts wizard.
4. To catch duplicates that were never opened by hand, go to Contacts and
   apply the Potential Duplicates filter.

License
-------

This module is licensed under the GNU Lesser General Public License v3
(LGPL-3). See the header of each source file for the full notice.

Support
-------

AllyRoot Tech
allyroottech@gmail.com
