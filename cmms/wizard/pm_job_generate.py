from odoo import models, fields, api
import datetime


class CmmsPmGenerateWizard(models.TransientModel):
    _name = "cmms.pm.generate.wizard"
    _description = "PM Generator"

    pm_date = fields.Date('PM Date', required=True, default=fields.Date.context_today)
    pm_schedule_ids = fields.Many2many('cmms.pm.schedule.master', string="Schedule", store=False, readonly=True)

    @api.onchange('pm_date')
    def date_change(self):
        _sch_obj = self.env['cmms.pm.schedule.master']
        _sch_recs = _sch_obj.search([('next_date', '=', self.pm_date),('company_id', '=', self.env.user.company_id.id)])
        self.pm_schedule_ids = _sch_recs

    @api.multi
    def generate_pm_job(self):
        _sch_obj = self.env['cmms.pm.schedule.master']
        _job_obj = self.env['cmms.job.order']
        _sch_recs = _sch_obj.search([('next_date', '=', self.pm_date),('company_id', '=', self.env.user.company_id.id)])
        _pm_job_ids = []
        if _sch_recs:
            _machines = _sch_recs.mapped('machine_ids')
            for m in _machines.filtered(lambda m: m.company_id.id == self.env.user.company_id.id and  m.is_active == True).sorted(key=lambda r: r.code):
                _exist = self.env['cmms.job.order'].search([('machine_id', '=', m.id),
                                                            ('job_order_type', '=', 'preventive'),
                                                            ('job_order_date', '=', self.pm_date)], limit=1)
                _m_sch_ids = _sch_recs.filtered(lambda s: m in s.machine_ids)
                _task_ids = _m_sch_ids.mapped('pm_task_ids')
                if _exist:
                    _pm_job_ids.append(_exist.id)
                    _ex_task_ids = _exist.sch_pm_task_ids.mapped('pm_task_id')
                    _need_to_create = _task_ids - _ex_task_ids
                    if _need_to_create:
                        _pm_new_task = map(lambda x: dict(pm_task_id=x), _need_to_create.ids)
                        _exist.write({'sch_pm_task_ids': map(lambda x: (0, 0, x), _pm_new_task)})
                else:
                    _pm_task_list = map(lambda x: dict(pm_task_id=x), _task_ids.ids)
                    _seq_obj_pm = self.env['ir.sequence'].search([('code', '=', 'cmms.job.order.preventive'),
                                                               ('company_id', '=', self.env.user.company_id.id)])
                    _pm_job_order = {
                        'machine_id': m.id,
                        'name': _seq_obj_pm.next_by_id(),
                        'job_order_type': 'preventive',
                        'job_order_date': self.pm_date,
                        'state': 'open',
                        'description': 'Preventive Maintenance',
                        'sch_pm_task_ids': map(lambda x: (0, 0, x), _pm_task_list),
                        'company_id': m.company_id.id

                    }
                    _job_order = _job_obj.create(_pm_job_order)
                    if _job_order:
                        _pm_job_ids.append(_job_order.id)
        if len(_pm_job_ids) > 0:
            _pm_jobs =_job_obj.search([('id', 'in', _pm_job_ids)])
            return self.env['report'].get_action(_pm_jobs, 'cmms.cmms_job_order_template')
        else:
            return False

        # _pm_date = None
        # if ids:
        #     _pm_obj = self.read(cr,uid,ids)
        #     _pm_date = _pm_obj[0]['pm_date']
        # if not _pm_date: _pm_date = datetime.date.today()
        # _sch_obj = self.pool.get('cmms.pm.schedule')
        # _pm_job_order_obj = self.pool.get('cmms.job.order')
        # _sch_ids = _sch_obj.search(cr,uid,[('start_date', '=', _pm_date)])
        # _machine_ids = []
        # if _sch_ids:
        #     for _s in _sch_obj.browse(cr,uid,_sch_ids):
        #         _machine_ids.append(_s.machine_id.id)
        #     dist_mac_ids = set(_machine_ids)
        #     _job_ids = []
        #     for m in dist_mac_ids:
        #         _pm_job_order = {
        #             'machine_id': m,
        #             'name': self.pool.get('ir.sequence').get(cr, uid , 'cmms.job.order.preventive') or '/',
        #             'job_order_type': 'preventive',
        #             'job_order_date': _pm_date,
        #             'job_order_datetime': datetime.datetime.now(),
        #             'state': 'open'
        #         }
        #         res = _pm_job_order_obj.create(cr, uid, _pm_job_order)
        #         _job_ids.append(res)
        #     _pm_job_order_obj.fill_pm_schedule(cr, uid, _job_ids)
CmmsPmGenerateWizard()




