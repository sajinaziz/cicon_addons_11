from datetime import datetime
import pytz
from odoo import models,  fields, api


class cicon_customer_order(models.Model):
    _name = 'cicon.customer.order'
    _inherit = ['mail.thread']
    _description = "Customer Order"

    name = fields.Char('Order Ref', size=50, required =True, readonly=True, states={'new': [('readonly', False)]}, track_visibility='always')
    partner_id = fields.Many2one('res.partner', string="Customer", required=True, domain="[('customer','=',True)]",  readonly=True, states={'new': [('readonly', False)]})
    # project_id = fields.Many2one('res.partner.project', 'Project', readonly = True, domain="[('partner_id','=', partner_id)]", required=True, states={'new': [('readonly', False)]}, track_visibility='always')
    project_id = fields.Many2one('cicon.job.site', 'Project', readonly=True, domain="[('partner_id','=', partner_id)]",required=True, states={'new': [('readonly', False)]}, track_visibility='always')
    page_info = fields.Char('Pages', size=50, readonly=True, states={'new': [('readonly', False)]})
    material_type = fields.Char('Material Type', size=50, readonly=True, states={'new': [('readonly', False)]})
    order_date = fields.Date('Order date', required=True, readonly=True, states={'new': [('readonly', False)]}, default= fields.Date.context_today, track_visibility='always')
    received_datetime = fields.Datetime('Received Date Time', required=True, readonly=True, states={'new': [('readonly', False)]}, default=fields.Datetime.now, copy=False)
    required_date = fields.Date('Required Date', required=True, readonly=True, states={'new': [('readonly', False)]}, track_visibility='onchange')
    production_note = fields.Text('Production Note', readonly=True, states={'new': [('readonly', False)]})
    technical_note = fields.Text('Technical Note', readonly=True, states={'new': [('readonly', False)]})
    contact_detail = fields.Text('Contact Details')
    project_engineer = fields.Char('Engineer', size=50, readonly=True, states={'new': [('readonly', False)]})
    created_by = fields.Many2one('res.users', 'Created By', required=True, readonly=True, default=lambda self: self.env.user)
    title = fields.Char('List Details', size=200, required=True, readonly=True, states={'new': [('readonly', False)]})
    subtitle = fields.Char('Sub List', size=200, required=False, readonly=True, states={'new': [('readonly', False)]})
    bbs_weight = fields.Float('Order Tonnage', digits=(10, 3), required =False, readonly=True, states={'new': [('readonly', False)]})
    company_id = fields.Many2one('res.company', "Company", required=True, default=lambda self: self.env.user.company_id)
    state = fields.Selection([('new', 'New'),
            ('confirmed', 'Confirm'),
            ('close', 'Completed'),
            ('cancel', 'Cancelled')], 'Status', default='new', track_visibility='onchange')
    last_order = fields.Many2one('cicon.customer.order', string='Previous Order', store=False, readonly=True)
    # old_id = fields.Integer('Old Id')

    _sql_constraints = [('order_name', 'unique(project_id,name)', 'Order Name Must be Unique per project')]

    _order = 'order_date desc'

    @api.onchange('partner_id')
    def customer_change(self):
        if self.partner_id and self.project_id:
            self.project_id = None

    @api.onchange('project_id')
    def project_change(self):
        if self.project_id:
            _pre_order = self.search([('project_id', '=', self.project_id.id)], order='id desc', limit=1)
            self.last_order = _pre_order


    @api.multi
    def order_confirm(self):
        self.write({'state': 'confirmed'})

    @api.multi
    def order_close(self):
        self.write({'state': 'close'})

    @api.multi
    def order_reopen(self):
        self.write({'state': 'new'})


    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if not default.get('name', False):
            default.update(name=('%s/Copy') % (self.name))
        default.update(state='new')
        return super(cicon_customer_order, self).copy(default)

    @api.multi
    def print_order(self):
        self.ensure_one(), 'This option should only be used for a single id at a time.'
        self.write({'state': 'confirmed'})
        return self.env['report'].get_action(self, 'cicon_prod.customer_requisition_template')

    # For Report
    def get_datetime_current(self, _datetime_to_convert=None):
        time_local = 'Asia/Dubai'
        time_fmt = "%Y-%m-%d %H:%M:%S"
        if _datetime_to_convert:
            _time_val = datetime.strptime(_datetime_to_convert, time_fmt)
        else:
            _time_val = datetime.utcnow()
        testDt = pytz.utc.localize(_time_val)
        TestDt = testDt.astimezone(pytz.timezone(time_local))
        return TestDt.strftime('%a,  %d-%b-%Y %H:%M')
cicon_customer_order()




