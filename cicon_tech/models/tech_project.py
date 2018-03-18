from odoo import models, fields, api


class CiconCustJobSite(models.Model):
    _inherit = 'cicon.job.site'

    @api.model
    def _get_last_site_ref(self):
        """ Compute last created site Ref on field on Creation Form 'last_site_ref' """
        _job_site_id = self.env['cicon.job.site'].search([('site_ref_no','!=',False)], order='id desc', limit=1)
        return _job_site_id.site_ref_no

    @api.multi
    def _get_submittal_count(self):
        """ Compute Valid Submittal Revisions Count for Job Site field 'submittal_count', just to show
        filtered submittal revision on Job Site"""
        _rev_obj = self.env['tech.submittal.revision']
        for _rec in self:
            _sub_count = _rev_obj.search_count([('job_site_id', '=', _rec.id),
                                                                       ('state', '!=', 'resubmitted')])
            _last_submiital = _rev_obj.search([('job_site_id', '=', _rec.id)],order='id desc',limit=1)
            _rec.submittal_count = _sub_count
            _rec.last_submittal_date = _last_submiital.submittal_date

    project_id = fields.Many2one('project.project', 'Project', domain="[('partner_id','=',partner_id)]",
                                 help="Link with Project Management or leave it blank")
    site_ref_no = fields.Char('Site Ref #', size=20,help="Unique Site Reference, Using in Submittal reference Number")
    coordinator_id = fields.Many2one('res.users', 'Co-ordinated By', help="Site Coordinator",
                                     domain="[('login','!=','admin')]")
    site_contact_ids = fields.One2many('tech.project.contact', 'job_site_id', "Job Site Contacts")
    last_site_ref = fields.Char(default=_get_last_site_ref, string='Previous Site Reference',
                                readonly=True, store=False, help="Last created Site Reference")
    submittal_count = fields.Integer(compute=_get_submittal_count, string="Submittal Count")
    last_submittal_date = fields.Date(compute=_get_submittal_count, string='Last Submitted',readonly=True)

    _sql_constraints = [('unique_site_ref', 'UNIQUE(site_ref_no)', 'Unique Site Reference')]


class ResCompany(models.Model):
    _inherit = 'res.company'
    # Each Company Can Set a Prefix , use to Create Reference Code on Submittal
    submittal_prefix = fields.Char('Submittal Prefix')




# class CicJobSite(models.Model):
#     """Job Site Information for Partners  """
#     _name = 'cic.job.site'
#     _description = "Job Site"
#
#     @api.model
#     def _get_last_site_ref(self):
#         """ Compute last created site Ref on field on Creation Form 'last_site_ref' """
#         _job_site_id = self.search([], order='id desc', limit=1)
#         return _job_site_id.site_ref_no
#
#     @api.one
#     def _get_submittal_count(self):
#         """ Compute Valid Submittal Revisions Count for Job Site field 'submittal_count', just to show
#         filtered submittal revision on Job Site"""
#         _sub_count = self.env['tech.submittal.revision'].search_count([('job_site_id', '=', self.id),
#                                                                        ('state', '!=', 'resubmitted')])
#         self.submittal_count = _sub_count
#
#     name = fields.Char('Job Site', size=250, required=True, help="Job Site Name")
#     partner_id = fields.Many2one('res.partner', 'Customer Name', ondelete='restrict',
#                                  domain="[('is_company','=',True),('customer','=',True)]", required=True,
#                                  help="Job Site Customer")
#     project_id = fields.Many2one('project.project', 'Project', domain="[('partner_id','=',partner_id)]",
#                                  help="Link with Project Management or leave it blank")
#     site_ref_no = fields.Char('Site Ref #', size=20, required=True, help="Unique Site Reference, Using in Submittal reference Number")
#     coordinator_id = fields.Many2one('res.users', 'Co-ordinated By', help="Site Coordinator",
#                                      domain="[('login','!=','admin')]")
#     po_box = fields.Char("PO.Box", size=50)
#     telephone = fields.Char('Telephone', size=50)
#     fax = fields.Char('Fax', size=50)
#     site_contact_ids = fields.One2many('tech.project.contact', 'job_site_id', "Job Site Contacts")
#     last_site_ref = fields.Char(default=_get_last_site_ref, string='Previous Site Reference',
#                                 readonly=True, store=False, help="Last created Site Reference")
#     submittal_count = fields.Integer(compute=_get_submittal_count, string="Submittal Count")
#
#     _sql_constraints = [
#         ('unique_customer', 'unique(partner_id,name)', 'Project Name must be unique'),
#         ('unique_site_ref', 'UNIQUE(site_ref_no)', 'Unique Site Reference')]
#
# CicJobSite()




