from odoo import models, fields, api
from datetime import datetime


class CmmsPmSchPlanReportWizard(models.TransientModel):
    _name = 'cmms.pm.sch.plan.report.wizard'
    _description = "PM Plan"

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

    def _get_year(self):
        res = []
        for y in range(2014,  datetime.today().year + 2, 1):
            res.append((str(y), str(y)))
        return res

    def _get_this_year(self):
        return str(datetime.today().year)

    def _get_this_month(self):
        return str(datetime.today().month)

    rpt_month = fields.Selection(_MONTHS, string="Month", required=True, default=_get_this_month)
    rpt_year = fields.Selection(_get_year, string="Year", required=True, default=_get_this_year)

    @api.multi
    def show_report(self,data):
        self.ensure_one()
        ctx = dict(self._context)
        ctx['rpt_month'] = int(self.rpt_month)
        ctx['rpt_year'] = int(self.rpt_year)
        ctx['heading'] = 'Maintenance Preventive Plan [' + dict(self._MONTHS)[self.rpt_month] + '-' + self.rpt_year + ']'
        datas = {'ids': self.env.context.get('active_ids')}
        return self.with_context(ctx).env['report'].get_action(self, report_name='cmms.cmms_pm_plan_report_template', data=datas)

CmmsPmSchPlanReportWizard()

