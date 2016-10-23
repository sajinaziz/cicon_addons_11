from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import pytz
import time
# import xlsxwriter
# import cStringIO
# import base64


class cicon_hr_attendance_log(models.Model):
    _name = "cicon.hr.attendance.log"
    _description = "CICON Attendance Log"
    _rec_name = 'utc_datetime'

    @api.one
    @api.depends('date', 'hour', 'minute')
    def gen_log_date(self):
        self.log_datetime = None
        self.utc_datetime = None
        if self.date:
            utc_z = pytz.utc
            local_z = pytz.timezone('Asia/Dubai')
            _str_time = str(self.date) + ' ' + str(self.hour)+ ':' + str(self.minute) + ':' + str(self.second)
            _strp_local = datetime.strptime(_str_time, "%Y%m%d %H:%M:%S")
            self.log_datetime = _strp_local.strftime('%Y-%m-%d %H:%M:%S')
            # _strp_local = _strp_local.replace(tzinfo=local_z)
            # _strp_local = pytz.timezone('Asia/Dubai').localize(_strp_local)
            _strp_local = local_z.localize(_strp_local)
            _strp_local.tzinfo
            utc = pytz.timezone('UTC')
            _utc_time = _strp_local.astimezone(utc)
            _utc_time.tzinfo
            self.utc_datetime = _utc_time.strftime('%Y-%m-%d %H:%M:%S')

    log_datetime = fields.Datetime(compute=gen_log_date, store=True, string='Date & Time Local')
    utc_datetime = fields.Datetime(compute=gen_log_date,store=True, string='Date & Time UTC')
    # log_datetime = fields.Datetime(  string='Date & Time Local')
    # utc_datetime = fields.Datetime( string='Date & Time UTC')
    employee_id = fields.Integer('Employee ID', required=True, index=True)
    date = fields.Integer('Punch Date', required=True, index=True)
    # date = fields.Date('Punch Date', required=True, index=True)
    hour = fields.Integer('Hour', required=True)
    minute = fields.Integer('Minute', required=True)
    second = fields.Integer('Second', required=True)
    type = fields.Integer('Type', required=True)
    device_id = fields.Integer('Device')

    _sql_constraints = [('uniq_log', 'UNIQUE(employee_id,date,hour,minute,second,type,device_id)', 'Log Cannot be Duplicated')]
    #
    # @api.model
    # def create(self, vals):
    #     rec = self.env['cicon.hr.attendance.log'].search([('id', '>', 0)], order='id desc', limit=1)
    #     punchDate = int(rec.date)
    #     punch_date  = '{:%Y-%m-%d}'.format(punchDate)
    #     vals.update({'date': punch_date})
    #     # print rec.date
    #     return super(cicon_hr_attendance_log, self).create(vals)

cicon_hr_attendance_log()


