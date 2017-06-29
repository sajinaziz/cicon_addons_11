from odoo import models, fields,api


class CiconUserIdentityType(models.Model):
    _name = 'cicon.user.identity.type'
    _description = "CICON User Identity"

    name = fields.Char('Identity Type', required=True)

    _sql_constraints = [('unique_type', 'UNIQUE(name)', 'Identity Type should be Unique!')]


class CiconPasswordCode(models.Model):
    _name = 'cicon.password.code'
    _description = "CICON Password Code"

    name = fields.Char('Password Code', required=True)
    pword = fields.Char('Password ', required=True)

    _sql_constraints = [('unique_name', 'UNIQUE(name)', 'Password Code should be Unique!')]


class CiconUserIdentity(models.Model):
    _name = 'cicon.user.identity'
    _description = "CICON User Identity"

    _inherit = ['mail.thread']

    name = fields.Char('Title', required=True, visibility='onchange')
    identity_type_id = fields.Many2one('cicon.user.identity.type', string="Identity Type", required=True, visibility='onchange')
    user_name = fields.Char('User Id / Name', visibility='onchange')
    pword_type = fields.Selection([('text', 'Text'), ('code', 'Code')], default='text', string="Password Type", visibility='onchange')
    pword_text = fields.Char('Password (Text)', visibility='onchange')
    pass_code_id = fields.Many2one('cicon.password.code', string='Password Code', visibility='onchange')
    notes = fields.Text('Notes')
    user_id = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user.id, required=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id)

    _sql_constraints = [('unique_name', 'UNIQUE(name)', 'Title should be Unique!')]
