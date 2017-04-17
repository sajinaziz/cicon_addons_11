from odoo import models, fields, api
from odoo.exceptions import UserError

JOB_ORDER_TYPE = [('breakdown', 'BREAKDOWN'), ('general', 'GENERAL')]


class CmmsJobOrderMasterWizard(models.TransientModel):
    _name = "cmms.job.order.master.wizard"
    _description = "CMMS Job Order Master Wizard"

    job_order_type = fields.Selection(JOB_ORDER_TYPE, "Job Order Type", required=True)
    last_code = fields.Char('Last Job Code', readonly=True, store=False)
    to_number = fields.Integer('Number of Job Order Required (Max 50)', default=20)

    @api.onchange('job_order_type')
    def _get_last(self):
        _master_obj = self.env['cmms.job.order.code']
        _rec = _master_obj.search([('job_order_type', '=', self.job_order_type), ('company_id', '=',  self.env.user.company_id.id)], order='id desc', limit=1)
        if _rec:
            self.last_code = _rec.name
        else:
            self.last_code = '/'

    @api.multi
    def generate_job_order(self):
        if self.to_number < 51:
            _job_obj = self.env['cmms.job.order.code']
            _j_ids = []
            for x in range(1, self.to_number + 1):
                _job = {
                    'created': False,
                    'printed': True,
                    'cancelled': False,
                    'job_order_type': self.job_order_type,
                    'company_id': self.env.user.company_id.id
                }

                _seq_obj_breakdown = self.env['ir.sequence'].search([('company_id', '=', self.env.user.company_id.id),
                                                                     ('code', '=', 'cmms.job.order.master.breakdown')])
                _seq_obj_gen = self.env['ir.sequence'].search([('code', '=', 'cmms.job.order.master.general'),
                                                               ('company_id', '=', self.env.user.company_id.id)])
                if self.job_order_type == 'breakdown' and _seq_obj_breakdown:
                    _job.update({'name': _seq_obj_breakdown.next_by_id()})
                elif self.job_order_type == 'general' and _seq_obj_gen:
                    _job.update({'name': _seq_obj_gen.next_by_id()})
                res = _job_obj.create(_job)
                if res:
                    _j_ids.append(res.id)
            if _j_ids:
                _job_codes = _job_obj.search([('id', 'in', _j_ids)])
                return self.env['report'].get_action(_job_codes, 'cmms.cmms_job_order_blank_template')
            else:
                return False
        else:
            raise UserError("Maximum 20 Records !")


CmmsJobOrderMasterWizard()
