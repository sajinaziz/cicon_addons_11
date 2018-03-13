from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    cicon_cheque = fields.Boolean(default=False,string="CICON Cheque")
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

    @api.onchange('amount', 'currency_id')
    def _onchange_amount(self):
        _res = super(AccountPayment,self)._onchange_amount()
        if not self.cicon_cheque:
            return _res
        else:
            _chq_ref = self.env.ref('cicon_cheque.account_payment_method_check_in')
            _domain = [('type', '=', 'bank'), ('company_id', '=', self.env.user.company_id.id),
                       ('inbound_payment_method_ids', 'in', [_chq_ref.id])]
            _journals = self.env['account.journal'].search(_domain)
            if _journals:
                self.journal_id = _journals[0]
            return {'domain': {'journal_id': _domain}}


