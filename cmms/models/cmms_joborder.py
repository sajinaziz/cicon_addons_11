from odoo import models, fields, api, tools
# from openerp.exceptions import Warning
from datetime import datetime
# keep job order type in list of tuples
JOB_ORDER_TYPE = [('breakdown', 'BREAKDOWN'), ('preventive', 'PREVENTIVE'), ('general', 'GENERAL')]


class CmmsJobCategory(models.Model):

    #keep jobcategory details
    _name = "cmms.job.category"
    _description = "Job Category"
    _log_access = False

    name = fields.Char('Job Category', required=True)

    _sql_constraint = [("unique_name", "unique(name)", "Job Category must be Unique")]

CmmsJobCategory()


class CmmsJobOrder(models.Model):
    _name = "cmms.job.order"
    _description = "Job Order"
    _inherit = ['mail.thread']

    #Inverse Sample for Job Order Code
    # def _set_job_code(self):
    #     for rec in self:
    #         if rec.job_order_code_id:
    #             rec.job_order_code_id.write({'created': True, 'cancelled': False})
    @api.multi
    def _calc_total(self):
        """ Calcute the total work hours """
        for rec in self:
            #calculate the sum of total spare parts
            rec.total_amount = sum([x.amount for x in rec.spare_part_ids])
            if rec.work_start_datetime and rec.work_end_datetime:
                #find out the start date
                _start = datetime.strptime(rec.work_start_datetime, tools.DEFAULT_SERVER_DATETIME_FORMAT)
                ##find out the end date
                _end = datetime.strptime(rec.work_end_datetime, tools.DEFAULT_SERVER_DATETIME_FORMAT)
                #find the difference between end and start
                _wh_diff = _end - _start
                #find out seconds from date diff value(_wh_diff)
                _wh_day_sec = _wh_diff.days * 24 * 3600
                #find out minute
                _wh_min = (_wh_day_sec + _wh_diff.seconds) / 60
                #find out hour
                _wh_hour = (_wh_min / 60)
                _wh_mod_min = _wh_min % 60
                _wh = _wh_hour + _wh_mod_min/60.0
                rec.work_hour = float(_wh)

    @api.model
    def _get_default_status(self):
        """ to  find out the default job order status   """
        #search status
        _status = self.env['cmms.job.order.status'].search([('sequence', '>', '0')], order='sequence', limit=1)
        if _status:
            return _status

    @api.multi
    @api.depends('work_end_datetime','job_order_date')
    def _get_job_completed_date(self):
        for rec in self:
            if rec.work_end_datetime:
                rec.completed_date = datetime.strptime(rec.work_end_datetime, tools.DEFAULT_SERVER_DATETIME_FORMAT).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
            else:
                rec.completed_date = rec.job_order_date


    # job order code id, store job order code  for created and cancelled are false
    job_order_code_id = fields.Many2one("cmms.job.order.code",
                                        domain="[('job_order_type','=',job_order_type),('printed','=',True),"
                                               "('created','=',False),('cancelled','=',False)]")

    name = fields.Char("Code", required=True, track_visibility='always', readonly=True, states={'open': [('readonly', False)]})
    # store the type of job orders
    job_order_type = fields.Selection(JOB_ORDER_TYPE, "JobOrderType", required=True)
    #machine id, store the machine ids (eg: SL-13)
    machine_id = fields.Many2one('cmms.machine', 'Machine', required=True, readonly=True, states={'open': [('readonly', False)]})
    #machine, store the machine names
    machine = fields.Char('Machine Name', related='machine_id.name', store=False, readonly=True)
    #machine type, store type of machines like cut & bend etc...
    machine_type = fields.Many2one('cmms.machine.type', string='Machine Type', related='machine_id.type_id', store=False, readonly=True)
    job_order_date = fields.Date('Job Order Date', required=True, readonly=True,
                                 states={'open': [('readonly', False)]}, track_visibility='onchange')
    description = fields.Char(string='Description', size=200, readonly=True,
                              states={'open': [('readonly', False)]})
    # job category id, create a relation to category table and store job category
    job_category_id = fields.Many2one('cmms.job.category', 'Job Category', readonly=True,
                                      states={'open': [('readonly', False)]})
    #company id, create a relation to company , store company and set the current logged user company as the default company
    company_id = fields.Many2one('res.company',  string="Company",
                                 default=lambda self: self.env.user.company_id)

    breakdown_datetime = fields.Datetime('Breakdown Time', readonly=True,
                                         states={'open': [('readonly', False)]})
    reported_datetime = fields.Datetime('Reported Date', readonly=True,
                                        states={'open': [('readonly', False)]})

    reported_by = fields.Char("Reported/Operated By", size=50, readonly=True,
                              states={'open': [('readonly', False)]})
    #foreman,  the foreman in charge
    foreman = fields.Char('Foreman In charge', size=50, readonly=True,
                          states={'open': [('readonly', False)]})
    #technician, store the person who is in charge of maintenance
    technician = fields.Char('Maintenance/Technician In charge', size=50, readonly=True,
                             states={'open': [('readonly', False)]})
    #reason, store the breakdown reason
    reason = fields.Text('Reason', size=500, readonly=True,
                         states={'open': [('readonly', False)]})
    #corrective_action, store the corrective action
    corrective_action = fields.Text('Action', size=500, readonly=True,
                                    states={'open': [('readonly', False)]})
    service = fields.Boolean('Service Assistance', readonly=True,
                             states={'open': [('readonly', False)]})
    #priority, store the different type of priorities
    priority = fields.Selection([('low', 'LOW PRIORITY'), ('normal', 'PRIORITY REPAIR'),
                                 ('high', 'PRIORITY NEXT DAY'), ('highest', 'URGENT REPAIR')], "Priority",
                                readonly=True,
                                states={'open': [('readonly', False)]}, default='low', track_visibility='onchange')

    attended_by = fields.Char('Attended By', size=100, readonly=True,
                              states={'open': [('readonly', False)]})

    work_start_datetime = fields.Datetime('Work Started', readonly=True,
                                          states={'open': [('readonly', False)]})
    work_end_datetime = fields.Datetime('Work End', readonly=True,
                                        states={'open': [('readonly', False)]})
    completed_date = fields.Date( compute=_get_job_completed_date, string="Completed Date", store=True)
    #status id, relate to job order status table and store status, then find out the default job order status
    status_id = fields.Many2one('cmms.job.order.status', string="Status", default=_get_default_status, track_visibility='onchange')
    state = fields.Selection(related='status_id.state_name', string="State",
                             store=True, readonly=True)
    #sch pm task ids, create a relation to cmms pm task job order line and store sch pm task ids
    sch_pm_task_ids = fields.One2many('cmms.pm.task.job.order.line', 'job_order_id', string="PM Tasks")
    #spare part ids, create a relation to cmms store invoice line and store spare part ids
    spare_part_ids = fields.One2many('cmms.store.invoice.line', 'job_order_id', readonly=True, string="Parts")
    # total amount, calculate total amount using _calc_total function
    total_amount = fields.Float(string="Total Amount", compute=_calc_total)
    #work hour, calulate the wrk hour using _calc_total function
    work_hour = fields.Float(string='Work Hours', compute=_calc_total)

    _order = 'job_order_date desc'

    _sql_constraints = [("unique_code", "unique(name)", "Job Order Code must be Unique")]

    #("unique_machine_job", "unique(machine_id,job_order_date,job_order_type)", "Job Order Machine/Day/Job Type")

    @api.onchange('job_order_code_id')
    def _set_code(self):
        if self.job_order_code_id:
            self.name = self.job_order_code_id.name

    # to load the job order code based on the job order type
    @api.onchange('job_order_type')
    def _get_job_code(self):
        if self.job_order_type:
            _last_rec = self.search([], order='id desc', limit=1)
            _last_id = _last_rec.job_order_code_id.id or 0
            _latest_rec = self.env['cmms.job.order.code'].search([('printed', '=', True), ('created', '=', False), ('cancelled', '=', False), ('company_id', '=', self.env.user.company_id.id), ('job_order_type', '=',  self.job_order_type), ('id', '>', _last_id)], order='id',   limit=1)
            self.job_order_code_id = _latest_rec.id
            self.name = _latest_rec.name
            _dm = {}
            if self.job_order_type == 'general':
               _dm['machine_id'] = [('is_machinery', '=', False),('company_id', '=', self.company_id.id)]
            elif self.job_order_type == 'breakdown' or self.job_order_type== 'preventive':
                _dm['machine_id'] = [('is_machinery', '=', True), ('company_id', '=', self.company_id.id)]
            return {'domain': _dm }

    @api.multi
    def unlink(self):
        """"
            change status on the button click
        """
        for rec in self:
            if rec.job_order_code_id:
                rec.job_order_code_id.write({'cancelled': True, 'created': False})
        res = super(CmmsJobOrder, self).unlink()
        return res

    @api.model
    def create(self, vals):
        res = super(CmmsJobOrder, self).create(vals)
        self.job_order_code_id.write({'cancelled': False, 'created': True})
        return res

    @api.multi
    def print_job_order(self):
        """Print Job Order form button click"""
        self.ensure_one()
        return self.env['report'].get_action(self, 'cmms.cmms_job_order_template')

