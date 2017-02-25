from odoo import models,fields,api

class CiconPurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    employee_id = fields.Many2one('hr.employee', string='Requested By')
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id',
                                    readonly=True)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string="Designation", readonly=True)
    #user_id = fields.Many2one('res.users', string='Handled By', track_visibility='onchange')  # no need
    approved_by = fields.Many2one('hr.employee', string="Approved By", track_visibility='onchange')
    issue_date = fields.Date(string="Date Issue", track_visibility='onchange', default=fields.Date.context_today)
    received_date = fields.Date(string="Date Received by Procurement", track_visibility='onchange',
                                default=fields.Date.context_today)
    # company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id)

    # state = fields.Selection([
    #     ('purchase_req', 'PR'),
    #     ('draft', 'Draft PO'),
    #     ('sent', 'RFQ Sent'),
    #     ('to approve', 'To Approve'),
    #     ('purchase', 'Purchase Order'),
    #     ('done', 'Done'),
    #     ('cancel', 'Cancelled'),
    #
    # ], string='Status', readonly=True, select=True, copy=False, default='purchase_req', track_visibility='onchange')

    #state = fields.Selection(selection_add=[("purchase_req", "PR")], default='purchase_req')