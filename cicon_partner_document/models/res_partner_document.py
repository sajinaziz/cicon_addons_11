from odoo import models,fields,api


class CiconDocument(models.Model):
    _inherit = 'cicon.document'

    partner_ids = fields.Many2many('res.partner', relation='cicon_partner_document_rel', column1='document_id', column2='partner_id', string="Customers")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    document_ids = fields.Many2many('cicon.document', relation='cicon_partner_document_rel' , column1='partner_id',
                                    column2='document_id', groups="cicon_document.cicon_document_user", string="Documents",
                                    domain=[('state', '=', 'active')]
                                    )

    def customer_new_doc(self):
        self.ensure_one()  # One Record
        form_id = self.env.ref('cicon_document.cicon_document_base_form')
        ctx = dict(
            default_res_model='res.partner',
            default_res_id=self.id,
            default_partner_ids =[self.id]
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cicon.document',
            'views': [(form_id.id, 'form')],
            'view_id': form_id.id,
            'target': 'current',
            'context': ctx,
        }
