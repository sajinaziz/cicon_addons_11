# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
#from openerp.osv import osv,fields,orm
import time
from datetime import date
from odoo.tools.translate import _
from odoo.tools import amount_to_text_en



# class AccountVoucherExt(models.Model):
#     _inherit = 'account.voucher'
#
#     check_number = fields.Char('Check Number', size=32, help="Check Sequence Based on last check created for Bank")
#     pv_number = fields.Char('Payment Voucher No',size=10 , help="Payment Voucher Number Sequence Based on last Created for Company ")
#     bank_account_id = fields.Many2one('res.partner.bank',string="Bank Account",domain="[('company_id','=',company_id)]",help="Bank Account for selected Company" )
#     bank_name = fields.Char(Related ='bank_account_id.bank_name',string="Bank Name", help="Bank Name For Selected Account" )
#     account_no = fields.Char(Related = 'bank_account_id.acc_number',string="Account Number", help="Account Number for Selected Bank Account")
#         #'check_format_id': fields.many2one('ir.actions.report.xml',  ondelete='set null',string='Check Format'),
#     check_format_id =  fields.Many2one('ir.actions.report.xml', domain="[('id','in',check_format_ids[0][2])]", ondelete='set null',string='Check Format',help="Available Check Format For Printing Check")
#     payment_info_ids = fields.One2many('cic.check.info','account_voucher_id',string="Check Payment Informations(CICON)",help="Check payment informations")
#     check_format_ids = fields.Many2many('ir.actions.report.xml',  string='Check Formats') # Dummy field to list out Available Check format for Selected Account
#    # previous_check_ids = fields.One2many('account.voucher',string="Previous Check For Supplier",help="Previously Created Check Details for Selected Customer") # Dummy field to list Previously Created Checks for the selected Customer
#     stamp_id = fields.Many2one('cic.check.stamp','Stamp Name')
#
#     _sql_constraints = [('unique_check_number','unique(check_number,bank_account_id)','Check Number Must be unique Per Bank Account') ]
#
#     def company_change(self, company_id , context=None):
#         #On Company Change increase Payment Voucher Number / Company
#         _val = {}
#         _warn = {}
#         if company_id:
#             _val['bank_account_id'] = None
#             _pv_ids = self.env['account.voucher'].search([('company_id','=',company_id)])
#             if _pv_ids:
#                 _last_pv_no = self.browse( max(_pv_ids)).pv_number
#                 try:
#                     _int_pv_no = int(_last_pv_no)
#                     _last_pv_no = _int_pv_no + 1
#                     _val['pv_number'] = _last_pv_no
#                 except (orm.except_orm, ValueError):
#                     _val['pv_number'] = None
#                     _warn = {
#                          'title': 'Warning!',
#                          'message': 'Last PV Number is not Number.'
#                     }
#
#         return {'value': _val,'warning':_warn}
#
#     def onchange_partner_id(self, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
#         # On Partner / Customer Change Fill Previously Created Check Details
#         if not context:
#             context = {}
#         res = super(AccountVoucherExt,self).onchange_partner_id(partner_id,journal_id,amount,currency_id,ttype,date,context=context)
#         if partner_id and context.get('write_check',False):
#             _av_ids = self.env['account.voucher'].search([('partner_id','=',partner_id)])
#             if len(_av_ids) >0:
#                 res['value'].update({'previous_check_ids': _av_ids})
#         return res
#
#
#     def bank_account_change(self, bank_acc_id,context=None):
#         # On Bank Change Fill available check formats and increase check sequence number Select the journal Id for selected Bank For Payment Method in View
#         _domain = {}
#         _val = {}
#         _warn = {}
#         format_ids =[]
#         if bank_acc_id:
#             _bank_obj = self.env('res.partner.bank').browse(bank_acc_id)
#             for _f in _bank_obj.check_formats:
#                 format_ids.append(_f.id)
#             _val['check_format_ids'] = format_ids
#             _domain['journal_id'] = [('id','=',_bank_obj.journal_id.id)]
#             _val['journal_id'] = _bank_obj.journal_id.id
#                 #if len(format_ids) == 1:
#                 #
#                 #    _val['check_format_id']=format_ids[0]
#                 #    _domain['check_format_id'] = [('id','in',format_ids)]
#                 #else:
#                 #    _val['check_format_id'] = None
#                 #    _domain['check_format_id'] = [('id','in',format_ids)]
#             _bank_ids = self.env['account.voucher'].search([('bank_account_id','=',bank_acc_id)])
#             if _bank_ids:
#                 _last_check_no = self.browse(max(_bank_ids)).check_number
#                 try:
#                     _int_check_no = int(_last_check_no)
#                     _last_check_no = _int_check_no + 1
#                     _val['check_number'] = _last_check_no
#
#                 except (orm.except_orm, ValueError):
#                     _val['check_number'] = None
#                     _warn = {
#                          'title': 'Warning!',
#                          'message':'Last Check Number was not a Number.'
#                     }
#         return {'domain': _domain,'value': _val,'warning':_warn}
#
#     def print_uae_check(self,ids, context=None):
#         #Print Check based on selected check format
#         _report_to_print = self.browse(context=None).check_format_id.report_name
#         if _report_to_print:
#             datas = {
#                 'model': 'account.voucher',
#                 'ids': ids,
#                 'form': self.read(context=context),
#             }
#             return {'type': 'ir.actions.report.xml', 'report_name': _report_to_print , 'datas': datas, 'nodestroy': True}
#         else:
#             raise UserWarning()
#             raise osv.except_osv('Error!', 'Check Format not Defined for Selected Bank.')
#             return None
#
#     def print_uae_voucher(self,ids,context=None):
#         #Print voucher for selected company
#         _report_to_print = self.browse(context=None).company_id.voucher_format.report_name
#         if _report_to_print:
#             datas = {
#                 'model': 'account.voucher',
#                 'ids': ids,
#                 'form': self.read( context=context),
#             }
#             return {'type': 'ir.actions.report.xml', 'report_name': _report_to_print , 'datas': datas, 'nodestroy': True}
#         else:
#             raise osv.except_osv('Error!', 'Voucher Format not Defined for This Company.')
#             return None
#
# AccountVoucherExt()

