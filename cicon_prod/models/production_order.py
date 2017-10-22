from odoo import models, osv, fields, api
from dateutil import parser
from odoo.exceptions import UserError


class cicon_prod_order(models.Model):
    _name = 'cicon.prod.order'
    _inherit = ['mail.thread']
    _description = 'CICON Production Order'

    @api.depends('product_lines')
    def _get_tonnage(self):
        for rec in self:
            rec.total_tonnage = sum([r.product_qty for r in rec.product_lines if r.unit_id.name == 'TON'])
            #rec.total_tonnage = sum([r.product_qty for r in rec.product_lines])
            _temp = []
            for line in rec.product_lines:
                _temp.extend(line.mapped('product_tmpl_id')._ids)
                # _temp_str.extend([x.name for x in line.product_tmpl_id])
            rec.template_ids = list(set(_temp))
            if rec.template_ids:
                rec.template_str = ','.join([x.name for x in rec.template_ids])


    name = fields.Char('Armaor Code / Internal Ref.', size=12, required=True, track_visibility="onchange", readonly=True, states={'pending': [('readonly', False)]})
    revision_no = fields.Integer('Revision No', required=True, readonly=True, track_visibility="onchange", states={'pending': [('readonly', False)]})
    description = fields.Char('Description', track_visibility="onchange", readonly=True, states={'pending': [('readonly', False)]})
    remarks = fields.Text('Remarks')
    customer_order_id = fields.Many2one ('cicon.customer.order', "Customer Order", readonly=True, states={'pending': [('readonly', False)]})
    required_date = fields.Date('Required Date', readonly=True, states={'pending': [('readonly', False)]})
    product_lines = fields.One2many('cicon.prod.order.line', 'prod_order_id', string="Products", readonly=True, states={'pending': [('readonly', False)]})
    tag_count = fields.Integer('Tags', readonly=True, states={'pending': [('readonly', False)]})
    bar_mark_count = fields.Integer('Bar Marks', readonly=True, states={'pending': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', related='customer_order_id.project_id.partner_id', string='Customer', readonly=True)
    #project_id = fields.Many2one('res.partner.project', related='customer_order_id.project_id', string='Project', readonly=True)
    project_id = fields.Many2one('cicon.job.site', related='customer_order_id.project_id', string='Project',readonly=True)
    state = fields.Selection([('pending', 'New'), ('confirm', 'Confirm'), ('progress', 'In Progress'),
                              ('ready', 'Ready To Deliver'), ('partial_delivery', 'Partially Delivered'),
                              ('delivered', 'Delivered'), ('cancel', 'Cancel'),
                              ('hold', 'On Hold'), ('transfer', 'Transfer')], default='pending',  string='Status', track_visibility="onchange")
    total_tonnage = fields.Float(compute=_get_tonnage, digits=(10, 3), store=True, string='Total Tonnage')
    created_user = fields.Many2one('res.users', string="Created By", readonly=True, states={'pending': [('readonly', False)]}, default=lambda self: self.env.user.id)
    # prod_note = fields.Char(store=False, string="Warning", readonly=True)
    planned_date = fields.Date('Planned Date')
    plan_id = fields.Many2one('cicon.prod.plan', string="Production Plan")
    sequence = fields.Integer('Sequence')
    template_ids = fields.Many2many('product.template', compute=_get_tonnage, store=False, string='Products')
    template_str = fields.Char(compute=_get_tonnage,store=False, string='Products')
    load = fields.Float("Load Priority")
    delivery_order_ids = fields.Many2many('cicon.prod.delivery.order', 'cicon_prod_order_dn_rel', 'prod_order_id', 'dn_id', "Delivery Orders",
                                        readonly=True)

    _order = "load, sequence, required_date desc"
    # _sequence = 'load'

    @api.multi
    def set_pending(self):
        return self.write({'state': 'pending'})

    @api.multi
    def set_cancel(self):
        if len(self.delivery_order_ids) == 0:
            return self.write({'state': 'cancel'})
        else:
            raise UserError("Please remove Order from Delivery Note!")

    @api.multi
    def set_confirm(self):
        if self.customer_order_id:
            return self.write({'state': 'confirm'})
        else:
            raise UserError("Please Select Customer Order!")

    @api.multi
    def create_dn(self):
        self.ensure_one()  # One Record
        # Find form view and pass context for default values
        form_id = self.env.ref('cicon_prod.cicon_dn_form_view')
        ctx = dict(
            default_customer_order_id=self.customer_order_id.id,
            default_prod_order_ids=[self.id],
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cicon.prod.delivery.order',
            'views': [(form_id.id, 'form')],
            'view_id': form_id.id,
            'target': 'current',
            'context': ctx,
        }

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name', False):
            default.update(name=('%s/C') % (self.name))
        default.update(state='pending')
        return super(cicon_prod_order, self).copy(default)

    @api.multi
    def plan_groups(self,  domain, **kwargs):
        _plans_valid = self.env['cicon.prod.plan'].search([('state', '=', 'done')])
        _plans = [category.name_get()[0] for category in _plans_valid]
        _fold = {}
        for _plan in _plans:
            _fold[_plan[0]] = True
        return _plans, _fold

    _group_by_full = {
        'plan_id': plan_groups,
    }

    # @api.one
    # def write(self, vals):
    #     if vals.get('planned_date:day'):
    #         _day_val = vals.pop('planned_date:day')
    #         _date_val = parser.parse(_day_val)
    #         vals.update({'planned_date': _date_val.strftime('%Y-%m-%d')})
    #     return super(cicon_prod_order, self).write(vals)

    _sql_constraints = [('unique_code', 'UNIQUE(name,revision_no)', 'Code By Revision Must be unique')]


cicon_prod_order()


class cicon_prod_order_line(models.Model):
    _name = 'cicon.prod.order.line'
    _description = "Production Order Line"

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

    prod_order_id = fields.Many2one('cicon.prod.order', string="Production Order")
    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True)], string='Product', required=True)
    product_qty = fields.Float('Quantity', digits=(10, 3), required=True)

    unit_id = fields.Many2one('product.uom', related='product_id.uom_id', string='Unit', readonly=True)
    categ_id = fields.Many2one('product.category', related='product_id.categ_id', string='Category', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id', readonly=True)
    dia_attrib_value_id = fields.Many2one('product.attribute.value', compute=_get_dia_value, string='Diameter', store=True)

cicon_prod_order_line()


class cicon_prod_plan(models.Model):
    _name = 'cicon.prod.plan'
    _description = "CICON Production Plan"
    _rec_name = 'display_name'

    @api.multi
    def _display_name(self):
        for rec in self:
            rec.display_name = rec.plan_date + '/' + str(rec.work_shift).upper()

    display_name = fields.Char(string="Name", compute=_display_name)
    plan_date = fields.Date('Plan Date', required=True, default=fields.Date.context_today)
    work_shift = fields.Selection([('day', 'Day'), ('night', 'Night')], required=True, string="Work Shift")
    prod_order_ids = fields.One2many('cicon.prod.order','plan_id', string="Orders")
    state = fields.Selection([('pending', 'Pending'), ('done', 'Complete')], default="pending", string="Status" , required=True)

    _sql_constraints = [('uniq_plan', 'UNIQUE(plan_date,work_shift)', "Unique Plan !")]

cicon_prod_plan()


class cicon_customer_order(models.Model):
    _inherit = 'cicon.customer.order'

    def _get_prod_order_count(self):
        #TODO: Check status requirement in calculation
        for rec in self:
            rec.prod_order_count = len(self.prod_order_ids) or 0
            rec.delivery_order_count= len(self.delivery_order_ids) or 0
            rec.prod_order_tonnage = sum([x.total_tonnage for x in self.prod_order_ids if x.state not in ('cancel')])
            rec.delivery_order_tonnage = sum([x.total_tonnage for x in self.delivery_order_ids])
            if rec.prod_order_tonnage > 0:
                rec.delivery_perc = int((rec.delivery_order_tonnage / rec.prod_order_tonnage )* 100)

    prod_order_ids = fields.One2many('cicon.prod.order', 'customer_order_id', string='Production Orders', copy=False)
    prod_order_count = fields.Integer('Production Order Count', compute=_get_prod_order_count, store=False, readonly=True)
    prod_order_tonnage = fields.Float('Production Tonnage', digits=(10,3), compute=_get_prod_order_count, store=False,
                                      readonly=True)
    delivery_order_ids = fields.One2many('cicon.prod.delivery.order', 'customer_order_id', string='Delivery Orders', copy=False)
    delivery_order_count = fields.Integer('Delivery Order Count', compute=_get_prod_order_count, store=False,
                                      readonly=True)
    delivery_order_tonnage = fields.Float('Delivery Tonnage', digits=(10,3), compute=_get_prod_order_count, store=False,
                                      readonly=True)
    delivery_perc = fields.Integer('Delivery Percentage', compute=_get_prod_order_count, store=False,
                                      readonly=True)


    @api.multi
    def order_cancel(self):
        self.ensure_one()
        if self.prod_order_count != 0:
            _status  =  self.prod_order_ids.mapped('state')
            if len(_status) == 1 and _status[0] == 'cancel':
                return self.write({'state': 'cancel'})
            else:
                raise UserError("Please Cancel Production Order !")
        else:
            return  self.write({'state': 'cancel'})


cicon_customer_order()


