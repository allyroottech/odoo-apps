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

from odoo.tests import common, tagged


@tagged('post_install', '-at_install')
class TestPartnerDuplicateWarning(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Deterministic phone parsing regardless of the database's own
        # default company configuration.
        us = cls.env['res.country'].search([('code', '=', 'US')], limit=1)
        cls.env.company.country_id = us.id

    def test_exact_email_match_is_case_and_whitespace_insensitive(self):
        p1 = self.env['res.partner'].create({'name': 'Email A', 'email': 'dup@example.com'})
        p2 = self.env['res.partner'].create({'name': 'Email B', 'email': ' DUP@Example.com '})
        self.assertEqual(p2.same_email_partner_id, p1)
        self.assertFalse(p2.similar_email_partner_id)

    def test_exact_phone_match_across_formats(self):
        p1 = self.env['res.partner'].create({'name': 'Phone A', 'phone': '+1 212-456-7890'})
        p2 = self.env['res.partner'].create({'name': 'Phone B', 'phone': '212 456 7890'})
        self.assertEqual(p2.same_phone_partner_id, p1)

    def test_typo_domain_is_flagged_as_similar_not_exact(self):
        p1 = self.env['res.partner'].create({'name': 'Typo A', 'email': 'typo@gmial.com'})
        p2 = self.env['res.partner'].create({'name': 'Typo B', 'email': 'typo@gmail.com'})
        self.assertEqual(p2.similar_email_partner_id, p1)
        self.assertFalse(p2.same_email_partner_id)

    def test_unrelated_domain_is_not_flagged(self):
        self.env['res.partner'].create({'name': 'Typo A', 'email': 'typo@gmial.com'})
        p3 = self.env['res.partner'].create({'name': 'Unrelated', 'email': 'typo@yahoo.com'})
        self.assertFalse(p3.similar_email_partner_id)
        self.assertFalse(p3.same_email_partner_id)

    def test_unique_contact_is_not_flagged(self):
        p = self.env['res.partner'].create({
            'name': 'Unique', 'email': 'unique@example.com', 'phone': '+1 212-000-0001'})
        self.assertFalse(p.same_email_partner_id)
        self.assertFalse(p.similar_email_partner_id)
        self.assertFalse(p.same_phone_partner_id)

    def test_children_of_same_company_sharing_mailbox_not_flagged(self):
        company = self.env['res.partner'].create({'name': 'Company', 'is_company': True})
        self.env['res.partner'].create({
            'name': 'Contact A', 'parent_id': company.id, 'email': 'info@company.com'})
        child_b = self.env['res.partner'].create({
            'name': 'Contact B', 'parent_id': company.id, 'email': 'info@company.com'})
        self.assertFalse(child_b.same_email_partner_id)

    def test_percent_in_local_part_does_not_over_match(self):
        # A literal '%' in the local-part must not act as a SQL LIKE wildcard.
        self.env['res.partner'].create({'name': 'Percent A', 'email': 'we%ird@example.com'})
        p2 = self.env['res.partner'].create({'name': 'Percent B', 'email': 'weXXXird@example.com'})
        self.assertFalse(p2.similar_email_partner_id)
        self.assertFalse(p2.same_email_partner_id)

    def test_blank_email_and_phone_do_not_false_match(self):
        p1 = self.env['res.partner'].create({'name': 'Blank A'})
        p2 = self.env['res.partner'].create({'name': 'Blank B'})
        self.assertFalse(p1.same_email_partner_id)
        self.assertFalse(p2.same_email_partner_id)
        self.assertFalse(p1.same_phone_partner_id)
        self.assertFalse(p2.same_phone_partner_id)

    def test_malformed_email_does_not_raise(self):
        p = self.env['res.partner'].create({
            'name': 'Malformed', 'email': 'not-an-email, still-not@x, @broken'})
        self.assertFalse(p.same_email_partner_id)
        self.assertFalse(p.similar_email_partner_id)

    def test_import_of_duplicate_row_is_not_blocked_and_gets_flagged(self):
        self.env['res.partner'].create({'name': 'Existing', 'email': 'importdup@example.com'})
        result = self.env['res.partner'].load(['name', 'email'], [['Imported', 'importdup@example.com']])
        self.assertTrue(result['ids'])
        self.assertFalse(result['messages'])
        imported = self.env['res.partner'].browse(result['ids'][0])
        self.assertTrue(imported.same_email_partner_id)
