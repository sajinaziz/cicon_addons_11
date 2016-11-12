from odoo import models, fields, api
from datetime import datetime,date,timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import calendar
import xlsxwriter
import cStringIO
import base64

JOB_ORDER_TYPE = [('breakdown', 'BREAKDOWN'), ('general', 'GENERAL'),('preventive','PREVENTIVE')]


class CmmsCommonReportWizard(models.TransientModel):
    _name = 'cmms.common.report.wizard'
    _description = "CMMS Reports"

    @api.onchange('report_by')
    def _get_date(self):
        today = datetime.today() # store the current date(today's date)
        first_day = today.replace(day=1) # find the first day of the current date or current month
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1]) # find the last day of the current date or current month
        week_day = (today.weekday()+1)% 7 # find the current day number: 1=monday, 6= saturday

        saturday = today - timedelta(7 + week_day - 6) #find the current day before  saturday  and convert to the date format
        this_saturday = '{:%Y-%m-%d}'.format(saturday)
        if self.report_by == "this_month":
            self.start_date = first_day # assign this month first day and last day
            self.end_date = last_day
        elif self.report_by == "last_month":
            last_day_prev_month = first_day - timedelta(days=1) # find  the last day of the previous month or last month
            first_day_prev_month = last_day_prev_month.replace(day=1) # find the first day of the previous month or last month
            self.start_date = first_day_prev_month # assign  first day and last day of the previous month
            self.end_date = last_day_prev_month
        elif self.report_by == "this_week":
            self.start_date = this_saturday # assign  the current day before  saturday and current day of this week
            self.end_date = today
        elif self.report_by == "last_week":
            sat_day = (saturday.weekday() + 1) % 7  # find the last week  saturday number
            self.start_date = saturday - timedelta(7 + sat_day - 6) # find  and assign the last saturday
            self.end_date = this_saturday #assign  the current day before  saturday




    report_by = fields.Selection([('this_month','This Month'),('this_week','This Week'),('last_month','Last Month'),('last_week','Last Week')],string='Report By')
    report_list = fields.Selection([('expense_report', 'Expense Summary'),
                                   ('expense_detailed', 'Expense Detailed'),
                                    ('job_order_report','Job Order Report'),
                                    ('parts_by_producttype_report','Parts Summary By Product Type Report'),
                                    ('machine_analysis_report','Machine Analysis Report'),
                                    ('machine_status_report','Machine Status Report'),
                                    ('parts_depreciation_report', 'Depreciation Report')],string='Report', required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    start_date = fields.Date('Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date('End Date', required=True, default=fields.Date.context_today)
    job_order_type = fields.Selection(JOB_ORDER_TYPE, "Job Order Type")
    machine_categ_ids = fields.Many2many('cmms.machine.category','cmms_report_machine_categ_sel_rel', 'wizard_id', 'categ_id',
                                         string="Machine Category")
    report_option = fields.Selection([('summary', 'Summary'), ('detail', 'Detailed')], string='Report Option',default='summary')

    #find the end date of the select month in report

    @api.onchange('rpt_month')
    def last_date_of_month(self):
        if self.rpt_month and self.report_year:
            month = int(self.rpt_month)
            year = int(self.report_year)
            selected_date = date(year, month, 1)

            if selected_date.month == 12:  # December
                last_day_selected_month = date(selected_date.year, selected_date.month, 31)
            else:
                last_day_selected_month = date(selected_date.year, selected_date.month + 1, 1) - timedelta(days=1)
            self.end_date = last_day_selected_month
            #print self.end_date

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

    def _get_this_month(self):
        return str(datetime.today().month)

    rpt_month = fields.Selection(_MONTHS, string="Month", required=True, default=_get_this_month)


    ''' fill year select box values '''
    current_year = datetime.today().strftime("%Y")
    last_year = int(current_year) - 1
    prev_last_year = int(last_year) - 1
    prev_year = int(prev_last_year) - 1

    report_year = fields.Selection(
        [(current_year, current_year), (last_year, last_year), (prev_last_year, prev_last_year),
         (prev_year, prev_year)],string="Year",default=current_year)

    @api.onchange('report_year')
    def _fill_date(self):
        if self.report_year > 0:
            #print self.report_year
            first_month = date(int(self.report_year), 1, 1)
            last_month = date(int(self.report_year), 12, 31)
            # year_data = self.report_year
            year_first_day = '{:%Y-%m-%d}'.format(first_month)
            year_last_day = '{:%Y-%m-%d}'.format(last_month)
            self.start_date = year_first_day
            self.end_date = year_last_day

    def _gen_depreciation_report(self, end_date):
        _types = self.env['cmms.spare.part.type'].search([('is_asset', '=', True)])
        _domain = [('invoice_date' ,'<=' , end_date), ('spare_part_type_id', 'in' , _types.ids), ('job_order_id','!=', False)]
        _fields = ['machine_id','invoice_date', 'amount']
        _group_by = [('machine_id'),('invoice_date:month')]
        _store_lines = self.env['cmms.store.invoice.line'].read_group(domain=_domain, fields=_fields, groupby=_group_by,lazy=False)
        _res_list = []
        _mac_ids = [r['machine_id'][0] for r in _store_lines]
        _all_machines = self.env['cmms.machine'].search([('id', 'in', list(set(_mac_ids)))])
        _records = {}
        for _machine in list(set(_mac_ids)):
            _res = [r for r in _store_lines if r['machine_id'][0] == _machine]
            _val = {}
            for _r in _res:
                _d_str = _r['invoice_date:month'].strip() + ' ' + '01'
                _invoice_date = datetime.strptime(_d_str, '%B %Y %d')
                _invoice_amount = float(_r['amount'])
                _run_amount = _invoice_amount
                _dep_value =  float(_invoice_amount /24)
                for x in range(0,25,1):
                    _month = _invoice_date + relativedelta(months=x)
                    if _val.get(_month):
                        _val[_month] = _val[_month] + _run_amount
                    else:
                        _val[_month] = _run_amount
                    _run_amount -= _dep_value
            _records[_all_machines.filtered(lambda m: m.id == _machine)] = _val

        _dates = []
        for c in _records:
            _dates.extend(_records[c].keys())
        _date_list = list(set(_dates))
        _date_list.sort()

        output = cStringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        row = 0
        col = 3
        worksheet.write(row, 0, 'Sn#')
        worksheet.write(row, 1, 'Code')
        worksheet.write(row, 2, 'Name')
        worksheet.write(row, 3, 'Category')
        for _d in _date_list:
           col += 1
           worksheet.write(row, col, _d.strftime('%b %Y'))
        for rec in _records:
            row += 1
            worksheet.write(row, 0, row)
            worksheet.write(row, 1, rec.code)
            worksheet.write(row, 2, rec.name)
            col = 3
            for _d in _date_list:
                col += 1
                v = (_records[rec]).get(_d, '')
                if v:
                    v_amount = round(float(v),2)
                    #print v_amount
                    worksheet.write(row, col, v_amount)
        workbook.close()
        output.seek(0)
        _r_name = 'Depreciation Report -' + datetime.today().strftime('%d-%b-%Y')
        _file_name = 'cmms_depreciation_' + datetime.today().strftime('%d-%b-%Y') + '.xlsx'
        vals = {
                'name': _r_name,
                'datas_fname': _file_name,
                'description': 'CMMS Depreciation Report',
                'type': 'binary',
                'db_datas': base64.encodestring(output.read()),
                'res_model': 'cmms.common.report.wizard'
        }
        file_id = self.env['ir.attachment'].create(vals)
        return file_id


    @api.multi
    def show_report(self,data):
        self.ensure_one()
        ctx = dict(self._context)
        start_date = datetime.strptime(self.start_date, '%Y-%m-%d').strftime('%d-%b-%Y')
        end_date = datetime.strptime(self.end_date, '%Y-%m-%d').strftime('%d-%b-%Y')
        ctx['from_date'] = start_date
        ctx['to_date'] = end_date
        datas = {'ids': self.env.context.get('active_ids', [])}
        if self.company_id:
            ctx['company_id'] = self.company_id.id
        if self.report_list == 'expense_report':
            ctx['show_summary'] = 1
            ctx['heading'] = "Expense Report - Summary [ " + start_date + ' To ' + end_date + ' ]'
            return self.with_context(ctx).env['report'].get_action(self,
                                                                   report_name='cmms.cmms_inventory_expense_report_summary',
                                                                   data=datas)
        elif self.report_list == 'expense_detailed':
            ctx['show_summary'] = 0
            ctx['heading'] = "Expense Report - Detailed [ " + start_date + ' To ' + end_date + ' ]'
            return self.with_context(ctx).env['report'].get_action(self,
                                                                   report_name='cmms.cmms_inventory_expense_report_summary',
                                                                   data=datas)

        if self.report_list == "job_order_report":
            _qry = [('job_order_date', '>=', self.start_date), ('job_order_date', '<=', self.end_date)]
            if self.job_order_type=="breakdown" or self.job_order_type=="general" or self.job_order_type=="preventive":
                _qry.append(('job_order_type', '=', self.job_order_type))
            if self.company_id:
                _qry.append(('company_id', '=', self.company_id.id))
            _job_orders = self.env['cmms.job.order'].search(_qry, order='job_order_date')
            if _job_orders.ids:
                return self.env['report'].get_action(_job_orders, 'cmms.job_order_report_template')
            else:
                raise UserError("No Report Exists For This Period")
            
        if self.report_list == 'parts_by_producttype_report':
            ctx['report_option'] = self.report_option
            if self.report_option == 'summary':
                ctx['heading'] = "Spare Parts Summary by Product Type" + "(" + start_date + ' to ' + end_date + ' )'
            elif self.report_option == 'detail':
                ctx['heading'] = "Spare Parts Details by Product Type" + "(" + start_date + ' to ' + end_date + ' )'
            return self.with_context(ctx).env['report'].get_action(self,
                                                                   report_name='cmms.report_partsby_producttype_summary_template',
                                                                   data=datas)
        if self.report_list == 'machine_analysis_report':
            ctx['year'] = self.report_year
            ctx['machine_categ_ids'] = self.machine_categ_ids._ids
            return self.with_context(ctx).env['report'].get_action(self,
                                                                   report_name='cmms.report_machine_analysis_summary_template',
                                                                   data=datas)
        if self.report_list == 'machine_status_report':
            if self.company_id:
                _qry = [('company_id', '=', self.company_id.id),('is_machinery','=', 'True')]
            _machines = self.env['cmms.machine'].search(_qry)
            if _machines.ids:
                return self.env['report'].get_action(_machines, 'cmms.report_machine_status_template')
            else:
                raise UserError("No Report Exists")

        if self.report_list == 'parts_depreciation_report':
            self._gen_depreciation_report(self.end_date)



