from odoo import models, fields, api
import time


class cicon_qc_observation_category(models.Model):
    _name = 'cicon.qc.observation.category'
    _description = "CICON QC Observation Category"

    name = fields.Char('Observation Category ')
    parent_id = fields.Many2one('cicon.qc.observation.category', 'Parent Category')
    child_ids = fields.One2many('cicon.qc.observation.category', 'parent_id', string='Children Categories')

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'Unique Category')]

    @api.multi
    def name_get(self):
        res = []
        for cat in self:
            names = [cat.name]
            pcat = cat.parent_id
            while pcat:
                names.append(pcat.name)
                pcat = pcat.parent_id
            res.append((cat.id, ' / '.join(reversed(names))))
        return res

    @api.one
    @api.constrains
    def _check(self):
        parent = self._parent_name
        # must ignore 'active' flag, ir.rules, etc. => direct SQL query
        query = 'SELECT "%s" FROM "%s" WHERE id = %%s' % (parent, self._table)
        current_id = self.id
        while current_id is not None:
            self._cr.execute(query, (current_id,))
            result = self._cr.fetchone()
            current_id = result[0] if result else None
            if current_id == self.id:
                    return False
        return True


cicon_qc_observation_category()


class cicon_qc_observation(models.Model):
    _name = 'cicon.qc.observation'
    _inherit = ['mail.thread']
    _description = "CICON QC Observation"

    name = fields.Char('Report No :', readonly=True)
    qc_check_ids = fields.Many2many( comodel_name='cicon.qc.check', relation='cicon_qc_observation_check_rel', column1='qc_observation_id', column2='qc_check_id', string='QC Checks' )
    reference = fields.Char('Reference No#', readonly=True, default='New', states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    category_id = fields.Many2one('cicon.qc.observation.category', string='Category', required=True ,
                                  readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]}, track_visibility='onchange')
    report_type = fields.Selection([('non_conf', 'Non Conformance'), ('opp_improve', 'Opportunity for Improve')], required=True,
                                   readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]}, string='Report Type')
    date = fields.Date('Date', default=fields.Date.context_today, readonly=True, states={'open': [('readonly', False)]})
    work_shift = fields.Selection([('day', 'Day'), ('night', 'Night')], string='Shift', readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    location = fields.Char('Location / Machine', readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    procedure_ref = fields.Text('Procedural Reference', readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    user_id = fields.Many2one('res.users', 'Created By', default=lambda self: self.env.user, readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    reported_by = fields.Many2one('hr.employee', 'Reported By', readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    resp_employee = fields.Many2one('hr.employee', 'Responsible Person', readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    resp_manager = fields.Many2one('hr.employee', 'Responsible Manager', readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    description = fields.Text('Observation',readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    root_cause = fields.Text('Root Cause', readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    corr_act = fields.Text('Corrective Action',readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    prev_act = fields.Text('Preventive Action', readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    state = fields.Selection([('new', 'New'), ('confirm', 'Confirmed'), ('action', 'Action Proposed'), ('done', 'Solved') ,('cancel', 'Cancelled')], string='Status', default='new', track_visibility='onchange' )
    condition = fields.Selection([('use', 'Use'), ('re_work', 'Re-Work'), ('scope', 'Scope'), ('other', 'Others')],
                                 string='Condition', readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    condition_text = fields.Text('Comments', readonly=True, states={'new': [('readonly', False)], 'open': [('readonly', False)]})
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id ,required=True)

    @api.model
    def create(self, vals):
        _qc_obs_seq = self.env['ir.sequence'].search([('company_id', '=', self.env.user.company_id.id),
                                                      ('code', '=', 'cic.qc.observation.seq')])
        vals.update({'name': _qc_obs_seq.next_by_id() or time.strftime('%Y/%m/%d/%H/%M')})
        # vals['name'] = self.env['ir.sequence'].next_by_code('cic.qc.observation.seq') or 'New'
        return super(cicon_qc_observation, self).create(vals)

    @api.multi
    def close_action(self):
        self.write({'state': 'done'})

    @api.multi
    def re_open_action(self):
        self.write({'state': 'new'})

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'Unique Name ')]

cicon_qc_observation()
