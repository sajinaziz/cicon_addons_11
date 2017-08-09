from odoo import models, fields, api


class CiconHrDailyAttendanceTemplate(models.AbstractModel): # Report File Name
    _name = 'report.cicon_hr.cicon_hr_daily_attendance_template'

    @api.model
    def render_html(self,docids,data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cicon_hr.cicon_hr_daily_attendance_template')
        _doc_ids = docids or data.get('ids', data.get('active_ids'))
        _docs = self.env['cicon.hr.attendance.sheet'].search([('id', 'in', _doc_ids)])
        docargs = {
            'docs': _docs,
            'doc_ids': _doc_ids,
            'doc_model': report.model,
            'getDepartments': self._get_departments,
            'getWorkShift': self._get_work_shift
        }
        return report_obj.render('cicon_hr.cicon_hr_daily_attendance_template', docargs)

    def _get_departments(self):
        return self.env['hr.department'].search([])

    def _get_work_shift(self):
        return self.env['cicon.hr.work.shift'].search([])
