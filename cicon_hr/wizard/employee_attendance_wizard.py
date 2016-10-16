from openerp import models, fields, api
from openerp import api
import time


_MONTHS = [('1', 'January'),
('2', 'February'),
('3', 'March'),
('4', 'April'),
('5', 'May'),
('6', 'June'),
('7', 'July'),
('8', 'August'),
('9', 'September'),
('10', 'October'),
('11', 'November'),
('12', 'December'),
]


class cicon_emp_attendance_wizard(models.TransientModel):
    _name = 'cicon.emp.attendance.wizard'
    _description = "CICON Employee Attendance Wizard"

    # def _get_year(self,cr,uid,context=None):
    #     res = []
    #     for y in range(2014, datetime.today().year + 1, 1):
    #         res.append((str(y), str(y)))
    #     return res

    @api.model
    def _get_first_date(self):
        return time.strftime("%Y-%m-01")

    #'month_sel': fields.selection(_MONTHS, string="Month", required=True),
    #'year_sel': fields.selection(_get_year, string="Year", required=True),
    work_shift = fields.Many2one('cicon.hr.work.shift', string='Work Shift')
    from_date = fields.Date(string='From Date', required=True, default=_get_first_date)
    to_date = fields.Date(string='To Date', required=True, default=fields.Date.context_today)
    employee_tags = fields.Many2many('hr.employee.category', 'cicon_hr_emp_attendance_tag_rel','wizard_id', 'tag_id', string='Employee Tags')
    employee_ids = fields.Many2many('hr.employee', 'cicon_hr_employee_attendance_rel', 'wizard_id', 'employee_id', string='Employee')
    leave_type = fields.Selection([('absent', 'Absent'), ('medical', 'Medical Leave'), ('annual', 'Annual Leave'), ('emergency', 'Emergency Leave'),('late_resume', 'Late Resume')], string='Leave Type')
    report_type = fields.Selection([('employee_leave', 'Employee Leave'), ('employee_attendance', 'Attendance'), ('employee_tag', 'Employee Tag')], "Report Type")

    @api.multi
    def show_report(self):
        self.ensure_one()
        #_month = int(_rec.month_sel)
        #_year = int(_rec.year_sel)
        #_from_date = datetime(_year, _month, 1)
        #_to_date = datetime(_year, _month, calendar.monthrange(_year, _month)[1])
        # _from_date = self.from_date
        # _to_date = self.to_date
        # context.update({'start_date': _from_date, 'end_date': _to_date})
        _emp_ids = []
        if self.report_type == 'employee_attendance':
            _emp_ids = [e.id for e in self.employee_ids]
        elif self.report_type == 'employee_tag':
            _dm = []
            if self.employee_tags:
                _dm.append(('category_ids', '=', self.employee_tags._ids))
            if self.work_shift:
                _dm.append(('work_shift', '=', self.work_shift.id))
            _eIds = self.env['hr.employee'].search(_dm, order='department_id')
            _emp_ids = [e.id for e in _eIds]
        ctx = dict(self._context)
        ctx['start_date'] = self.from_date
        ctx['end_date'] = self.to_date
        ctx['employee_ids'] = _emp_ids
        if self.leave_type:
            ctx['leave_type'] = self.leave_type
        if self.report_type == 'employee_leave':
            return self.with_context(ctx).env['report'].get_action(self, report_name='cicon_hr.employee_leave_report_weekly',data={})
        else:
            return self.with_context(ctx).env['report'].get_action(self, report_name='cicon_hr.employee_attendance_report_template',data={})


cicon_emp_attendance_wizard()
