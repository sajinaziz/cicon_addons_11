from odoo import models, fields, api


class ProdPlanningWizard(models.Model):
    _name = 'cic.prod.plan.wizard'
    _description = "Production Plan Wizard"

    prod_order_ids = fields.Many2many('cicon.prod.order', 'prod_order_plan_wizard_rel', 'wizard_id', 'prod_order_id',

                                      string='Production Orders', required=True)
    prod_plan_id = fields.Many2one('cicon.prod.plan', required=True, string="Production Plan")
    load = fields.Integer("Load Priority", required=True)
    remarks = fields.Char("Remarks")

    @api.one
    def update_plan(self):
        #TODO: Check for Order Status
        _order_ids = [x.id for x in self.prod_order_ids]
        _orders = self.env['cicon.prod.order'].browse(_order_ids)
        return _orders.write({'plan_id': self.prod_plan_id.id, 'state': 'progress', 'load': self.load, 'remarks': self.remarks})

ProdPlanningWizard()


