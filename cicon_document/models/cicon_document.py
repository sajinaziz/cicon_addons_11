from odoo import models,fields,api


class CiconDocumentDirectory(models.Model):
    _name = 'cicon.document.directory'
    _description = "CICON Document Directory"

    name = fields.Char('Directory Name', required=True)
    parent_id = fields.Many2one('cicon.document.directory', string='Parent Directory')


class Documents(models.Model):
    _name = 'cicon.document'
    _description = "CICON Documents"

    # @api.depends('res_model', 'res_id')
    # def _compute_reference(self):
    #     for res in self:
    #         if res.res_model and res.res_id:
    #             res.reference = "%s,%s" % (res.res_model, res.res_id)

    name = fields.Char('Document Name', required=True)
    dir_id = fields.Many2one('cicon.document.directory', string='Directory', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    note = fields.Text('Notes')
    description = fields.Char("Description")
    is_private = fields.Boolean('Private', default=False)
    expiry_date = fields.Date('Document Expiry')
    res_model = fields.Char('Resource Model')
    res_id = fields.Integer('Resource ID')
    #reference = fields.Char(string='Reference', compute='_compute_reference', readonly=True, store=False)
    attachment_ids = fields.Many2many('ir.attachment', 'cicon_document_attachment_rel', 'cicon_document_id',
                                      'attachment_id', 'Attachments',
                                      help="You may attach files to this Document")