class CicCheckStamp(models.Model):
    _name = 'cic.check.stamp'
    _description = "CHECK Stamp"
    _rec_name = "stamp_name"

    stamp_name = fields.Char('Stamp Name', size=50)
    image = fields.Binary('Select Stamp Image')
    enabled = fields.Boolean('Enable')

CicCheckStamp()


# class ResPartnerBank(models.Model):
#     _inherit = "res.partner.bank"
#     # Additional Columns to Store IBAN and banks cheque format
#     # _columns = {
#     #     #'check_format': fields.many2one('ir.actions.report.xml', string='Check Format' , domain="[('model','=','account.voucher')]"),
#     #     'cicon_iban': fields.char('Remarks [IBAN]', size=20 ,help="IBAN Number- Validation disbaled " ),
#     #     'check_formats': fields.many2many('ir.actions.report.xml','partner_bank_check_rel','bank_account_id','check_format_id', domain="[('model','=','account.voucher')]", string='Check Formats', help="Available Cheque format fot the bank" )
#     # }
#
#     cicon_iban = fields.Char('Remarks [IBAN]', size=20, help="IBAN Number- Validation disbaled ")
#     check_formats = fields.Many2many('ir.actions.report.xml', 'partner_bank_check_rel', 'bank_account_id',
#                                       'check_format_id', domain="[('model','=','account.voucher')]",
#                                       string='Check Formats', help="Available Cheque format fot the bank")
#
#
# ResPartnerBank()


class ResCompany(models.Model):
    #Company voucher format
    _inherit = 'res.company'


    voucher_format = fields.Many2one('ir.actions.report.xml', string='Voucher Format',
                                      help="Voucher Format for Check ", domain="[('model','=','account.voucher')]")


ResCompany()


class CicCheckInfo(models.Model):
    _name = 'cic.check.info'
    _description = "CHECK Payment Details"

    name = fields.Char('Payment Info', size=200)
    rel_pv_number = fields.Char(Related ='account_voucher_id.pv_number',string='Payment Voucher No')
    rel_check_number = fields.Char(Related = 'account_voucher_id.check_number', string= 'Check Number')
    rel_partner_id = fields.Many2one('res.partner' , Related ='account_voucher_id.partner_id', string="Account Name")
    account_voucher_id = fields.Many2one('account.voucher',"Account Voucher")
    sun_account = fields.Char("Sun Account",size=10)
    amount = fields.Float("Amount")