class cicon_hr_attendance_sheet(models.Model):
    _name = 'cicon.hr.attendance.sheet'
    _description = 'CICON Daily Attendance'
    _rec_name = 'attendance_date'

    attendance_date = fields.Date('Attendance Date', required=True)
    # employee_type = fields.Boolean('Workers')
    attendance_ids = fields.One2many('cicon.hr.attendance', 'sheet_id', string='Attendance')
    filtered_ids = fields.One2many('cicon.hr.attendance', 'sheet_id', string='Attendance', domain=[('work_shift','!=', False)] )
    missing_log_ids = fields.One2many('cicon.hr.attendance', 'sheet_id', string='Missing / Absent', domain=[ '&', ('work_shift','!=', False), '|', ('sign_in','=',False),  ('sign_out','=',False)])
    # employee_type = fields.Selection([('worker', 'Workers'), ('staff', 'Office Staff')], "Show Punches", default='worker')

    _sql_constraints = [('uniq_sheet', 'UNIQUE(attendance_date)', 'One Sheet per Date')]

    _order = 'attendance_date DESC'

    #
    # @api.onchange('employee_type')
    # def change_type(self):
    #     res = {'attendance_ids': '', 'missing_log_ids': ''}
    #     if self.employee_type == 'worker':
    #         res.update({'attendance_ids': [('cicon_employee_id','=', 5228)]})
    #         res.update({'missing_log_ids': [('work_shift','!=', False)]})
    #     else:
    #         res.update({'attendance_ids': [('work_shift','=', False)]})
    #         res.update({'missing_log_ids': [('work_shift','=', False)]})
    #     print res
    #     return {'domain': res}

    @api.multi
    def fill_log(self):
        assert len(self) == 1 # ids Length fix 1
        if self.attendance_ids: # Check for Existing Attendance clear if True
            _exits_ids = [x.id for x in self.attendance_ids]
            self.write({'attendance_ids': [(5, 0, _exits_ids)]})
        _date = self.attendance_date
        _employees = self.env['hr.employee'].search([('cicon_employee_id', '>', 0)])
        _atts = self.get_processed_attendance(_date, _employees)
        for _att in _atts:
            _att['sheet_id'] = self.id
            self.env['cicon.hr.attendance'].create(_att)
        return True

    def get_processed_attendance(self, _date , _employees):
        _date_int = int(time.strftime('%Y%m%d', time.strptime(_date, '%Y-%m-%d'))) # Convert date to Int as Log Required date in Int
        res = []
        _logs = self.env['cicon.hr.attendance.log'].search([('date', '>=', _date_int), ('date', '<=', _date_int + 1)]) #Find all logs for two days For night shift
        _leaves = self.env['cicon.hr.employee.leave'].search(['|', ('start_date', '<=', _date), ('end_date', '>=', _date)]) # Find All Leaves for the date
        if _logs:
            for _employee in _employees:
                _emp_log = {'employee_id': _employee.id, 'sign_in': '', 'sign_out': '', 'cicon_employee_id':_employee.cicon_employee_id ,'date_value': _date_int, 'leave_id': ''}
                _emp_in_log = [i for i in _logs if i.employee_id == _employee.cicon_employee_id and i.type in [1] and i.date == _date_int]
                _emp_out_log = [i for i in _logs if i.employee_id == _employee.cicon_employee_id and i.type in [3, 4] and i.date == _date_int]
                _emp_leave = [l for l in _leaves if l.employee_id.id == _employee.id]
                if _emp_in_log:
                    _emp_log['sign_in'] = _emp_in_log[0]
                    if _emp_log['sign_in'] and _emp_in_log[0].hour < 12: # Day Shift
                        _emp_out_log = [i for i in _logs if (i['employee_id']) == _employee['cicon_employee_id'] and i['type'] in [3, 4] and i['date'] == _date_int]
                    elif _emp_log['sign_in'] and _emp_in_log[0].hour > 12:
                        _emp_out_log = [i for i in _logs if (i['employee_id']) == _employee['cicon_employee_id'] and i['type'] in [3, 4] and i['date'] == _date_int + 1]
                if _emp_out_log:
                    _emp_log['sign_out'] = _emp_out_log[-1]
                if _emp_leave:
                    _emp_log['leave_id'] = _emp_leave[0].id
                if (_emp_log['sign_in'] and _emp_log['sign_out']) and _emp_log['sign_in'].log_datetime > _emp_log['sign_out'].log_datetime:
                    _emp_log['sign_out'] = None
                _emp_log['sign_in'] = _emp_log['sign_in'] and _emp_log['sign_in'].id or _emp_log['sign_in']
                _emp_log['sign_out'] = _emp_log['sign_out'] and _emp_log['sign_out'].id or _emp_log['sign_out']
                res.append(_emp_log)
        return res

    #For Report
    def get_work_hour(self, _wh):
        _wh_str = str(_wh).split('.')
        return _wh_str[0]+':'+ _wh_str[1]

    def getSelectionValue(self, model, fieldName, field_val):
        return dict(self.pool.get(model).fields_get(self._cr, self._uid)[fieldName]['selection'])[field_val]


    # @api.multi
    # def export_to_excel(self):
    #     assert len(self) == 1
    #
    #     output = cStringIO.StringIO()
    #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     worksheet = workbook.add_worksheet()
    #     # expenses = (
    #     #     ['Rent', 1000],
    #     #     ['Gas',   100],
    #     #     ['Food',  300],
    #     #     ['Gym',    50],)
    #     # row = 0
    #     # col = 0
    #     # for item, cost in (expenses):
    #     #     worksheet.write(row, col,     item)
    #     #     worksheet.write(row, col + 1, cost)
    #     #     row += 1
    #     #
    #     #
    #     # worksheet.write(row, 0, 'Total')
    #     # worksheet.write(row, 1, '=SUM(B1:B4)')
    #     row = 0
    #     for _att in self.attendance_ids:
    #         worksheet.write(row, 0,    _att.cicon_employee_id)
    #         worksheet.write(row,  1, _att.cicon_employee_id)
    #         worksheet.write(row,  2, _att.employee_id.name)
    #         worksheet.write(row, 3, _att.sign_in.log_datetime)
    #         worksheet.write(row, 4, _att.sign_out.log_datetime)
    #         worksheet.write(row, 5, _att.work_hour)
    #         row += 1
    #     workbook.close()
    #
    #     output.seek(0)
    #     vals = {
    #                 'name': 'TestExcel.xlsx',
    #                 'datas_fname': 'MyFirstExcel.xlsx',
    #                 'description': 'XXXXXXXXXXXXX',
    #                 'type': 'binary',
    #                 'db_datas': base64.encodestring(output.read()),
    #                 'res_model': 'cicon.hr.attendance.sheet',
    #                 'res_id': self.id,
    #
    #     }
    #     file_id = self.env['ir.attachment'].create(vals)
    #     print file_id
    #     return file_id



