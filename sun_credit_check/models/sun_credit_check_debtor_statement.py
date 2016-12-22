from odoo import models, fields, api
from lxml import etree

class SunCreditCheckDebtorStatement(models.Model):
    _name= 'sun.credit.check.debtor.statement'
    _description = "Debtor Statement"


    # _columns = {
    #     'sun_credit_check_id': fields.many2one('sun.credit.check', string='Sun Credit Check'),
    #     'acc_name':fields.char('Account Name'),
    #     'acc_code': fields.char('Account Code'),
    #     'acc_db': fields.char('Account DB'),
    #     'trans_date': fields.char('Transaction Date'),
    #     'trans_date_int': fields.integer('Transaction Date Dummy'),
    #     'acc_period': fields.char('Account Period'),
    #     'reference': fields.char('Reference'),
    #     'description': fields.char('Description'),
    #     'over_days': fields.integer('Extra Days'),
    #     'interest_rate':fields.float('Interest Rate'),
    #     'interest_amount':fields.float('Interest Amount'),
    #     'is_allocated':fields.boolean('Is Allocated'),
    #     'credit': fields.float('Credit'),
    #     'debit': fields.float('Debit'),
    #     'due': fields.boolean('Due'),
    #     'over_due': fields.boolean('Over Due'),
    # }

    sun_credit_check_id =  fields.Many2one('sun.credit.check', string='Sun Credit Check')
    acc_name = fields.Char('Account Name')
    acc_code = fields.Char('Account Code')
    acc_db = fields.Char('Account DB')
    trans_date = fields.Char('Transaction Date')
    trans_date_int = fields.Integer('Transaction Date Dummy')
    acc_period =  fields.Char('Account Period')
    reference =  fields.Char('Reference')
    description = fields.Char('Description')
    over_days = fields.Integer('Extra Days')
    interest_rate = fields.Float('Interest Rate')
    interest_amount = fields.Float('Interest Amount')
    is_allocated =  fields.Boolean('Is Allocated')
    credit = fields.Float('Credit')
    debit = fields.Float('Debit')
    due = fields.Boolean('Due')
    over_due = fields.Boolean('Over Due')


SunCreditCheckDebtorStatement()

