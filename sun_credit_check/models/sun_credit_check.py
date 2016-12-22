from dateutil import relativedelta
# from dateutil.relativedelta import relativedelta
from odoo import models,fields,api
from odoo import tools
from operator import itemgetter
import time
#from datetime import datetime
from datetime import datetime,date,timedelta
from odoo.exceptions import UserError
#from time import strftime, strptime, time
#from datetime import datetime
#from dateutil.relativedelta import relativedelta
#import datetime
#
#import datetime
#import dateutil

class SunCreditCheck(models.Model):
    _name = 'sun.credit.check'
    _description = "Sun System Credit Check from odoo"

    # def get_check_amount(self,cr, uid, partner_id, context=None):
    #     amount = 0
    #     _check_ids = self.pool.get('cic.check.receipt').search(cr,uid,[('partner_id','=',partner_id), ('state', 'not in' ,['bounced','cleared','replaced'])])
    #     if len(_check_ids) > 0:
    #        _checks_amount = self.pool.get('cic.check.receipt').read(cr, uid,_check_ids, ['amount'])
    #        amount = sum(x['amount'] for x in _checks_amount)
    #     return amount

    @api.multi
    def get_check_amount(self, partner_id, context=None):
        amount = 0
        _check_ids = self.env['cic.check.receipt'].search([('partner_id','=',partner_id), ('state', 'not in' ,['bounced','cleared','replaced'])])
        if len(_check_ids) > 0:
           _checks_amount = self.env['cic.check.receipt'].read(_check_ids, ['amount'])
           amount = sum(x['amount'] for x in _checks_amount)
        return amount


    # def _get_check_aging(self,cr,uid,ids,field,arg,context=None):
    #
    #     res ={}
    #     for i in self.browse(cr,uid,ids):
    #         res[i.id] = {'check_aging_ids':[],'cheque_details_ids':[]}
    #         _aging_ids = self.pool.get('cic.check.aging.view').search(cr,uid,[('partner_id','=',i.partner_id.id)])
    #         _check_ids  = self.pool.get('cic.check.receipt').search(cr,uid,[('partner_id','=',i.partner_id.id),('state','in',['received','submitted','resubmitted'])])
    #         res[i.id]['check_aging_ids'] = _aging_ids
    #         res[i.id]['cheque_details_ids'] = _check_ids
    #     return res


    @api.multi
    def _get_check_aging(self, ids, field, arg):

        res = {}
        #for i in self.browse(ids):
        for i in self:
            res[i.id] = {'check_aging_ids': [], 'cheque_details_ids': []}
            _aging_ids = self.env['cic.check.aging.view'].search([('partner_id', '=', i.partner_id.id)])
            _check_ids = self.env('cic.check.receipt').search([('partner_id', '=', i.partner_id.id), (
            'state', 'in', ['received', 'submitted', 'resubmitted'])])
            res[i.id]['check_aging_ids'] = _aging_ids
            res[i.id]['cheque_details_ids'] = _check_ids
        return res


    # _columns = {
    #     'date_create': fields.datetime(string='Date'),
    #     'partner_id': fields.many2one('res.partner',string='Customer' ,required=True,domain="[('customer','=',True)]"),
    #     'status': fields.char(string='Status', size=25, readonly=True), # TODO: identify blockd customers
    #     #Payment Terms should be assigned on each project in future. Some projects have different payment term than the customer's Payment Term. ( Solved Adding project payment Term in projects).
    #     'payment_terms': fields.related('partner_id','property_payment_term',type='many2one',
    #                                     relation='account.payment.term',string ='Customer Payment Term', readonly=True),
    #     'cheque_hold': fields.integer(string='Cases of Holding of Cheque'),
    #     'cheque_last_held': fields.date(string='Last Cheque Held On',  readonly=True),
    #     'cheque_bounce': fields.integer(string='Cases of Check Bounce') ,
    #     'cheque_last_bounced': fields.date(string='Last Cheque Bounced On',  readonly=True),
    #
    #     #'check_inhand_amount1': fields.function(get_check_amount,type='float',string="Cheque in Hand",readonly=True),
    #     'check_inhand_amount': fields.float("Check In Hand" ,  readonly=True),
    #     'credit_limit': fields.float("Credit Limit" ,  readonly=True),
    #     'sun_credit_details_ids': fields.one2many(obj='sun.credit.checkdetails', fields_id='credit_check_id', string='Sun Accounts/Projects'),
    #     'check_aging_ids': fields.function(_get_check_aging,relation='cic.check.aging.view',type='one2many',string="Aging",readonly=True,multi='check'),
    #     'cheque_details_ids': fields.function(_get_check_aging,relation='cic.check.receipt',type='one2many',string="Cheque Details",readonly=True,multi='check'),
    #
    #     #'cheque_details_id': fields.one2many('cic.check.receipt','partner_id', domain=[('state','in',['received','submitted'])], string= "Partner Checks",readonly=True, help="PDC Receipts with state is Received , Submitted",groups="account.group_account_invoice"),
    #     #'submitted_check_ids': fields.one2many('cic.check.receipt','partner_id', domain=[('state','=','submitted')], string= "Partner Checks On hand",readonly=True, help="PDC Receipts with state is Submitted",groups="account.group_account_invoice"),
    #     #'bounced_check_ids': fields.one2many('cic.check.receipt','partner_id', domain=[('state','=','bounced')], string= "Partner Checks Bounced", readonly=True,  help="PDC Receipts with state Bounced",groups="account.group_account_invoice"),
    #     #'bounce_history_ids': fields.one2many('cic.check.bounce.history', 'partner_id', string="Bounce History",readonly=True, help="Bounced Checks History",groups="account.group_account_invoice"),
    #
    #     #Sales Person should be assigned on each project in future. Some projects have different  Sales Person than the customer  (Took sales person from project.project, if sales person exists in project.project then use that for project sales person
    #     'sales_person': fields.char(string='Sales Person', size=255, readonly=True),
    #     'remarks': fields.text('Remarks'),
    #     'verification_remarks': fields.text('Verification Remarks'),
    #     'management_note': fields.text('Management Note'),
    #     'user_id': fields.many2one('res.users', 'User',   readonly=True),
    #     #Period should vary based on project payment Terms (Solved by adding payment terms to project.project.  Verify based on payment days.)
    #     'period':fields.char('Period', size=10,readonly=True),
    #     'filter_overdue':fields.boolean('Filter By Over Due'),
    #     'filter_due':fields.boolean('Filter By Due'),
    #     'include_allocated':fields.boolean('Include Allocated'),
    #     #TODO:Attachment should be checked for licence file. (Licence attachment should from different menu with a licence tag.)
    #     'has_attachment':fields.boolean('Has attachment'),
    #     'debtor_statement_lines': fields.one2many('sun.credit.check.debtor.statement','sun_credit_check_id',string='Debtor Statement'),
    #     'state': fields.selection([('new','New'),('draft','Draft'),('verified','Verified'),('approved','Approved'),('rejected','Rejected')],
    #                               required= True,track_visibility='onchange',string="Status"),
    # }


    date_create = fields.Date(string='Date',default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True,
                                  domain="[('customer','=',True)]")
    status = fields.Char(string='Customer Status', size=25,readonly=True)  # TODO: identify blockd customers
    # Payment Terms should be assigned on each project in future. Some projects have different payment term than the customer's Payment Term. ( Solved Adding project payment Term in projects).
    payment_terms = fields.Many2one('account.payment.term',string='Customer Payment Term', readonly=True)
    cheque_hold = fields.Integer(string='Cases of Holding of Cheque')
    cheque_last_held = fields.Date(string='Last Cheque Held On', readonly=True,default=fields.Date.context_today)
    cheque_bounce = fields.Integer(string='Cases of Check Bounce')
    cheque_last_bounced = fields.Date(string='Last Cheque Bounced On', readonly=True,default=fields.Date.context_today)

    # 'check_inhand_amount1': fields.function(get_check_amount,type='float',string="Cheque in Hand",readonly=True),
    check_inhand_amount =  fields.Float("Check In Hand", readonly=True)
    credit_limit = fields.Float("Credit Limit", readonly=True)
    sun_credit_details_ids = fields.One2many('sun.credit.checkdetails', 'credit_check_id', string='Sun Accounts/Projects')
    check_aging_ids = fields.One2many('cic.check.aging.view',compute = _get_check_aging, string="Aging", readonly=True, multi='check')
    cheque_details_ids = fields.One2many('cic.check.receipt', compute = _get_check_aging,string="Cheque Details", readonly=True, multi='check')

    # 'cheque_details_id': fields.one2many('cic.check.receipt','partner_id', domain=[('state','in',['received','submitted'])], string= "Partner Checks",readonly=True, help="PDC Receipts with state is Received , Submitted",groups="account.group_account_invoice"),
    # 'submitted_check_ids': fields.one2many('cic.check.receipt','partner_id', domain=[('state','=','submitted')], string= "Partner Checks On hand",readonly=True, help="PDC Receipts with state is Submitted",groups="account.group_account_invoice"),
    # 'bounced_check_ids': fields.one2many('cic.check.receipt','partner_id', domain=[('state','=','bounced')], string= "Partner Checks Bounced", readonly=True,  help="PDC Receipts with state Bounced",groups="account.group_account_invoice"),
    # 'bounce_history_ids': fields.one2many('cic.check.bounce.history', 'partner_id', string="Bounce History",readonly=True, help="Bounced Checks History",groups="account.group_account_invoice"),

    # Sales Person should be assigned on each project in future. Some projects have different  Sales Person than the customer  (Took sales person from project.project, if sales person exists in project.project then use that for project sales person
    sales_person = fields.Char(string='Sales Person', size=255, readonly=True)
    remarks = fields.Text('Remarks')
    verification_remarks = fields.Text('Verification Remarks')
    management_note =  fields.Text('Management Note')
    user_id = fields.Many2one('res.users', 'User', readonly=True, default=lambda self: self.env.user)
    # Period should vary based on project payment Terms (Solved by adding payment terms to project.project.  Verify based on payment days.)
    period = fields.Char('Period', size=10, readonly=True)
    filter_overdue = fields.Boolean('Filter By Over Due')
    filter_due = fields.Boolean('Filter By Due')
    include_allocated = fields.Boolean('Include Allocated',Default='New')
    # TODO:Attachment should be checked for licence file. (Licence attachment should from different menu with a licence tag.)
    has_attachment = fields.Boolean('Has attachment')
    debtor_statement_lines = fields.One2many('sun.credit.check.debtor.statement', 'sun_credit_check_id',
                                              string='Debtor Statement')
    state = fields.Selection([('new', 'New'), ('draft', 'Draft'), ('verified', 'Verified'), ('approved', 'Approved'),
         ('rejected', 'Rejected')], required=True, track_visibility='onchange', string="Status",default='new')

    #
    # _defaults ={
    #     'date_create': fields.date.context_today,
    #     'user_id': lambda obj, cr, uid, context: uid,
    #     'state': 'new',#Should not change to draft ( To handle Stages)
    #     'include_allocated':False,
    # }

    # def action_reset(self,cr,uid,ids,context=None):
    #     return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
    #
    # def action_verified(self,cr,uid,ids,context=None):
    #     return self.write(cr, uid, ids, {'state': 'verified'}, context=context)
    #
    # def action_approved(self,cr,uid,ids,context=None):
    #     return self.write(cr, uid, ids, {'state': 'approved'}, context=context)
    #
    # def action_rejected(self,cr,uid,ids,context=None):
    #     return self.write(cr, uid, ids, {'state': 'rejected'}, context=context)

    @api.multi
    def action_reset(self):
        return self.write({'state': 'draft'})

    @api.multi
    def action_verified(self):
        return self.write({'state': 'verified'})

    @api.multi
    def action_approved(self):
        return self.write({'state': 'approved'})

    @api.multi
    def action_rejected(self):
        return self.write({'state': 'rejected'})

    # ######Overriding create to pass values to openerp table
    # def create(self, cr, uid, ids, context=None):
    #     partner_id = ids['partner_id']
    #     _val = {}
    #     if partner_id:
    #         _val = self.get_partner_info(cr, uid, partner_id,False, context)
    #         ids.update({'status':_val['status']})
    #         ids.update({'period':_val['period']})
    #         ids.update({'cheque_last_bounced':_val['cheque_last_bounced']})
    #         ids.update({'cheque_last_held':_val['cheque_last_held']})
    #         ids.update({'check_inhand_amount':_val['check_inhand_amount']})
    #         ids.update({'credit_limit':_val['credit_limit']})
    #         ####Change the state new to draft at the time of record creation
    #         if ids['state'] == 'new':
    #             ids.update({'state':'draft'})
    #     #####Don't save to database if there is no credit records from sun system
    #     if ids['sun_credit_details_ids']:
    #         result = super(sun_credit_check, self).create(cr, uid, ids, context=context)
    #     else:
    #         raise osv.except_osv('Error', 'Please Check Customer SUN Account Details')
    #     return result


        ######Overriding create to pass values to openerp table

    # @api.model
    # def create(self,ids):
    #     partner_id = ids['partner_id']
    #     print 'hhhhh'
    #     print partner_id
    #     _val = {}
    #     if partner_id:
    #         _val = self.get_partner_info(partner_id,False)
    #
    #         ids.update({'status': _val['status']})
    #         ids.update({'period': _val['period']})
    #         ids.update({'cheque_last_bounced': _val['cheque_last_bounced']})
    #         ids.update({'cheque_last_held': _val['cheque_last_held']})
    #         ids.update({'check_inhand_amount': _val['check_inhand_amount']})
    #         ids.update({'credit_limit': _val['credit_limit']})
    #         ####Change the state new to draft at the time of record creation
    #         if ids['state'] == 'new':
    #             ids.update({'state': 'draft'})
    #     #####Don't save to database if there is no credit records from sun system
    #     if ids['sun_credit_details_ids']:
    #         result = super(SunCreditCheck, self).create(ids)
    #     else:
    #         raise UserError('Please Check Customer SUN Account Details')
    #     return result

    @api.model
    def create(self, vals):
        partner_id = self.partner_id
        _val = {}
        if partner_id:
            _val = self.get_partner_info(False)

            vals.update({'status': _val['status']})
            vals.update({'period': _val['period']})
            vals.update({'cheque_last_bounced': _val['cheque_last_bounced']})
            vals.update({'cheque_last_held': _val['cheque_last_held']})
            vals.update({'check_inhand_amount': _val['check_inhand_amount']})
            vals.update({'credit_limit': _val['credit_limit']})
            ####Change the state new to draft at the time of record creation
            if vals['state'] == 'new':
                vals.update({'state': 'draft'})
        #####Don't save to database if there is no credit records from sun system
        if vals['sun_credit_details_ids']:
            result = super(SunCreditCheck, self).create(vals)
        else:
            raise UserError('Please Check Customer SUN Account Details')
        return result

    #
    # def on_partner_change(self, cr, uid, ids, partner_id , context=None):
    #     _val = {}
    #     if partner_id:
    #         _val = self.get_partner_info(cr, uid, partner_id,True, context)
    #     return {'value': _val}

    @api.onchange('partner_id')
    def on_partner_change(self):
        _val = {}
        if self.partner_id:
            _val = self.get_partner_info(False)
        return {'value': _val}

    # def _calc_invoice_extra_days(self,cr,uid,in_date,pt_days,context=None):
    #     _days=''
    #     if in_date > 0:
    #         _dt1=datetime.date.today()
    #         _today = _dt1.strftime("%Y%m%d")
    #         _today=datetime.datetime.strptime(str(_today), '%Y%m%d')
    #         #Invoiced date is converted to date format from dmy
    #         _t2 = datetime.datetime.strptime(str(in_date), '%d/%m/%Y')
    #         #First of invoiced month
    #         _t2 = datetime.datetime(_t2.year, _t2.month, 1)
    #         #First of invoiced next month
    #         _invoiced_next_month = datetime.datetime(_t2.year + (_t2.month / 12), ((_t2.month % 12) + 1), 1)
    #         # End of invoiced month
    #         _invoiced_month_end =_invoiced_next_month- timedelta(days=1)
    #         _days = abs((_today - _invoiced_month_end).days)
    #         _days=_days-pt_days
    #     return _days

    def _calc_invoice_extra_days(self,in_date, pt_days):
        _days = ''
        if in_date > 0:
            _dt1 = datetime.today()
            _today = _dt1.strftime("%Y%m%d")
            _today = datetime.strptime(str(_today), '%Y%m%d')
            # Invoiced date is converted to date format from dmy
            _t2 = datetime.strptime(str(in_date), '%d/%m/%Y')
            # First of invoiced month
            _t2 = datetime(_t2.year, _t2.month, 1)
            # First of invoiced next month
            _invoiced_next_month = datetime(_t2.year + (_t2.month / 12), ((_t2.month % 12) + 1), 1)
            # End of invoiced month
            _invoiced_month_end = _invoiced_next_month - timedelta(days=1)
            _days = abs((_today - _invoiced_month_end).days)
            _days = _days - pt_days
        return _days


    #####Convert Payment days to period format required by sunsystem
    # def _calc_period(self,cr,uid,days_payment,context=None):
    #
    #     dt = datetime.date.today()
    #     ibm_period = dt.strftime("%Y%m")
    #
    #     #Ibm Test
    #     if days_payment > 0:
    #         dt=datetime.date.today()
    #         ibm_first_of_month = date(day=1, month=dt.month, year=dt.year)
    #         ibm_last_of_last_month = ibm_first_of_month - timedelta(days=5) # To override february 28 issues when calculating based on days
    #         #TODO: Find solution for leap year issues
    #         ibm_pt_reduced_date = ibm_last_of_last_month - timedelta(days_payment)
    #         ibm_period = ibm_pt_reduced_date.strftime("%Y%m")
    #
    #     ibm_list = list(ibm_period)
    #     ibm_list.insert(4,'0')
    #     ibm_period = "".join(ibm_list)
    #     return ibm_period
    #


    def _calc_period(self, days_payment, context=None):

        dt = datetime.today()
        ibm_period = dt.strftime("%Y%m")

        # Ibm Test
        if days_payment > 0:
            dt = datetime.today()
            ibm_first_of_month = date(day=1, month=dt.month, year=dt.year)
            ibm_last_of_last_month = ibm_first_of_month - timedelta(days=5)  # To override february 28 issues when calculating based on days
            # TODO: Find solution for leap year issues
            ibm_pt_reduced_date = ibm_last_of_last_month - timedelta(days_payment)
            ibm_period = ibm_pt_reduced_date.strftime("%Y%m")

        ibm_list = list(ibm_period)
        ibm_list.insert(4, '0')
        ibm_period = "".join(ibm_list)
        return ibm_period

    #####Only to Display Due for the - Months in Note
    # def _calc_invoice_date_details(self,cr,uid,days_payment,_invc_date,context=None):
    #
    #     _dt = datetime.date.today()
    #     _ibm_period = _dt.strftime("%Y%m%d")
    #     #In this it removes added 0 in above function
    #     if days_payment > 0:
    #         _dt=datetime.date.today()
    #         _ibm_first_of_month = datetime.date(day=1, month=_dt.month, year=_dt.year)
    #         _ibm_last_of_last_month = _ibm_first_of_month - timedelta(days=1)
    #         _ibm_pt_reduced_date = _ibm_last_of_last_month - timedelta(days_payment)
    #         _ibm_period = _ibm_pt_reduced_date.strftime("%Y%m%d")
    #     _date1=datetime.datetime.strptime(str(_ibm_period), '%Y%m%d')
    #     _date2=datetime.datetime.strptime(str(_invc_date), '%Y%m%d')
    #     r= relativedelta.relativedelta(_date1,_date2)
    #     #_date = datetime(year=int(s[0:4]), month=int(s[4:6]), day=int(s[6:8]))
    #     return str(r.months)

    def _calc_invoice_date_details(self,  days_payment, _invc_date, context=None):

        _dt = datetime.today()
        _ibm_period = _dt.strftime("%Y%m%d")
        # In this it removes added 0 in above function
        if days_payment > 0:
            _dt = datetime.today()
            _ibm_first_of_month = datetime(day=1, month=_dt.month, year=_dt.year)
            _ibm_last_of_last_month = _ibm_first_of_month - timedelta(days=1)
            _ibm_pt_reduced_date = _ibm_last_of_last_month - timedelta(days_payment)
            _ibm_period = _ibm_pt_reduced_date.strftime("%Y%m%d")
        _date1 = datetime.strptime(str(_ibm_period), '%Y%m%d')
        _date1 = datetime.strptime(str(_ibm_period), '%Y%m%d')
        _date2 = datetime.datetime.strptime(str(_invc_date), '%Y%m%d')
        r = relativedelta.relativedelta(_date1, _date2)
        # _date = datetime(year=int(s[0:4]), month=int(s[4:6]), day=int(s[6:8]))
        return str(r.months)



    #####Load sunaccount code from openerp, then load Account credit details from sunsystem.
    # def get_partner_info(self,cr, uid, partner_id, status, context):
    #     _val = {}
    #     _val['has_attachment'] = None
    #     _val['sales_person'] = None
    #     _val['payment_terms'] = None
    #     _val['check_inhand_amount'] = 0
    #     _val['credit_limit'] = 0
    #     _val['cheque_bounce']=0
    #     _val['cheque_hold']=0
    #     _val['cheque_last_held'] = False
    #     _val['cheque_last_bounced'] = False
    #     _val['status'] = ''
    #     _val['period'] = ''
    #     _val['filter_overdue'] = False
    #     _val['filter_due'] = False
    #     _val['include_allocated'] = False
    #     _val['sun_credit_details_ids'] =None
    #     #_val['check_aging_ids'] =None
    #
    #
    #     partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
    #     _val['has_attachment'] = len(partner.attachment_ids)
    #     _val['sales_person'] = partner.user_id.name
    #     payment_term = partner.property_payment_term
    #     _val['payment_terms'] = payment_term.id
    #     _val['check_inhand_amount'] = self.get_check_amount(cr,uid,partner_id)
    #     #_val['check_inhand_amount1'] = self.get_check_amount(cr,uid,partner_id)
    #     _val['credit_limit'] = partner.credit_limit
    #
    #     sun_accounts = [{'sun_acc_no':x.sun_account_no, 'sun_db': x.sun_db, 'proj_id': x.project_id.id} for x in partner.sun_account_ids]
    #
    #     _val['status'] = 'Active' if partner.active else 'Blocked'
    #
    #
    #     ratings = partner.rating_ids
    #     if status:
    #         _val['partner_rating_ids'] = [x.id for x in ratings]
    #
    #     if ratings:
    #         record = len(ratings)
    #         rating = ratings[record-1].rating_category_id.name
    #         _val['status'] = _val['status'] + ' / ' + rating
    #
    #     cheque_bounce_history = self.pool.get('cic.check.bounce.history').search(cr, uid, [('partner_id', '=',partner_id),('state', 'in' ,['bounced'])])
    #     if cheque_bounce_history:
    #         _val['cheque_bounce'] = len(cheque_bounce_history)
    #         _last_bounce_date  = self.pool.get('cic.check.bounce.history').read(cr,uid,max(cheque_bounce_history),context=None)
    #         _val['cheque_last_bounced']=_last_bounce_date["bounced_date"]
    #        # _val['cheque_last_bounced']=cheque_bounce_history["bounced_date"]
    #
    #     cheque_held_history = self.pool.get('cic.check.bounce.history').search(cr, uid, [('partner_id', '=',partner_id),('state', 'in' ,['hold'])])
    #     if cheque_held_history:
    #         _val['cheque_hold'] = len(cheque_held_history)
    #         _last_hold_date  = self.pool.get('cic.check.bounce.history').read(cr,uid,max(cheque_held_history),context=None)
    #         _val['cheque_last_held']=_last_hold_date["bounced_date"]
    #
    #
    #     #Find Current Period based on today
    #     payment_term_days=0
    #     if payment_term:
    #         payment_term_days = payment_term.line_ids[0].days
    #         #if payment_term_days <= 0:
    #         #    _val['status'] = _val['status'] + ' / ' + payment_term.name
    #     ibm_period = self._calc_period(cr, uid,payment_term_days)
    #     _val['period'] = ibm_period  # To Display in Form
    #     #Ibm End Test
    #
    #     data = []
    #     for sun_account in sun_accounts:
    #         ibm_period=_val['period']  #If none of the below condition is true then partner payment term will be passed to sql
    #         prj_cr_limit = _val['credit_limit'] #Default credit limit will be partner credit limit
    #         if sun_account['proj_id'] :  #checking whether sun account has project, and project has seperate payment term
    #             proj_payment =  self.pool.get('project.project').browse(cr,uid,sun_account['proj_id'])
    #             if proj_payment.project_payment_term_id :
    #                 payment_term_days = proj_payment.project_payment_term_id.line_ids[0].days
    #                 ibm_period= self._calc_period(cr, uid,payment_term_days)
    #             if proj_payment.project_credit_limit > 0:
    #                 prj_cr_limit= proj_payment.project_credit_limit
    #
    #
    #
    #         query = "EXEC dbo.GetSunAccountBalanceCombined @SunAccountNo = '" + sun_account['sun_acc_no'] +\
    #                 "', @SunDb = '" + sun_account['sun_db'] + "', @ToPeriod = " + ibm_period   # Ibm replace the actual value
    #         result = self.pool.get('import.odbc.dbsource').fetch_data(cr, uid, dbsource='open_ERP', query=query, context=context)
    #
    #         for x in result:
    #             x.update({'prj_period':str(ibm_period),
    #                       'prj_pay_days':payment_term_days,
    #                       'prj_cr_limit':prj_cr_limit})
    #             data.append(x)
    #
    #     suncode_info = []
    #     for x in data:
    #         project_id = (item for item in sun_accounts if item["sun_acc_no"] == x['ACCNT_CODE'].strip() and item["sun_db"] == x['SUN_DB'].strip()).next()
    #         _invcedate=''
    #         ##Payment Due months, Due Days with Note
    #         #_duemonths=''
    #         #_due_months_in_word =''
    #         _t1 = x['FirstPendingInvoice']
    #         if _t1 <> 0 :
    #             s=str(_t1)
    #             s_datetime = datetime.datetime.strptime(s, '%Y%m%d')
    #             _invcedate="  [" + s_datetime.strftime("%d/%m/%Y") +"]"
    #             ##To Calculate Due in words
    #             #_duemonths= self._calc_invoice_date_details(cr, uid,x['prj_pay_days'],x['FirstPendingInvoice'])
    #             #if _duemonths > 0:
    #             #    _due_months_in_word = "  Due For " + str(_duemonths) +" Months"
    #
    #
    #         suncode_info.append({'partner_id':partner_id,
    #                           'project_id': project_id["proj_id"],
    #                           'sun_db': x['SUN_DB'.strip()],
    #                           'account_code': x['ACCNT_CODE'.strip()],
    #                           'account_name':x['ACCNT_NAME'.strip()] ,
    #                           'sun_note': _invcedate, # + _due_months_in_word,
    #                           'last_transaction': x['LAST_TRANS'],
    #                           'prj_period' :x['prj_period'],
    #                           'project_credit_limit' :x['prj_cr_limit'],
    #                           'proj_sun_account_balance': x['ACC_BALNCE'] * -1,
    #                           'proj_account_balance': x['ACC_BALNCE'] * -1,
    #                           'proj_sun_account_due': x['CurrentDueAmount'] * -1,
    #                           'proj_account_due': x['CurrentDueAmount'] * -1,
    #                           #'proj_overdue_plus_due':  (x['DueAmount'] * -1) + (x['OverDueAmount']*-1),
    #                           'proj_over_due':x['OverDueAmount']*-1,
    #                           'proj_total_due': x['TotalDueAmount'] * -1,})
    #
    #         _val['sun_credit_details_ids'] = suncode_info
    #
    #
    #     ##_val['cheque_againg_ids'] = self.pool.get('cic.check.aging.view').search(cr,uid,[('partner_id','=',partner_id)])
    #     #
    #     #
    #     _aging_ids = self.pool.get('cic.check.aging.view').search(cr,uid,[('partner_id','=',partner_id)])
    #     _cheque_ids = self.pool.get('cic.check.receipt').search(cr,uid,[('partner_id','=',partner_id),('state','in',['received','submitted','re_submitted'])])
    #     _val['check_aging_ids'] = _aging_ids
    #     _val['cheque_details_ids'] = _cheque_ids
    #     _val['debtor_statement_lines'] = []
    #
    #     return _val

    #####Load sunaccount code from openerp, then load Account credit details from sunsystem.
    def get_partner_info(self,status):
        _val = {}
        _val['has_attachment'] = None
        _val['sales_person'] = None
        _val['payment_terms'] = None
        _val['check_inhand_amount'] = 0
        _val['credit_limit'] = 0
        _val['cheque_bounce']=0
        _val['cheque_hold']=0
        _val['cheque_last_held'] = False
        _val['cheque_last_bounced'] = False
        _val['status'] = ''
        _val['period'] = ''
        _val['filter_overdue'] = False
        _val['filter_due'] = False
        _val['include_allocated'] = False
        _val['sun_credit_details_ids'] =None
        #_val['check_aging_ids'] =None

        # print partner_id
        # print 'hhhh'
        partner = self.partner_id
        # print partner
        # print 'hhhh'
       # _val['has_attachment'] = len(partner.attachment_ids)
        _val['sales_person'] = partner.user_id.name
        #payment_term = partner.project_payment_term_id
        #_val['payment_terms'] = payment_term.id
        _val['check_inhand_amount'] = self.get_check_amount(self.partner_id.id)
        #_val['check_inhand_amount1'] = self.get_check_amount(cr,uid,partner_id)
        _val['credit_limit'] = partner.credit_limit

        # for x in partner.sun_account_ids:
        #
        #     sun_accounts = [{'sun_acc_no':x.sun_account_no, 'sun_db': x.sun_db, 'proj_id': x.project_id.id}]

        sun_accounts = [{'sun_acc_no': x.sun_account_no, 'sun_db': x.sun_db, 'proj_id': x.project_id.id} for x in
                        partner.sun_account_ids]
        #print sun_accounts

        _val['status'] = 'Active' if partner.active else 'Blocked'


        #ratings = partner.rating_ids
        # if status:
        #     _val['partner_rating_ids'] = [x.id for x in ratings]
        #
        # if ratings:
        #     record = len(ratings)
        #     rating = ratings[record-1].rating_category_id.name
        #     _val['status'] = _val['status'] + ' / ' + rating

        cheque_bounce_history = self.env['cic.check.bounce.history'].search([('partner_id', '=',self.partner_id.id),('state', 'in' ,['bounced'])])
        if cheque_bounce_history:
            _val['cheque_bounce'] = len(cheque_bounce_history)
            _last_bounce_date = self.env['cic.check.bounce.history'].read(max(cheque_bounce_history))
            _val['cheque_last_bounced'] = _last_bounce_date["bounced_date"]
           # _val['cheque_last_bounced']=cheque_bounce_history["bounced_date"]

        cheque_held_history = self.env['cic.check.bounce.history'].search([('partner_id', '=',self.partner_id.id),('state', 'in' ,['hold'])])
        if cheque_held_history:
            _val['cheque_hold'] = len(cheque_held_history)
            _last_hold_date  = self.env['cic.check.bounce.history'].read(max(cheque_held_history))
            _val['cheque_last_held']=_last_hold_date["bounced_date"]

        #Find Current Period based on today
        payment_term_days=0
        if self.payment_terms:
            payment_term_days = self.payment_terms.line_ids[0].days
            #if payment_term_days <= 0:
            #    _val['status'] = _val['status'] + ' / ' + payment_term.name
        ibm_period = self._calc_period(payment_term_days)
        _val['period'] = ibm_period  # To Display in Form
        #Ibm End Test
        data = []
        for sun_account in sun_accounts:
            ibm_period = _val['period']  #If none of the below condition is true then partner payment term will be passed to sql
            prj_cr_limit = _val['credit_limit'] #Default credit limit will be partner credit limit
            if sun_account['proj_id'] :  #checking whether sun account has project, and project has seperate payment term
                proj_payment = self.env['project.project'].search([('id','=',sun_account['proj_id'])])
                if proj_payment.project_payment_term_id :
                    payment_term_days = proj_payment.project_payment_term_id.line_ids[0].days
                    ibm_period= self._calc_period(payment_term_days)
                if proj_payment.project_credit_limit > 0:
                    prj_cr_limit= proj_payment.project_credit_limit

        query = "EXEC dbo.GetSunAccountBalanceCombined @SunAccountNo = '" + sun_account['sun_acc_no'] + \
                "', @SunDb = '" + sun_account['sun_db'] + "', @ToPeriod = " + ibm_period  #
        print query
        result = self.env['import.odbc.dbsource'].fetch_data(dbsource='SQL', query=query)
        print result
        for x in result:
            x.update({'prj_period':str(ibm_period),
                      'prj_pay_days':payment_term_days,
                      'prj_cr_limit':prj_cr_limit})
            data.append(x)

        # print 'gggg'
        # print data
        suncode_info = []
        for x in data:

            project_id = (item for item in sun_accounts if item["sun_acc_no"] == x['ACCNT_CODE'].strip() and item["sun_db"] == x['SUN_DB'].strip()).next()
            _invcedate=''
            ##Payment Due months, Due Days with Note
            #_duemonths=''
            #_due_months_in_word =''
            _t1 = x['FirstPendingInvoice']
            if _t1 != 0 :
                s=str(_t1)
                s_datetime = datetime.strptime(s, '%Y%m%d')
                _invcedate="  [" + s_datetime.strftime("%d/%m/%Y") +"]"
                ##To Calculate Due in words
                #_duemonths= self._calc_invoice_date_details(cr, uid,x['prj_pay_days'],x['FirstPendingInvoice'])
                #if _duemonths > 0:
                #    _due_months_in_word = "  Due For " + str(_duemonths) +" Months"


            suncode_info.append({'partner_id':self.partner_id,
                              'project_id': project_id["proj_id"],
                              'sun_db': x['SUN_DB'.strip()],
                              'account_code': x['ACCNT_CODE'.strip()],
                              'account_name':x['ACCNT_NAME'.strip()] ,
                              'sun_note': _invcedate, # + _due_months_in_word,
                              'last_transaction': x['LAST_TRANS'],
                              'prj_period' :x['prj_period'],
                              'project_credit_limit' :x['prj_cr_limit'],
                              'proj_sun_account_balance': x['ACC_BALNCE'] * -1,
                              'proj_account_balance': x['ACC_BALNCE'] * -1,
                              'proj_sun_account_due': x['CurrentDueAmount'] * -1,
                              'proj_account_due': x['CurrentDueAmount'] * -1,
                              #'proj_overdue_plus_due':  (x['DueAmount'] * -1) + (x['OverDueAmount']*-1),
                              'proj_over_due':x['OverDueAmount']*-1,
                              'proj_total_due': x['TotalDueAmount'] * -1,})

            _val['sun_credit_details_ids'] = suncode_info

        #print _val['sun_credit_details_ids']
        ##_val['cheque_againg_ids'] = self.pool.get('cic.check.aging.view').search(cr,uid,[('partner_id','=',partner_id)])
        #
        #
        _aging_ids = self.env['cic.check.aging.view'].search([('partner_id','=',self.partner_id.id)])
        _cheque_ids = self.env['cic.check.receipt'].search([('partner_id','=',self.partner_id.id),('state','in',['received','submitted','re_submitted'])])
        _val['check_aging_ids'] = _aging_ids
        _val['cheque_details_ids'] = _cheque_ids
        _val['debtor_statement_lines'] = []

        print _val
        return _val


    # def on_change_sun_credit_details(self, cr, uid, ids ,sun_credit_details_ids,partner_id, filter_overdue=False, filter_due=False, include_allocated=False, context=None):
    #     _res = {'debtor_statement_lines':[]}
    #     values = self.resolve_2many_commands(cr, uid, 'sun_credit_details_ids', sun_credit_details_ids, ['account_code', 'sun_db','project_id'], context)
    #     _res.update({'debtor_statement_lines': self._get_sun_statement_data(cr, uid, values,partner_id,filter_overdue,filter_due,include_allocated)})
    #     return {'value': _res}

    @api.multi
    def on_change_sun_credit_details(self,sun_credit_details_ids,partner_id, filter_overdue=False, filter_due=False, include_allocated=False):
        _res = {'debtor_statement_lines':[]}
        #print sun_credit_details_ids
        values = self.resolve_2many_commands('sun_credit_details_ids', sun_credit_details_ids, ['account_code', 'sun_db','project_id'])
        #print values
        _res.update({'debtor_statement_lines': self._get_sun_statement_data(values,partner_id,filter_overdue,filter_due,include_allocated)})
        return {'value': _res}

    # def _get_sun_statement_data(self,cr,uid,sun_accounts ,partner_id,filter_overdue,filter_due,include_allocated, context=None):
    #     _followup_lines = []
    #     partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
    #     payment_term = partner.property_payment_term
    #     ibm_period=''
    #     for sun_acc in sun_accounts:
    #         payment_term_days=0
    #         if payment_term:
    #             payment_term_days = payment_term.line_ids[0].days
    #         ibm_period = self._calc_period(cr, uid,payment_term_days)
    #         if sun_acc['project_id'] :  #checking whether sun account has project, and project has seperate payment term
    #             _project_obj = self.pool.get('project.project').browse(cr,uid,sun_acc['project_id'])
    #             if _project_obj.project_payment_term_id:
    #                 payment_term_days = _project_obj.project_payment_term_id.line_ids[0].days
    #                 ibm_period= self._calc_period(cr, uid,payment_term_days)
    #         _a = ' '
    #         if include_allocated:
    #             _a='A'
    #         query = "EXEC dbo.GetSunAccountBalanceDetails @SunAccountNo = '" + sun_acc['account_code'] +\
    #                "', @SunDb = '" + sun_acc['sun_db'] + "'" + ",@A= '" + _a + "'"
    #         result = self.pool.get('import.odbc.dbsource').fetch_data(cr, uid, dbsource='open_ERP', query=query, context=context)
    #         for x in result:
    #             d_c = x['D_C']
    #             amt_c = 0
    #             amt_d = 0
    #             if d_c == 'D':
    #                 amt_d = x['AMOUNT'] * -1
    #                 # elif d_c == 'C':
    #                 #     amt_c = x['AMOUNT'] * -1
    #             elif d_c == 'C':
    #                 amt_c = x['AMOUNT']
    #             invcedate=''
    #             inv_date = ''
    #             _t1 = x['TRANS_DATE']
    #             if _t1 <> 0 or _t1 <> '':
    #                 s=str(_t1)
    #                 s_datetime = datetime.datetime.strptime(s.strip(), '%Y%m%d')
    #                 #invcedate="  [" + s_datetime.strftime("%d/%m/%Y") +"]"
    #                 invcedate =s_datetime.strftime("%d/%m/%Y")
    #                 #invcedate = time.strptime(invcedate, "%d/%m/%Y")
    #             _over_due = False
    #             _due = False
    #             _tt=x['PERIOD'.strip()]
    #             if int(ibm_period) == int(_tt):
    #                 _due = True
    #             if int(_tt) < int(ibm_period):
    #                 _over_due = True
    #             _over_days=0
    #             _int_amount=0
    #             _alloc=False
    #             if x['ALLOCATION'.strip()] == 'A':
    #                 _alloc=    True
    #             if _over_due :
    #                 _over_days= self._calc_invoice_extra_days(cr,uid,invcedate,payment_term_days)
    #                 if  partner.interest_rate_od > 0 :
    #                     _int_rate= partner.interest_rate_od
    #                     _int_amount=self.percent(cr,uid,_int_rate,amt_d,_over_days)
    #
    #             if filter_due & filter_overdue:
    #                 if _due or _over_due:
    #                     _followup_lines.append({
    #                         'acc_name': x['ACCNT_NAME'.strip()],
    #                         'acc_code': x['ACCNT_CODE'.strip()] ,
    #                         'acc_db': sun_acc['sun_db'] + " " +   x['ACCNT_CODE'.strip()] ,
    #                         'trans_date': invcedate, #x['TRANS_DATE'.strip()],
    #                         'trans_date_int':x['TRANS_DATE'.strip()],
    #                         'acc_period':_tt, # x['PERIOD'.strip()],
    #                         'over_due': _over_due,
    #                         'due': _due,
    #                         'is_allocated': _alloc,
    #                         'reference': x['TREFERENCE'.strip()],
    #                         'description': x['DESCRIPTN'.strip()],
    #                         'over_days': _over_days,
    #                         'interest_amount': _int_amount,
    #                         'credit': amt_c,
    #                         'debit': amt_d
    #                     })
    #             elif filter_overdue :  #statement_over_due_only
    #                 if _over_due:
    #                     _followup_lines.append({
    #                         'acc_name': x['ACCNT_NAME'.strip()],
    #                         'acc_code': x['ACCNT_CODE'.strip()] ,
    #                         'acc_db': sun_acc['sun_db'] + " " +   x['ACCNT_CODE'.strip()] ,
    #                         'trans_date': invcedate, #x['TRANS_DATE'.strip()],
    #                         'trans_date_int':x['TRANS_DATE'.strip()],
    #                         'acc_period':_tt, # x['PERIOD'.strip()],
    #                         'over_due': _over_due,
    #                         'due': _due,
    #                         'is_allocated': _alloc,
    #                         'reference': x['TREFERENCE'.strip()],
    #                         'description': x['DESCRIPTN'.strip()],
    #                         'over_days': _over_days,
    #                         'interest_amount': _int_amount,
    #                         'credit': amt_c,
    #                         'debit': amt_d
    #                     })
    #             elif filter_due :
    #                 if _due:
    #                     _followup_lines.append({
    #                         'acc_name': x['ACCNT_NAME'.strip()],
    #                         'acc_code': x['ACCNT_CODE'.strip()] ,
    #                         'acc_db': sun_acc['sun_db'] + " " +   x['ACCNT_CODE'.strip()] ,
    #                         'trans_date': invcedate, #x['TRANS_DATE'.strip()],
    #                         'trans_date_int':x['TRANS_DATE'.strip()],
    #                         'acc_period':_tt, # x['PERIOD'.strip()],
    #                         'over_due': _over_due,
    #                         'due': _due,
    #                         'is_allocated': _alloc,
    #                         'reference': x['TREFERENCE'.strip()],
    #                         'description': x['DESCRIPTN'.strip()],
    #                         'over_days': _over_days,
    #                         'interest_amount': _int_amount,
    #                         'credit': amt_c,
    #                         'debit': amt_d
    #                     })
    #
    #             else :
    #                 _followup_lines.append({
    #                     'acc_name': x['ACCNT_NAME'.strip()],
    #                     'acc_code': x['ACCNT_CODE'.strip()] ,
    #                     'acc_db': sun_acc['sun_db'] + " " +   x['ACCNT_CODE'.strip()] ,
    #                     'trans_date': invcedate, #x['TRANS_DATE'.strip()],
    #                     'trans_date_int':x['TRANS_DATE'.strip()],
    #                     'acc_period':_tt, # x['PERIOD'.strip()],
    #                     'over_due': _over_due,
    #                     'due': _due,
    #                     'is_allocated': _alloc,
    #                     'reference': x['TREFERENCE'.strip()],
    #                     'description': x['DESCRIPTN'.strip()],
    #                     'over_days': _over_days,
    #                     'interest_amount': _int_amount,
    #                     'credit': amt_c,
    #                     'debit': amt_d
    #                 })
    #     _followup_lines = sorted(_followup_lines, key=itemgetter('trans_date_int'))
    #     return _followup_lines

    @api.multi
    def _get_sun_statement_data(self,sun_accounts, partner_id, filter_overdue, filter_due, include_allocated):

        print 'test fn'
        print sun_accounts
        _followup_lines = []
        partner = self.env['res.partner'].search([('id','=',partner_id)])
        #payment_term = partner['property_payment_term']
        ibm_period = ''
        for sun_acc in sun_accounts:
            payment_term_days = 0
            # if payment_term:
            #     payment_term_days = payment_term.line_ids[0].days
            ibm_period = self._calc_period(payment_term_days)
            if sun_acc['project_id']:  # checking whether sun account has project, and project has seperate payment term
                _project_obj = self.env['project.project'].search([('id','=',sun_acc['project_id'])])
                if _project_obj.project_payment_term_id:
                    payment_term_days = _project_obj.project_payment_term_id.line_ids[0].days
                    ibm_period = self._calc_period(payment_term_days)
            _a = ' '
            if include_allocated:
                _a = 'A'
            query = "EXEC dbo.GetSunAccountBalanceDetails @SunAccountNo = '" + sun_acc['account_code'] + \
                    "', @SunDb = '" + sun_acc['sun_db'] + "'" + ",@A= '" + _a + "'"
            # query = "EXEC dbo.sun_account @SunAccountNo = '" + sun_acc['account_code'] + \
            #         "', @SunDb = '" + sun_acc['sun_db'] + "'" + ",@A= '" + _a + "'"
            print query
            result = self.env['import.odbc.dbsource'].fetch_data(dbsource='SQL', query=query)
            print result
            for x in result:
                d_c = x['D_C']
                amt_c = 0
                amt_d = 0
                if d_c == 'D':
                    amt_d = x['AMOUNT'] * -1
                    # elif d_c == 'C':
                    #     amt_c = x['AMOUNT'] * -1
                elif d_c == 'C':
                    amt_c = x['AMOUNT']
                invcedate = ''
                inv_date = ''
                _t1 = x['TRANS_DATE']
                if _t1 != 0 or _t1 != '':
                    s = str(_t1)
                    s_datetime = datetime.strptime(s.strip(), '%Y%m%d')
                    # invcedate="  [" + s_datetime.strftime("%d/%m/%Y") +"]"
                    invcedate = s_datetime.strftime("%d/%m/%Y")
                    # invcedate = time.strptime(invcedate, "%d/%m/%Y")
                _over_due = False
                _due = False
                _tt = x['PERIOD'.strip()]
                if int(ibm_period) == int(_tt):
                    _due = True
                if int(_tt) < int(ibm_period):
                    _over_due = True
                _over_days = 0
                _int_amount = 0
                _alloc = False
                if x['ALLOCATION'.strip()] == 'A':
                    _alloc = True
                if _over_due:
                    _over_days = self._calc_invoice_extra_days(invcedate, payment_term_days)
                    if partner.interest_rate_od > 0:
                        _int_rate = partner.interest_rate_od
                        _int_amount = self.percent(_int_rate, amt_d, _over_days)

                if filter_due & filter_overdue:
                    if _due or _over_due:
                        _followup_lines.append({
                            'acc_name': x['ACCNT_NAME'.strip()],
                            'acc_code': x['ACCNT_CODE'.strip()],
                            'acc_db': sun_acc['sun_db'] + " " + x['ACCNT_CODE'.strip()],
                            'trans_date': invcedate,  # x['TRANS_DATE'.strip()],
                            'trans_date_int': x['TRANS_DATE'.strip()],
                            'acc_period': _tt,  # x['PERIOD'.strip()],
                            'over_due': _over_due,
                            'due': _due,
                            'is_allocated': _alloc,
                            'reference': x['TREFERENCE'.strip()],
                            'description': x['DESCRIPTN'.strip()],
                            'over_days': _over_days,
                            'interest_amount': _int_amount,
                            'credit': amt_c,
                            'debit': amt_d
                        })
                elif filter_overdue:  # statement_over_due_only
                    if _over_due:
                        _followup_lines.append({
                            'acc_name': x['ACCNT_NAME'.strip()],
                            'acc_code': x['ACCNT_CODE'.strip()],
                            'acc_db': sun_acc['sun_db'] + " " + x['ACCNT_CODE'.strip()],
                            'trans_date': invcedate,  # x['TRANS_DATE'.strip()],
                            'trans_date_int': x['TRANS_DATE'.strip()],
                            'acc_period': _tt,  # x['PERIOD'.strip()],
                            'over_due': _over_due,
                            'due': _due,
                            'is_allocated': _alloc,
                            'reference': x['TREFERENCE'.strip()],
                            'description': x['DESCRIPTN'.strip()],
                            'over_days': _over_days,
                            'interest_amount': _int_amount,
                            'credit': amt_c,
                            'debit': amt_d
                        })
                elif filter_due:
                    if _due:
                        _followup_lines.append({
                            'acc_name': x['ACCNT_NAME'.strip()],
                            'acc_code': x['ACCNT_CODE'.strip()],
                            'acc_db': sun_acc['sun_db'] + " " + x['ACCNT_CODE'.strip()],
                            'trans_date': invcedate,  # x['TRANS_DATE'.strip()],
                            'trans_date_int': x['TRANS_DATE'.strip()],
                            'acc_period': _tt,  # x['PERIOD'.strip()],
                            'over_due': _over_due,
                            'due': _due,
                            'is_allocated': _alloc,
                            'reference': x['TREFERENCE'.strip()],
                            'description': x['DESCRIPTN'.strip()],
                            'over_days': _over_days,
                            'interest_amount': _int_amount,
                            'credit': amt_c,
                            'debit': amt_d
                        })

                else:
                    _followup_lines.append({
                        'acc_name': x['ACCNT_NAME'.strip()],
                        'acc_code': x['ACCNT_CODE'.strip()],
                        'acc_db': sun_acc['sun_db'] + " " + x['ACCNT_CODE'.strip()],
                        'trans_date': invcedate,  # x['TRANS_DATE'.strip()],
                        'trans_date_int': x['TRANS_DATE'.strip()],
                        'acc_period': _tt,  # x['PERIOD'.strip()],
                        'over_due': _over_due,
                        'due': _due,
                        'is_allocated': _alloc,
                        'reference': x['TREFERENCE'.strip()],
                        'description': x['DESCRIPTN'.strip()],
                        'over_days': _over_days,
                        'interest_amount': _int_amount,
                        'credit': amt_c,
                        'debit': amt_d
                    })
        _followup_lines = sorted(_followup_lines, key=itemgetter('trans_date_int'))
        return _followup_lines

    # def percent(self,cr,uid,percentage, amount,_days):
    #     percentage = percentage / 100
    #     _f =(amount *(1.0 + (percentage/360)) ** _days) - amount
    #     #(amount // 100.00) * percentage
    #     return _f

    def percent(self, percentage, amount,_days):
        percentage = percentage / 100
        _f =(amount *(1.0 + (percentage/360)) ** _days) - amount
        #(amount // 100.00) * percentage
        return _f


