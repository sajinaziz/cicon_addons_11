from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil import rrule, parser
from datetime import datetime

_RRULE_TYPE = [
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('yearly', 'Year(s)')
            ]


class CmmsPmInterval(models.Model):
    _name = "cmms.pm.interval"
    _description = "Interval For PM Tasks"
    _log_access = False

    name = fields.Char('Interval', size=20, required=True)
    rrule_type = fields.Selection(_RRULE_TYPE , 'Recurrency',
            help="Let the event automatically repeat at that interval" , requied=True)
    count = fields.Integer('Repeat', help="Repeat x times", required=True)

    _sql_constraints = [('unique_interval', 'unique(name)', 'Scheme Must be unique')]
CmmsPmInterval()


class CmmsBaseSchedule(models.Model):
    _name = "cmms.base.schedule"
    _description = "Base Schedule"

    #store months in a dictionary with key
    months = {
    1: "January", 2: "February", 3: "March", 4: "April", \
    5: "May", 6: "June", 7: "July", 8: "August", 9: "September", \
    10: "October", 11: "November", 12: "December"}

    #store week days in a list of tuples with key

    _week_list= [('MO', 'Monday'), ('TU', 'Tuesday'), ('WE', 'Wednesday'), ('TH', 'Thursday'), ('FR', 'Friday'), ('SA', 'Saturday'), ('SU', 'Sunday')]

    date = fields.Date('Date', required=True, default=fields.Date.context_today)
    create_date = fields.Datetime('Created', readonly=True)
    end_type = fields.Selection([('count', 'Number of repetitions'), ('end_date','End date'), ('no_end', 'No End')],
                                default='no_end', string='Recurrence Termination')
    count = fields.Integer('Repeat', help="Repeat x times")
    select1 = fields.Selection([('date', 'Date of month'), ('day', 'Day of month')], 'Option')
    day = fields.Integer('Date of month', default=1)
    week_list = fields.Selection(_week_list, 'Weekday')
    byday = fields.Selection([
            ('1', 'First'),
            ('2', 'Second'),
            ('3', 'Third'),
            ('4', 'Fourth'),
            ('5', 'Fifth'),
            ('-1', 'Last')], 'By day')
    week_day = fields.Selection(_week_list, 'Weekday')
    month_list = fields.Selection(months.items(), 'Month')
    end_date = fields.Date('Repeat Until')
    recurrency = fields.Boolean('Recurrent', help="Recurrent Task", default=True)

CmmsBaseSchedule()


