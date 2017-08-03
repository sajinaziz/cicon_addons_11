from odoo import models, fields, api


class QcCommonReportWizard(models.TransientModel):
    _name = 'qc.common.report.wizard'
    _description = "QC Reports"

    report_list = fields.Selection([('steel_approval_report', 'Steel Approval Report')],string='Report', required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    @api.multi
    def show_report(self, data):
        self.ensure_one()
        ctx = dict(self._context)
        job_sites = self.env['qc.material.approval'].search([]).mapped('job_site_id')
        if self.company_id:
            ctx['company_id'] = self.company_id.id
        if self.report_list == 'steel_approval_report':
            ctx['heading'] = "Steel Approval Report"
            return self.with_context(ctx).env['report'].get_action(job_sites, 'cicon_qc.qc_material_approval_report_template')


