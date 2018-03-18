from odoo import models, fields, api


class CiconTechRfi(models.Model):
    _name = 'cicon.tech.rfi'
    _description = "RFI"

    _inherit = ['mail.thread']

    name = fields.Char('RFI Reference', required=True, index=True)
    partner_id = fields.Many2one('res.partner', string="Customer/Contractor", domain=[('customer', '=', True)], required=True)
    job_site_id = fields.Many2one('cicon.job.site', string="Project / Job Site",
                                  domain="[('partner_id', '=', partner_id)]", required=True)
    site_contact_ids = fields.Many2many('tech.project.contact', 'cicon_tech_rfi_contact_rel',
                                        'rfi_id', 'contact_id', string="Contacts")
    element = fields.Char('Element', required=True)
    rfi_count_on_job_site = fields.Integer("RFI Count")
    level = fields.Char('Level')
    rfi_date = fields.Date('RFI Date', default=fields.Date.context_today, required=True)
    subject = fields.Char('Subject')
    description = fields.Html('Description')
    created_by = fields.Many2one('res.users', string="Raised By", default=lambda self: self.env.user, required=True)
    coordinator_id = fields.Many2one('res.users', 'Co-ordinated By', help="Site Coordinator",
                                     readonly=True,related='job_site_id.coordinator_id',store=False)
    #consultant_id = fields.Many2one('tech.consultant', string="Consultant")
    consultant_id = fields.Many2one('res.partner', string='Consultant', related='job_site_id.consultant_id', readonly=True)

    #attachment_count = fields.Integer('Attachment No:')
    attachment_count = fields.Char('Attachment No:')
    response_last_date = fields.Date("Response Required Date")
    contractor_remarks = fields.Text('Contractor Remarks')
    contractor_subject = fields.Text('Contractor Subject')
    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 default=lambda self: self.env.user.company_id)
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Submitted'), ('done', 'Replied'),
                              ('cancel', 'Cancelled')], string="Status", track_visibility='onchange', required=True, default='draft')

    _sql_constraints = [('unique_rfi', 'UNIQUE(name)', 'RFI Reference Must be Unique'),
                        ('unique_rfi_count', 'UNIQUE(rfi_count_on_job_site,job_site_id)', 'RFI Count Must be Unique / Site')]

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id and self.job_site_id:
            self.job_site_id = None

    def _generate_new_rfi_code(self, job_site_id):
        _rfi_count = 1
        _job_site_obj = self.env['cicon.job.site'].browse(job_site_id)
        _last_rfi_on_site = self.env['cicon.tech.rfi'].search([('job_site_id', '=', _job_site_obj.id)], order="id desc", limit=1)
        if _last_rfi_on_site:
            _rfi_count = _last_rfi_on_site.rfi_count_on_job_site + 1
        _prefix = "RFI-"
        _prefix += self.env.user.company_id.submittal_prefix or 'CIC'
        _rfi_code = _prefix + '-' + str(_job_site_obj.site_ref_no) + '-' + str(_rfi_count).zfill(3)
        return {'rfi_code': _rfi_code, 'rfi_count': _rfi_count}

    @api.onchange('job_site_id')
    def _onchange_job_site(self):
        if self.partner_id and self.job_site_id:
            _new_rfi = self._generate_new_rfi_code(self.job_site_id.id)
            self.name = _new_rfi['rfi_code']
            self.rfi_count_on_job_site = _new_rfi['rfi_count']
            if self.site_contact_ids:
                self.site_contact_ids = None

    @api.multi
    def cancel_rfi(self):
        self.write({'state': 'cancel'})

    @api.multi
    def print_rfi(self):
        self.ensure_one()
        if self.state == 'draft':
            self.write({'state': 'pending'})
        return self.env['report'].get_action(self, 'cicon_tech_rfi.report_rfi_template')

    @api.multi
    def pending_rfi(self):
        self.write({'state': 'pending'})

    @api.multi
    def done_rfi(self):
        self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            _new_rfi_ = self._generate_new_rfi_code(vals.get('job_site_id'))
            vals.update({'name': _new_rfi_['rfi_code']})
        return super(CiconTechRfi, self).create(vals)


