from odoo import models, fields


class DocumentType(models.Model):
    _name = 'tech.document_type'
    _description = 'Submittal Document Type'
    _log_access = False

    name = fields.Char('Document Type Name', size=50, required=True)
    suffix = fields.Char('Suffix', size=20)

    _sql_constraints = [('unique_doc_type', 'unique(name)', 'Document Type Name Should be Unique')]

