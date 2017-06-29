from odoo import models,fields, api
from datetime import datetime
from dateutil import rrule
import time


class cicon_hr_process_attendance_wizard(models.TransientModel):
    _name = 'cicon.hr.process.attendance.wizard'
    _description = "CICON Process Attendance"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    emp_selection = fields.Selection([('emp_dept', 'By Department'), ('emp_tag', 'Employee Tag')], "Employee Selection",
                                     required=True)
    dept_ids = fields.Many2many('hr.department', 'cicon_hr_department_attendance_rel', 'wizard_id', 'department_id',
                                string='Departments')
    tag_ids = fields.Many2many('hr.employee.category', 'cicon_hr_tag_emp_attendance_rel', 'wizard_id', 'tag_id',
                               string='Tags')

    @api.multi
    def fill_attendance(self):
        self.ensure_one()
        _attendance = self.env['cicon.hr.attendance']
        _att_sheet = self.env['cicon.hr.attendance.sheet']
        _selected_dates = list(rrule.rrule(rrule.DAILY, dtstart=datetime.strptime(self.start_date, '%Y-%m-%d'), until=datetime.strptime(self.end_date, '%Y-%m-%d')))
        _selected_dates.sort()
        if self.emp_selection == 'emp_dept':
            _emp = self.env['hr.employee'].search([('department_id', 'in', self.dept_ids._ids)])
        else:
            _emp = self.env['hr.employee'].search([('category_ids', 'in', self.tag_ids._ids)])
        print _emp
        print _selected_dates
        for _date in _selected_dates:
            _date_int = int(time.strftime('%Y%m%d', time.strptime(_date.strftime('%Y-%m-%d'), '%Y-%m-%d')))
            _res = _att_sheet.get_processed_attendance(_date.strftime('%Y-%m-%d'), _emp)
            _sheet = _att_sheet.search([('attendance_date', '=', _date.strftime('%Y-%m-%d'))], limit=1)
            _ex_att = _attendance.search([('date_value', '=', _date_int)])
            if self.emp_selection == 'emp_dept':
                _del_att = _ex_att.filtered(lambda r: r.employee_id.department_id.id in self.dept_ids._ids)
            else:
                _del_att = _ex_att.filtered(lambda r: r.employee_id.id in _emp._ids)
                _del_att.unlink()
            for r in _res:
                if _sheet:
                    r['sheet_id'] = _sheet.id
                _attendance.create(r)
        return True

cicon_hr_process_attendance_wizard()