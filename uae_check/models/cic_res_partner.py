from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # _columns = {
    #     'on_hand_check_ids': fields.one2many('cic.check.receipt','partner_id', domain=[('state','=','received')], string= "Partner Checks On hand",readonly=True, help="PDC Receipts with state is Received",groups="account.group_account_invoice"),
    #     'submitted_check_ids': fields.one2many('cic.check.receipt','partner_id', domain=[('state','=','submitted')], string= "Partner Checks On hand",readonly=True, help="PDC Receipts with state is Submitted",groups="account.group_account_invoice"),
    #     'bounced_check_ids': fields.one2many('cic.check.receipt','partner_id', domain=[('state','=','bounced')], string= "Partner Checks Bounced", readonly=True,  help="PDC Receipts with state Bounced",groups="account.group_account_invoice"),
    #     'bounce_history_ids': fields.one2many('cic.check.bounce.history', 'partner_id', string="Bounce History",readonly=True, help="Bounced Checks History",groups="account.group_account_invoice"),
    #     #'attachment_ids': fields.one2many('ir.attachment','res_id',domain=[('res_model','=','res.partner')],string="Documents")
    #
    # }

    on_hand_check_ids = fields.One2many('cic.check.receipt', 'partner_id', domain=[('state', '=', 'received')],
                                         string="Partner Checks On hand", readonly=True,
                                         help="PDC Receipts with state is Received",
                                         groups="account.group_account_invoice")
    submitted_check_ids = fields.One2many('cic.check.receipt','partner_id', domain=[('state','=','submitted')], string= "Partner Checks On hand",readonly=True, help="PDC Receipts with state is Submitted",groups="account.group_account_invoice")
    bounced_check_ids = fields.One2many('cic.check.receipt','partner_id', domain=[('state','=','bounced')], string= "Partner Checks Bounced", readonly=True,  help="PDC Receipts with state Bounced",groups="account.group_account_invoice")
    bounce_history_ids = fields.One2many('cic.check.bounce.history', 'partner_id', string="Bounce History",readonly=True, help="Bounced Checks History",groups="account.group_account_invoice")
    #     #'attachment_ids': fields.one2many('ir.attachment','res_id',domain=[('res_model','=','res.partner')],string="Documents")
    state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
ResPartner()


