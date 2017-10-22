from datetime import datetime
from dateutil.relativedelta import *
from odoo import models, fields, api
from odoo.exceptions import *


class CiconSteelWeightType(models.Model):
    _name =  'cicon.steel.weight.type'
    _description = 'Weight Type'

    name = fields.Char('Weight Type', required=True)
    allowed_template_ids = fields.Many2many('product.template', 'cicon_weight_type_tmpl_rel', 'weight_type_id', 'template_id', string='Allowed Templates')

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'Unique Name')]

CiconSteelWeightType()


class CiconContract(models.Model):
    _name = "cicon.contract"
    _inherit = ['mail.thread']
    _description = "Contract/LPO"

    @api.depends('contract_line_ids')
    def _get_products(self):
        _products = []
        for rec in self:
            for l in rec.contract_line_ids:
                _products.extend(l.mapped('prod_group_tmpl_id.product_ids'))
            _Ids = [x.id for x in _products]
            rec.product_ids = _Ids

    def _get_prod_order_count(self):
        for rec in self:
            rec.prod_order_count = len(self.prod_order_ids) or 0

    partner_id = fields.Many2one('res.partner', "Customer", domain=[('customer', '=', True)], required=True,
                                 readonly=True, states={'new': [('readonly', False)]})
    name = fields.Char('LPO Reference', required=True, readonly=True, states={'new': [('readonly', False)]}, track_visibility='always')
    code = fields.Char('Internal Reference',  readonly=True, states={'new': [('readonly', False)]}, track_visibility='onchange')
    contract_date = fields.Date('Contract Date',  readonly=True, states={'new': [('readonly', False)]}, track_visibility='onchange',
                                default=fields.Date.context_today)
    start_date = fields.Date('Start Date',  readonly=True, states={'new': [('readonly', False)]}, track_visibility='onchange')
    end_date = fields.Date('End/Expiry Date',  readonly=True, states={'new': [('readonly', False)]}, track_visibility='onchange')
    # project_ids = fields.Many2many('res.partner.project', 'cicon_prod_contract_proj_rel', 'contract_id', 'project_id',
    #                                string="Projects",  readonly=True, states={'new': [('readonly', False)]})

    project_ids = fields.Many2many('cicon.job.site', 'cicon_prod_contract_proj_rel', 'contract_id', 'project_id',
                                   string="Projects", readonly=True, states={'new': [('readonly', False)]})
    contract_line_ids = fields.One2many('cicon.contract.line', 'contract_id', "Contract Lines",
                                        readonly=True, states={'new': [('readonly', False)]})
    bbs_provider = fields.Selection([('cicon', 'By CICON'), ('customer', 'By Customer')], string="BBS",
                                    readonly=True, states={'new': [('readonly', False)]})
    stb_in_bbs = fields.Boolean('Straight Bar Include in BBS',  readonly=True, states={'new': [('readonly', False)]})
    weight_type_ids = fields.One2many('cicon.contract.weight.type', 'contract_id', string="Weight Types",
                                      readonly=True, states={'new': [('readonly', False)]})
    stb_as_cb = fields.Boolean('Straight Bar in BBS Charged as Cut & Bend',
                               readonly=True, states={'new': [('readonly', False)]})
    remarks = fields.Text('Remarks',  readonly=True, states={'new': [('readonly', False)]})
    payment_terms = fields.Text('Payment Terms & Conditions',  readonly=True, states={'new': [('readonly', False)]})
    steel_origin_ids = fields.Many2many('product.attribute.value', 'cicon_prod_contract_origin_rel',
                                        'contract_id', 'origin_id', string="Allowed Origins",  readonly=True, states={'new': [('readonly', False)]})
    allow_other_origin = fields.Boolean("Steel Origin Mixing Allowed", default=False, readonly=True, states={'new': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string="Created By",   readonly=True, states={'new': [('readonly', False)]})
    validity_type = fields.Selection([('date', 'Period'), ('quantity', 'Quantity'), ('date_quantity', 'Period/Quantity')],
                                     string='Validity Type', default='date',  readonly=True, states={'new': [('readonly', False)]}, track_visibility='onchange')
    extra_days_allowed = fields.Integer('Extra Day(s)',  readonly=True, states={'new': [('readonly', False)]}, track_visibility='onchange')
    product_ids = fields.Many2many('product.product', compute=_get_products, string="Product", readonly=True)
    prod_order_ids = fields.One2many('cicon.prod.order', 'contract_id', string="Production Orders", readonly=True)
    state = fields.Selection([('new', 'Draft'), ('active', 'Active'), ('expired', 'Expired'), ('close', 'Closed')],
                             default='new', string='Status', track_visibility='onchange')
    prod_order_count = fields.Integer('Production Order Count', compute=_get_prod_order_count, store=False, readonly=True)

    _sql_constraints = [('uniq_name', 'UNIQUE(name,partner_id)', 'Unique Name Per Customer')]

    @api.one
    @api.constrains('contract_line_ids')
    def _check_products(self):
        _product_ids = []
        _product_ids.extend(i for x in self.contract_line_ids for i in x.prod_group_tmpl_id.product_ids._ids )
        _set_prod_ids = list(set(_product_ids))
        if len(_set_prod_ids) < len(_product_ids):
            raise UserError("Duplicate Products Found , Please Remove !")

    @api.multi
    def set_active(self):
        return self.write({'state': 'active'})

    @api.multi
    def set_expired(self):
        return self.write({'state': 'expired'})

    @api.multi
    def set_close(self):
        return self.write({'state': 'close'})

    @api.multi
    def set_draft(self):
        return self.write({'state': 'new'})


CiconContract()


class CiconContractWeightType(models.Model):
    _name = 'cicon.contract.weight.type'
    _description = "Contract Weight Type"

    contract_id = fields.Many2one('cicon.contract', string="Contract")
    template_id = fields.Many2one('product.template', string="Product Template", required=True)
    weight_type_id = fields.Many2one('cicon.steel.weight.type', string="Weight Type", required=True)

    _sql_constraints = [('uniq_entry', 'UNIQUE(contract_id,template_id)', 'Unique Template Per Contract')]

CiconContractWeightType()


class CiconContractLine(models.Model):
    _name = 'cicon.contract.line'
    _description = "Contract Lines"

    def _get_balance_qty(self):
        for rec in self:
            _prod_orders = self.env['cicon.prod.order'].search([('contract_id', '=', rec.contract_id.id)])
            _move_lines = self.env['cicon.prod.order.line'].search([('prod_order_id', 'in', _prod_orders._ids),
                                                                    ('product_id', 'in', rec.prod_group_tmpl_id.product_ids._ids)])
            rec.delivered_qty = sum(x.product_qty for x in _move_lines if x.prod_order_id.state == 'delivered')
            rec.pending_qty = sum(x.product_qty for x in _move_lines if x.prod_order_id.state not in ('delivered', 'cancel', 'pending'))
            rec.return_qty = sum(x.product_qty for x in _move_lines if x.prod_order_id.state == 'return')
            rec.balance_qty = ((rec.quantity - rec.delivered_qty) - rec.pending_qty) + rec.return_qty

    prod_group_tmpl_id = fields.Many2one('cicon.product.group.template', 'Product Group Template', required=True)
    description = fields.Char(related='prod_group_tmpl_id.description', string="Description", readonly=True)
    unit_id = fields.Many2one('product.uom', related='prod_group_tmpl_id.unit_id', string="Unit", readonly=True)
    contract_id = fields.Many2one('cicon.contract', string="Contract/LPO")
    quantity = fields.Float('Quantity', decimal=(18, 3), required=True)
    extra_qty_allowed = fields.Integer('Extra Quantity Allowed')
    unit_price = fields.Float('Unit Price')
    notes = fields.Char('Notes')
    restriction_type = fields.Selection([('restrict', 'Restrict & Alert'), ('alert', 'Warning')], string="Restriction Type" , required=True, default='restrict')

    delivered_qty = fields.Float('Delivered Qty', compute=_get_balance_qty, store=False, decimal=(18, 3))
    pending_qty = fields.Float('Pending Qty', compute=_get_balance_qty, store=False, decimal=(18, 3))
    return_qty = fields.Float('Return Qty', compute=_get_balance_qty, store=False, decimal=(18, 3))
    balance_qty = fields.Float('Balance Qty', compute=_get_balance_qty, store=False, decimal=(18, 3))

    _sql_constraints = [('unique_template', 'UNIQUE(prod_group_tmpl_id,contract_id)',
                         "Unique Group Template Per Sales Order")]


CiconContractLine()


class CiconProdOrder(models.Model):
    _inherit = 'cicon.prod.order'

    contract_id = fields.Many2one('cicon.contract', string="Contract", copy=False)
    expiry_date = fields.Date('Expiry Date', related='contract_id.end_date', readonly=True)
    contract_warning = fields.Char(string="Warning")

    @api.onchange('contract_id', 'required_date')
    def _change_contract(self):
        _warn = {}
        if self.contract_id:
            if self.contract_id.validity_type != 'quantity':
                _so_ex_date = datetime.strptime(self.contract_id.end_date, '%Y-%m-%d')
                _sch_date = datetime.today()
                if self.required_date: #TODO: Check if need to change Date checking with another field
                    _sch_date = datetime.strptime(self.required_date, '%Y-%m-%d')
                _so_ex_date += relativedelta(days=+self.contract_id.extra_days_allowed)
                if _sch_date >= _so_ex_date:
                    _warn = {
                       'title': 'Warning',
                       'message': 'SO Date Expired, Please Verify'
                    }
        return {'warning': _warn}

    @api.one
    @api.constrains('product_lines', 'contract_id')
    def _check_lines_qty(self):
        res = True
        _warn = ''
        if self.product_lines and self.contract_id:
            if self.contract_id.validity_type not in ('date'):
                _group_tmpls = self.contract_id.contract_line_ids
                for tmp in _group_tmpls:
                    #Get all line except for current
                    _prod_orders = self.env['cicon.prod.order'].search([('contract_id', '=', tmp.contract_id.id),
                                                                         ('state', 'not in', ('cancel','pending'))])
                    _moves = self.env['cicon.prod.order.line'].search([('prod_order_id', 'in', _prod_orders._ids),
                                                                       ('product_id', 'in', tmp.prod_group_tmpl_id.product_ids._ids)])
                    _del_qty = sum(a.product_qty for a in _moves)
                    _ret_qty = 0 # sum(a.product_qty for a in _moves) #TODO: Return Quantity
                    _temp_qty = (_del_qty - _ret_qty)
                    #Get all line for current
                    _line = self.product_lines.filtered(lambda l: l.product_id.id in tmp.prod_group_tmpl_id.product_ids._ids)
                    if _line:
                        _qty = sum(x.product_qty for x in _line)
                        if (_temp_qty + _qty) > (tmp.quantity + tmp.extra_qty_allowed):
                            if tmp.restriction_type == 'restrict':
                                res = False
                                raise ValidationError("Quantity Exceed the limit")
                            else:
                                _warn += ' Quantity Exceeds for %s, ' % tmp.prod_group_tmpl_id.name
            else:
                _so_ex_date = datetime.strptime(self.contract_id.end_date, '%Y-%m-%d')
                _sch_date = datetime.today()
                if self.required_date:
                    _sch_date = datetime.strptime(self.required_date, '%Y-%m-%d' )
                    _so_ex_date += relativedelta(days=+self.contract_id.extra_days_allowed)
                if _sch_date >= _so_ex_date:
                    res = False
                    raise ValidationError('SO Expired !')
            if self.contract_warning or _warn:
                self.write({'contract_warning': _warn})
        return res

    @api.multi
    def set_progress(self):
        if self._check_lines_qty():
            return self.write({'state': 'progress'})
        else:
            return False

CiconProdOrder()


class CiconProdOrderLine(models.Model):
    _inherit = 'cicon.prod.order.line'

    @api.depends('product_id')
    def _get_contract_line_id(self):
        for rec in self:
            if rec.product_id and rec.contract_id:
                for l in rec.contract_id.contract_line_ids:
                    _prod_line = [l.id for x in l.prod_group_tmpl_id.product_ids if x.id == rec.product_id.id]
                    if _prod_line:
                        rec.cicon_contract_line_id = _prod_line[0]

    contract_id = fields.Many2one('cicon.contract', related='prod_order_id.contract_id', store=False, string="Contract")
    cicon_contract_line_id = fields.Many2one('cicon.contract.line', compute=_get_contract_line_id, string="Contract Line", store=False)

    @api.onchange('contract_id')
    def _change_contract(self):
        _dm = {'product_id': ''}
        if self.contract_id:
            _dm = {'product_id': [('id', 'in', self.contract_id.product_ids._ids)]}
        return {'domain': _dm}

CiconProdOrderLine()