cicon_hr_attendance_sheet()


class cicon_hr_attendance(models.Model):
    _name = 'cicon.hr.attendance'
    _description = "Attendance"

    @api.one
    def _calc_work_hours(self):
        self.work_hour = 0
        if self.sign_in and self.sign_out and self.date_value:
            _in = datetime.strptime(self.sign_in.log_datetime, '%Y-%m-%d %H:%M:%S')
            _out = datetime.strptime(self.sign_out.log_datetime, '%Y-%m-%d %H:%M:%S')
            _float_time = str(_out - _in).split(':')
            if len(_float_time) == 3 and _float_time[0].isdigit() and _float_time[1].isdigit():
                self.work_hour = float(_float_time[0] + '.' + _float_time[1])
            self.date = time.strftime('%Y-%m-%d', time.strptime(str(self.date_value), '%Y%m%d'))
        elif self.date_value > 0:
            self.date = time.strftime('%Y-%m-%d', time.strptime(str(self.date_value), '%Y%m%d'))

    @api.one
    def _get_punch_logs(self):
        self.punch_log_count = 0
        if self.date_value:
            _punch_ids = self.env['cicon.hr.attendance.log'].search([('employee_id','=',self.cicon_employee_id), ('date','=',self.date_value)],count=True)
            self.punch_log_count = _punch_ids

    @api.one
    @api.depends('employee_id', 'date')
    def _get_emp_leave(self):
        if self.employee_id and self.date:
            holiday_id = self.env['cicon.hr.employee.leave'].search([('start_date', '<=', self.date), ('end_date', '>=', self.date), ('employee_id', '=', self.employee_id.id)], limit=1)
            self.leave_id = holiday_id.id

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    cicon_employee_id = fields.Integer(related='employee_id.cicon_employee_id', store=True, string='ID')
    work_shift = fields.Many2one('cicon.hr.work.shift', related='employee_id.work_shift', store=False, string="Shift")
    date_value = fields.Integer('Date Integer', required=True, index=True)
    date = fields.Date(compute=_calc_work_hours, string='Date', store=False)
    sign_in = fields.Many2one('cicon.hr.attendance.log',  string='Sign In')
    sign_out = fields.Many2one('cicon.hr.attendance.log',  string='Sign Out')
    work_hour = fields.Float(compute=_calc_work_hours, string="Work Hour", store=False)
    sheet_id = fields.Many2one('cicon.hr.attendance.sheet', string='Attendance Sheet', ondelete='cascade')
    leave_id = fields.Many2one('cicon.hr.employee.leave',compute=_get_emp_leave, string='Leave')
    punch_log_count = fields.Integer(compute=_get_punch_logs, store=False, string="Punches")

    _order = 'cicon_employee_id,date_value'

    _sql_constraints = [('uniq_sheet', 'UNIQUE(employee_id,sheet_id)', 'One Employee per Sheet')]

    @api.constrains('sign_in', 'sign_out')
    def _verify_in_out(self):
        if self.sign_in and self.sign_out:
            if self.sign_in.log_datetime > self.sign_out.log_datetime:
                raise Warning('Sign IN Time < Sign OUT Time')

    @api.multi
    def show_employee_leave_form(self):
        self.ensure_one()
        compose_form = self.env.ref('cicon_hr.cicon_hr_employee_leave_form_view_wizard', False)
        ctx = dict(default_employee_id=self.employee_id.id,
                default_leave_type='absent',
                default_start_date=self.date,
                default_end_date=self.date)
        return {
            'name': 'Employee Leave',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cicon.hr.employee.leave',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx

        }


cicon_hr_attendance()


class cicon_hr_work_shift(models.Model):
    _name = 'cicon.hr.work.shift'
    _description = "Work Shift"

    name = fields.Char("Shift", required=True)

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'Shift Name')]

cicon_hr_work_shift()
