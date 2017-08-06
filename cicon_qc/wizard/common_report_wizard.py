from odoo import models, fields, api


class QcCommonReportWizard(models.TransientModel):
    _name = 'qc.common.report.wizard'
    _description = "QC Reports"

    report_list = fields.Selection([('steel_approval_report', 'Steel Approval Report')],string='Report', required=True)
    option_select = fields.Selection([('include', 'Include'), ('exclude', 'Exclude')], string="Options",
                                     default='include', help='Include/Exclude records')
    origin_value_ids = fields.Many2many('product.attribute.value',
                                             domain="[('attribute_id.name','=','Steel Origin' )]", string='Origins')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    @api.multi
    def show_report(self, data):
        self.ensure_one()
        ctx = dict(self._context)
        if self.company_id:
            ctx['company_id'] = self.company_id.id
        if self.report_list == 'steel_approval_report':
            ctx['heading'] = "Steel Approval Report"
            _qry = [('attribute_id.name','=','Steel Origin' )]
            if self.origin_value_ids:
                if self.option_select =='include':
                    _qry.append(('id', 'in', self.origin_value_ids._ids))
                elif self.option_select =='exclude':
                    _qry.append(('id', 'not in', self.origin_value_ids._ids))
            _origin_ids = self.env['product.attribute.value'].search(_qry)
            job_sites = self.with_context(ctx).env['qc.material.approval'].search([]).mapped('job_site_id').filtered(lambda a: a.archive == False)
            _datas = {'origin_ids': _origin_ids._ids}
            return self.with_context(ctx).env['report'].get_action(job_sites, report_name='cicon_qc.qc_material_approval_report_template',data=_datas)


