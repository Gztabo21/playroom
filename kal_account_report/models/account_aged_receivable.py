# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
import logging


_logger = logging.getLogger(__name__)

class ReportAccountAgedReceivable(models.Model):
    _inherit = "account.aged.receivable"

    payment_reference = fields.Char()
    seller_name = fields.Char('Seller')
    invoice_date_due = fields.Date(group_operator="min")


    @api.model
    def _init_filter_partner(self, options, previous_options=None):
        if not self.filter_partner:
            return

        options['partner'] = True
        options['partner_ids'] = previous_options and previous_options.get('partner_ids') or []
        options['partner_categories'] = previous_options and previous_options.get('partner_categories') or []
        selected_partner_ids = [int(partner) for partner in options['partner_ids']]
        selected_partners = selected_partner_ids and self.env['res.partner'].browse(selected_partner_ids) or self.env['res.partner']
        options['selected_partner_ids'] = selected_partners.mapped('name')
        selected_partner_category_ids = [int(category) for category in options['partner_categories']]
        selected_partner_categories = selected_partner_category_ids and self.env['res.partner.category'].browse(selected_partner_category_ids) or self.env['res.partner.category']
        options['selected_partner_categories'] = selected_partner_categories.mapped('name')
        options['seller'] = True
        options['seller_ids'] = previous_options and previous_options.get('seller_ids') or []
        selected_seller_ids = [int(seller) for seller in options['seller_ids']]

        options['sellers'] = previous_options and previous_options.get('sellers') or []
        selected_seller_ids = [int(seller) for seller in options['sellers']]
        selected_sellers = selected_seller_ids and self.env['res.users'].browse(selected_seller_ids) or self.env['res.users']
        options['selected_sellers'] = selected_sellers.mapped('name')        

    @api.model
    def _get_options_partner_domain(self, options):
        domain = []
        if options.get('partner_ids'):
            partner_ids = [int(partner) for partner in options['partner_ids']]
            domain.append(('partner_id', 'in', partner_ids))
        if options.get('partner_categories'):
            partner_category_ids = [int(category) for category in options['partner_categories']]
            domain.append(('partner_id.category_id', 'in', partner_category_ids))
        if options.get('seller_ids'):
            seller_ids = [int(seller) for seller in options['seller_ids']]
            domain.append(('partner_id.user_id.id', 'in', seller_ids))
        return domain
   
    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self._get_options(options)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic_accounts') is not None:
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
        if options.get('analytic_tags') is not None:
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in (options.get('partner_categories') or [])]
            options['selected_seller_ids'] = [self.env['res.users'].browse(int(seller)).name for seller in options['seller_ids']]

        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))

        if options.get('journals'):
            journals_selected = set(journal['id'] for journal in options['journals'] if journal.get('selected'))
            for journal_group in self.env['account.journal.group'].search([('company_id', '=', self.env.company.id)]):
                if journals_selected and journals_selected == set(self._get_filter_journals().ids) - set(journal_group.excluded_journal_ids.ids):
                    options['name_journal_group'] = journal_group.name
                    break

        report_manager = self._get_report_manager(options)
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons_in_sequence(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view']._render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        return info



    @api.model
    def _get_column_details(self, options):
        columns = super(ReportAccountAgedReceivable, self)._get_column_details(options)
        columns.insert(2, self._field_column('invoice_date_due'))
        columns.insert(2, self._field_column('payment_reference'))
        columns.insert(3, self._field_column('seller_name'))
        return columns

    @api.model
    def _get_sql(self):
        options = self.env.context['report_options']
        query = ("""
                SELECT
                    {move_line_fields},
                    account_move_line.partner_id AS partner_id,
                    partner.name AS partner_name,
                    COALESCE(trust_property.value_text, 'normal') AS partner_trust,
                    COALESCE(account_move_line.currency_id, journal.currency_id) AS report_currency_id,
                    account_move_line.payment_id AS payment_id,
                    move.payment_reference as payment_reference,
                    move.invoice_date_due as invoice_date_due,
                    COALESCE(account_move_line.date_maturity, account_move_line.date) AS report_date,
                    account_move_line.expected_pay_date AS expected_pay_date,
                    move.move_type AS move_type,
                    move.name AS move_name,
                    max(seller_partner.seller_name) AS seller_name,
                    max(seller_partner.seller_id) AS seller_id,
                    journal.code AS journal_code,
                    account.name AS account_name,
                    account.code AS account_code,""" + ','.join([("""
                    CASE WHEN period_table.period_index = {i}
                    THEN %(sign)s * ROUND((
                        account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
                    ) * currency_table.rate, currency_table.precision)
                    ELSE 0 END AS period{i}""").format(i=i) for i in range(6)]) + """
                FROM account_move_line
                JOIN account_move move ON account_move_line.move_id = move.id
                LEFT JOIN res_users usuario ON move.invoice_user_id = usuario.id
                LEFT JOIN res_partner contactos ON account_move_line.partner_id = contactos.id
                LEFT JOIN res_users seller_partner2 ON contactos.user_id = seller_partner2.id
                LEFT JOIN (select id as seller_id, name as seller_name from  res_partner) AS seller_partner on seller_partner.seller_id = seller_partner2.partner_id

                JOIN account_journal journal ON journal.id = account_move_line.journal_id
                JOIN account_account account ON account.id = account_move_line.account_id
                JOIN res_partner partner ON partner.id = account_move_line.partner_id
                LEFT JOIN ir_property trust_property ON (
                    trust_property.res_id = 'res.partner,'|| account_move_line.partner_id
                    AND trust_property.name = 'trust'
                    AND trust_property.company_id = account_move_line.company_id
                )
                JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
                LEFT JOIN LATERAL (
                    SELECT part.amount, part.debit_move_id
                    FROM account_partial_reconcile part
                    WHERE part.max_date <= %(date)s
                ) part_debit ON part_debit.debit_move_id = account_move_line.id
                LEFT JOIN LATERAL (
                    SELECT part.amount, part.credit_move_id
                    FROM account_partial_reconcile part
                    WHERE part.max_date <= %(date)s
                ) part_credit ON part_credit.credit_move_id = account_move_line.id
                JOIN {period_table} ON (
                    period_table.date_start IS NULL
                    OR COALESCE(account_move_line.date_maturity, account_move_line.date) <= DATE(period_table.date_start)
                )
                AND (
                    period_table.date_stop IS NULL
                    OR COALESCE(account_move_line.date_maturity, account_move_line.date) >= DATE(period_table.date_stop)
                )
                WHERE account.internal_type = %(account_type)s
                GROUP BY account_move_line.id, partner.id, trust_property.id, journal.id, move.id, account.id,
                         period_table.period_index, currency_table.rate, currency_table.precision --, seller_partner.seller_name,seller_partner2.id
                HAVING ROUND(account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0), currency_table.precision) != 0
            """).format(
            move_line_fields=self._get_move_line_fields('account_move_line'),
            currency_table=self.env['res.currency']._get_query_currency_table(options),
            period_table=self._get_query_period_table(options),
        )
        params = {
            #'seller': options['filter_seller'],
            'account_type': options['filter_account_type'],
            'sign': 1 if options['filter_account_type'] == 'receivable' else -1,
            'date': options['date']['date_to'],
        }
        return self.env.cr.mogrify(query, params).decode(self.env.cr.connection.encoding)

class report_account_aged_partner(models.AbstractModel):
    _inherit = "account.aged.partner"

    filter_seller = True