class CmmsPmScheduleMaster(models.Model):
    _name = "cmms.pm.schedule.master"
    _description = "PM Task Schedule"

    _inherits = {'cmms.base.schedule': 'base_sch_id'}

    @api.one
    @api.depends('rrule_type', 'date', 'interval', 'end_date', 'week_day', 'select1', 'end_type','week_list','byday')
    def compute_rule_string(self):
        """
        Compute rule string according to value type RECUR of iCalendar from the values given.
        @param self: the object pointer
        @param data: dictionary of freq and interval value
        @return: string containing recurring rule (empty if no rule)
        """
        def get_week_string(freq):
            if freq == 'weekly':
                byday = self.week_day
                if byday:
                    return ';BYDAY=' + byday
            return ''

        def get_month_string(freq):
            if freq == 'monthly':
                if self.select1 == 'date' and self.day < 1 or self.day > 31:
                    raise UserError('Please select a proper day of the month.')
                if self.select1 =='day':
                    return ';BYDAY=' + str(self.byday) + str(self.week_list)
                elif self.select1 =='date':
                    return ';BYMONTHDAY=' + str(self.day)
            return ''

        def get_end_date():
            _end_date = ''
            if self.end_date:
                _end_date = self.end_date
            return (self.end_type == 'count' and (';COUNT=' + str(self.count)) or '') +\
                             ((_end_date and self.end_type == 'end_date' and (';UNTIL=' + _end_date)) or '')

        def get_date_start():
            _date_start_ = fields.Date.from_string(self.date)
            return 'DTSTART:' + _date_start_.strftime('%Y%m%d') + 'T090000'

        freq = self.rrule_type
        res = ''
        if freq:
            interval_srting = self.interval and (';INTERVAL=' + str(self.interval)) or ''
            res = get_date_start() + ' RRULE:FREQ=' + freq.upper() + get_week_string(freq) + interval_srting + get_end_date() + get_month_string(freq)
        self.rrule_str = res

    # @api.one
    # @api.depends('rrule_str')

    def _get_next_date(self):
        for rec in self:
            _after = fields.Datetime.from_string(datetime.today().strftime('%Y-%m-%d 09:00:00'))
            rec.next_date = None
            _next_date = rrule.rrulestr(rec.rrule_str).after(_after, inc=False)
            if _next_date:
                rec.next_date = _next_date.strftime('%Y-%m-%d')

    @api.one
    @api.depends('pm_scheme_id', 'interval_id')
    def _get_task_ids(self):
        if self.pm_scheme_id and self.interval_id:
            _task = self.env['cmms.pm.task.master'].search([('pm_scheme_id', '=', self.pm_scheme_id.id), ('interval_id', '=', self.interval_id.id)])
            self.pm_task_ids = _task.ids

    def _search_next_date(self, operator, value):
        if operator == '=':
            _after = parser.parse(value)
            _recs = self.search([])
            _res = _recs.filtered(lambda r:  rrule.rrulestr(r.rrule_str).after(_after, inc=True) and rrule.rrulestr(r.rrule_str).after(_after, inc=True).strftime('%Y-%m-%d') == _after.strftime('%Y-%m-%d'))
            return [('id', 'in', _res._ids)]

    @api.multi
    def _display_name(self):
        for rec in self:
            rec.display_name = rec.pm_scheme_id.name + '/' + rec.interval_id.name

    #display name, generate  the display name ,combine the scheme name  and interval name using function
    display_name = fields.Char(string='Name', compute=_display_name, store=False)
    #pm scheme id, relate to scheme table and store pm scheme
    pm_scheme_id = fields.Many2one('cmms.pm.scheme', 'PM Scheme', required=True)
    #interval id, relate to interval table and store interval
    interval_id = fields.Many2one('cmms.pm.interval', "Interval", required=True)
    #rrule_str, compute rule string using function
    rrule_str = fields.Char(compute=compute_rule_string, string='RRule String', store=True)
    start_date = fields.Date("Start Date")
    #machine ids, create many2many relation to machine table and store machine ids
    machine_ids = fields.Many2many('cmms.machine', 'cmms_pm_sch_machine_rel', 'sch_id', 'machine_id', string="Machines", domain="[('pm_scheme_id','=',pm_scheme_id)]", required=True)
    #base_sch_id, create a relation to cmms base schedule and store it
    base_sch_id = fields.Many2one('cmms.base.schedule', ondelete='cascade', required=True)
    #pm task ids, create a manytomany relation and store task ids
    pm_task_ids = fields.Many2many('cmms.pm.task.master', compute=_get_task_ids, string="PM Tasks", store=False)

    rrule_type = fields.Selection(_RRULE_TYPE, related='interval_id.rrule_type', store=True, readonly=True, string='Recurrency',help="Let the event automatically repeat at that interval")
    interval = fields.Integer('Repeat Every', related='interval_id.count', store=False,  help="Repeat every (Days/Week/Month/Year)", readonly=True)

    next_date = fields.Date('Next Date', search=_search_next_date, compute=_get_next_date, store=False)
    #company id, create a relation to res company . store companies and set the current logged users company as the default company
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    @api.onchange('pm_scheme_id')
    def _filter_valid_interval(self):
        _dm = {}
        _exists_tasks = self.env['cmms.pm.task.master'].search([('pm_scheme_id', '=', self.pm_scheme_id.id)])
        _intervals = _exists_tasks.mapped('interval_id')
        _dm['interval_id'] = [('id', 'in', _intervals._ids)]
        return {'domain': _dm}


    @api.onchange('interval_id')
    def _check_machine_not_scheduled(self):
        _dm = {}
        _exists = self.env['cmms.pm.schedule.master'].search([('pm_scheme_id','=',self.pm_scheme_id.id),
                                                              ('interval_id','=',self.interval_id.id),
                                                              ])
        _machines = _exists.mapped('machine_ids')
        _dm['machine_ids'] = [('id', 'not in', _machines._ids),('pm_scheme_id','=',self.pm_scheme_id.id),('company_id', '=', self.company_id.id ) ]
        return {'domain': _dm }




    #TODO:Need to remove
    _sql_constraints = [('unique_schedule', 'CHECK(1=1)', "Task/Day/Machine should be Unique")]




CmmsPmScheduleMaster()







