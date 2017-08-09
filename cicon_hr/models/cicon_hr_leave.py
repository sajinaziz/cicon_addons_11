from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError


class cicon_hr_employee_leave(models.Model):
    _name = 'cicon.hr.employee.leave'
    _description = 'Employee Leave'
    _rec_name = 'leave_type'

    @api.multi
    def name_get(self):
        res = []
        for r in self.read(['leave_type']):
            _leave_type = dict(self.fields_get(['leave_type'])['leave_type']['selection'])[r['leave_type']]
            res.append((r['id'], _leave_type))
        return res

    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
        DATE_FORMAT = "%Y-%m-%d"
        from_dt = datetime.strptime(date_from, DATE_FORMAT)
        to_dt = datetime.strptime(date_to, DATE_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + 1
        return diff_day

    @api.one
    @api.depends('start_date', 'end_date')
    def _calc_days(self):
        self.days_count = 0
        if self.start_date and self.end_date:
            self.days_count = self._get_number_of_days(self.start_date, self.end_date)

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    leave_type = fields.Selection([('absent', 'Absent'), ('medical', 'Medical Leave'), ('annual', 'Annual Leave'), ('emergency', 'Emergency Leave'), ('late_resume', 'Late Resume')], string='Leave Type', required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    days_count = fields.Integer(compute=_calc_days, string="Days")
    note = fields.Text('Remarks')

    _order = 'id desc'

    @api.one
    @api.constrains('start_date', 'end_date', 'employee_id')
    def _check_date(self):
        holiday_ids = self.search([('start_date', '<=', self.end_date), ('end_date', '>=', self.start_date), ('employee_id', '=', self.employee_id.id), ('id', '<>', self.id)])
        if holiday_ids:
            raise Warning('You can not have 2 leaves that overlaps on same day!')

    @api.multi
    def save_record(self):
        self.ensure_one()
        return True
    #
    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     print args
    #     return super(cicon_hr_employee_leave,self).search( args=args, offset=offset,limit=limit, order= order, count= count)

    _sql_constraints = [('date_check1', "CHECK (start_date <= end_date)", "The start date must be an greater to the end date.")]

cicon_hr_employee_leave()

