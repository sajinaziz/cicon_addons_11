from odoo import models, fields, api


class QcMaterialGrade(models.Model):
    _name = 'qc.material.grade'
    _description = "Material Grade"

    name = fields.Char('Grade', required=True)

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'Grade Must be Unique!')]


class QcMaterialApproval(models.Model):
    _name = 'qc.material.approval'
    _description = "QC Material Approval"
    _inherit = ['mail.thread']
    _rec_name = 'display_name'

    def _display_name(self):
        for rec in self:
            rec.display_name = rec.job_site_id.name + ' / ' + rec.origin_attrib_value_id.name

    display_name = fields.Char("Record", compute=_display_name)
    job_site_id = fields.Many2one('cicon.job.site', string="Job Site")
    date = fields.Date('Date', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', related='job_site_id.partner_id', string='Customer', readonly=True)
    consultant_id = fields.Many2one('res.partner', related='job_site_id.consultant_id', string='Consultant', readonly=True)
    client_id = fields.Many2one('res.partner', related='job_site_id.consultant_id', string='Client' , readonly=True)
    origin_attrib_value_id = fields.Many2one('product.attribute.value',
                                             domain="[('attribute_id.name','=','Steel Origin' )]", string='Origin')
    state = fields.Selection([('pending', 'Pending'),
                              ('verbal', 'Verbal'), ('approve', 'Approved'),
                              ('reject', 'Rejected')], string='Status', default='pending', track_visibility='onchange')
    remarks = fields.Text('Remarks')

    _sql_constraints = [('uniq_rec', 'UNIQUE(job_site_id,origin_attrib_value_id)', 'Origin must be unique for Job Site!')]


    @api.multi
    def set_pending(self):
        self.ensure_one()
        self.write({'state': 'pending'})

    @api.multi
    def set_approve(self):
        self.ensure_one()
        self.write({'state': 'approve'})

    @api.multi
    def set_verbal(self):
        self.ensure_one()
        self.write({'state': 'verbal'})

    @api.multi
    def set_reject(self):
        self.ensure_one()
        self.write({'state': 'reject'})


class CiconJobSite(models.Model):
    _inherit = 'cicon.job.site'

    qc_material_approval_ids = fields.One2many('qc.material.approval', 'job_site_id', string="Material Approvals")