CmmsJobOrder()

# class to store job order status details
class CmmsJobOrderStatus(models.Model):
    _name = "cmms.job.order.status"
    _description = "Job Order Status"

    name = fields.Char('Status', required=True)
    state_name = fields.Selection([('open', 'Pending'),
                              ('cancel', 'Cancelled'),
                              ('done', 'Completed')], 'State', default='open', required=True)
    sequence = fields.Integer('Sequence')
    fold = fields.Boolean('Fold', default=False)

    _order = 'sequence'

    _sql_constraints = [('uniq_status', 'UNIQUE(name)', 'Status Should be Unique!')]

CmmsJobOrderStatus()

# class to store job order code
class CmmsJobOrderCode(models.Model):
    _name = "cmms.job.order.code"
    _description = "Job Order Code"

    name = fields.Char('Job Order Code', size=12, required=True)

    job_order_type = fields.Selection(JOB_ORDER_TYPE, "Job Order Type", required=True)
    created = fields.Boolean('Is Created')
    printed = fields.Boolean('Is Printed')
    cancelled = fields.Boolean('Is Cancelled')
    company_id = fields.Many2one('res.company', "Company", required=True)

    _sql_constraint = [("unique_name", "unique(name)", "Job Order Code must be Unique")]

CmmsJobOrderCode()

# To store PmTask joborder lines
class CmmsPmTaskJobOrderLine(models.Model):
    _name = 'cmms.pm.task.job.order.line'
    _description = "PM Job Order Tasks"

    #job_order_id, relate to job order and store the job order ids
    job_order_id = fields.Many2one('cmms.job.order', string="Job Order")
    #pm task id, relate to pm task manager and store the tasks
    pm_task_id = fields.Many2one('cmms.pm.task.master', string="PM Task", readonly=True)
    #interval_id, relate to pm interval and store the task intervals
    interval_id = fields.Many2one('cmms.pm.interval', related='pm_task_id.interval_id', string='Interval', store=False, readonly=True)
    #machine id, relate to machine table and store the machine ids
    machine_id = fields.Many2one('cmms.machine', ralated='job_order_id.machine_id', string="Machine", store=False)
    date_completed = fields.Date('Completed Date', related='job_order_id.completed_date', store=True, readonly=True)
    state = fields.Selection(related='job_order_id.state', store=True, string = "Status", readonly=True)
    remarks = fields.Char('Remarks')

    @api.onchange('state')
    def _change_state(self):
        if self.state == 'done':
            if not self.date_completed:
                self.date_completed = fields.Date.today()

CmmsPmTaskJobOrderLine()



