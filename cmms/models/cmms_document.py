from odoo import models, fields, api, tools
from datetime import datetime,date,timedelta
from odoo.tools.mimetypes import guess_mimetype

class CmmsDocument(models.Model):

    _inherit = 'ir.attachment'

    # res_model = fields.Char('Resource Model', readonly=True,
    #                         help="The database object this attachment will be attached to.",defult='cmms.common.report.wizard')


    # @api.model
    # def create(self, vals):
    #     vals['res_model'] = 'cmms.common.report.wizard'
    #     print vals
    #     return super(CmmsDocument, self).create(vals)


CmmsDocument()
