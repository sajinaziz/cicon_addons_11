from odoo import models, osv, fields, api


class cic_order_state_wizard(models.TransientModel):
    _name = 'cic.order.state.wizard'
    _description = "Change Order State"

    #state = fields.Selection([('delivered', 'Delivered'),('cancel', 'Cancel'),
    #TODO: to be remove Delivered State in case using DN Order
    state = fields.Selection([('delivered', 'Delivered'),('hold', 'On Hold'), ('transfer', 'Transfer')], string='Status', required=True)
    prod_order_ids = fields.Many2many('cicon.prod.order', 'order_state_wizard_rel', 'wizard_id', 'prod_order_id', string='Production Orders',required=True)

    @api.one
    def change_state(self):
        #TODO: Check Status before change
        _order_ids = [x.id for x in self.prod_order_ids]
        _orders = self.env['cicon.prod.order'].browse(_order_ids)
        return _orders.write({'state': self.state})


cic_order_state_wizard()

