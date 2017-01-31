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

    consultant_id = fields.Many2one('res.partner', string='Consultant' )
    client_id = fields.Many2one('res.partner', string = 'Client')
    company_id = fields.Many2one('res.company', string='Company')

    _sql_constraints = [
        ('unique_cust_project', 'unique(partner_id,name)', 'Project Name must be unique for each customer')]

CiconJobSite()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_consultant = fields.Boolean('Is Consultant')
    is_client = fields.Boolean('Is Client')

