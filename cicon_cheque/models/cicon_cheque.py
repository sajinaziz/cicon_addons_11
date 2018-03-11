from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    inbound_check_payment = fields.Boolean('Cheque Payment', default=True)
    cheque_date = fields.Date('Cheque Date')
    check_number_inbound = fields.Char('Cheque Number', size=32,
                                       help="Cheque Number")
    deposit_date = fields.Date('Submission Date')

    rv_number = fields.Char('RV Voucher No', size=10,
                            help="RV Number")
    voucher_number = fields.Char('Collection Voucher No.')
    received_date = fields.Date('Received Date')
    note = fields.Text('Notes')
    state = fields.Selection(selection_add=[('deposit', 'Submitted'), ('reject', 'Bounce'), ('posted', 'Posted')])