SunCreditCheck()

# For Loading Customer Credit details from sun system, Details will be loaded from sql stored procedure
class SunCreditCheckdetails(models.Model):
    _name = 'sun.credit.checkdetails'
    _description = "Sun System Credit Check details on each sun account"

    # _columns= {
    #     'credit_check_id': fields.many2one('sun.credit.check',required=True,ondelete='cascade'),
    #     'partner_id': fields.many2one('res.partner',string='Customer' ,required=True,domain="[('customer','=',True)]"),
    #     'project_id': fields.many2one('project.project',string="Project", readonly=True,domain="[('partner_id','=',partner_id)]"),
    #     'sun_db': fields.char(string='Sun DB', size=10, readonly=True),
    #     'account_code': fields.char(string='Account Code', size=15, readonly=True),
    #     'account_name': fields.char(string='Account Name', size=50, readonly=True),
    #     'last_transaction': fields.integer(string='Last Transaction', readonly=True),
    #     'prj_period': fields.char(string='Period', readonly=True),
    #     'project_paymentterm': fields.char(string='Project/Sun Account Payment Term', size=50, readonly=True),  #TODO: get project payment term if exists for each project
    #     'project_credit_limit': fields.float('Credit Limit',digits=(15, 2),readonly=True),  #TODO: get credit limit on each project if exists
    #     'proj_account_balance': fields.float('Account Balance',digits=(15, 2)),
    #     'proj_sun_account_balance': fields.float('Sun Account Balance',digits=(15, 2), readonly=True),
    #     'proj_sun_account_due': fields.float('Sun Account Due',digits=(15, 2), readonly=True),
    #     'proj_account_due': fields.float('Current Due',digits=(15, 2)),  #Current Due (payment days/28 mod 1,= numberof period.  Due Period
    #     'proj_total_due': fields.float('Total Due',digits=(15, 2)),  # Current Due + Over Due
    #     'proj_name_details':fields.char(string='Project PT and Period and ...',readonly=True),
    #     'prj_pay_days':fields.integer(readonly=True),
    #     'proj_over_due':fields.float('Over Due',digits=(15,2)),
    #     'sun_note':fields.char(string="Note"),
    #
    # }

    credit_check_id = fields.Many2one('sun.credit.check', required=True, ondelete='cascade')
    partner_id  = fields.Many2one('res.partner', string='Customer', required=True, domain="[('customer','=',True)]")
    project_id = fields.Many2one('project.project', string="Project", readonly=True,
                                  domain="[('partner_id','=',partner_id)]")
    sun_db = fields.Char(string='Sun DB', size=10, readonly=True)
    account_code = fields.Char(string='Account Code', size=15, readonly=True)
    account_name = fields.Char(string='Account Name', size=50, readonly=True)
    last_transaction = fields.Integer(string='Last Transaction', readonly=True)
    prj_period = fields.Char(string='Period', readonly=True)
    project_paymentterm = fields.Char(string='Project/Sun Account Payment Term', size=50,
                                       readonly=True)  # TODO: get project payment term if exists for each project
    project_credit_limit = fields.Float('Credit Limit', digits=(15, 2), readonly=True)  # TODO: get credit limit on each project if exists
    proj_account_balance = fields.Float('Account Balance', digits=(15, 2))
    proj_sun_account_balance = fields.Float('Sun Account Balance', digits=(15, 2), readonly=True)
    proj_sun_account_due = fields.Float('Sun Account Due', digits=(15, 2), readonly=True)
    proj_account_due = fields.Float('Current Due', digits=(15, 2))  # Current Due (payment days/28 mod 1,= numberof period.  Due Period
    proj_total_due = fields.Float('Total Due', digits=(15, 2))  # Current Due + Over Due
    proj_name_details = fields.Char(string='Project PT and Period and ...', readonly=True)
    prj_pay_days = fields.Integer(readonly=True)
    proj_over_due = fields.Float('Over Due', digits=(15, 2))
    sun_note = fields.Char(string="Note")

    # def load_details(self, cr, uid, ids, context=None):
    #     assert len(ids) == 1, 'This option should only be used for a single id at a time.'
    #     ctx = dict(context)
    #     ctx.update({
    #         'prj_credit_id': ids[0]
    #     })
    #     try:
    #         details_form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sun_credit_check',
    #                                                                               'wizard_records_form_view')[1]
    #     except ValueError:
    #         details_form_id = False
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'wizard.check.allocated',
    #         'view_id': details_form_id,
    #         'target': 'new',
    #         'context': ctx,
    #     }

    @api.multi
    def load_details(self,ids,context=None):
        #print ids
        #assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.ensure_one()
        ctx = dict(context)
        ctx.update({
            'prj_credit_id': ids[0]
        })
        try:
            details_form_id = self.env['ir.model.data'].get_object_reference('sun_credit_check', 'wizard_records_form_view')[1]
        except ValueError:
            details_form_id = False
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.check.allocated',
            'view_id': details_form_id,
            'target': 'new',
            'context': ctx,
        }

SunCreditCheckdetails()




    #def _calc_period(self,cr,uid,days_payment,context=None):
    #
    #    dt = datetime.date.today()
    #    ibm_period = dt.strftime("%Y%m")
    #
    #    #Ibm Test
    #    if days_payment > 0:
    #        _prd=days_payment/28
    #        dt=datetime.date.today()
    #        ibm_first_of_month = date(day=1, month=dt.month, year=dt.year)
    #        ibm_last_of_last_month = ibm_first_of_month - timedelta(days=1)
    #        ibm_reducred_period=ibm_last_of_last_month-relativedelta( months = int(_prd ))
    #        #ibm_pt_reduced_date = ibm_last_of_last_month - timedelta(days_payment)
    #        ibm_period = ibm_reducred_period.strftime("%Y%m")
    #
    #    ibm_list = list(ibm_period)
    #    ibm_list.insert(4,'0')
    #    ibm_period = "".join(ibm_list)
    #    return ibm_period



    #def validate_partner(self,cr,uid,param,context=None):
    #    if param['sun_account_code']==123:
    #        return 'OK'
    #    else:
    #        return 'Not OK'
