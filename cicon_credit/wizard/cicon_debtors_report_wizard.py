from odoo import fields, models, api


class CiconDebtorsReportWizard(models.TransientModel):
    _name = 'cicon.debtors.report.wizard'
    _description = "CICON Debtors Report Wizard"

    report_option = fields.Selection([('report_sun_check', 'Aging Report (With LC & Check)'),
                                      ('report_sun_aging', 'Aging Report (Sun System)')], string='Report Options',
                                     default='report_sun_check')
    report_period = fields.Selection([('invoice_date', 'Invoice Date'), ('invoice_period', 'Invoice Period')],
                                     default='invoice_date', string="Report Period")
    start_date = fields.Date('From')
    end_date = fields.Date('To')

    @api.multi
    def show_report(self):
        _company = self.env.user.company_id
        return self.env.ref('cicon_credit.action_cicon_debtors_report').report_action(_company)

