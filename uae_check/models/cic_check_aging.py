
from odoo import models, fields, api
from odoo import tools

class CicCheckAgingView(models.Model):
    _name = 'cic.check.aging.view'
    _description = 'Check Aging View'
    _auto = False
    _rec_name = "partner_id"

    # _columns = {
    #     'partner_id': fields.many2one('res.partner',"Partner",readonly=True),
    #     'project_id': fields.many2one('project.project',"Project",readonly=True),
    #     'non_cleared_cheque': fields.float("Non Cleared Cheque", readonly=True ),
    #     'current_month_cheque': fields.float("Current Month", readonly=True),
    #     'next_month': fields.float("Next Month", readonly=True),
    #     'one_plus_month': fields.float("+1 Month", readonly=True),
    #     'two_plus_month': fields.float("+2 Month", readonly=True),
    #     'three_plus_month': fields.float("+3+ Months", readonly=True),
    #     'amount': fields.float("Total Cheque in Hand", readonly=True),
    #
    # }

    partner_id = fields.Many2one('res.partner', "Partner", readonly=True)
    project_id = fields.Many2one('project.project', "Project", readonly=True)
    non_cleared_cheque = fields.Float("Non Cleared Cheque", readonly=True)
    current_month_cheque = fields.Float("Current Month", readonly=True)
    next_month = fields.Float("Next Month", readonly=True)
    one_plus_month = fields.Float("+1 Month", readonly=True)
    two_plus_month = fields.Float("+2 Month", readonly=True)
    three_plus_month = fields.Float("+3+ Months", readonly=True)
    amount = fields.Float("Total Cheque in Hand", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr,'cic_check_aging_view')
        self.env.cr.execute("""
         create or replace view cic_check_aging_view as (SELECT partner_id,project_id, max(id) as id, SUM(CASE  WHEN check_submission_date < current_date THEN  amount END) AS "non_cleared_cheque" ,
                    SUM(CASE  WHEN  extract(month from check_submission_date)   = extract(month from current_date) THEN  amount END) AS "current_month_cheque",
                    SUM(CASE  WHEN  extract(month from check_submission_date)  = extract(month from current_date) + 1    THEN  amount END) AS "next_month",
                    SUM(CASE  WHEN  extract(month from check_submission_date)  = extract(month from current_date) + 2    THEN  amount END) AS "one_plus_month",
                    SUM(CASE  WHEN  extract(month from check_submission_date)  = extract(month from current_date) + 3    THEN  amount END) AS "two_plus_month",
                    SUM(CASE  WHEN  extract(month from check_submission_date)  > extract(month from current_date) + 3    THEN  amount END) AS "three_plus_month",
                    sum(amount) as amount
                    FROM cic_check_receipt WHERE state <> 'cleared' and state <> 'replaced' Group By 1,2)

         """)

CicCheckAgingView()
