from openerp.report import report_sxw
from openerp import models, fields, api
from datetime import datetime
from datetime import timedelta
from dateutil import rrule
import time


# class CiconAttendanceReport(report_sxw.rml_parse):
#
#     def __init__(self, cr, uid, name , context=None):
#         super(CiconAttendanceReport, self).__init__(cr, uid, name, context=context)
#         self.localcontext.update({
#             'time': time,
#         })
#         self.context = context
#
#
# class cicon_hr_daily_attendance_report(models.AbstractModel): # Report File Name
#     _name = 'report.cicon_hr.cicon_hr_daily_attendance_template'
#     _inherit = 'report.abstract_report'
#     _template = 'cicon_hr.cicon_hr_daily_attendance_template'
#     _wrapped_report_class = CiconAttendanceReport


class employee_attendance_report(models.AbstractModel): # Report File Name
    _name = 'report.cicon_hr.employee_attendance_report_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cicon_hr.employee_attendance_report_template')
        _docs = dict(employees=self.env['hr.employee'].search([('id', 'in', self._context.get('employee_ids'))]))
        rml = report_sxw.rml_parse(self._cr, self._uid, 'employee_attendance_report_template')
        docargs = {
            'doc_ids': self._context.get('employee_ids', False),
            'doc_model': report.model,
            'docs': _docs,
            'formatLang': rml.formatLang,
            'get_employee_attendance': self._get_employee_attendance,
            'fromDate': self._context.get('start_date'),
            'toDate': self._context.get('end_date')

        }
        return report_obj.render('cicon_hr.employee_attendance_report_template', docargs)

    def _get_employee_attendance(self, emp_id):
        if emp_id:
            _filter = [('employee_id', '=', emp_id), ('date', '>=', self._context.get('start_date')), ('date', '<=', self._context.get('end_date'))]
            _attendance_objs = self.env['cicon.hr.attendance'].search(_filter)
            _tempDate = datetime.strptime(self._context.get('start_date'), '%Y-%m-%d')
            _endDate = datetime.strptime(self._context.get('end_date'), '%Y-%m-%d')
            _attendances = {}
            while _tempDate <= _endDate:
                _att = [a for a in _attendance_objs if a.employee_id.id == emp_id and a.date == _tempDate.strftime('%Y-%m-%d')]
                if _att:
                    _attendances[_tempDate.strftime('%Y-%m-%d')] = {'attendance': _att[0],'att_day': _tempDate.strftime('%d-%m-%Y , %a')}
                else:
                    _attendances[_tempDate.strftime('%Y-%m-%d')] = None
                _tempDate += timedelta(days=1)
            return _attendances
        return []


class employee_leave_report(models.AbstractModel): # Report File Name
    _name = 'report.cicon_hr.employee_leave_report_weekly'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cicon_hr.employee_leave_report_weekly')
        _docs = self._get_emp_leave()
        rml = report_sxw.rml_parse(self._cr, self._uid, 'employee_leave_report_weekly')
        docargs = {
            'doc_model': report.model,
            'docs': _docs,
            'formatLang': rml.formatLang,
            'fromDate': self._context.get('start_date'),
            'toDate': self._context.get('end_date')
        }
        return report_obj.render('cicon_hr.employee_leave_report_weekly', docargs)

    def get_selection(self, model, field_name, val):
        return dict(self.env[model]._columns[field_name].selection).get(val)

    def _get_emp_leave(self):
        fromDate = self._context.get('start_date')
        toDate = self._context.get('end_date')
        _dmn = [('start_date', '<=', toDate), ('end_date', '>=', fromDate)]
        if self._context.get('leave_type', False):
            _dmn.append(('leave_type','=', self._context.get('leave_type')))
        print _dmn
        leave_ids = self.env['cicon.hr.employee.leave'].search(_dmn)
        employees = leave_ids.mapped('employee_id')
        _selected_dates = list(rrule.rrule(rrule.DAILY, dtstart=datetime.strptime(fromDate, '%Y-%m-%d'), until=datetime.strptime(toDate, '%Y-%m-%d')))
        _selected_dates.sort()
        _emp_leaves = []
        for emp in employees:
            _emp_leave_ids = leave_ids.filtered(lambda r: r.employee_id.id == emp.id)
            _leave_dates = []
            _leave_dict = {}
            for _emp_leave in _emp_leave_ids:
                _start_date = datetime.strptime(_emp_leave.start_date, '%Y-%m-%d')
                _end_date = datetime.strptime(_emp_leave.end_date, '%Y-%m-%d')
                _leave_dict.update({x.strftime('%Y-%m-%d'): self.get_selection('cicon.hr.employee.leave', 'leave_type', _emp_leave.leave_type)[:2].upper() for x in list(set(_selected_dates) & set(list(rrule.rrule(rrule.DAILY, dtstart=_start_date, until=_end_date))))})
            _emp_leaves.append(dict(employee=emp, leaves=_leave_dict))
        return {'data': _emp_leaves, 'period': _selected_dates}



