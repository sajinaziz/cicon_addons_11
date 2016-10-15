from odoo import models, fields, api, tools
from odoo.exceptions import UserError

class CiconProdDeliveryOrder(models.Model):
    _name = 'cicon.prod.delivery.order'
    _description = "Delivery Order"
    _inherit = ['mail.thread']

    @api.depends('dn_line_ids')
    def _get_tonnage(self):
        for rec in self:
            rec.total_tonnage = sum([r.product_qty for r in rec.dn_line_ids if r.unit_id.name == 'TON'])
            #rec.tot_del_qty = sum([r.product_qty for r in rec.dn_line_ids])

    name = fields.Char("DN Number", required=True, track_visibility="onchange", readonly=True, states={'pending': [('readonly', False)]})
    dn_date = fields.Date("DN Date", required=True,  track_visibility="onchange", readonly=True, states={'pending': [('readonly', False)]})
    dn_delivered_date = fields.Date("Delivered Date", track_visibility="onchange", readonly=True, states={'pending': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string="Customer", related="customer_order_id.partner_id", store=True)
    project_id = fields.Many2one('res.partner.project', string="Project", related="customer_order_id.project_id", store=True)
    customer_order_id = fields.Many2one('cicon.customer.order', " Customer Order", track_visibility="onchange", readonly=True, states={'pending': [('readonly', False)]})
    prod_order_ids = fields.Many2many('cicon.prod.order', 'cicon_prod_order_dn_rel', 'dn_id', 'prod_order_id', "Production Orders",
                                      domain="[('customer_order_id','=', customer_order_id), ('state','in', ('confirm','progress','ready','partial_delivery'))]",
                                      track_visibility="onchange", readonly=True, states={'pending': [('readonly', False)]})
    remarks = fields.Char("Remarks")
    product_tmpl_ids = fields.Many2many('product.template', 'cicon_dn_product_tmpl_rel', 'dn_id', 'product_tmpl_id', "Product Templates", track_visibility="onchange", readonly=True, states={'pending': [('readonly', False)]})
    state = fields.Selection([('pending', 'Pending'), ('partial', 'Partially Delivered'), ('done', 'Delivered')], string="Status", required=True, default='pending' , readonly=True)
    dn_line_ids = fields.One2many('cicon.prod.delivery.order.line', 'dn_id', string="DN Lines", track_visibility="onchange", readonly=True, states={'pending': [('readonly', False)]})
    dn_product_line_ids = fields.One2many('cicon.prod.delivery.product.line.view', 'dn_id', readonly=True, string="DN Product Lines")
    trip_details = fields.Char('Trailer/Driver')
    total_tonnage = fields.Float(compute=_get_tonnage, digits=(10, 3), store=True, string='Total Tonnage')
    #tot_del_qty = fields.Float("Tot Qty", digits=(10, 3),compute=_get_tonnage, store=True)

    _sql_constraints = [('uniq_dn', 'UNIQUE(name)', "DN Should be unique")]


    @api.onchange('customer_order_id')
    def _change_customer_order(self):
        if self.prod_order_ids:
            _cust_order_id = self.prod_order_ids.mapped('customer_order_id')
            if len(_cust_order_id) > 1 or self.customer_order_id != _cust_order_id:
                self.prod_order_ids =[]

    @api.onchange('prod_order_ids')
    def _change_prod_order(self):
        if self.prod_order_ids:
            _order_lines = self.env['cicon.prod.order.line'].search([('prod_order_id', 'in', self.prod_order_ids._ids)])
            _product_tmpls = _order_lines.mapped('product_tmpl_id')
            _dm = {'product_tmpl_ids': [('id', 'in', _product_tmpls._ids)]}
            return {'domain': _dm}

    @api.onchange('product_tmpl_ids')
    def _change_prod_tmpl(self):
        _dn_lines = []
        #TODO: Check for balance quantity
        if self.prod_order_ids and self.product_tmpl_ids:
            _order_lines = self.env['cicon.prod.order.line'].search([('prod_order_id', 'in', self.prod_order_ids._ids),
                                                                     ('product_tmpl_id', 'in', self.product_tmpl_ids._ids)])

            for _p_order in self.prod_order_ids:
                _prod_ids =_order_lines.mapped('product_id')
                _prod_del_order_lines = self.env['cicon.prod.delivery.order.line'].search([('prod_order_id', '=',_p_order.id)])
                for _p_id in _prod_ids:
                    _total_prod_qty = sum([x.product_qty for x in _p_order.product_lines if x.product_id.id == _p_id.id])
                    _total_prod_del_qty = sum([x.product_qty for x in _prod_del_order_lines if x.product_id == _p_id])
                    if _total_prod_qty > _total_prod_del_qty or _total_prod_qty == _total_prod_del_qty:
                        if _total_prod_del_qty!=0:
                            bal_qty = _total_prod_qty - _total_prod_del_qty
                            if bal_qty != 0:
                                _dn_lines.append({
                                    'product_id': _p_id,
                                    'prod_order_id': _p_order.id,
                                    'product_qty': bal_qty,
                                    'tot_del_qty':_total_prod_del_qty

                                })
                        elif _total_prod_qty > 0:
                            _dn_lines.append({
                                'product_id': _p_id,
                                'prod_order_id': _p_order.id,
                                'product_qty': _total_prod_qty,
                                'tot_del_qty': 0
                            })
                    elif _total_prod_qty < _total_prod_del_qty:
                        raise UserError('Exceed Quantity')

                self.dn_line_ids = _dn_lines

            _prods = _order_lines.mapped('product_id')
            _prod_lines = []
            for _prod in _prods:
                _prod_sum = sum([x.product_qty for x in _order_lines if x.product_id.id == _prod.id])
                _prod_lines.append({'product_id': _prod, 'product_qty': _prod_sum})
            self.dn_product_line_ids = _prod_lines

    def _check_prod_qty(self, prod_order):
        _previous_del = self.env['cicon.prod.delivery.order'].search([('prod_order_ids','in',prod_order.id)])


    @api.multi
    def set_done(self):
        self.ensure_one()
        if self.dn_line_ids and self.dn_date:
            self.write({'state': 'done'})
            for p_order in self.prod_order_ids:
                _total_prod_qty = sum([x.product_qty for x in p_order.product_lines])
                _prod_del_ids= self.env['cicon.prod.delivery.order.line'].search([('prod_order_id','=', p_order.ids)])
                _total_prod_del_qty = sum([x.product_qty for x in _prod_del_ids])
                if _total_prod_del_qty == _total_prod_qty:
                    p_order.write({'state': 'delivered'})
                elif _total_prod_qty > _total_prod_del_qty:
                    p_order.write({'state': 'partial_delivery'})
                else:
                    raise UserError('Exceed Quantity')

        else:
            raise UserError('Select Delivery Date')

    @api.multi
    def set_pending(self):
        self.ensure_one()
        self.write({'state': 'pending'})
    #
    # '''' check quantity constains  '''
    #
    # @api.constrains('prod_order_qty', 'tot_del_qty', 'dn_line_ids')
    # def _check_qty(self):
    #     for record in self:
    #         print record.product_qty
    #         if record.tot_del_qty > record.prod_order_qty:
    #             raise UserError(
    #                 "Total Quantity supplied cannot greater than Order Qty:supplied qty - %s" % record.tot_del_qty)


CiconProdDeliveryOrder()


class CiconProdDeliveryOrderLine(models.Model):
    _name = 'cicon.prod.delivery.order.line'
    _description = "Delivery Line"

    @api.one
    @api.depends('product_id')
    def _get_dia_value(self):
        self.dia_attrib_value_id = None
        if self.product_id:
            for a in self.product_id.attribute_value_ids:
                if a.attribute_id.name == "Diameter":
                    self.dia_attrib_value_id = a.id
                    break
                elif a.attribute_id.name == "Reduce Coupler Type":
                    self.dia_attrib_value_id = a.id
                    break
            if self.prod_order_id:
                _order_lines = self.env['cicon.prod.order.line'].search([('prod_order_id', '=', self.prod_order_id.id),
                                                                         ('product_id', '=', self.product_id.id)])
                self.prod_order_qty = sum([x.product_qty for x in _order_lines])
                # _prod_order_lines = self.env['cicon.prod.delivery.order.line'].search([('prod_order_id', '=', self.prod_order_id.id),
                #                                                          ('product_id', '=', self.product_id.id)])
                # self.tot_del_qty = sum([x.product_qty for x in _prod_order_lines])

    dn_id = fields.Many2one('cicon.prod.delivery.order', string="DN")
    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True)], string='Product', required=True)
    prod_order_id = fields.Many2one('cicon.prod.order', string="Production Order")
    product_qty = fields.Float('Quantity To Deliver', digits=(10, 3), required=True)
    prod_order_qty = fields.Float('Order Quantity',compute=_get_dia_value, digits=(10, 3),readonly=True,store=True)
    tot_del_qty = fields.Float('Delivered Quantity',  digits=(10, 3), readonly=True)
    unit_id = fields.Many2one('product.uom', related='product_id.uom_id', string='Unit', readonly=True)
    categ_id = fields.Many2one('product.category', related='product_id.categ_id', string='Category', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id', readonly=True)
    dia_attrib_value_id = fields.Many2one('product.attribute.value', compute=_get_dia_value, string='Diameter',
                                          store=True)
    state = fields.Selection(related='prod_order_id.state', string='State', store=False, readonly=True)


class CiconProdDeliveryProductLineView(models.Model):
    _name = 'cicon.prod.delivery.product.line.view'
    _description = "Delivery Product Line"
    _auto = False

    dn_id = fields.Many2one('cicon.prod.delivery.order', string="DN",readonly=True)
    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True)], string='Product', readonly=True)
    product_qty = fields.Float('Quantity', digits=(10, 3), readonly=True)
    unit_id = fields.Many2one('product.uom', related='product_id.uom_id', string='Unit', readonly=True)
    categ_id = fields.Many2one('product.category', related='product_id.categ_id', string='Category', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id', readonly=True)


    def _from(self):
        from_str = """
        cicon_prod_delivery_order_line
        """
        return from_str

    def _select(self):
        select_str = """
        SELECT MAX(id) as id,dn_id,product_id, sum( product_qty) as product_qty"""
        return select_str

    def _group_by(self):
        group_by_str = """GROUP BY dn_id,product_id"""
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))




