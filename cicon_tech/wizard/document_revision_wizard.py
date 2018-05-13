from odoo import models, fields, api


class DocumentRevisionWizard(models.TransientModel):
    """
     Wizard for document revision multiple documents
    """
    _name = 'tech.document.revision.wizard'
    _description = "Document Revision Helper Wizard"

    date = fields.Date('Date', default=fields.Date.context_today)
    created_by = fields.Many2one('res.users', 'Revision Done By', default=lambda self: self.env.user)
    document_ids = fields.Many2many('tech.submittal.document.revision', store=False, string="Document",
                                    help="Documents to revise")

    @api.model
    def default_get(self, fields):
        """
            Fill fields with default values
             get active_ids (selected document ids)
             and fill in  field documents_ids with revised information as new list
            :parameter fields: fields list

        """
        res = super(DocumentRevisionWizard, self).default_get(fields)
        _selected_docs = self.env['tech.submittal.document.revision'].search([
            ('id', 'in', self._context['active_ids'])])
        _docs = []
        for d in _selected_docs:
            # find status and update if last char isdigit +1
            _status = d.document_status
            _rev_val = _status[-1]
            if _rev_val.isdigit():
                _status = _status[:-1] + str((int(_status[-1]) + 1))
            else:
                _status += str(d.rev_no + 1)
            # Append to the list with special many2many addition commands (0,False, values)
            _docs.append((0, False,
                          {
                              'name': d.name,
                              'document_type_id': d.document_type_id.id,
                              'description': d.description,
                              'document_status': _status,
                              'rev_no': d.rev_no + 1,
                              'parent_id': d.id,
                              'draft_time': 0,
                              'document_id': d.document_id.id,
                              'submittal_id': d.submittal_id.id,
                              'revision_id': d.revision_id.id
                          }
                          ))
        res.update({'document_ids': _docs})
        return res

    @api.model
    def create(self, vals):
        """
            override create as documents vals need to updated with
            date and created by
        """
        _doc_rev_obj = self.env['tech.submittal.document.revision']
        for _doc in vals['document_ids']:
            _doc_rev = _doc[2]
            _doc_rev.update({'date': vals['date']})
            _doc_rev.update({'created_by': vals['created_by']})
            _doc_rev_obj.create(_doc_rev)
        return super(DocumentRevisionWizard, self).create(vals)

    @api.multi
    def revise_drawings(self):
        """Dummy Button Function"""
        return True


class TechBBSWeightWizard(models.TransientModel):
    _name = 'tech.bbs.weight.wizard'
    _description = """ BBS Weight"""

    revision_id = fields.Many2one('tech.submittal.revision', string='Submittal Revision', required=True)
    bbs_weight = fields.Float('BBS Weight', required=True)

    @api.multi
    def update_weight(self):
        self.ensure_one()
        return self.revision_id.write({'bbs_weight': self.bbs_weight})