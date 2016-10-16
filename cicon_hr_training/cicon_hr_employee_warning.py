from openerp import models, fields, api
import time


class cicon_hr_employee_warning_type(models.Model):
    _name = 'cicon.hr.employee.warning.type'
    _description = 'Employee Warning Type'

    name = fields.Char('Warning Type', required=True)

    _sql_constraints = [('uniq_type', 'UNIQUE(name)', 'Unique Employee Warning Type')]

cicon_hr_employee_warning_type()


class cicon_hr_employee_warning(models.Model):
    _name = 'cicon.hr.employee.warning'
    _description = 'Employee Warning'

    name = fields.Char('Reference', readonly=True)
    date = fields.Date('Date', required=True)
    warning_type_id = fields.Many2one('cicon.hr.employee.warning.type', string="Warning Type", required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    deduction = fields.Integer('Deduction Day(s)')

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'Unique Employee Warning')]

    @api.model
    def create(self, vals):
        vals.update({'name': self.env['ir.sequence'].get('cicon.hr.employee.warning.seq') or time.strftime('%Y/%m/%d/%H/%M')})
        return super(cicon_hr_employee_warning, self).create(vals)

cicon_hr_employee_warning()


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    warning_ids = fields.One2many('cicon.hr.employee.warning', 'employee_id', string='Warnings', groups="base.group_hr_user,base.group_hr_hse_user")

hr_employee()