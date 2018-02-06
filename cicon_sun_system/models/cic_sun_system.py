from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    sun_account_ids = fields.One2many('cic.sun.account', 'partner_id', 'Sun Accounts', ondelete='restrict')


class CicSunDb(models.Model):
    _name = 'cic.sun.db'
    _description = 'Sun Account DB'
    _rec_name = 'db_code'

    db_name = fields.Char('DB Name', size=10, required=True)
    db_code = fields.Char('DB Code', size=10, required=True)

    _sql_constraints = [
        ('db_code_uniq', 'UNIQUE(db_code)', 'Sun DB must be unique!'),
        ('db_name_uniq', 'UNIQUE(db_name)', 'Sun DB must be unique!')]


class CicSunAccount(models.Model):
    _name = 'cic.sun.account'
    _description = "Sun System Account Numbers"
    _rec_name = "sun_account_no"

    def _get_db_selection(self):
        sun_db_ids = self.env['cic.sun.db'].search([])
        res = []
        for x in sun_db_ids:
            res.append((x.db_code, x.db_name))
        return res

    sun_db = fields.Selection(selection=_get_db_selection, string='SUN DB', required=True)
    sun_account_no = fields.Char('Sun Account Number', size=10, help="Sun System Account Number", required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)

    _sql_constraints = [
        ('acc_no_uniq', 'UNIQUE(sun_db,sun_account_no)', 'Sun Account Number must be unique!'),]


