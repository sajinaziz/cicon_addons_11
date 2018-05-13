from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    logo2 = fields.Binary('Logo 2')
    #Fax field Removed in Odoo 11 re added as still maintained in Region
    fax = fields.Char("Fax")




