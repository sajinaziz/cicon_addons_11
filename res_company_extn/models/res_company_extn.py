from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    logo2 = fields.Binary('Logo 2',)

ResCompany()


