from odoo import models,fields,api


# class CiconDocument(models.Model):
#     _inherit = 'cicon.document'
#
#     partner_id = fields.Many2one('res.partner', string="Customer")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    document_ids = fields.Many2many('cicon.document', relation='cicon_partner_document_rel' , column1='partner_id',
                                    column2='document_id', groups="cicon_document.cicon_document_user", string="Documents",
                                    domain=[('state', '=', 'active')]
                                    )
