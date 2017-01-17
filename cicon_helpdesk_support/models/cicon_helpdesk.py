from odoo import models, fields, api

class CiconHelpDesk(models.Model):
    _name = 'cicon.help.desk'
    _inherit = ['mail.thread']
    _description = "Help Desk Support"

    name = fields.Char('Subject',required=True)
    team_id = fields.Many2one('help.desk.team',string='Help Desk Team')
    assigned_to = fields.Many2one('res.users',string='Assigned To',required=True)
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority')
    employee_id = fields.Many2one('res.users',string='Employee',required=True)
    email = fields.Char(string='Employee Email',required=True)
    ticket_type = fields.Selection([('question','Question'),('issue','Issue')])
    description = fields.Text(String='Description of the Ticket')
    state = fields.Selection([('new', 'NEW'), ('progress', 'IN PROGRESS'),('solve', 'SOLVED'),
                              ('cancel', 'CANCELLED')], "Status",default='new', track_visibility='onchange')

    @api.multi
    def mark_new(self):
        self.ensure_one()
        # print self.drawing_no
        self.write({'state': 'new'})

    @api.multi
    def mark_progress(self):
        self.ensure_one()
        # print self.drawing_no
        self.write({'state': 'progress'})

    @api.multi
    def mark_solve(self):
        self.ensure_one()
        # print self.drawing_no
        self.write({'state': 'solve'})

    @api.multi
    def mark_cancel(self):
        self.ensure_one()
        # print self.drawing_no
        self.write({'state': 'cancel'})



class CiconHelpDeskTeam(models.Model):
    _name = 'help.desk.team'
    _description = "Help Desk Team"

    name = fields.Char('Name',required=True)
    members = fields.Many2many('res.users','res_users_helpdesk_rel', string="Members")
    _sql_constraints = [('uniq_name', 'UNIQUE(name)', "Team Name Should be Unique")]


