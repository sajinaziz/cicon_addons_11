import time
from odoo.report import report_sxw
from datetime import datetime
from dateutil import rrule


class EmpLeaveReport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(EmpLeaveReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time,
                                 'getSelectionValue': self.getSelectionValue,
                                 'getEmployeeLeave': self.get_employee_leave})

    def getSelectionValue(self, model, fieldName, field_val):
        return dict(self.pool.get(model).fields_get(self.cr, self.uid)[fieldName]['selection'])[field_val]

    def get_employee_leave(self, employee_id, report_year=None):
        if not report_year:
            report_year = datetime.today().year # set as current Year
        res = {}
        _emp_leave_obj = self.pool.get('cicon.hr.employee.leave')
        _leave_ids = _emp_leave_obj.search(self.cr, self.uid, [('employee_id', '=', employee_id)])
        _leave_days = []
        for leave in _emp_leave_obj.browse(self.cr, self.uid, _leave_ids):
            _start_date = datetime.strptime(leave.start_date, '%Y-%m-%d')
            _end_date = datetime.strptime(leave.end_date, '%Y-%m-%d')
            for d in rrule.rrule(rrule.DAILY, dtstart=_start_date, until=_end_date):
                _leave_days.append((leave.leave_type, d))
        _leave_types = [x[0] for x in _leave_days]
        for ltype in set(_leave_types):
            _ltype_val = self.getSelectionValue('cicon.hr.employee.leave', 'leave_type', ltype)
            res.update({_ltype_val: {}})
            m = 1
            while m <= 12:
                _leave_count = len([x for x in _leave_days if x[0] == ltype and x[1].month == m and x[1].year == report_year])
                res[_ltype_val][str(m)] =_leave_count
                m += 1
        return res

report_sxw.report_sxw('report.emp.leave.summary.webkit',
                      'hr.employee',
                      'cicon_addons/cicon_hr/report/emp_leave_report_summary.mako',
                      parser=EmpLeaveReport)
