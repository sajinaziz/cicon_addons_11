from openerp import models, fields, api
import time


class cicon_hr_training_title(models.Model):
    _name = 'cicon.hr.training.title'
    _description = 'CICON Training Title'

    name = fields.Char('Training Title', required=True)
    description = fields.Text('Description')
    department_id = fields.Many2one('hr.department', string="Trained By Department")
    coordinator_id = fields.Many2one('hr.employee',  string='Coordinator')
    score = fields.Integer('Score')

    _sql_constraints = [('uniq_name', 'UNIQUE(name)',  'Unique Name')]


cicon_hr_training_title()


class cicon_hr_employee_training(models.Model):
    _name = 'cicon.hr.employee.training'
    _description = 'CICON HR Training'

    def _calc_percentage(self):
        for rec in self:
            if rec.achieved_score <= rec.title_id.score and rec.title_id.score > 0:
                rec.score_percent = (rec.achieved_score / rec.title_id.score) * 100
                if rec.score_percent <= 40:
                    rec.grade = 'Poor'
                elif rec.score_percent > 40 and rec.score_percent <= 60:
                    rec.grade = 'Fair'
                elif rec.score_percent > 60 and rec.score_percent <= 80:
                    rec.grade = 'Good'
                elif rec.score_percent > 80 and rec.score_percent <= 100:
                    rec.grade = 'Excellent'

    name = fields.Char('Reference', readonly=True)
    certificate_no = fields.Char('Certificate #')
    title_id = fields.Many2one('cicon.hr.training.title', string='Training Title', required=True)
    training_date = fields.Date('Training Date', required=True)
    department_id = fields.Many2one('hr.department', related='title_id.department_id', store=False, readonly=True, string="Trained By Department")
    coordinator_id = fields.Many2one('hr.employee', related='title_id.coordinator_id', store=False, readonly=True, string='Coordinator')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string="Job Title", store=False, readonly=True)
    expiry_date = fields.Date('Expiry Date')
    score = fields.Integer(related='title_id.score', store=False, readonly=True)
    achieved_score = fields.Float('Score')
    file_name = fields.Char('File Name')
    certificate_file = fields.Binary('Certificate')
    score_percent = fields.Float('Score', compute=_calc_percentage, store=False)
    grade = fields.Char('Grade', compute=_calc_percentage, store=False)

    @api.model
    def create(self, vals):
        vals.update({'name': self.env['ir.sequence'].get('cicon.hr.employee.training.seq') or time.strftime('%Y/%m/%d/%H/%M')})
        return super(cicon_hr_employee_training, self).create(vals)

    _sql_constraints = [('uniq_cert', 'UNIQUE(employee_id,title_id,certificate_no)', 'Unique Certificate Per Employee'),
                        ('uniq_seq', 'UNIQUE(name)', 'Unique Sequence')]

cicon_hr_employee_training()


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    training_ids = fields.One2many('cicon.hr.employee.training', 'employee_id', string='Trainings')

hr_employee()
