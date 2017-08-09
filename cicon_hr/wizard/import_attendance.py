from odoo import models, fields, api
import base64
import csv


class cicon_hr_import_attendance(models.TransientModel):
    _name = 'cicon.hr.import.attendance'
    _description = "Import Attendance"

    log_files = fields.One2many('cicon.hr.attendance.log.file', 'wizard_id', string='Log Files', required=True)
    emp_id_list = fields.Char('Employees not available' , readonly=True)

    @api.multi
    def import_log(self):
        _fields = ['employee_id', 'date', 'hour', 'minute', 'second', 'type', 'device_id']
        _attendance_log_obj = self.env['cicon.hr.attendance.log']
        for _file in self.log_files:
            # with open(_file.log_file, 'rb') as csvfile:
            #     spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            #     for row in spamreader:
            #         print ', '.join(row)
            _emp_ids = []
            _log_read = base64.decodestring(_file.log_file)
            log_lines = _log_read.split('\n')
            for line in log_lines:
                _line_split = line.split(',')
                if len(_line_split) == 7:
                    values = dict(zip(_fields, _line_split))
                    _emp_ids.append(int(values.get('employee_id', 0)))
                    _domain = zip(_fields, '=' * len(_fields), _line_split)
                    _exists = _attendance_log_obj.search_count(_domain)
                    if _exists == 0:
                        _val = _attendance_log_obj.create(values)
            _company_emp_ids = self.env['hr.employee'].search([('company_id', '=', self.env.user.company_id.id)])
            _emp_ids = list(set(_emp_ids))
            _diff = [e for e in _emp_ids if e not in _company_emp_ids.mapped('cicon_employee_id')]
            if _diff:
                self.emp_id_list = ', '.join(str(i) for i in sorted(_diff))
                ctx = dict(self._context)
                ctx['hide_import'] = True
                return {
                    'name': 'Employee not registered',
                    'view_mode': 'form',
                    'view_id': self.env.ref('cicon_hr.cicon_hr_import_attendance_view').id,
                    'view_type': 'form',
                    'res_id': self.id,
                    'res_model': 'cicon.hr.import.attendance',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'context': ctx
                }
            else:
                return True

cicon_hr_import_attendance()


class cicon_hr_attendance_log_file(models.TransientModel):
    _name = 'cicon.hr.attendance.log.file'
    _description = 'Log File'

    log_file = fields.Binary('Log File', filter="*.log")
    name = fields.Char('Filename')
    wizard_id = fields.Many2one('cicon.hr.import.attendance', string='Wizard')

cicon_hr_import_attendance()