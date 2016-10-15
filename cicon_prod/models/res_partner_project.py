from odoo import models, fields, api


class res_partner_project(models.Model):
    _name = 'res.partner.project'
    _description = "Partner Project"

    name = fields.Char('Project Name', size=250, required=True)
    partner_id = fields.Many2one('res.partner', 'Customer Name', ondelete='restrict',
                                 domain="[('is_company','=',True),('customer','=',True)]", required=True)


    _sql_constraints = [
        ('unique_customer_project', 'unique(partner_id,name)', 'Project Name must be unique for each customer')]

res_partner_project()

