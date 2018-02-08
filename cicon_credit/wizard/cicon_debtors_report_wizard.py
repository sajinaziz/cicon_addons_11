from odoo import fields, models, api


class CiconDebtorsReportWizard(models.TransientModel):
    _name = 'cicon.debtors.report.wizard'
    _description = "CICON Debtors Report Wizard"

    start_date = fields.Date('From')
    end_date = fields.Date('To')
    partner_ids = fields.Many2many('res.partner',relation='cicon_debtor_report_partner_rel',column1='wizard_id',
                                   column2='partner_id', string='Partners')

    @api.multi
    def show_report(self):
        return self.env.ref('cicon_credit.action_cicon_debtors_report').report_action(self.partner_ids)

