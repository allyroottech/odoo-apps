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

import difflib

from odoo import api, fields, models, tools

# Only used to catch a mistyped domain (e.g. "gmil.com" vs "gmail.com") when
# the email username already matches exactly - kept as a narrow, separate
# check rather than general fuzzy matching (which would be noisy/confusing).
DOMAIN_SIMILARITY_THRESHOLD = 0.85


class ResPartner(models.Model):
    _inherit = 'res.partner'

    same_email_partner_id = fields.Many2one(
        'res.partner', compute='_compute_duplicate_contact_partner_id', store=True,
        help="Another contact sharing the same email address.")
    same_phone_partner_id = fields.Many2one(
        'res.partner', compute='_compute_duplicate_contact_partner_id', store=True,
        help="Another contact sharing the same phone number.")
    similar_email_partner_id = fields.Many2one(
        'res.partner', compute='_compute_duplicate_contact_partner_id', store=True,
        help="Another contact with the same email username but a slightly different domain (possible typo).")

    @api.depends('email', 'phone_sanitized')
    def _compute_duplicate_contact_partner_id(self):
        for partner in self:
            partner.same_email_partner_id = False
            partner.same_phone_partner_id = False
            partner.similar_email_partner_id = False
            if partner.parent_id:
                # Same guard as core's _compute_same_vat_partner_id: several
                # contacts under one company can legitimately share one
                # general mailbox/phone (e.g. info@company.com).
                continue

            Partner = self.env['res.partner'].with_context(active_test=False).sudo()
            partner_id = partner._origin.id
            domain = [('id', '!=', partner_id), '!', ('id', 'child_of', partner_id)] if partner_id else []

            if partner.email:
                normalized = tools.email_normalize(partner.email)
                if normalized and '@' in normalized:
                    partner.same_email_partner_id = Partner.search(
                        domain + [('email', '=ilike', normalized)], limit=1)

                    if not partner.same_email_partner_id:
                        partner.similar_email_partner_id = partner._find_similar_email_domain_partner(
                            Partner, domain, normalized)

            if partner.phone_sanitized:
                partner.same_phone_partner_id = Partner.search(
                    domain + [('phone_sanitized', '=', partner.phone_sanitized)], limit=1)

    def _find_similar_email_domain_partner(self, Partner, domain, normalized_email):
        """Find a contact with the same email username but a slightly
        different, near-matching domain (e.g. a typo like "gmil.com" for
        "gmail.com"). Only the domain part is fuzzy-compared, and only once
        the username already matches exactly, to keep this narrow."""
        username, _, email_domain = normalized_email.rpartition('@')
        # Escape SQL LIKE wildcards that may legally appear in a local-part
        # (e.g. "ab%cd@...") so they aren't treated as pattern wildcards.
        username_escaped = username.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        candidates = Partner.search(domain + [('email', '=ilike', f'{username_escaped}@%')], limit=20)
        for candidate in candidates:
            candidate_email = tools.email_normalize(candidate.email) or ''
            candidate_domain = candidate_email.rpartition('@')[2]
            if not candidate_domain or candidate_domain == email_domain:
                continue
            if difflib.SequenceMatcher(None, email_domain, candidate_domain).ratio() >= DOMAIN_SIMILARITY_THRESHOLD:
                return candidate
        return False
