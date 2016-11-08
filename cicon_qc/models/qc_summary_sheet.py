from odoo import models,  fields, api
from datetime import time


class QcSummary(models.Model):
    _name = 'cic.qc.summary'
    _description = "QC Summary Sheet"

    @api.one
    @api.depends('dn_line_ids', 'certificate_line_ids')
    def _get_order_codes(self):
        _code_ids = []
        _mill_ids = []
        for d in self.dn_line_ids:
            _code_ids.extend([o.id for o in d.order_code_ids])
        for m in self.certificate_line_ids:
            _mill_ids.extend([m.certificate_id.id])
        self.order_codes = _code_ids
        self.heat_numbers = _mill_ids

    def _search_order_code(self, operator, value):
        _order_codes = self.env['cicon.prod.order'].search([('name', operator, value)])
        _prod_dns = self.env['cicon.prod.delivery.order'].search([('prod_order_ids', 'in', _order_codes.ids)])
        _qc_dn_line_ids = self.env['cic.qc.dn.line'].search([('delivery_order_id', 'in', _prod_dns.ids)])
        _summary_ids = [s.qc_summary_id.id for s in _qc_dn_line_ids]
        return [('id', 'in', _summary_ids)]

    def _search_heat_number(self, operator, value):
        _heat_nos = self.env['cic.qc.mill.cert.line'].search([('name', operator, value)])
        _heat_ids = [o.id for o in _heat_nos]
        _cert_line_ids = self.env['cic.qc.cert.line'].search([('certificate_id', 'in', _heat_ids)])
        _summary_ids = [s.qc_summary_id.id for s in _cert_line_ids]
        return [('id', 'in', _summary_ids)]

    def _get_attachments(self):
        if self.certificate_line_ids:
            _cert_ids = self.certificate_line_ids.mapped('certificate_id')
            _file_ids = _cert_ids.mapped('cert_file_id')
            _attach_ids = self.env['ir.attachment'].search([('res_model', '=', 'cic.qc.mill.cert.file'),
                                                            ('res_id', 'in', _file_ids._ids)])
            self.attachment_ids = list(_attach_ids._ids)

    name = fields.Char('Trip Reference', readonly=True,default='New')
    dn_date = fields.Date('DN Date', required=True, default=fields.Date.context_today)
    delivery_date = fields.Date('Delivery Date', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', domain="[('customer','=',True)]", string="Customer", required=True)
    project_id = fields.Many2one('cicon.job.site', 'Project', domain="[('partner_id','=',partner_id)]")
    certificate_line_ids = fields.One2many('cic.qc.cert.line', 'qc_summary_id', string="Mill Certificates")
    dn_line_ids = fields.One2many('cic.qc.dn.line', 'qc_summary_id', string="Delivery Notes")
    wb_ticket = fields.Integer('Weigh Bridge')
    loading_list = fields.Boolean('Loading List')
    order_codes = fields.Many2many('cicon.prod.order', compute=_get_order_codes, search=_search_order_code, store=False, string='Order Codes', readonly=True)
    heat_numbers = fields.Many2many('cic.qc.mill.cert.line', compute=_get_order_codes, search=_search_heat_number, store=False, string='Heat Numbers', readonly=True)
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id ,required=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments', compute=_get_attachments, readonly=True,store=False)

    _sql_constraints = [('uniq_summary', 'UNIQUE(name)', 'Summary Name Must be Unique')]

    _order = 'id desc'

    @api.model
    def create(self, vals):
        _qc_summary_seq = self.env['ir.sequence'].search([('company_id', '=', self.env.user.company_id.id),
                                                          ('code', '=', 'cic.qc.summary.seq')])
        vals.update({'name': _qc_summary_seq.next_by_id() or time.strftime('%Y/%m/%d/%H/%M')})

        # vals['name'] = self.env['ir.sequence'].next_by_code('cic.qc.summary.seq') or 'New'
        return super(QcSummary, self).create(vals)

QcSummary()


class QcCertLine(models.Model):
    _name = 'cic.qc.cert.line'
    _description = 'CICON Certificates Note'

    qc_summary_id = fields.Many2one('cic.qc.summary', string='QC Summary', required=True, ondelete='cascade')
    certificate_id = fields.Many2one('cic.qc.mill.cert.line', string='Heat Number')
    dia_attrib_value_id = fields.Many2one('product.attribute.value', related='certificate_id.dia_attrib_value_id',
                                          readonly=True, string='Diameter', store=False)
    origin_attrib_value_id = fields.Many2one('product.attribute.value', related='certificate_id.origin_attrib_value_id',
                                          readonly=True, string='Origin', store=False)
    length_attrib_value_id = fields.Many2one('product.attribute.value', related='certificate_id.length_attrib_value_id',
                                          readonly=True, string='Length', store=False)
    issued_date = fields.Date('Issued Date', related='certificate_id.cert_file_id.issued_date', readonly=True)
    page_number = fields.Char('Page Number', related='certificate_id.cert_file_id.page_number', readonly=True, store=False)

    quantity = fields.Float('Remarks', digits=(10, 3))
    sequence = fields.Integer('Sequence')

    _order = 'sequence'

    @api.onchange('certificate_id')
    def _onchange_certificate(self):
        if self.certificate_id:
            self.sequence = self.certificate_id.dia_attrib_value_id.sequence

    #_sql_constraints = [('uniq_line', 'UNIQUE(qc_summary_id,dia_attrib_value_id,origin_attrib_value_id)', 'Cert Line Name Must be Unique')]
    _sql_constraints = [('uniq_line', 'CHECK(1=1)','Cert Line Name Must be Unique')]

QcCertLine()


class QcDnLine(models.Model):
    _name = 'cic.qc.dn.line'
    _description = 'CICON Delivery Note'
    _rec_name = 'delivery_order_id'

    # dn_no = fields.Char('Delivery Note Number', required=True)
    delivery_order_id = fields.Many2one('cicon.prod.delivery.order', string="Delivery Note", required=True)
    qc_summary_id = fields.Many2one('cic.qc.summary', string='QC Summary', ondelete='cascade')
    #order_code_ids = fields.Many2many('cic.qc.order.code', 'dn_line_id', 'order_code_id', string='Order Codes')
    order_code_ids = fields.Many2many('cicon.prod.order', related='delivery_order_id.prod_order_ids',
                                      string='Order Codes', readonly=True)

    #_sql_constraints = [('uniq_dn', 'UNIQUE(dn_no)', 'DN  Must be Unique')]
    _sql_constraints = [('uniq_dn', 'UNIQUE(delivery_order_id,qc_summary_id)', 'DN  Must be Unique')]

QcDnLine()


class QcCertType(models.Model):
    _name = 'cic.qc.cert.type'
    _description = "CICON Mill Certificate Type"

    name = fields.Char('Certificate Type', required=True)

    _sql_constraints = [('uniq_cert_type', 'UNIQUE(name)', 'Certificate Type Must be Unique')]

QcCertType()


class QcMillCertFile(models.Model):
    _name = 'cic.qc.mill.cert.file'
    _description = "CICON Mill Certificate file"

    @api.one
    @api.depends('certificates_ids')
    def _get_default_val(self):
        if self.certificates_ids:
            self.default_dia_val = self.certificates_ids[0].dia_attrib_value_id
            self.default_length_val = self.certificates_ids[0].length_attrib_value_id

    @api.multi
    def _get_dia(self):
        for rec in self:
            if rec.certificates_ids:
                rec.dia_ids = rec.certificates_ids.mapped('dia_attrib_value_id')
                rec.length_ids = rec.certificates_ids.mapped('length_attrib_value_id')
                rec.heat_nos = ','.join(i.name for i in rec.certificates_ids)

    def _search_dia(self, operator, value):
        _cert_lines = self.env['cic.qc.mill.cert.line'].search([('dia_attrib_value_id', operator, value)])
        _cert_file_ids = _cert_lines.mapped('cert_file_id')
        return [('id', 'in', _cert_file_ids._ids)]

    def _search_length(self, operator, value):
        _cert_lines = self.env['cic.qc.mill.cert.line'].search([('length_attrib_value_id', operator, value)])
        _cert_file_ids = _cert_lines.mapped('cert_file_id')
        return [('id', 'in', _cert_file_ids._ids)]

    def _search_heat_no(self, operator, value):
        _cert_lines = self.env['cic.qc.mill.cert.line'].search([('name', operator, value)])
        _cert_file_ids = _cert_lines.mapped('cert_file_id')
        return [('id', 'in', _cert_file_ids._ids)]

    name = fields.Char('Certificate Number', index=True, size=32, required=True)
    supplier_id = fields.Many2one('res.partner', domain=[('supplier', '=', True)], required=True, string='Supplier')
    page_number = fields.Char('Page Number')
    description = fields.Char('Description')
    cert_type_id = fields.Many2one('cic.qc.cert.type', string="Certificate Type", required=True)
    issued_date = fields.Date('Issued Date', required=True)
    product_template = fields.Many2one('product.template', string="Product Template", required=True)
    origin_attrib_value_id = fields.Many2one('product.attribute.value',
                                             domain="[('attribute_id.name','=','Steel Origin' )]", string='Origin')
    certificates_ids = fields.One2many('cic.qc.mill.cert.line', 'cert_file_id', string='Heat Numbers',
                                        required=True)
    file_path = fields.Char('File Path ')
    default_dia_val = fields.Many2one('product.attribute.value', string="Default Dia Value", compute=_get_default_val)
    default_length_val = fields.Many2one('product.attribute.value', string="Default Length Value",
                                         compute=_get_default_val)
    dia_ids = fields.Many2many('product.attribute.value', string="Diameter", readonly=True,
                               compute=_get_dia, search=_search_dia)
    length_ids = fields.Many2many('product.attribute.value', string="Length", readonly=True,
                                  compute=_get_dia, search=_search_length)
    heat_nos = fields.Char("Heat Numbers", compute=_get_dia, store=False, readonly=True, search=_search_heat_no)

    _order = 'id desc'

    _sql_constraints = [('unique_name', 'UNIQUE(supplier_id,name)', 'Certificate Number must be Unique')]

QcMillCertFile()




class QcMillCertLine(models.Model):
    _name = 'cic.qc.mill.cert.line'
    _description = 'CICON Mill Certificate Line'
    _rec_name = 'name'

    name = fields.Char("Heat Number", index=True, required=True)
    cert_file_id = fields.Many2one('cic.qc.mill.cert.file', string='Certificate File', ondelete='cascade')
    product_template = fields.Many2one('product.template', related='cert_file_id.product_template',
                                       string="Product Template",  store=True, readonly=True)
    origin_attrib_value_id = fields.Many2one('product.attribute.value', related='cert_file_id.origin_attrib_value_id',
                                             store=True, readonly=True, string='Origin')
    dia_attrib_value_id = fields.Many2one('product.attribute.value',
                                          domain="[('attribute_id.name','=','Diameter')]", string='Diameter')
    length_attrib_value_id = fields.Many2one('product.attribute.value', domain="[('attribute_id.name','=','Length')]",
                                             string='Length')
    issued_date = fields.Date( related='cert_file_id.issued_date', readonly=True, store=False)


    _sql_constraints = [('uniq_cert', 'UNIQUE(name,cert_file_id)', 'Summary Name Must be Unique')]

QcMillCertLine()





