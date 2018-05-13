from odoo import models, fields


class CiconAllowedSigns(models.Model):
    '''Allowed Managers for a user to use digital sign on official Documents'''
    _name = "cicon.allowed.signs"
    _description = "Allowed Signatures"

    sign_manager_id = fields.Many2one('res.users', required=True, string="Manager", domain="[('sign_authority','=',True)]")
    allow_sign = fields.Boolean('Allowed to use Manager Signature')
    user_id = fields.Many2one('res.users', string="User")

    _sql_constraints = [('uniq_manager_id', 'UNIQUE(user_id,sign_manager_id)', 'Unique Manager for User ')]


class ResUsers(models.Model):
    _inherit = 'res.users'

    sign_authority = fields.Boolean('Has Sign Authority')
    signature_image = fields.Binary('Signature', filter='*.png,*.gif,*.jpeg')
    allowed_digital_sign_ids = fields.One2many('cicon.allowed.signs', 'user_id', string="Digital Signing Authority(Managers)")




