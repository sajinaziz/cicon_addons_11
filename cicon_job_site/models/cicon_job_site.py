from odoo import models,fields,api

class CiconJobSite(models.Model):

    _name = 'cicon.job.site'
    _description = "Cicon JobSite"
    _inherit = ['mail.thread']

    name = fields.Char('Job Site', size=250, required=True, help="Project Name")
    partner_id = fields.Many2one('res.partner', 'Customer Name', ondelete='restrict',
                                 domain="[('is_company','=',True),('customer','=',True)]", required=True)
    po_box = fields.Char("PO.Box", size=50)
    telephone = fields.Char('Telephone', size=50)
    fax = fields.Char('Fax', size=50)

    _sql_constraints = [
        ('unique_cust_project', 'unique(partner_id,name)', 'Project Name must be unique for each customer')]

CiconJobSite()