from openerp.report import report_sxw
from openerp import models, fields, api

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


class cicon_hr_daily_attendance_report(models.AbstractModel): # Report File Name
    _name = 'report.cicon_hr.cicon_hr_daily_attendance_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cicon_hr.cicon_hr_daily_attendance_template')
        _docs = self.env[report.model].browse(self._ids)
        rml = report_sxw.rml_parse(self._cr, self._uid, 'cicon_hr_daily_attendance_template')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': _docs,
            'formatLang': rml.formatLang,
            'getDepartments': self._get_departments,
            'getWorkShift': self._get_work_shift
        }
        return report_obj.render('cicon_hr.cicon_hr_daily_attendance_template', docargs)

    def _get_departments(self):
        return self.env['hr.department'].search([])

    def _get_work_shift(self):
        return self.env['cicon.hr.work.shift'].search([])
