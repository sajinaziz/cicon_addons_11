from odoo import models, fields, api
from datetime import datetime,date,timedelta
from odoo.exceptions import UserError
import calendar

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
                                    ('machine_status_report','Machine Status Report')],string='Report', required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    start_date = fields.Date('Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date('End Date', required=True, default=fields.Date.context_today)
    job_order_type = fields.Selection(JOB_ORDER_TYPE, "Job Order Type")
    machine_categ_ids = fields.Many2many('cmms.machine.category','cmms_report_machine_categ_sel_rel', 'wizard_id', 'categ_id',
                                         string="Machine Category")


   # print report_year

    ''' fill year select box values '''
    current_year = datetime.today().strftime("%Y")
    last_year = int(current_year) - 1
    prev_last_year = int(last_year) - 1
    prev_year = int(prev_last_year) - 1

    report_year = fields.Selection(
        [(current_year, current_year), (last_year, last_year), (prev_last_year, prev_last_year),
         (prev_year, prev_year)],string="Year")

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
            _job_orders = self.env['cmms.job.order'].search(_qry)
            if _job_orders.ids:
                return self.env['report'].get_action(_job_orders, 'cmms.job_order_report_template')
            else:
                raise UserError("No Report Exists For This Period")
        if self.report_list == 'parts_by_producttype_report':
            ctx['heading'] = "Spare Parts Summary" + '\n' + "  From[ " + start_date + ' To ' + end_date + ' ]'
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
