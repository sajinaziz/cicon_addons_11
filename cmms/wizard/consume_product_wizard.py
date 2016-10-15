# from openerp import fields, models, api
#
#
# class ConsumeProductWizrad(models.Model):
#     _name = 'consume.product.wizard'
#     _description = "Consume Product Wizard"
#
#     name = fields.Char('Reference', required=True)
#     company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.user.company_id)
#     warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
#     picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')
#     src_location_id = fields.Many2one('stock.location', string='Stock Location', required=True)
#     consu_location_id = fields.Many2one('stock.location', string='Consumed Location', required=True)
#     consu_line_ids = fields.One2many('consume.product.line', 'consu_prod_wizard_id', string='Product Lines')
#
#     @api.onchange('picking_type_id')
#     def change_picking_type(self):
#         if self.picking_type_id:
#             self.src_location_id = self.picking_type_id.default_location_src_id
#             self.consu_location_id = self.picking_type_id.default_location_dest_id
#
#     @api.multi
#     def move_scrap(self):
#         """
#         Move the scrap/damaged product into scrap location
#         """
#         self.ensure_one()
#         _stock_move_obj = self.env['stock.move']
#         for move_prod in self.consu_line_ids:
#             if move_prod.product_qty <= 0:
#                 raise Warning('Please provide a positive quantity to scrap.')
#             default_val = {
#                 'name': 'Consume: ' + move_prod.store_line_id.product_id.name,
#                 'origin': self.name,
#                 'picking_type_id': self.picking_type_id.id,
#                 'product_id': move_prod.store_line_id.product_id.id,
#                 'location_id': self.src_location_id.id,
#                 'product_uom_qty': move_prod.store_line_id.quantity,
#                 'product_uom': move_prod.store_line_id.product_id.uom_id.id,
#                 'scrapped': True,
#                 'location_dest_id': self.consu_location_id.id,
#             }
#              #   'restrict_lot_id': self.restrict_lot_id.id,
#             scrap_move = _stock_move_obj.create(default_val)
#             scrap_move.action_done()
#         view = {'type': 'ir.actions.act_window_close'}
#         return view
#
#
# class ConsumeProductLine(models.Model):
#     _name = 'consume.product.line'
#     _description = "Consume Product Line"
#
#     consu_prod_wizard_id = fields.Many2one('consume.product.wizard', string='Consume Product Wizard', ondelete='cascade')
#     store_line_id = fields.Many2one('cmms.store.invoice.line', string='Store Invoice Line', required=True,ondelete='cascade')
#     product_id = fields.Many2one('product.product', related='store_line_id.product_id', string='Product',
#                                  readonly=True)
#     product_uom = fields.Many2one('product.uom', related='store_line_id.product_id.uom_id', readonly=True,
#                                   string='Product Unit of Measure')
#     product_qty = fields.Float(related='store_line_id.quantity', readonly=True, string='Quantity')
#
#