CicCheckInfo()


class CicCheckReceipt(models.Model):

    _inherit = ['mail.thread','ir.needaction_mixin']
    _name = "cic.check.receipt"
    _description = "Check Receipt (PDC Receipt)"
    _rec_name = 'check_number'

    @api.multi
    def _next_action_date(self):
        # Next action date as per state, submitted: submitted date , bounced : latest re submission Date from bounce history
        res = {}
        for i in self:
            if len(i.bounced_history_ids) > 0:
                _bh_ids=[]
                for h in i.bounced_history_ids:
                    _bh_ids.append(h.id)
                _bh_id = max(_bh_ids)
                _bh_obj = self.env['cic.check.bounce.history'].search([('id','=',_bh_id)])
                res[i.id] = _bh_obj.re_submit_date
            else:
                res[i.id] = i.check_submission_date
        return res


    is_replacement = fields.Boolean(string="Replacement Check",default = False)
    partner_id = fields.Many2one('res.partner', "Customer", required=True, help="Customer")
    sun_account_id = fields.Many2one('cic.sun.account', string='Sun Account', domain="[('partner_id','=',partner_id)]")
    project_id = fields.Many2one('project.project', "Project", domain="[('partner_id','=',partner_id)]",
                                  help="Project")
    amount = fields.Float('Amount', help="Check Amount")
    text_amount = fields.Char("Text Amount", size=100)
    check_date = fields.Date('Cheque/LC Date', help="Check/LC Date", required=True, default=fields.Date.context_today)
    check_number = fields.Char('Cheque/LC Number', size=10, required=True, help="Check/LC Number")
    check_submission_date = fields.Date('Submission Date', track_visibility="onchange",
                                         help="Date Submitted to bank, required to change Status to Submitted")
    # 'sun_account': fields.char('Sun Account No',size=10 ,help="CICON Sun System Account" ),
    remarks = fields.Text('Remarks', help="Remarks If any ")
    rv_number = fields.Char('RV Number', size=10, help="Receive voucher Number given for Customer")
    company_id = fields.Many2one('res.company', "Company(Database)", required=True,
                                 help="Company Name where Customer registered For Finance")
    cic_division_id = fields.Many2one('cic.divisions', string='Cheque Received By',
                                       help="Division Where Check collected")
    res_bank_id = fields.Many2one('res.bank', "Bank", required=True, help="Cheque Bank Name")
    rcvd_date = fields.Date('Received Date', help="Collected Date" , default = fields.Date.context_today)
    credited_date = fields.Date('Credited Date', track_visibility="onchange", help="Account Credited Date")
    cleared = fields.Boolean('Cleared & Credited')
    bounced_history_ids = fields.One2many('cic.check.bounce.history', 'check_receipt_id', string="Bounced History",
                                           help="History if bounced")
    state = fields.Selection(
        [('received', 'In Hand'), ('submitted', 'Submitted'), ('bounced', 'Bounced'), ('re_submitted', 'Re Submitted'),
         ('cleared', 'Cleared'), ('replaced', 'Replaced'), ('hold', 'Hold'), ('return', 'Return Back')],
        required=True, track_visibility='onchange', string="Status", default = 'received')
    # next_action_date = fields.Date(compute=_next_action_date,string='Next Action', store=True,
    #                                     help="Date for Next submission or Action")
    next_action_date = fields.Date(string='Next Action', store=True,
                                   help="Date for Next submission or Action")
    # 'account_period_id': fields.many2one('account.period',string="Account Period")
    created_user_id = fields.Many2one('res.users', string='Created User',  default=lambda self: self.env.user)
    cv_number = fields.Char('Collection Voucher No.', size=12)
    # 'partner_sun_system_id': fields.related('partner_id','sun_account_id',type='many2one',relation='cic.sun.account', string="Sun Account"),
    replaced_check_ids = fields.Many2many('cic.check.receipt', 'cic_check_replaced_rel', 'check_replaced_with',
                                           'check_replaced', string="Replaced checks")
    # 'active': fields.boolean('Active')
    is_lc = fields.Boolean(string="Letter of Credit(LC)")

    @api.multi
    def onchange_amount(self,amount):
        text_amount = amount_to_text_en.amount_to_text(amount, 'en', 'Dirham')
        return {'value': {'text_amount': text_amount}}

    # Credited Date should be greater than Check Date

    # @api.model
    # def default_get(self, cr, uid , fields, context=None):
    #     res = super(CicCheckReceipt,self).default_get(cr, uid ,fields, context=context)
    #     if context.get('active_ids') and context.get('check_replace'):
    #         _checks_obj = self.browse(context.get('active_ids'))
    #         _partner_id = 0
    #         for c in _checks_obj:
    #             if _partner_id == 0:
    #                 _partner_id = c.partner_id.id
    #             if _partner_id != c.partner_id.id:
    #                 raise Warning('Please Select Checks for one Customer')
    #                 return False
    #             if c.state == 'cleared':
    #                 raise Warning('Warning','Cleared Check Cannot be Replaced ')
    #                 return False
    #         for i in _checks_obj:
    #             res.update({'partner_id':i.partner_id.id})
    #             res.update({'project_id':i.project_id.id})
    #             res.update({'is_replacement':True})
    #             res.update({'replaced_check_ids': context.get('active_ids')})
    #             break
    #     return res

    #To Find if the same cheque Number is used by the customer. Requested # Sameer 16/09/2014
    # @api.onchange('partner_id', 'bank_id', 'check_number')
    # def cheque_warning(self, partner_id=None, bank_id=None, check_number=None):
    #     warning_msg = {}
    #     if partner_id and bank_id and check_number:
    #         _check_ids = self.search([('partner_id', '=', partner_id), ('res_bank_id', '=', bank_id), ('check_number','=',check_number)])
    #         if _check_ids:
    #             warning_msg = {
    #                 'title': 'Duplicate Check Number!',
    #                 'message': 'Duplicate check number found, Please verify !'
    #                 }
    #     return {'warning': warning_msg}

    @api.multi
    def _validate_check_submitted_date(self):
        for c in self:
            if c.credited_date:
                if c.check_date > c.credited_date:
                    return False
        return True
    _constraints = [(_validate_check_submitted_date,'Error ! Please Verify  Credited Date.', ['check_date'])]

    # def onchange_cleared(self,cleard_status, credited_date, submitted_date ,context=None):
    #     val = {}
    #     #if cleard_status and not credited_date:
    #     #    val['credited_date'] = time.strftime('%Y-%m-%d')
    #     #elif not cleard_status and credited_date:
    #     #    val['credited_date'] = None
    #     if cleard_status:
    #         if submitted_date:
    #             val['credited_date']= submitted_date
    #         else:
    #             val['credited_date']= time.strftime('%Y-%m-%d')
    #     else:
    #         val['credited_date'] = None
    #     return {'value': val}

    # @api.onchange('partner_id')
    # def partner_change(self, bank_id=None, check_no = None):
    #     val={}
    #     _domain ={}
    #     _waring_msg = {}
    #     val['res_bank_id'] = None
    #     val['project_id']= None
    #     val['sun_account_id']= None
    #     if self.partner_id:
    #         _domain['sun_account_id'] = [('partner_id','=',self.partner_id)]
    #         _account_ids = []
    #         _sun_ids = self.env['cic.sun.account'].search([('partner_id','=',self.partner_id),('project_id','=',False)], limit=1)
    #         val['sun_account_id'] = _sun_obj['id']
    #         for b in _partner_obj.bank_ids:
    #             _account_ids.append(b.id)
    #         if len(_account_ids) > 0:
    #             _acc_id = max(_account_ids)
    #             if _acc_id:
    #                 _bank_id = self.env('res.partner.bank').browse(_acc_id).bank.id
    #             val['res_bank_id'] = _bank_id
    #         if bank_id and check_no:
    #             _waring_msg = self.cheque_warning(None, partner_id, bank_id, check_no)
    #     return (0,0, {'value': val, 'domain': _domain, 'waring': _waring_msg.get('warning')})

    # @api.onchange('project_id')
    # def project_change(self, project_id,partner_id):
    #     val = {}
    #     _domain ={}
    #     _domain['sun_account_id'] = None
    #     if project_id and partner_id:
    #         val['sun_account_id'] = None
    #         _domain['sun_account_id'] = [('partner_id','=',partner_id)]
    #         _sun_ids = self.env('cic.sun.account').search([('project_id','=',project_id)])
    #         if _sun_ids:
    #             _sun_obj = self.env('cic.sun.account').read(_sun_ids,['id'])[0]
    #             val['sun_account_id'] = _sun_obj['id']
    #             _domain['sun_account_id'].append(('project_id','=',project_id))
    #     return {'value':val,'domain':_domain}

    @api.multi
    def print_voucher(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'uae_check.cheque_receipt_voucher_template')

    @api.multi
    def action_reset(self):
        self.ensure_one()
        self.write({'state': 'received'})

    @api.multi
    def action_submit(self):
        self.ensure_one()
        for r in self:
            if r.check_submission_date:
                self.write({'state': 'submitted'})
            else:
                raise Warning('Please Select Submitted Date')

    @api.multi
    def action_hold(self):
        self.ensure_one()
        if self.check_submission_date:
            form_id = self.env.ref('uae_check.cic_bounced_history_form')
            ctx = dict({
            'default_check_receipt_id':  self.id,
            'default_state': 'hold'
            })
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'name' : 'Hold Check History',
                'res_model': 'cic.check.bounce.history',
                'views': [(form_id.id, 'form')],
                'view_id': form_id.id,
                'target': 'new',
                'context': ctx,
                }
        else:
             raise Warning('Please Select Submitted Date')

    @api.multi
    def action_return_back(self):
        self.ensure_one()
        if self.check_submission_date:
            form_id = self.env.ref('uae_check.cic_bounced_history_form')
            ctx = dict({
            'default_check_receipt_id':  self.id,
            'default_state': 'return'
            })
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'name' : 'Return Back',
                'res_model': 'cic.check.bounce.history',
                'views': [(form_id.id, 'form')],
                'view_id': form_id.id,
                'target': 'new',
                'context': ctx,
                }
        else:
             raise Warning('Please Select Submitted Date')

    @api.multi
    def action_replace(self):
        self.ensure_one()
        form_id = self.env.ref('uae_check.cic_bounced_history_form')
        ctx = dict({
            'default_check_receipt_id':  self.id,
            'default_state': 'replaced'
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'name': 'Replace History',
            'res_model': 'cic.check.bounce.history',
            'views': [(form_id.id, 'form')],
            'view_id': form_id.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_bounce(self):
        self.ensure_one()
        form_id = self.env.ref('uae_check.cic_bounced_history_form')
        ctx = dict({
            'default_check_receipt_id':  self.id,
            'default_state': 'bounced'
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'name': 'Bounced Check History',
            'res_model': 'cic.check.bounce.history',
            'views': [(form_id.id, 'form')],
            'view_id': form_id.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def set_bounced(self, id):
            r = self.browse(id)
            _b_history = []
            for b in r.bounced_history_ids:
                _b_history.append(b.id)
            if len(_b_history) > 0:
                self.write({'state': 'bounced'})
            else:
                raise Warning('Please Enter Bounced Check Details/Reason!')

    @api.multi
    def set_hold(self,id):
        self.write({'state': 'hold'})

    @api.multi
    def set_return_back(self,id):
       self.write({'state': 'return'})

    @api.multi
    def set_replaced(self,id):
        self.write({'state': 'replaced'})

    @api.multi
    def action_clear(self):
        self.ensure_one()
        for r in self:
            if r.credited_date and r.check_submission_date:
                if r.credited_date < r.check_submission_date or r.credited_date < r.check_date :
                    raise Warning('Credited Date must be Greater Than Submission Date ')
                else:
                    self.write({'state': 'cleared'})
            else:
                raise Warning('Please Select Credited / Submitted Date')

    @api.multi
    def action_resubmit(self):
        self.ensure_one()
        for r in self:
            _b_history = []
            for b in r.bounced_history_ids:
                _b_history.append(b.id)
            if len(_b_history) >0:
                self.write({'state': 're_submitted'})
            else:
                raise Warning('Please Enter Bounced Check Details/Reason!')


    @api.model
    def create(self, vals):
        res = super(CicCheckReceipt,self).create(vals)
        if vals.get('is_replacement'):
            for i in self.browse([res]):
                if i.replaced_check_ids:
                    for r in i.replaced_check_ids:
                        self.write({'state': 'replaced'})
                else:
                    raise Warning('Please Select Minimum one check to be replaced!')
        return res
        
CicCheckReceipt()


class CicDivisions(models.Model):
    _name = "cic.divisions"
    _description = "CIC Divisions"
    _log_access = False

    name = fields.Char('Division Name',size=100 ,required=True)
    company_id = fields.Many2one('res.company', "Company")

    _sql_constraints = [('unique_division','unique(name)','Division Name Must Be Unique')]
CicDivisions()


class CicJournalVouchers(models.Model):
    _name = "cic.journal.vouchers"
    _description =" Cicon Journal Vouchers"
    _rec_name= 'jvp_no'

    jvp_no = fields.Char('JVP Number', size=10)
    #account_period_id = fields.Many2one('account.period', string="Account Period")
    company_id = fields.Many2one('res.company', "Company")
    created_user_id = fields.Many2one('res.users', "Prepared By", default=lambda self: self.env.user)
    voucher_details_ids =  fields.One2many('cic.journal.voucher.details', 'cic_journal_id',string="Journal Details")


CicJournalVouchers()

class CicJournalVoucherDetails(models.Model):
    _name = "cic.journal.voucher.details"
    _description = "Cicon Journal Voucher Details"
    _rec_name= 'cic_journal_id'

    doc_date = fields.Date('Doc Date')
    sun_account = fields.Char('Sun Account No', size=10)
    cic_journal_id = fields.Many2one('cic.journal.vouchers', 'JVP Number')
    company_id = fields.Many2one('res.company', "Division Name(Company)")
    partner_id = fields.Many2one('res.partner', "Account Name")
    description = fields.Char('Description', size=250)
    amount_dr = fields.Float('Dr. Amount')
    amount_cr = fields.Float('Cr. Amount')
    reconcile_ref =  fields.Char('Reconcile Ref')

CicJournalVoucherDetails()


class CicCheckBounceHistory(models.Model):
    _name = 'cic.check.bounce.history'
    _description = "Check Bounce"
    _rec_name = 'check_receipt_id'

    bounced_date = fields.Date('Bounced/Holded/Replaced/Return Date', required=True)
    re_submit_date = fields.Date('Re-Submission Date')
    reason = fields.Char('Reason', size=100)
    remarks = fields.Text('Remarks')
    replaced_with_cash = fields.Boolean('Is Replaced With Cash' , default = False)
    check_receipt_id = fields.Many2one('cic.check.receipt', string='Check Receipt', required=True,
                                        ondelete='cascade')
    partner_id = fields.Many2one('res.partner', Related = 'check_receipt_id.partner_id',
                                 string="Customer", store=True)
    res_bank_id = fields.Many2one('res.bank', Related ='check_receipt_id.res_bank_id', string="Bank")
    state = fields.Selection(
        [('bounced', 'Bounced'), ('hold', 'Holded'), ('replaced', 'Replaced'), ('return', 'Return Back')],
        string="State", required=True)

    @api.multi
    def save_history(self):
        for r in self:
            if r.state == 'bounced':
                _rc_obj = self.env['cic.check.receipt']
                _rc_obj.set_bounced(r.check_receipt_id.id)
            elif r.state == 'hold':
                _rc_obj = self.env['cic.check.receipt']
                _rc_obj.set_hold(r.check_receipt_id.id)
            elif r.state == 'replaced':
                _rc_obj = self.env['cic.check.receipt']
                _rc_obj.set_replaced(r.check_receipt_id.id)
            elif r.state == 'return':
                _rc_obj = self.env['cic.check.receipt']
                _rc_obj.set_return_back(r.check_receipt_id.id)
        return True

    # Bounced Date Should be Greater than or Equal to Check Date And Re- Submit date should be greater than or equal to Bounced Date
    @api.multi
    def _validate_check_bounced_date(self):
        for b in self:
            if b.state == 'bounced':
                if b.check_receipt_id.check_date > b.bounced_date:
                    return False
                if b.bounced_date > b.re_submit_date:
                    return False
            elif b.state == 'hold':
                if b.re_submit_date < date.today().strftime('%Y-%m-%d') :
                    return False
        return True
    _constraints = [(_validate_check_bounced_date,'Error ! Please Verify  Bounced / Hold or Re-submitted  Date.', ['bounced_date'])]


CicCheckBounceHistory()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: