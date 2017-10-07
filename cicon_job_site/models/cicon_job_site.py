from odoo import models,fields,api


class CiconJobSite(models.Model):

    _name = 'cicon.job.site'
    _description = "Cicon JobSite"
    _inherit = ['mail.thread']

    name = fields.Char('Job Site', size=250, required=True, help="Project Name",  track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', 'Customer Name', ondelete='restrict',
                                 domain="[('is_company','=',True),('customer','=',True)]", required=True,  track_visibility='onchange')
    po_box = fields.Char("PO.Box", size=50)
    telephone = fields.Char('Telephone', size=50)
    fax = fields.Char('Fax', size=50)

    consultant_id = fields.Many2one('res.partner', domain="[('is_consultant','=', True)]", string='Consultant',  track_visibility='onchange' )
    client_id = fields.Many2one('res.partner',  domain="[('is_client','=', True)]", string='Client',  track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company')
    active = fields.Boolean('Active', default=True,  track_visibility='onchange')
    archive = fields.Boolean('Archive', help="This will hide project from reports",  default=False,  track_visibility='onchange')
    note = fields.Text('Notes')

    _sql_constraints = [
        ('unique_cust_project', 'unique(partner_id,name)', 'Project Name must be unique for each customer')]

    @api.multi
    def toggle_archive(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.archive = not record.archive

CiconJobSite()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_consultant = fields.Boolean('Is Consultant')
    is_client = fields.Boolean('Is Client')

