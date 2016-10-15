from odoo import models, fields, api


class CiconQcCheckOperation(models.Model):
    _name = 'cicon.qc.check.operation'
    _description = "QC Check operations"

    name = fields.Char('Operation', required=True)
    description = fields.Text("Description")

    _sql_constraints = [('uniq_check_op','UNIQUE(name)', ('Unique check operation name !'))]


class CiconQcCheck(models.Model):
    _name = 'cicon.qc.check'
    _description = "Quality Checks"

    #TODO: Inherit Mail Addon if need

    name = fields.Char('QC Check Ref:', readonly=True)
    prod_order_id = fields.Many2one('cicon.prod.order', string="Production Order", requried=True)
    operation_id = fields.Many2one('cicon.qc.check.operation', string="Qc Check", required=True)
    date = fields.Date('Date', default=fields.Date.context_today)
    state = fields.Selection([('new', 'TO DO'), ('pass', 'PASS'), ('fail', 'FAIL')], string='Status', default='new')
    note = fields.Text( string='Notes')
    user_id = fields.Many2one('res.users', string="User" , default= lambda self: self.env.user)

    _sql_constraints = [('uniq_check', 'UNIQUE(name)', ('Unique check Reference!'))]

    @api.multi
    def set_pass(self):
        self.ensure_one()
        self.write({'state': 'pass'})

    @api.multi
    def set_fail(self):
        self.ensure_one()
        self.write({'state': 'fail'})

    @api.multi
    def set_todo(self):
        self.ensure_one()
        self.write({'state': 'new'})

    @api.onchange('operation_id')
    def _on_change_operation(self):
        if not self.note:
            self.note = self.operation_id.description

    @api.model
    def create(self, vals):
        _qc_check_seq = self.env['ir.sequence'].search([('code', '=', 'cic.qc.check.seq')])
        vals.update({'name': _qc_check_seq.next_by_id() or '/'})
        return super(CiconQcCheck, self).create(vals)






