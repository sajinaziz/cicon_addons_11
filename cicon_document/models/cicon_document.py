from odoo import models,fields,api


class CiconDocumentDirectoryProperty(models.Model):
    _name = 'cicon.document.directory.property'
    _description = "Directory Property"

    name = fields.Char('Property Name', required=True)

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', "Property Name Should be Unique" )]


class CiconDocumentDirectory(models.Model):
    _name = 'cicon.document.directory'
    _description = "CICON Document Directory"

    name = fields.Char('Directory Name', required=True)
    # parent_id = fields.Many2one('cicon.document.directory', string='Parent Directory')
    property_ids = fields.Many2many('cicon.document.directory.property', 'cicon_doc_dir_property_rel',
                                    'directory_id', "property_id", string="Properties")

    _sql_constraints = [('uniq_dir_name', 'UNIQUE(name)', "Directory Name Should be Unique")]


class CiconDocumentPropertyValue(models.Model):
    _name = 'cicon.document.property.value'
    _description = "Document Directory Property"

    document_id = fields.Many2one('cicon.document', string="Document", ondelete='cascade')
    property_id = fields.Many2one('cicon.document.directory.property', "Property", required=True)
    property_value = fields.Char('Value', required=True)

    _sql_constraints = [('uniq_name', 'UNIQUE(document_id,property_id)', "Property Should be Unique")]


class CiconDocument(models.Model):
    _name = 'cicon.document'
    _description = "CICON Documents"

    @api.depends('res_model', 'res_id')
    def _compute_reference(self):
        for _rec in self:
            if _rec.rev_number > 0:
                _rec.display_name = _rec.name + "-Rev." + str(_rec.rev_number)
            else:
                _rec.display_name = _rec.name

            if _rec.res_model and _rec.res_id:
                _rec.reference = "%s,%s" % (_rec.res_model, _rec.res_id)

    def _get_all_parents(self):
        for _rec in self:
            parent = self._parent_name
            cr = self._cr
            parent_ids = []
            query = 'SELECT "%s" FROM "%s" WHERE id = %%s' % (parent, self._table)
            current_id = _rec.id
            while current_id:
                cr.execute(query, (current_id,))
                result = cr.fetchone()
                current_id = result[0] if result else False
                if current_id:
                    parent_ids.append(current_id)
            _rec.parent_ids = parent_ids

    @api.depends('doc_code')
    def _count_doc_code(self):
        for _rec in self:
            if _rec.id:
                _rec.doc_code_count = self.env['cicon.document'].search_count([('dir_id', '=', _rec.dir_id.id),
                                                                           ('doc_code','=ilike',_rec.doc_code),
                                                                           ('id','not in', _rec.parent_ids._ids),
                                                                           ('id', '!=', _rec.id)
                                                                           ])

    display_name = fields.Char(compute=_compute_reference , string="Document")
    name = fields.Char('Document Name', required=True,copy=False)
    parent_id = fields.Many2one('cicon.document', string='Parent Document',copy=False)
    rev_number = fields.Integer('Revision', default=0, required=True, copy=False)

    dir_id = fields.Many2one('cicon.document.directory', string='Directory', required=True)
    doc_code = fields.Char('Document ID', required=True)
    doc_code_count = fields.Integer('Duplicate Count', compute=_count_doc_code)
    note = fields.Text('Notes')
    description = fields.Char("Description")
    is_private = fields.Boolean('Private', default=False)
    expiry_date = fields.Date('Document Expiry', copy=False)
    res_model = fields.Char('Resource Model')
    res_id = fields.Integer('Resource ID')
    reference = fields.Char(string='Reference', compute='_compute_reference', readonly=True, store=False)
    attachment_ids = fields.Many2many('ir.attachment', 'cicon_document_attachment_rel', 'cicon_document_id',
                                      'attachment_id', 'Attachments',
                                      help="You may attach files to this Document", required=True, copy=False)
    property_ids = fields.Many2many(related='dir_id.property_ids', store=False, string="Properties")
    property_value_ids = fields.One2many('cicon.document.property.value', 'document_id', string="Property Values")

    doc_date = fields.Date('Date', default=fields.Date.today(), copy=False)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, copy=False)
    state = fields.Selection([('active', 'Active'), ('inactive', 'In-Active')], string="Status", default='active', copy=False)
    parent_ids = fields.Many2many('cicon.document',compute=_get_all_parents,store=False,readonly=True)


    #_sql_constraints = [('uniq_doc_code', 'UNIQUE(dir_id,doc_code,rev_number)', "Document Code Should be Unique")]

    @api.onchange('parent_id')
    def onchange_parent(self):
        if self.parent_id:
            self.name = self.parent_id.name
            self.rev_number = self.parent_id.rev_number +1
            self.dir_id = self.parent_id.dir_id
            self.doc_code = self.parent_id.doc_code
            self.note = self.parent_id.note
            self.description = self.parent_id.description
            self.is_private = self.parent_id.is_private
            self.res_model = self.parent_id.res_model
            self.res_id = self.parent_id.res_id

    def revise_document(self):
        self.ensure_one()  # One Record
        form_id = self.env.ref('cicon_document.cicon_document_base_form')
        ctx = dict(
            default_parent_id=self.id,
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

    def get_similar_doc(self):
        self.ensure_one()  # One Record
        _dup_docs_ids = self.env['cicon.document'].search([('dir_id', '=', self.dir_id.id),
                                                 ('doc_code', '=ilike', self.doc_code),
                                                 ('id', 'not in', self.parent_ids._ids),
                                                  ('id', '!=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'name': 'Similar Documents',
            'view_mode': 'tree,form',
            'res_model': 'cicon.document',
            'target': 'current',
            'domain': [('state','=','active'), ('id','in',_dup_docs_ids.ids)]
        }


    @api.model
    def create(self, vals):
        _res = super(CiconDocument, self).create(vals=vals)
        if _res.parent_id:
            _res.parent_id.write({'state': 'inactive'})
        return _res



